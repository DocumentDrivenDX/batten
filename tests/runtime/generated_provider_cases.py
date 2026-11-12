"""Pure fixture builders for generated provider boundary workflows."""

import time
from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import SimpleNamespace
from typing import Any, Literal, cast

from batten.contracts import Actor, ArtifactRef, ExecutionScope, OperationCall
from batten.umf_postgres._generated_page import GeneratedPageExecution
from batten.umf_postgres.generated import GeneratedUmfExecution
from batten.umf_postgres.generated_read import GeneratedReadExecution
from batten.umf_postgres.generated_read_v2 import GeneratedReadExecutionV2
from batten.umf_postgres.generated_read_v3 import GeneratedReadExecutionV3
from read_artifacts import read_executor
from umf_access.unified import SessionIdentity
from umf_access_generated_executor import ExecutionScope as GeneratedScope
from umf_access_generated_executor import (
    GeneratedExecutor,
    GeneratedOrdinaryPageCall,
    GeneratedOrdinaryPageRoot,
    GeneratedReadAtom,
    GeneratedReadCallV2,
)


class Authority:
    def __init__(self, inputs: dict[str, dict[str, str]]):
        self.inputs = inputs

    async def check(self, actor: Actor, operation: str) -> bool:
        self.inputs["amount"][next(iter(self.inputs["amount"]))] = "2"
        return operation in {"inspect", "ordinary"} or operation.startswith("Query.")


@dataclass(frozen=True)
class PageRouteCase:
    provider: GeneratedPageExecution
    native: Any
    artifact: ArtifactRef
    actor: Actor
    page: GeneratedOrdinaryPageCall


def page_route_scenario(
    kind: Literal["person", "batch", "service"],
    route: tuple[str, str] = ("demo", "Note"),
    *,
    missing_method: str | None = None,
) -> PageRouteCase:
    """Build a protocol-only route case, not a verified combined-v7 artifact."""
    base, _root = read_executor("v5")
    roots = (GeneratedOrdinaryPageRoot("demo/Note", "demo", "Note"),)
    executor = cast(
        GeneratedExecutor,
        SimpleNamespace(
            read_profile="weft.generated-read-algebra/7",
            native_table=base.native_table,
            target=base.target,
            trusted_artifact=base.trusted_artifact,
            read_algebra_json=base.read_algebra_json,
            ordinary_page_roots=roots,
        ),
    )
    result: dict[str, object] = {
        "schema": base.native_table.source_digest,
        "page": {"rootId": "demo/Note", "rows": []},
    }
    native = SimpleNamespace(
        schema=base.native_table.source_digest,
        module="demo",
        read_profile=executor.read_profile,
        target_binding_digest=base.target.binding_digest,
        artifact_digest=base.trusted_artifact.artifact_digest,
        receipt_digest=base.trusted_artifact.receipt_digest,
        algebra_json=base.read_algebra_json,
        ordinary_page_roots=roots,
        identities=[],
        calls=[],
        result=result,
    )

    def identify(call: GeneratedOrdinaryPageCall) -> bytes:
        native.identities.append(call)
        return b"p" * 32

    async def execute(
        call: GeneratedOrdinaryPageCall, *, identity: object, scope: object
    ) -> dict[str, object]:
        native.calls.append((call, identity, scope))
        return result

    def validate(result_value: object, call: GeneratedOrdinaryPageCall) -> bool:
        return (
            result_value is result
            and bool(native.calls)
            and native.calls[-1][0] == call
        )

    native.ordinary_page_identity = identify
    native.execute_ordinary_page = execute
    native.validate_ordinary_page_result = validate
    if missing_method is not None:
        delattr(native, missing_method)

    async def factory() -> Any:
        return native

    actor = Actor(f"page-{kind}", kind=kind)
    provider = GeneratedPageExecution(
        executor,
        factory,
        Authority({"amount": {"string": "unchanged"}}),
        {"ordinary": route},
    )
    return PageRouteCase(
        provider,
        native,
        ArtifactRef("page-fixture", "d" * 64),
        actor,
        GeneratedOrdinaryPageCall("demo/Note", (), None, 1),
    )


