"""Staged part receipts, conditional completion and truthful durable reconciliation."""

from __future__ import annotations

import contextlib
import os
from collections.abc import AsyncIterable, AsyncIterator, Sequence
from dataclasses import asdict

from batten.storage import (
    AbortReceipt,
    Condition,
    Digest,
    PartPage,
    PartReceipt,
    StorageError,
    UploadInfo,
    UploadRef,
    WriteReceipt,
)

from ._features import required
from ._filesystem import Filesystem, JSONMap, identifier, keys, regular
from ._observations import CURRENT
from ._part_pages import PartPages
from ._scope import Attempt, Scope, worker
from ._transfers import Transfers
from ._upload_state import UploadState, condition, part, receipt


class Uploads:
    def __init__(self, fs: Filesystem, transfers: Transfers):
        self.fs = fs
        self.transfers = transfers
        self.state = UploadState(fs)
        self.pages = PartPages(fs.limits)

    async def _get(
        self, scope: Scope, upload: UploadRef, expired: bool = False
    ) -> JSONMap:
        value = await worker(self.state.read, upload, scope.authority.identity, expired)
        extra: frozenset[str] = (
            frozenset({"resumable_upload"})
            if value["origin"] != scope.nonce
            else frozenset()
        )
        if extra and not value["resumable"]:
            raise StorageError("denied")
        digest = Digest(**value["digest"]) if value["digest"] else None
        extra |= required("write", condition(value["condition"]), digest)
        attempt = CURRENT.get()
        if attempt is not None:
            attempt.features |= extra
        await scope.authorize("write", value["key"], extra)
        return value

    async def begin(
        self, scope: Scope, key: str, requested: Condition, digest: Digest | None
    ) -> UploadInfo:
        keys(key, self.fs.limits)
        resumable = await scope.permits("write", key, "resumable_upload")
        result = await worker(
            self.state.begin,
            key,
            scope.authority.identity,
            digest,
            requested,
            scope.nonce,
            resumable,
        )
        if not resumable:
            scope.closers.add(
                lambda: worker(
                    self._abort, result.upload, scope.authority.identity, Attempt()
                )
            )
        return result

    async def status(self, scope: Scope, upload: UploadRef) -> UploadInfo:
        value = await self._get(scope, upload, True)
        return self.state.info(upload, value)

    async def write_part(
        self,
        scope: Scope,
        upload: UploadRef,
        number: int,
        source: bytes | AsyncIterable[bytes],
        expected: Digest | None,
        attempt: Attempt,
    ) -> PartReceipt:
        if not 1 <= number <= self.fs.limits.max_parts:
            raise StorageError("invalid_request")
        await self._get(scope, upload)
        value = await worker(self.state.claim, upload, scope.authority.identity, number)
        accepted: PartReceipt | None = None
        try:
            attempt.effect = "unknown"
            blob, size, digest = await self.transfers.stage(
                scope,
                value["key"],
                source,
                self.fs.limits.max_part_bytes,
                expected,
                value["busy"][str(number)],
            )
            if size == 0:
                raise StorageError("invalid_request")
            await scope.authorize("write", value["key"])
            accepted = PartReceipt(
                upload, number, size, blob, digest if expected else None
            )
            return accepted
        finally:
            await worker(
                self.state.release, upload, scope.authority.identity, number, accepted
            )

    async def list_parts(
        self, scope: Scope, upload: UploadRef, cursor: str | None, limit: int
    ) -> PartPage:
        if not 0 < limit <= self.fs.limits.max_page_items:
            raise StorageError("invalid_request")
        value = await self._get(scope, upload)
        accepted = sorted(
            (part(p) for p in value["parts"].values()), key=lambda p: p.part_number
        )
        return self.pages.page(
            scope, upload, value["parts_revision"], accepted, cursor, limit
        )

    def _claim_completion(
        self, upload: UploadRef, identity: str, parts: Sequence[PartReceipt]
    ) -> JSONMap:
        with self.fs.locked():
            value = self.state.read(upload, identity)
            manifest = [asdict(p) for p in parts]
            if value["state"] == "complete" and value["manifest"] == manifest:
                return value
            if value["state"] != "open" or value["busy"] or not parts:
                raise StorageError("upload_conflict")
            if [p.part_number for p in parts] != list(range(1, len(parts) + 1)):
                raise StorageError("upload_conflict")
            if len(parts) != len(value["parts"]) or any(
                p.upload != upload
                or asdict(p) != value["parts"].get(str(p.part_number))
                for p in parts
            ):
                raise StorageError("upload_conflict")
            if sum(p.size_bytes for p in parts) > self.fs.limits.max_object_bytes:
                raise StorageError("limit_exceeded")
            value["state"], value["manifest"] = "completing", manifest
            self.state.save(upload, value)
            return value

    async def _source(
        self, value: JSONMap, parts: Sequence[PartReceipt]
    ) -> AsyncIterator[bytes]:
        for p in parts:
            fd = await worker(
                regular, self.fs.blobs, identifier(p.token), on_cancel=os.close
            )
            try:
                consumed = 0
                while True:
                    data = await worker(os.read, fd, self.fs.limits.max_chunk_bytes)
                    if not data:
                        break
                    consumed += len(data)
                    if consumed > p.size_bytes:
                        raise StorageError("integrity_mismatch")
                    yield data
                if consumed != p.size_bytes:
                    raise StorageError("integrity_mismatch")
            finally:
                await worker(os.close, fd)

    async def complete(
        self,
        scope: Scope,
        upload: UploadRef,
        parts: Sequence[PartReceipt],
        attempt: Attempt,
    ) -> WriteReceipt:
        await self._get(scope, upload)
        value = await worker(
            self._claim_completion, upload, scope.authority.identity, parts
        )
        if value["state"] == "complete":
            previous = receipt(value["receipt"])
            if previous is None:
                raise StorageError("io_failure")
            return previous
        digest = Digest(**value["digest"]) if value["digest"] else None
        try:
            completed = await self.transfers.write(
                scope,
                value["key"],
                self._source(value, parts),
                condition(value["condition"]),
                digest,
                attempt,
            )
            value["state"], value["receipt"] = "complete", asdict(completed)
            await worker(self.state.save, upload, value)
            return completed
        except BaseException:
            value["state"] = "unknown" if attempt.effect == "unknown" else "open"
            await worker(self.state.save, upload, value)
            raise

    def _abort(
        self, upload: UploadRef, identity: str, attempt: Attempt
    ) -> AbortReceipt:
        with self.fs.locked():
            value = self.state.read(upload, identity)
            outcomes = {
                "complete": "already_complete",
                "aborted": "already_aborted",
                "completing": "unknown",
                "unknown": "unknown",
            }
            if value["state"] in outcomes:
                return AbortReceipt(outcomes[value["state"]])
            value["state"] = "aborting"
            self.state.save(upload, value)
            attempt.effect = "unknown"
            for entry in value["parts"].values():
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(identifier(entry["token"]), dir_fd=self.fs.blobs)
            value["parts"] = {}
            if value["busy"]:
                self.state.save(upload, value)
                return AbortReceipt("unknown")
            value["state"] = "aborted"
            self.state.save(upload, value)
            return AbortReceipt("aborted")

    async def abort(
        self, scope: Scope, upload: UploadRef, attempt: Attempt
    ) -> AbortReceipt:
        await self._get(scope, upload)
        return await worker(self._abort, upload, scope.authority.identity, attempt)
