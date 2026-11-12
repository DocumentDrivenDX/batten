"""Shared generated-provider input snapshots and read-profile refusals."""

from collections.abc import Mapping
from typing import cast

from batten.contracts import OperationCall, OperationOutcome


def snapshot_inputs(values: Mapping[str, object], maximum: int) -> dict[str, object]:
    """Snapshot exact scalar wire values before awaiting authority or native I/O."""
    copied: dict[str, object] = {}
    used = 0
    for name, value in values.items():
        if type(name) is not str or not name:
            raise ValueError("invalid input identity")
        used += len(name.encode("utf-8"))
        if used > maximum or len(copied) >= 4096:
            raise ValueError("input capacity exceeded")
        if value is None:
            copied[name] = None
            continue
        if (
            not isinstance(value, Mapping)
            or len(cast(Mapping[object, object], value)) != 1
        ):
            raise ValueError("unsupported input shape")
        wrapper, scalar = next(iter(cast(Mapping[object, object], value).items()))
        if not isinstance(wrapper, str) or type(scalar) not in {str, bool}:
            raise ValueError("unsupported input shape")
        used += len(wrapper.encode("utf-8")) + len(str(scalar).encode("utf-8"))
        if used > maximum or len(copied) >= 4096:
            raise ValueError("input capacity exceeded")
        copied[name] = {wrapper: scalar}
    return copied


def read_refusal(call: OperationCall) -> OperationOutcome | None:
    if call.scope is None or call.scope.principal != call.actor:
        return OperationOutcome("denied", "", {}, "scope_invalid")
    if call.phase != "invoke" or call.key is not None or call.confirmation is not None:
        return OperationOutcome("invalid", "", {}, "unsupported")
    if call.scope.consistency not in {None, "statement"}:
        return OperationOutcome("invalid", "", {}, "unsupported")
    if call.actor.kind not in {"person", "batch"} or call.actor.delegation is not None:
        return OperationOutcome("denied", "", {}, "authority_unsupported")
    return None


def native_read_refusal(result: Mapping[str, object], schema: str) -> OperationOutcome:
    """Preserve the upstream fixed error vocabulary without exposing diagnostics."""
    status, code = "unavailable", "native_refused"
    error = result.get("error")
    if (
        set(result) == {"schema", "error"}
        and result["schema"] == schema
        and isinstance(error, Mapping)
    ):
        value = cast(Mapping[str, object], error)
        native_code = value.get("code")
        if set(value) == {"code"} and type(native_code) is str:
            status, code = {
                "DENIED": ("denied", "denied"),
                "INVALID": ("invalid", "invalid"),
                "INVALID_CURSOR": ("invalid", "invalid_cursor"),
                "PRECONDITION_FAILED": ("precondition_failed", "precondition_failed"),
                "LIMIT_EXCEEDED": ("unavailable", "limit_exceeded"),
                "TOO_MANY_ROWS": ("unavailable", "limit_exceeded"),
                "SCHEMA_MISMATCH": ("unavailable", "schema_mismatch"),
                "BUSY": ("unavailable", "busy"),
            }.get(native_code, (status, code))
    return OperationOutcome(status, "", {}, code)
