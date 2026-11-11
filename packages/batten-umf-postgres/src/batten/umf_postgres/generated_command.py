"""Declared table commands bound to a generated artifact's PostgreSQL inventory."""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Literal, Protocol, cast

from batten.contracts import Identity, OperationCall, OperationOutcome
from umf_access.unified import AsyncSession, SessionIdentity
from umf_access_generated_executor import GeneratedExecutor

from ._generated_values import native_read_refusal, snapshot_inputs

_WRITE_KINDS = frozenset({"insert", "update", "delete", "upsert"})
_RECEIPT = re.compile(r"[0-9a-f]{64}")


class _NativeCommand(Protocol):
    async def execute(
        self, request: dict[str, object], *, identity: SessionIdentity
    ) -> dict[str, object]: ...


@dataclass(frozen=True, slots=True)
class GeneratedCommandRoute:
    """A declared table command and its single returned string Key."""

    operation: str
    record: tuple[str, str]
    key_id: str
    key_field: str


class GeneratedCommandExecution:
    """Run commands using UMF's owned transaction and authenticated receipt ledger."""

    def __init__(
        self,
        executor: GeneratedExecutor,
        session: AsyncSession,
        bundle: dict[str, object],
        installation_reference: dict[str, object],
        prepared_writes: bytes,
        *,
        prepared_sha256: str,
        routes: Mapping[str, GeneratedCommandRoute],
        authority: Identity,
        confirm: Callable[[OperationCall], Awaitable[bool]],
        outcome_secret: bytes,
    ) -> None:
        from umf_access.unified.prepared_writes import PreparedPostgresWrites

        table = executor.native_table
        if (
            not routes
            or session.transaction_owner != "adapter"
            or bundle.get("sourceDigest") != table.source_digest
            or bundle.get("bundleDigest") != table.bundle_digest
            or bundle.get("configurationDigest") != table.configuration_digest
        ):
            raise ValueError("command binding differs from admitted generated table")
        self._module = _text(_object(table.native_source["configuration"])["module"])
        self._schema = table.source_digest
        self._bundle_digest = table.bundle_digest
        self._artifact_digest = executor.trusted_artifact.artifact_digest
        self._routes = MappingProxyType(dict(routes))
        _validate_routes(self._routes, self._module, bundle, dict(table.operations))
        self._authority = authority
        self._confirm = confirm
        native = PreparedPostgresWrites(
            session,
            table,
            installation_reference,
            prepared_writes,
            expected_sha256=prepared_sha256,
            outcome_secret=outcome_secret,
        )
        if native.operations != frozenset(route.operation for route in routes.values()):
            raise ValueError("prepared commands differ from configured routes")
        self._native: _NativeCommand = native

    @property
    def operations(self) -> frozenset[str]:
        return frozenset(self._routes)

    @property
    def artifact_digest(self) -> str:
        return self._artifact_digest

    def capabilities(self) -> Mapping[str, str]:
        return {
            "command.outcome": "1",
            "command.observe": "1",
            **{
                f"command.operation/{host_id}": json.dumps(
                    (self._module, route.operation),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                for host_id, route in self._routes.items()
            },
        }

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        route = self._routes.get(call.operation)
        refused = _refusal(call, route)
        if refused is not None:
            return refused
        assert route is not None
        key = cast(str, call.key)
        try:
            inputs = snapshot_inputs(call.inputs, 1_048_576)
        except ValueError:
            return OperationOutcome("invalid", "", {}, "invalid")
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        if call.phase == "invoke" and not await self._confirm(call):
            return _outcome(key, "rejected", code="CONFIRMATION_REQUIRED")
        native_key = _native_key(call, key)
        response = await self._native.execute(
            _request(
                self._schema,
                self._module,
                route.operation,
                call.phase,
                native_key,
                inputs,
            ),
            identity=SessionIdentity(
                cast(Literal["person", "batch"], call.actor.kind), call.actor.subject
            ),
        )
        return _translate(
            response, self._schema, self._bundle_digest, call, route, native_key
        )


def _validate_routes(
    routes: Mapping[str, GeneratedCommandRoute],
    module: str,
    bundle: Mapping[str, object],
    inventory: Mapping[str, str],
) -> None:
    raw = _text(_object(bundle["source"])["utf8"])
    if sha256(raw.encode("utf-8")).hexdigest() != bundle["sourceDigest"]:
        raise ValueError("command source bytes differ from the admitted digest")
    source = json.loads(raw)
    owner = next(item for item in source["modules"] if item["id"] == module)
    tables = owner["extensions"]["umf.tables"]
    declarations = {item["id"]: item for item in tables["commands"]}
    records = {
        item["id"]: item for item in owner["elements"] if item["kind"] == "record"
    }
    if len({route.operation for route in routes.values()}) != len(routes):
        raise ValueError("duplicate command declaration")
    for host_id, route in routes.items():
        if not host_id or inventory.get(route.operation) not in _WRITE_KINDS:
            raise ValueError("command is outside the admitted inventory")
        _validate_declaration(
            route, module, declarations[route.operation], tables, records
        )


def _validate_declaration(
    route: GeneratedCommandRoute, module: str, declared: Any, tables: Any, records: Any
) -> None:
    body = declared["body"]
    target = next(row for row in tables["tables"] if row["id"] == body["table"])
    ref = {"module": module, "element": route.key_field}
    key = next(
        (
            item
            for item in records[route.record[1]]["keys"]
            if item["id"] == route.key_id
        ),
        None,
    )
    if (
        route.record[0] != module
        or target["record"] != {"module": module, "element": route.record[1]}
        or key is None
        or key["fields"] != [ref]
        or ref not in body.get("returning", [])
        or body.get("maxRows") != 1
        or declared.get("batch") is not None
        or declared.get("replay") != "caller-key-required"
        or declared.get("consistency") != "transaction"
    ):
        raise ValueError(
            "command does not match its recoverable single-Key declaration"
        )


def _refusal(
    call: OperationCall, route: GeneratedCommandRoute | None
) -> OperationOutcome | None:
    if (
        call.scope is None
        or not call.scope.api_digest
        or call.scope.principal != call.actor
        or call.actor.kind not in {"person", "batch"}
        or call.actor.delegation is not None
    ):
        return OperationOutcome("denied", "", {}, "scope_invalid")
    if (
        route is None
        or call.phase not in {"invoke", "observe"}
        or (call.phase == "observe" and call.confirmation is not None)
        or not _valid_invocation_key(call.key)
    ):
        return OperationOutcome("invalid", "", {}, "invalid")
    return None


def _valid_invocation_key(key: str | None) -> bool:
    try:
        return (
            key is not None
            and 0 < len(key.encode("utf-8")) <= 128
            and "\x00" not in key
        )
    except UnicodeError:
        return False


def _native_key(call: OperationCall, key: str) -> str:
    scope = call.scope
    assert scope is not None
    fields = [
        scope.application.id,
        scope.application.digest,
        scope.api_digest,
        call.operation,
        key,
    ]
    return sha256(json.dumps(fields, separators=(",", ":")).encode("utf-8")).hexdigest()


def _request(
    schema: str,
    module: str,
    operation: str,
    phase: str,
    key: str,
    inputs: dict[str, object],
) -> dict[str, object]:
    return {
        "contract": "umf.access/1",
        "schema": schema,
        "kind": "table",
        "module": module,
        "operation": operation,
        "call": {"kind": "single", "inputs": inputs},
        "phase": phase,
        "mutation": True,
        "idempotency_key": key,
    }


def _translate(
    response: Mapping[str, object],
    schema: str,
    bundle_digest: str,
    call: OperationCall,
    route: GeneratedCommandRoute,
    native_key: str,
) -> OperationOutcome:
    if "error" in response:
        refusal = native_read_refusal(response, schema)
        if refusal.status in {"invalid", "denied", "precondition_failed"}:
            return refusal
        return OperationOutcome("uncertain", "", {}, "native_refused")
    key = cast(str, call.key)
    try:
        if set(response) != {"schema", "table"} or response["schema"] != schema:
            raise ValueError("native command envelope differs")
        table = _object(response["table"])
        return _receipt_outcome(
            table, key, native_key, schema, bundle_digest, route, call.phase
        )
    except (KeyError, ValueError):
        return OperationOutcome("uncertain", "", {}, "native_refused")


def _receipt_outcome(
    table: Mapping[str, object],
    key: str,
    native_key: str,
    schema: str,
    bundle_digest: str,
    route: GeneratedCommandRoute,
    phase: str,
) -> OperationOutcome:
    if table["version"] != "umf.table-write-result/0.1" or table["key"] != native_key:
        raise ValueError("native command identity differs")
    status = _text(table["status"])
    if status == "not-observed" and phase == "observe":
        if (
            table["durability"] != "not-observed"
            or "result" in table
            or "receipt" in table
        ):
            raise ValueError("unexpected unobserved outcome")
        return _outcome(key, status)
    if status not in {"applied", "recovered"} or (
        phase == "observe" and status != "recovered"
    ):
        raise ValueError("unexpected command status")
    if table["commitResponsibility"] != "adapter" or table["durability"] != "committed":
        raise ValueError("native command was not durably committed")
    receipt = _object(table["receipt"])
    if (
        receipt["version"] != "umf.table-outcome/0.1"
        or receipt["sourceDigest"] != schema
        or receipt["bundleDigest"] != bundle_digest
        or receipt["module"] != route.record[0]
        or receipt["operation"] != route.operation
    ):
        raise ValueError("native command receipt differs")
    reference = _text(receipt["invocationDigest"])
    if _RECEIPT.fullmatch(reference) is None:
        raise ValueError("invalid receipt reference")
    affected = _affected(table, route) if status == "applied" else []
    return _outcome(key, status, receipt=reference, affected=affected)


def _affected(
    table: Mapping[str, object], route: GeneratedCommandRoute
) -> list[object]:
    result = _object(table["result"])
    frames = _array(result["items"])
    if len(frames) != 1:
        raise ValueError("native command returned multiple items")
    frame = _object(frames[0])
    rows = _array(frame["rows"])
    if len(rows) > 1 or frame["affectedCount"] != {"integerToken": str(len(rows))}:
        raise ValueError("native command effect count differs from returned Keys")
    return [
        {
            "record": route.record,
            "keyId": route.key_id,
            "components": [{"string": _text(_object(row)[route.key_field])}],
        }
        for row in rows
    ]


def _outcome(
    key: str,
    status: str,
    *,
    receipt: str | None = None,
    affected: list[object] | None = None,
    code: str | None = None,
) -> OperationOutcome:
    return OperationOutcome(
        "succeeded",
        key,
        {
            "version": "batten.command-result/1",
            "status": status,
            "durability": "committed" if receipt is not None else "none",
            "invocationKey": key,
            "affected": affected or [],
            "receipt": receipt,
            "code": code,
            "confirmation": None,
        },
    )


def _object(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("expected object")
    return cast(Mapping[str, object], value)


def _array(value: object) -> list[object]:
    if type(value) is not list:
        raise ValueError("expected array")
    return cast(list[object], value)


def _text(value: object) -> str:
    if type(value) is not str or not value:
        raise ValueError("expected non-empty text")
    return value
