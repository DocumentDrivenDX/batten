"""Whitelist safe host errors without echoing provider diagnostics."""

import sys
from typing import cast

from lintel.ports import ExecutionError, ExecutionErrorCode


def failure(status: str, code: str | None) -> ExecutionError:
    aliases = {
        "not_admitted": "API_MISMATCH",
        "scope_invalid": "DENIED",
        "deadline_exceeded": "LIMIT_EXCEEDED",
        "limit_exceeded": "LIMIT_EXCEEDED",
        "invalid_selection": "INVALID",
        "unsupported_selection": "UNSUPPORTED",
        "invalid_key": "INVALID",
        "timeout": "BUSY",
        "SCHEMA_MISMATCH": "API_MISMATCH",
    }
    public = aliases.get(code or "", (code or "").upper())
    try:
        return ExecutionError(cast(ExecutionErrorCode, public))
    except ValueError:
        return ExecutionError("DENIED" if status == "denied" else "BUSY")


def native_failure(error: BaseException) -> ExecutionError:
    """Consume only the public nominal native error class and its fixed code."""
    kind: object = getattr(
        sys.modules.get("umf_access.unified"), "GeneratedNativeError", None
    )
    current: BaseException | None = error
    for _ in range(8):
        if current is None:
            break
        if isinstance(kind, type) and type(current) is kind:
            code: object = getattr(current, "code", None)
            if type(code) is str and code in {
                "DENIED",
                "INVALID",
                "UNSUPPORTED",
                "LIMIT_EXCEEDED",
                "SCHEMA_MISMATCH",
                "PRECONDITION_FAILED",
                "BUSY",
            }:
                return failure("denied" if code == "DENIED" else "unavailable", code)
        if isinstance(current, TimeoutError):
            return ExecutionError("LIMIT_EXCEEDED")
        current = current.__cause__
    return ExecutionError("BUSY")
