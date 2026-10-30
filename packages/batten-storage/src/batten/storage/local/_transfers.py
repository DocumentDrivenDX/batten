"""Bounded immutable transfer staging and conditional publication."""

from __future__ import annotations

import contextlib
import hashlib
import os
import uuid
from collections.abc import AsyncIterable, AsyncIterator
from typing import BinaryIO

from batten.storage import (
    Condition,
    Digest,
    ObjectInfo,
    StorageError,
    TransferVerification,
    WriteReceipt,
)

from ._filesystem import Filesystem, identifier, regular
from ._observations import count
from ._scope import Attempt, Scope, worker


async def chunks(
    source: bytes | AsyncIterable[bytes], maximum: int
) -> AsyncIterator[bytes]:
    if isinstance(source, bytes):
        for offset in range(0, len(source), maximum):
            yield source[offset : offset + maximum]
    else:
        async for part in source:
            if len(part) > maximum:
                raise StorageError("limit_exceeded")
            if part:
                yield part


def write_all(target: BinaryIO, data: bytes) -> int:
    offset = 0
    while offset < len(data):
        written = target.write(memoryview(data)[offset:])
        if written <= 0:
            raise OSError("write made no progress")
        offset += written
    return offset


def open_blob(fs: Filesystem, blob: str) -> BinaryIO:
    fd = regular(fs.blobs, identifier(blob), os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    return os.fdopen(fd, "wb", buffering=0)


def discard_blob(target: BinaryIO, fs: Filesystem, blob: str) -> None:
    target.close()
    with contextlib.suppress(FileNotFoundError):
        os.unlink(identifier(blob), dir_fd=fs.blobs)


class Transfers:
    def __init__(self, filesystem: Filesystem):
        self.fs = filesystem
        self.active = 0

    async def stage(
        self,
        scope: Scope,
        key: str,
        source: bytes | AsyncIterable[bytes],
        maximum: int,
        expected: Digest | None,
        reserved_blob: str | None = None,
    ) -> tuple[str, int, Digest]:
        reservation = self.fs.budget.reserve()
        blob = reserved_blob or uuid.uuid4().hex
        target: BinaryIO | None = None
        size = 0
        digest = hashlib.sha256()
        try:
            target = await worker(
                open_blob,
                self.fs,
                blob,
                on_cancel=lambda file: discard_blob(file, self.fs, blob),
            )
            async for part in chunks(source, self.fs.limits.max_chunk_bytes):
                await scope.authorize("write", key)
                size += len(part)
                if size > maximum:
                    raise StorageError("limit_exceeded")
                await worker(write_all, target, part)
                count("bytes_written", len(part))
                digest.update(part)
            result = Digest("sha256", digest.hexdigest())
            if expected is not None and result != expected:
                raise StorageError("integrity_mismatch")
            return blob, size, result
        except BaseException:
            if target is not None:
                await worker(discard_blob, target, self.fs, blob)
            raise
        finally:
            if target is not None:
                await worker(target.close)
            reservation.release()

    async def write(
        self,
        scope: Scope,
        key: str,
        source: bytes | AsyncIterable[bytes],
        condition: Condition,
        expected: Digest | None,
        attempt: Attempt,
    ) -> WriteReceipt:
        from ._filesystem import keys

        keys(key, self.fs.limits)
        blob, size, digest = await self.stage(
            scope, key, source, self.fs.limits.max_object_bytes, expected
        )
        try:
            await scope.authorize("write", key)
            info = await worker(self.fs.publish, key, blob, size, condition, attempt)
            verification = TransferVerification(digest, "source") if expected else None
            return WriteReceipt(info, verification)
        except BaseException:
            if attempt.effect == "none":
                with contextlib.suppress(FileNotFoundError):
                    await worker(os.unlink, blob, dir_fd=self.fs.blobs)
            raise

    async def stat(self, key: str, condition: Condition) -> ObjectInfo:
        def observe() -> ObjectInfo:
            value = self.fs.record(key)
            self.fs.condition(value, condition)
            if value is None:
                raise StorageError("not_found")
            return self.fs.info(value)

        return await worker(observe)