class Native:
    schema = "b" * 64
    module = "fabricated"

    def __init__(self, executor: GeneratedExecutor | None = None) -> None:
        self.executor = executor
        self.read_profile = executor.read_profile if executor is not None else None
        self.target_binding_digest = ""
        if executor is not None:
            self.schema = executor.native_table.source_digest
            self.module = "demo"
            self.target_binding_digest = executor.target.binding_digest
        self.calls: list[
            tuple[Mapping[str, object], SessionIdentity, GeneratedScope]
        ] = []
        self.response: dict[str, object] | None = None

    async def execute(
        self,
        request: dict[str, object],
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]:
        self.calls.append((request, identity, scope))
        return (
            self.response
            if self.response is not None
            else {
                "schema": self.schema,
                "table": {
                    "version": "umf.table-read-result/0.1",
                    "kind": "many",
                    "module": self.module,
                    "operation": request["operation"],
                    "sourceDigest": self.schema,
                    "rows": [],
                    "cursor": None,
                },
            }
        )

    async def execute_read_v3(
        self,
        call: GeneratedReadCallV2,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]:
        bound = cast(GeneratedExecutor, self.executor).bind_read_v3(call, scope)
        values = (
            call.key
            if call.key is not None
            else cast(GeneratedReadAtom, call.where).values
        )
        self.calls.append((
            {"call": {"kind": "single", "inputs": {"amount": values[0]}}},
            identity,
            scope,
        ))
        frame: dict[str, object] = {
            "version": "umf.generated-read-result/2",
            "kind": bound.result_kind,
            "terminal": call.terminal,
            "sourceDigest": self.schema,
            "module": call.module,
            "record": call.record,
        }
        if bound.result_kind == "scalar":
            frame["value"] = (
                {"integerToken": "1"} if call.terminal == "count" else {"boolean": True}
            )
        else:
            frame.update({
                "columns": [
                    {"field": dict(field), "output": dict(output)}
                    for field, output in zip(bound.fields, bound.outputs, strict=True)
                ],
                "rows": [[example_literal(output) for output in bound.outputs]],
                "cursor": None,
            })
        return (
            self.response
            if self.response is not None
            else {"schema": self.schema, "table": frame}
        )


def example_literal(output: Mapping[str, object]) -> Mapping[str, object]:
    values: dict[str, Mapping[str, object]] = {
        "string": {"string": "fabricated"},
        "boolean": {"boolean": True},
        "integer": {"integerToken": "9007199254740993"},
        "decimal": {"decimalToken": "1.23"},
        "date": {"date": "2026-11-04"},
        "timestamp": {"timestamp": "2026-11-04T00:00:00.000000Z"},
        "uuid": {"uuid": "00000000-0000-0000-0000-000000000001"},
    }
    return values[cast(str, output["carrier"])]


