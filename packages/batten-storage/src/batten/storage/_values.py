"""Immutable portable values, independent of every concrete provider."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, fields


class StorageError(Exception):
    def __init__(self, code: str, effect: str = "none", incident_id: str | None = None):
        self.code = code
        self.effect = effect
        self.incident_id = incident_id or uuid.uuid4().hex
        super().__init__(f"{code} ({self.incident_id})")


@dataclass(frozen=True, slots=True)
class Limits:
    max_object_bytes: int
    max_chunk_bytes: int
    max_page_items: int
    max_scan_entries: int
    max_key_bytes: int
    max_depth: int
    max_cursor_bytes: int
    cursor_ttl_seconds: int
    operation_timeout_ms: int
    max_transfer_buffer_bytes: int
    max_active_transfers: int
    max_parts: int
    max_part_bytes: int
    max_active_uploads: int
    max_retained_uploads: int
    upload_ttl_seconds: int
    max_parallel_parts: int
    max_backend_requests_per_page: int
    max_page_buffer_bytes: int
    max_retry_attempts: int

    def __post_init__(self) -> None:
        if any(
            type(getattr(self, f.name)) is not int or getattr(self, f.name) <= 0
            for f in fields(self)
        ):
            raise StorageError("invalid_request")
        if (
            self.max_chunk_bytes * self.max_active_transfers
            > self.max_transfer_buffer_bytes
        ):
            raise StorageError("invalid_request")


@dataclass(frozen=True, slots=True)
class Any:
    kind: str = field(default="any", init=False)


@dataclass(frozen=True, slots=True)
class Absent:
    kind: str = field(default="absent", init=False)


@dataclass(frozen=True, slots=True)
class Matches:
    version: str | None
    kind: str = field(default="matches", init=False)

    def __post_init__(self) -> None:
        if not self.version:
            raise StorageError("invalid_request")


ReadCondition = Any | Matches
WriteCondition = Any | Absent | Matches
Condition = WriteCondition


@dataclass(frozen=True, slots=True)
class Digest:
    algorithm: str
    hex: str

    def __post_init__(self) -> None:
        if self.algorithm != "sha256" or not re.fullmatch("[a-f0-9]{64}", self.hex):
            raise StorageError("invalid_request")


@dataclass(frozen=True, slots=True)
class ObjectInfo:
    key: str
    size_bytes: int
    modified_at: str | None
    version: str | None
    validator_kind: str | None = "revision"


@dataclass(frozen=True, slots=True)
class TransferVerification:
    digest: Digest
    scope: str


@dataclass(frozen=True, slots=True)
class WriteReceipt:
    info: ObjectInfo
    verification: TransferVerification | None = None
    outcome: str = "complete"


@dataclass(frozen=True, slots=True)
class DeleteReceipt:
    outcome: str


@dataclass(frozen=True, slots=True)
class ReadSelection:
    offset: int
    length: int
    object_size_bytes: int


@dataclass(frozen=True, slots=True)
class KeyEntry:
    key: str


@dataclass(frozen=True, slots=True)
class ListEntry:
    key: str
    size_bytes: int | None = None
    modified_at: str | None = None
    version: str | None = None
    validator_kind: str | None = None


@dataclass(frozen=True, slots=True)
class ListPage:
    items: tuple[KeyEntry | ListEntry, ...]
    common_prefixes: tuple[str, ...]
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class UploadRef:
    id: str


@dataclass(frozen=True, slots=True)
class PartReceipt:
    upload: UploadRef
    part_number: int
    size_bytes: int
    token: str
    digest: Digest | None = None


@dataclass(frozen=True, slots=True)
class PartPage:
    items: tuple[PartReceipt, ...]
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class UploadInfo:
    upload: UploadRef
    state: str
    min_part_bytes: int
    max_part_bytes: int
    max_parts: int
    expires_at: str
    receipt: WriteReceipt | None = None


@dataclass(frozen=True, slots=True)
class AbortReceipt:
    outcome: str


@dataclass(frozen=True, slots=True)
class ProviderProfile:
    features: frozenset[str]
    concurrency_domain: str
    publication: str
    limits: Limits
