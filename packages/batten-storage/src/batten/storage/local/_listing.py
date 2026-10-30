"""Bounded descriptor traversal; opaque cursors retain exact scan progress."""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Protocol

from batten.storage import KeyEntry, ListEntry, ListPage, StorageError

from ._budget import Reservation
from ._filesystem import Filesystem, directory, keys
from ._observations import count
from ._pages import PageBuffer
from ._scope import Scope, worker


class Entries(Protocol):
    def __next__(self) -> os.DirEntry[str]: ...
    def __iter__(self) -> Iterator[os.DirEntry[str]]: ...
    def close(self) -> None: ...


@dataclass
class Frame:
    fd: int
    iterator: Entries
    prefix: str

    def close(self) -> None:
        self.iterator.close()
        os.close(self.fd)


def frame(fd: int, prefix: str) -> Frame:
    try:
        return Frame(fd, os.scandir(fd), prefix)
    except BaseException:
        os.close(fd)
        raise


def next_entry(current: Frame) -> tuple[str, bool] | None:
    entry = next(current.iterator, None)
    if entry is None:
        return None
    if entry.is_symlink():
        raise StorageError("path_conflict")
    return entry.name, entry.is_dir(follow_symlinks=False)


@dataclass
class Cursor:
    owner: str
    scope: Scope
    options: tuple[str, bool, str, int]
    frames: list[Frame]
    expiry: float
    reservation: Reservation
    busy: bool = False
    pending: tuple[str, bool] | None = None
    guard: Lock = field(default_factory=Lock)

    def close(self) -> None:
        with self.guard:
            for current in self.frames:
                current.close()
            self.frames.clear()
            self.reservation.release()


class Listing:
    def __init__(self, filesystem: Filesystem):
        self.fs = filesystem
        self.cursors: dict[str, Cursor] = {}

    def _start(self, prefix: str) -> Frame | None:
        fd = os.dup(self.fs.objects)
        try:
            encoded = keys(prefix[:-1], self.fs.limits) if prefix else []
            for part in encoded:
                child = directory(fd, "d" + part)
                os.close(fd)
                fd = child
            return frame(fd, prefix)
        except FileNotFoundError:
            os.close(fd)
            return None
        except BaseException:
            os.close(fd)
            raise

    async def _cursor(
        self, scope: Scope, options: tuple[str, bool, str, int], token: str | None
    ) -> tuple[str, Cursor]:
        if token is not None:
            state = self.cursors.get(token)
            if (
                state is None
                or state.owner != scope.authority.identity
                or state.scope is not scope
                or state.options != options
                or state.busy
            ):
                raise StorageError("cursor_invalid")
            if time.monotonic() >= state.expiry:
                await worker(state.close)
                self.cursors.pop(token, None)
                raise StorageError("cursor_expired")
            return token, state
        for old, stale in tuple(self.cursors.items()):
            if not stale.busy and time.monotonic() >= stale.expiry:
                await worker(stale.close)
                self.cursors.pop(old, None)
        if len(self.cursors) >= self.fs.limits.max_active_transfers:
            raise StorageError("limit_exceeded")
        reservation = self.fs.budget.reserve()
        try:
            first = await worker(
                self._start, options[0], on_cancel=lambda f: f.close() if f else None
            )
            state = Cursor(
                scope.authority.identity,
                scope,
                options,
                [first] if first else [],
                time.monotonic() + self.fs.limits.cursor_ttl_seconds,
                reservation,
            )
        except BaseException:
            reservation.release()
            raise
        token = uuid.uuid4().hex
        if len(token.encode()) > self.fs.limits.max_cursor_bytes:
            await worker(state.close)
            raise StorageError("limit_exceeded")
        self.cursors[token] = state
        return token, state

    async def _candidate(self, state: Cursor) -> tuple[str, bool] | None:
        if state.pending is not None:
            candidate, state.pending = state.pending, None
            return candidate
        current = state.frames[-1]
        candidate = await worker(next_entry, current)
        if candidate is None:
            await worker(current.close)
            state.frames.pop()
            return None
        count("scanned_entries", 1)
        name, is_directory = candidate
        if not name or name[0] not in "do":
            return None
        try:
            logical = bytes.fromhex(name[1:]).decode()
        except (UnicodeError, ValueError):
            raise StorageError("io_failure") from None
        key = current.prefix + logical
        keys(key, self.fs.limits)
        if (name[0] == "d") != is_directory:
            raise StorageError("path_conflict")
        return key, is_directory

    async def _page(
        self, scope: Scope, state: Cursor
    ) -> tuple[tuple[KeyEntry | ListEntry, ...], tuple[str, ...]]:
        _prefix, recursive, detail, limit = state.options
        buffer = PageBuffer(self.fs.limits.max_page_buffer_bytes, detail)
        requests = 0
        while state.frames and len(buffer.items) + len(buffer.prefixes) < limit:
            if requests >= min(
                self.fs.limits.max_scan_entries,
                self.fs.limits.max_backend_requests_per_page,
            ):
                break
            requests += 1
            candidate = await self._candidate(state)
            if candidate is None:
                continue
            key, is_directory = candidate
            try:
                await scope.authorize("list", key + "/" if is_directory else key)
            except StorageError as error:
                if error.code != "denied":
                    raise
                continue
            if is_directory and recursive:
                parent = state.frames[-1]
                child = await worker(
                    directory,
                    parent.fd,
                    "d" + key.removeprefix(parent.prefix).encode().hex(),
                    on_cancel=os.close,
                )
                state.frames.append(
                    await worker(frame, child, key + "/", on_cancel=lambda f: f.close())
                )
            elif not buffer.append(key, is_directory):
                state.pending = (key, is_directory)
                break
        return tuple(buffer.items), tuple(buffer.prefixes)

    async def list(
        self,
        scope: Scope,
        prefix: str,
        recursive: bool,
        detail: str,
        token: str | None,
        limit: int,
    ) -> ListPage:
        if not 0 < limit <= self.fs.limits.max_page_items or detail not in {
            "keys",
            "basic",
        }:
            raise StorageError("invalid_request")
        if prefix and not prefix.endswith("/"):
            raise StorageError("invalid_key")
        if prefix:
            keys(prefix[:-1], self.fs.limits)
        token, state = await self._cursor(
            scope, (prefix, recursive, detail, limit), token
        )
        state.busy = True
        try:
            items, prefixes = await self._page(scope, state)
            await scope.authorize("list", prefix)
            page = ListPage(items, prefixes, token if state.frames else None)
            if (
                len(json.dumps(asdict(page)).encode())
                > self.fs.limits.max_page_buffer_bytes
            ):
                raise StorageError("limit_exceeded")
            self.cursors.pop(token, None)
            if page.next_cursor is None:
                await worker(state.close)
            else:
                fresh = uuid.uuid4().hex
                state.expiry = time.monotonic() + self.fs.limits.cursor_ttl_seconds
                self.cursors[fresh] = state
                page = ListPage(items, prefixes, fresh)
            count("returned_items", len(items) + len(prefixes))
            return page
        except BaseException:
            await worker(state.close)
            self.cursors.pop(token, None)
            raise
        finally:
            state.busy = False

    async def close_scope(self, scope: Scope) -> None:
        for token, state in tuple(self.cursors.items()):
            if state.scope is scope:
                await worker(state.close)
                self.cursors.pop(token, None)

    async def close(self) -> None:
        for state in self.cursors.values():
            await worker(state.close)
        self.cursors.clear()
