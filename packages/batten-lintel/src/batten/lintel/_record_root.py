"""Explicit Record-root exposure pins, separate from source commands."""

from dataclasses import dataclass

from lintel.ports import ElementRef, OperationRef


@dataclass(frozen=True)
class ExposureRecordRoot:
    ref: OperationRef
    host_operation: str
    source_digest: str
    artifact_digest: str
    receipt_digest: str
    binding_digest: str
    algebra_sha256: str
    primary_key_id: str
    fields: tuple[ElementRef, ...]
    key_wrappers: tuple[str, ...]
    field_wrappers: tuple[tuple[ElementRef, str], ...]
    nullable_fields: tuple[ElementRef, ...] = ()

    def __post_init__(self) -> None:
        if type(self.ref) is not OperationRef:
            raise ValueError("Record exposure requires an exact qualified reference")
        for name in ("fields", "nullable_fields"):
            values = tuple(getattr(self, name))
            if any(type(value) is not ElementRef for value in values):
                raise ValueError("Record exposure requires qualified Field references")
            object.__setattr__(self, name, values)
        object.__setattr__(self, "key_wrappers", tuple(self.key_wrappers))
        object.__setattr__(
            self, "field_wrappers", tuple(tuple(pair) for pair in self.field_wrappers)
        )