def malformed_results(result: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    frame = cast(Mapping[str, object], result["table"])
    edits: list[dict[str, object]]
    if frame["kind"] == "scalar":
        edits = [
            {"value": None},
            {"value": {"string": "invalid"}},
            {"value": {"integerToken": "-1"}},
        ]
    else:
        columns = cast(list[Mapping[str, object]], frame["columns"])
        row = [
            example_literal(cast(Mapping[str, object], column["output"]))
            for column in columns
        ]
        edits = [
            {"rows": [[None, *row[1:]]]},
            {"rows": [[{"integerToken": "1"}, *row[1:]]]},
            {"rows": [row] * 1001},
            {"rows": [[{"string": "\x01" * 1_400_000}, *row[1:]]]},
        ]
        if frame.get("terminal") in ("one", "get"):
            edits.extend([{"rows": []}, {"rows": [row, row]}])
    return tuple(
        {"schema": result["schema"], "table": {**frame, **edit}} for edit in edits
    )


def malformed_cases(
    profile: str, kind: str, result: Mapping[str, object]
) -> tuple[dict[str, object], ...]:
    return (
        malformed_results(result)
        if (profile, kind) not in {("fixed", kind), (profile, "service")}
        else ()
    )


def wrong_root_call(profile: str, call: OperationCall) -> OperationCall:
    return (
        replace(call, inputs={"read": {"module": "foreign"}})
        if profile != "fixed"
        else replace(call, scope=None)
    )


def scenario(
    profile: str, kind: Literal["person", "batch", "service"] = "person"
) -> tuple[
    Native,
    GeneratedReadExecution | GeneratedUmfExecution,
    Mapping[str, object],
    dict[str, str],
    Actor,
    ExecutionScope,
    OperationCall,
]:
    executor, root = (
        read_executor(
            "v3"
            if profile.startswith("v3_")
            else ("v2" if profile.startswith("v2_") else "v1")
        )
        if profile != "fixed"
        else (None, {})
    )
    native = Native(executor)
    expected = (
        {"string": "generated_fixture_actor"}
        if executor
        else {"integerToken": "9007199254740993"}
    )
    values = {"amount": dict(expected)}
    authority = Authority(values)
    actor = Actor("fabricated-actor", kind=kind)
    scope = ExecutionScope(
        ArtifactRef("fabricated", "fixture"),
        actor,
        "request",
        time.monotonic() + 60,
        "lease",
    )

    async def factory() -> Native:
        return native

    inputs: Mapping[str, object] = values
    if executor is not None:
        predicates = cast(Mapping[str, Mapping[str, object]], root["predicates"])
        predicate = next(
            identity
            for identity, descriptor in predicates.items()
            if descriptor["fieldId"] == "demo/owner" and descriptor["operator"] == "eq"
        )
        inputs = {
            "read": {
                "module": "demo",
                "record": "Note",
                "fields": None,
                "filters": [{"predicate": predicate, "values": [values["amount"]]}],
                "order": [],
                "limit": 10,
            }
        }
        if profile == "read":
            provider = GeneratedReadExecution(
                factory, authority, executor, {"inspect": ("demo", "Note")}
            )
            call = OperationCall("inspect", inputs, actor, scope=scope)
            return native, provider, inputs, expected, actor, scope, call
        if profile.startswith(("v2_", "v3_")):
            terminal = cast(
                Literal["all", "first", "one", "get", "count", "exists"],
                profile.split("_")[1],
            )
            values_wire: dict[str, object] = {
                "version": "umf.generated-read-call/2",
                "root": {"module": "demo", "record": "Note"},
                "selection": None,
                "where": {
                    "op": "atom",
                    "predicateId": predicate,
                    "values": [values["amount"]],
                },
                "orders": [],
                "limit": 10
                if terminal == "all" and not profile.endswith("complete")
                else None,
                "terminal": terminal,
                "key": None,
            }
            if terminal == "get":
                values_wire.update({"where": None, "key": [values["amount"]]})
            inputs = {"read": values_wire}
            provider_type = (
                GeneratedReadExecutionV3
                if profile.startswith("v3_")
                else GeneratedReadExecutionV2
            )
            provider = provider_type(
                factory, authority, executor, {"inspect": ("demo", "Note")}
            )
        else:
            raise ValueError("unknown read profile")
    else:
        provider = GeneratedUmfExecution(factory, authority)
    call = OperationCall("inspect", inputs, actor, scope=scope)
    return native, provider, inputs, expected, actor, scope, call


def invalid_read_inputs(
    call: OperationCall,
    actor: Actor,
    scope: ExecutionScope,
    kind: str,
    denial: object,
    limit: object,
    precondition: object,
    private: object,
) -> tuple[tuple[OperationCall, object, set[str]], ...]:
    """Return malformed request/response data; no provider calls or assertions."""
    return (
        (call, denial, {"denied"}),
        (call, limit, {"denied"} if kind == "service" else {"unavailable"}),
        (
            call,
            precondition,
            {"denied"} if kind == "service" else {"precondition_failed"},
        ),
        (call, private, {"denied"} if kind == "service" else {"unavailable"}),
        (replace(call, scope=None), None, {"invalid", "denied"}),
        (
            replace(call, scope=replace(scope, principal=Actor("foreign"))),
            None,
            {"invalid", "denied"},
        ),
        (replace(call, phase="observe"), None, {"invalid", "denied"}),
        (replace(call, key="f" * 32), None, {"invalid", "denied"}),
        (replace(call, confirmation="unverified"), None, {"invalid", "denied"}),
        (
            replace(call, scope=replace(scope, consistency="request-snapshot-1")),
            None,
            {"invalid", "denied"},
        ),
        (
            replace(call, scope=replace(scope, consistency="unknown")),
            None,
            {"invalid", "denied"},
        ),
        (
            replace(call, actor=replace(actor, delegation="unverified")),
            None,
            {"invalid", "denied"},
        ),
    )
