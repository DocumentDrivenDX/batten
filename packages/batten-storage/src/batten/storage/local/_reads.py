"""Immutable-generation range streams with authority checks at each delivery."""

from __future__ import annotations

import hashlib
import os
from collections.abc import AsyncIterator
from types import TracebackType

from batten.storage import (
    Condition,
    Digest,
    ObjectInfo,
    ReadSelection,
    StorageError,
    TransferVerification,
)

from ._budget import Reservation
from ._features import required
from ._filesystem import Filesystem, regular
from ._observations import count
from ._scope import Attempt, Scope, worker


class Read:
    def __init__(
        self,
        fs: Filesystem,
        scope: Scope,
        key: str,
        offset: int,
        length: int | None,
        condition: Condition,
        expected: Digest | None,
    ):
        self._fs, self._scope, self._key = fs, scope, key
        self._offset, self._length, self._condition = offset, length, condition
        self._expected = expected
        self._features = required(
            "read", condition, expected, offset != 0 or length is not None
        )
        self._fd = -1
        self.info = ObjectInfo(key, 0, None, None, None)
        self.selection = ReadSelection(0, 0, 0)
        self.verification: TransferVerification | None = None
        self._remaining = 0
        self._digest = hashlib.sha256()
        self._entered = False
        self._reservation: Reservation | None = None

    def _open(self) -> tuple[int, ObjectInfo, ReadSelection]:
        if self._offset < 0 or self._length is not None and self._length < 0:
            raise StorageError("invalid_request")
        with self._fs.locked():
            value = self._fs.record(self._key)
            self._fs.condition(value, self._condition)
            if value is None:
                raise StorageError("not_found")
            info = self._fs.info(value)
            if self._offset > info.size_bytes:
                raise StorageError("range_not_satisfiable")
            length = min(
                self._length if self._length is not None else info.size_bytes,
                info.size_bytes - self._offset,
            )
            if length > self._fs.limits.max_object_bytes:
                raise StorageError("limit_exceeded")
            fd = regular(self._fs.blobs, value["blob"])
            try:
                os.lseek(fd, self._offset, os.SEEK_SET)
            except BaseException:
                os.close(fd)
                raise
            return fd, info, ReadSelection(self._offset, length, info.size_bytes)

    async def _enter(self, attempt: Attempt) -> Read:
        if self._entered:
            raise StorageError("invalid_request")
        self._reservation = self._fs.budget.reserve()
        result = await worker(self._open, on_cancel=lambda value: os.close(value[0]))
        self._fd, self.info, self.selection = result
        self._remaining = self.selection.length
        self._entered = True
        self._scope.closers.add(self.aclose)
        return self

    async def __aenter__(self) -> Read:
        try:
            return await self._scope.run(
                "read", self._key, self._enter, features=self._features
            )
        except BaseException:
            await self.aclose()
            raise

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def _next(self, attempt: Attempt) -> bytes:
        if self._remaining == 0:
            actual = Digest("sha256", self._digest.hexdigest())
            if self._expected is not None:
                if actual != self._expected:
                    raise StorageError("integrity_mismatch")
                self.verification = TransferVerification(actual, "delivered")
            await self.aclose()
            return b""
        size = min(self._remaining, self._fs.limits.max_chunk_bytes)
        value = await worker(os.read, self._fd, size)
        if not value:
            raise StorageError("io_failure")
        self._remaining -= len(value)
        count("bytes_read", len(value))
        self._digest.update(value)
        return value

    async def __anext__(self) -> bytes:
        if not self._entered:
            raise StorageError("invalid_request")
        if self._fd < 0:
            raise StopAsyncIteration
        try:
            value = await self._scope.run(
                "read", self._key, self._next, features=self._features
            )
            if not value:
                raise StopAsyncIteration
            return value
        except BaseException:
            await self.aclose()
            raise

    async def aclose(self) -> None:
        if self._fd >= 0:
            fd, self._fd = self._fd, -1
            await worker(os.close, fd)
        if self._reservation is not None:
            self._reservation.release()
        self._scope.closers.discard(self.aclose)
