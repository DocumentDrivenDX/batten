"""Public host ports; executable trust is supplied by composition, never app data."""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from ._values import (
    AbortReceipt,
    Absent,
    Any,
    Condition,
    DeleteReceipt,
    Digest,
    ListPage,
    ObjectInfo,
    PartPage,
    PartReceipt,
    ReadCondition,
    ReadSelection,
    TransferVerification,
    UploadInfo,
    UploadRef,
    WriteReceipt,
)


class Authority(Protocol):
    @property
    def identity(self) -> str: ...
    async def check(
        self, operation: str, key: str, features: frozenset[str]
    ) -> None: ...
    async def observe(
        self,
        operation: str,
        code: str,
        effect: str,
        incident_id: str,
        metrics: Mapping[str, int | float | None],
    ) -> None: ...


class ObjectRead(Protocol):
    info: ObjectInfo
    selection: ReadSelection
    verification: TransferVerification | None

    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def aclose(self) -> None: ...


class ObjectStore(Protocol):
    def open_read(
        self,
        key: str,
        *,
        offset: int = 0,
        length: int | None = None,
        condition: ReadCondition = Any(),
        expected_digest: Digest | None = None,
    ) -> AbstractAsyncContextManager[ObjectRead]: ...
    async def stat(
        self, key: str, *, condition: ReadCondition = Any()
    ) -> ObjectInfo: ...
    async def write(
        self,
        key: str,
        source: bytes | AsyncIterable[bytes],
        *,
        condition: Condition = Absent(),
        expected_digest: Digest | None = None,
    ) -> WriteReceipt: ...
    async def delete(
        self, key: str, *, condition: ReadCondition = Any()
    ) -> DeleteReceipt: ...
    async def list(
        self,
        *,
        prefix: str = "",
        recursive: bool = False,
        detail: str = "keys",
        cursor: str | None = None,
        limit: int,
    ) -> ListPage: ...
    async def begin_upload(
        self,
        key: str,
        *,
        condition: Condition = Absent(),
        expected_digest: Digest | None = None,
    ) -> UploadInfo: ...
    async def upload_status(self, upload: UploadRef) -> UploadInfo: ...
    async def write_part(
        self,
        upload: UploadRef,
        part_number: int,
        source: bytes | AsyncIterable[bytes],
        *,
        expected_digest: Digest | None = None,
    ) -> PartReceipt: ...
    async def list_parts(
        self, upload: UploadRef, *, cursor: str | None = None, limit: int
    ) -> PartPage: ...
    async def complete_upload(
        self, upload: UploadRef, parts: Sequence[PartReceipt]
    ) -> WriteReceipt: ...
    async def abort_upload(self, upload: UploadRef) -> AbortReceipt: ...
    async def aclose(self) -> None: ...


class StorageContext(Protocol):
    def storage(self, resource: str) -> ObjectStore: ...


def for_resource(context: StorageContext, resource: str) -> ObjectStore:
    return context.storage(resource)
