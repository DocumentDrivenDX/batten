"""Approval business behavior through a public table port, never a native client."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import cast

from batten.contracts import OperationCall, OperationOutcome
from batten.tables import TablePort

OPERATIONS = {
    "list": "list_requests",
    "get": "get_request",
    "submit": "submit_request",
    "edit": "edit_request",
    "decide": "decide_request",
}
REQUIRED: dict[str, set[str]] = {
    "list": set(),
    "get": {"id"},
    "submit": {"title"},
    "edit": {"id", "title", "revision"},
    "decide": {"id", "revision", "decision"},
}


def object_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("unexpected native outcome shape")
    return cast(dict[str, object], value)


def rows(value: object, subjects: Mapping[str, str]) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("unexpected native row shape")
    result: list[dict[str, str]] = []
    for item in cast(list[object], value):
        row = object_value(item)
        expected = {"id", "owner", "title", "state", "revision", "decided_by"}
        if set(row) != expected or any(not isinstance(v, str) for v in row.values()):
            raise ValueError("unexpected native record shape")
        record = cast(dict[str, str], dict(row))
        for field in ("owner", "decided_by"):
            if record[field] and record[field] not in subjects:
                raise ValueError("unknown native principal")
            record[field] = subjects.get(record[field], record[field])
        result.append(record)
    return result


def validated(call: OperationCall) -> dict[str, str]:
    if call.operation not in REQUIRED or set(call.inputs) != REQUIRED[call.operation]:
        raise ValueError("undeclared operation or inputs")
    data: dict[str, str] = {}
    for name, value in call.inputs.items():
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > (240 if name == "title" else 64)
        ):
            raise ValueError("invalid input")
        data[name] = value.strip()
    if call.operation == "decide" and data["decision"] not in {"approved", "rejected"}:
        raise ValueError("invalid decision")
    return data


def parameters(call: OperationCall) -> dict[str, object]:
    data = validated(call)
    mutation = call.operation not in {"list", "get"}
    if call.phase not in {"invoke", "observe"} or (
        call.phase == "observe" and not mutation
    ):
        raise ValueError("invalid phase")
    if mutation:
        if call.key is None:
            raise ValueError("original invocation key required")
        data["revision"] = uuid.uuid5(
            uuid.NAMESPACE_URL, "batten.approval.revision/" + call.key
        ).hex
    if call.operation == "submit":
        data["id"] = uuid.uuid5(
            uuid.NAMESPACE_URL, "batten.approval.request/" + str(call.key)
        ).hex
    if call.operation in {"edit", "decide"}:
        data["expected_revision"] = cast(str, call.inputs["revision"])
    if call.operation == "decide":
        data["state"] = data.pop("decision")
    return {name: {"string": value} for name, value in data.items()}


class ApprovalOperations:
    def __init__(self, tables: TablePort, subjects: Mapping[str, str]):
        self.tables, self.subjects = tables, subjects

    async def prepare(self) -> None:
        await self.tables.prepare()

    async def aclose(self) -> None:
        await self.tables.aclose()

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        invocation = call.key or ""
        try:
            inputs = parameters(call)
        except ValueError:
            return OperationOutcome("invalid", invocation, {}, "invalid")
        native = await self.tables.execute(
            call.actor,
            OPERATIONS[call.operation],
            inputs,
            key=call.key,
            phase=call.phase,
            mutation=call.operation not in {"list", "get"},
        )
        if "error" in native:
            code = object_value(native["error"]).get("code")
            statuses = {
                "DENIED": "denied",
                "INVALID": "invalid",
                "PRECONDITION_FAILED": "precondition_failed",
                "WRITE_OUTCOME_UNKNOWN": "uncertain",
                "CONFLICT": "precondition_failed",
            }
            return OperationOutcome(
                statuses.get(str(code), "unavailable"),
                invocation,
                {},
                str(code) if code in statuses else "provider_unavailable",
            )
        table = object_value(native["table"])
        if call.operation in {"list", "get"}:
            return OperationOutcome(
                "succeeded",
                invocation,
                {
                    "rows": rows(table["rows"], self.subjects),
                    "cursor": table.get("cursor"),
                },
            )
        return self._mutation(table, invocation)

    def _mutation(
        self, table: Mapping[str, object], invocation: str
    ) -> OperationOutcome:
        status = table.get("status")
        if (
            status not in {"applied", "recovered"}
            or table.get("durability") != "committed"
        ):
            return OperationOutcome(
                "uncertain", invocation, {}, "original_outcome_unconfirmed"
            )
        receipt = object_value(table["receipt"])
        effects = cast(list[object], receipt["effects"])
        count = object_value(effects[0]).get("integerToken")
        if count == "0":
            return OperationOutcome(
                "precondition_failed", invocation, {}, "stale_or_denied"
            )
        if count != "1":
            return OperationOutcome(
                "unavailable", invocation, {}, "unexpected_effect_count"
            )
        return OperationOutcome(
            "succeeded",
            invocation,
            {"recovered": status == "recovered", "durability": "committed"},
        )
