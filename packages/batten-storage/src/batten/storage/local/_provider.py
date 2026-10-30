"""Local composition and the public storage facade; optional imports stay here."""

from __future__ import annotations

import os
from collections.abc import AsyncIterable, Sequence
from pathlib import Path

from batten.storage import (
    AbortReceipt,
    Absent,
    Any,
    Authority,
    Condition,
    DeleteReceipt,
    Digest,
    Limits,
    ListPage,
    ObjectInfo,
    PartPage,
    PartReceipt,
    ProviderProfile,
    ReadCondition,
    StorageError,
    UploadInfo,
    UploadRef,
    WriteReceipt,
)

from ._features import required
from ._filesystem import Filesystem, initialize_sync
from ._listing import Listing
from ._reads import Read
from ._scope import Attempt, Scope, translate, worker
from ._transfers import Transfers
from ._uploads import Uploads


class LocalProvider:
    def __init__(self, root: Path, limits: Limits):
        if not root.is_absolute():
            raise StorageError("invalid_request")
        (self.root, self.limits) = (root, limits)
        self.fs = Filesystem(root, limits)
        self.transfers = Transfers(self.fs)
        self.uploads = Uploads(self.fs, self.transfers)
        self.listing = Listing(self.fs)
        self.scopes: set[Scope] = set()
        self.ready = False
        self.profile = ProviderProfile(
            frozenset({
                "create_only",
                "conditional_replace",
                "conditional_delete",
                "conditional_read",
                "read_range",
                "multipart_upload",
                "resumable_upload",
                "verified_transfer",
                "atomic_publish",
            }),
            "adapter_managed",
            "atomic_replace",
            limits,
        )

    async def prepare(self) -> None:
        if self.ready:
            return
        try:
            await worker(self.fs.prepare)
            self.ready = True
        except BaseException as error:
            await worker(self.fs.close)
            if isinstance(error, Exception):
                raise translate(error, "none") from None
            raise

    def bind(self, authority: Authority) -> LocalStore:
        if len(self.scopes) >= self.limits.max_active_transfers:
            raise StorageError("limit_exceeded")
        scope = Scope(authority, self.limits.operation_timeout_ms, lambda: self.ready)
        self.scopes.add(scope)
        scope.closers.add(lambda: self.listing.close_scope(scope))
        scope.closers.add(lambda: self.uploads.pages.close_scope(scope))
        return LocalStore(self, scope)

    async def aclose(self) -> None:
        self.ready = False
        for scope in tuple(self.scopes):
            await scope.close()
        self.scopes.clear()
        await self.listing.close()
        await worker(self.fs.close)


class LocalStore:
    def __init__(self, provider: LocalProvider, scope: Scope):
        (self._provider, self._scope) = (provider, scope)

    def open_read(
        self,
        key: str,
        *,
        offset: int = 0,
        length: int | None = None,
        condition: ReadCondition = Any(),
        expected_digest: Digest | None = None,
    ) -> Read:
        return Read(
            self._provider.fs,
            self._scope,
            key,
            offset,
            length,
            condition,
            expected_digest,
        )

    async def stat(self, key: str, *, condition: ReadCondition = Any()) -> ObjectInfo:
        return await self._scope.run(
            "stat",
            key,
            lambda a: self._provider.transfers.stat(key, condition),
            features=required("read", condition),
        )

    async def write(
        self,
        key: str,
        source: bytes | AsyncIterable[bytes],
        *,
        condition: Condition = Absent(),
        expected_digest: Digest | None = None,
    ) -> WriteReceipt:
        return await self._scope.run(
            "write",
            key,
            lambda a: self._provider.transfers.write(
                self._scope, key, source, condition, expected_digest, a
            ),
            features=required("write", condition, expected_digest),
        )

    def _delete(
        self, key: str, condition: Condition, attempt: Attempt
    ) -> DeleteReceipt:
        fs = self._provider.fs
        with fs.locked():
            value = fs.record(key)
            fs.condition(value, condition)
            if value is None:
                return DeleteReceipt("absent")
            with fs.parent(key) as (fd, name):
                attempt.effect = "unknown"
                os.unlink(name, dir_fd=fd)
            os.unlink(value["blob"], dir_fd=fs.blobs)
            return DeleteReceipt("deleted")

    async def delete(
        self, key: str, *, condition: ReadCondition = Any()
    ) -> DeleteReceipt:
        return await self._scope.run(
            "delete",
            key,
            lambda a: worker(self._delete, key, condition, a),
            features=required("delete", condition),
        )

    async def list(
        self,
        *,
        prefix: str = "",
        recursive: bool = False,
        detail: str = "keys",
        cursor: str | None = None,
        limit: int,
    ) -> ListPage:
        return await self._scope.run(
            "list",
            prefix,
            lambda a: self._provider.listing.list(
                self._scope, prefix, recursive, detail, cursor, limit
            ),
        )

    async def begin_upload(
        self,
        key: str,
        *,
        condition: Condition = Absent(),
        expected_digest: Digest | None = None,
    ) -> UploadInfo:
        return await self._scope.run(
            "write",
            key,
            lambda a: self._provider.uploads.begin(
                self._scope, key, condition, expected_digest
            ),
            features=required("write", condition, expected_digest)
            | frozenset({"multipart_upload"}),
        )

    async def upload_status(self, upload: UploadRef) -> UploadInfo:
        return await self._scope.run(
            "write",
            "",
            lambda a: self._provider.uploads.status(self._scope, upload),
            features=frozenset({"multipart_upload"}),
        )

    async def write_part(
        self,
        upload: UploadRef,
        part_number: int,
        source: bytes | AsyncIterable[bytes],
        *,
        expected_digest: Digest | None = None,
    ) -> PartReceipt:
        return await self._scope.run(
            "write",
            "",
            lambda a: self._provider.uploads.write_part(
                self._scope, upload, part_number, source, expected_digest, a
            ),
            features=required("write", Any(), expected_digest)
            | frozenset({"multipart_upload"}),
        )

    async def list_parts(
        self, upload: UploadRef, *, cursor: str | None = None, limit: int
    ) -> PartPage:
        return await self._scope.run(
            "write",
            "",
            lambda a: self._provider.uploads.list_parts(
                self._scope, upload, cursor, limit
            ),
            features=frozenset({"multipart_upload"}),
        )

    async def complete_upload(
        self, upload: UploadRef, parts: Sequence[PartReceipt]
    ) -> WriteReceipt:
        return await self._scope.run(
            "write",
            "",
            lambda a: self._provider.uploads.complete(self._scope, upload, parts, a),
            features=frozenset({"multipart_upload"}),
        )

    async def abort_upload(self, upload: UploadRef) -> AbortReceipt:
        return await self._scope.run(
            "write",
            "",
            lambda a: self._provider.uploads.abort(self._scope, upload, a),
            features=frozenset({"multipart_upload"}),
        )

    async def aclose(self) -> None:
        await self._scope.close()
        self._provider.scopes.discard(self._scope)


def create_store(root: Path, limits: Limits) -> LocalProvider:
    return LocalProvider(root, limits)


async def initialize(root: Path) -> None:
    try:
        await worker(initialize_sync, root)
    except Exception as error:
        raise translate(error, "none") from None
