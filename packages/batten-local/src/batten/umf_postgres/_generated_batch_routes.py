"""Snapshot checked Record exposure pins before selected request execution."""

from dataclasses import dataclass
from typing import Protocol


class _Ref(Protocol):
    @property
    def module(self) -> str: ...
    @property
    def id(self) -> str: ...


class _Field(Protocol):
    @property
    def module(self) -> str: ...
    @property
    def element(self) -> str: ...


class RecordRoot(Protocol):
    @property
    def ref(self) -> _Ref: ...
    @property
    def host_operation(self) -> str: ...
    @property
    def source_digest(self) -> str: ...
    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def binding_digest(self) -> str: ...
    @property
    def algebra_sha256(self) -> str: ...
    @property
    def primary_key_id(self) -> str: ...
    @property
    def fields(self) -> tuple[_Field, ...]: ...
    @property
    def key_wrappers(self) -> tuple[str, ...]: ...
    @property
    def field_wrappers(self) -> tuple[tuple[_Field, str], ...]: ...


@dataclass(frozen=True)
class RecordRoute:
    host_operation: str
    module: str
    record: str
    source_digest: str
    artifact_digest: str
    receipt_digest: str
    binding_digest: str
    algebra_sha256: str
    primary_key_id: str
    fields: tuple[tuple[str, str], ...]
    key_wrappers: tuple[str, ...]
    field_wrappers: tuple[tuple[tuple[str, str], str], ...]


def snapshot_route(operation: str, root: RecordRoot) -> RecordRoute:
    module, record = root.ref.module, root.ref.id
    fields = tuple((field.module, field.element) for field in root.fields)
    wrappers = tuple(
        ((field.module, field.element), wrapper)
        for field, wrapper in root.field_wrappers
    )
    values = (
        operation,
        root.host_operation,
        module,
        record,
        root.source_digest,
        root.artifact_digest,
        root.receipt_digest,
        root.binding_digest,
        root.algebra_sha256,
        root.primary_key_id,
        *root.key_wrappers,
        *(value for ref, wrapper in wrappers for value in (*ref, wrapper)),
        *(value for ref in fields for value in ref),
    )
    if any(type(value) is not str or not value for value in values):
        raise ValueError("Record root identity or pins differ")
    if operation != root.host_operation:
        raise ValueError("Record operation differs from route")
    return RecordRoute(
        operation,
        module,
        record,
        root.source_digest,
        root.artifact_digest,
        root.receipt_digest,
        root.binding_digest,
        root.algebra_sha256,
        root.primary_key_id,
        fields,
        tuple(root.key_wrappers),
        wrappers,
    )


__all__ = ["RecordRoot", "RecordRoute", "snapshot_route"]
