"""Exact command outcome projection; no command dispatch occurs here."""

from collections.abc import Mapping
from typing import Literal, cast

from batten.lintel import _decode
from batten.lintel._config import ExposureOperation

from lintel.ports import CommandResult, ExecutionError


def command_result(
    value: Mapping[str, object],
    exposure: ExposureOperation,
    invocation_key: str,
    phase: str,
) -> CommandResult:
    payload = _decode.object_value(
        value,
        {
            "version",
            "status",
            "durability",
            "invocationKey",
            "affected",
            "receipt",
            "code",
            "confirmation",
        },
    )
    if (
        payload["version"] != "batten.command-result/1"
        or payload["invocationKey"] != invocation_key
    ):
        raise ExecutionError("INVALID")
    status, durability = payload["status"], payload["durability"]
    if (
        not isinstance(status, str)
        or not isinstance(durability, str)
        or status
        not in {
            "applied",
            "recovered",
            "not-observed",
            "unknown",
            "rejected",
        }
        or durability
        not in {
            "committed",
            "pending-caller-commit",
            "unknown",
            "none",
        }
    ):
        raise ExecutionError("INVALID")
    if (
        phase == "observe" and status not in {"recovered", "not-observed", "rejected"}
    ) or (phase == "invoke" and status == "not-observed"):
        raise ExecutionError("INVALID")
    if status in {"unknown", "not-observed", "rejected"}:
        expected = "unknown" if status == "unknown" else "none"
        if (
            durability != expected
            or _decode.sequence(payload["affected"])
            or payload["receipt"] is not None
        ):
            raise ExecutionError("INVALID")
    elif durability not in {"committed", "pending-caller-commit"}:
        raise ExecutionError("INVALID")
    elif not isinstance(payload["receipt"], str) or not payload["receipt"]:
        raise ExecutionError("INVALID")
    if any(
        value is not None and not isinstance(value, str)
        for value in (payload["receipt"], payload["code"], payload["confirmation"])
    ):
        raise ExecutionError("INVALID")
    return CommandResult(
        cast(
            Literal["applied", "recovered", "not-observed", "unknown", "rejected"],
            status,
        ),
        invocation_key,
        cast(
            Literal["committed", "pending-caller-commit", "unknown", "none"],
            durability,
        ),
        tuple(
            _decode.key(value, exposure)
            for value in _decode.sequence(payload["affected"])
        ),
        payload["receipt"],
        cast(str | None, payload["code"]),
        cast(str | None, payload["confirmation"]),
    )
