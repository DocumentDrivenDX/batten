"""Build fixture values for generated v4 provider workflows."""

import hashlib
import json
import time
from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Literal, cast
from unittest.mock import AsyncMock, Mock

import umf_access.generated as generated_api
from batten.contracts import (
    Actor,
    ArtifactRef,
    ExecutionScope,
    Operation,
    OperationCall,
    OperationOutcome,
    SelectedCallSpec,
    SelectedKey,
    Selection,
)
from batten.lintel import ExposureConfig, ExposureRecordRoot
from batten.umf_postgres.generated_batch import GeneratedBatchExecution
from batten.umf_postgres.generated_table import GeneratedTableExecution
from lintel.ports import ElementRef, OperationRef
from read_artifacts import read_executor
from umf_access.unified import (
    AsyncSession,
    GeneratedNativeError,
    SessionIdentity,
    SessionPolicy,
)
from umf_access_generated_executor import ExecutionScope as GeneratedScope
from umf_access_generated_executor import GeneratedGetManyCall, GeneratedReadCallV2


def _provider_case(
    kind: Literal["person", "batch", "service"], authority: Any, composite: bool | str
) -> dict[str, Any]:
    profile = "v5" if composite == "v5" else "v4"
    executor, _source_root = read_executor(profile)
    trust = executor.trusted_artifact
    refs = (ElementRef("demo", "id"), ElementRef("demo", "owner"))
    root = ExposureRecordRoot(
        OperationRef("demo", "Note", "record"),
        "inspect",
        executor.native_table.source_digest,
        trust.artifact_digest,
        trust.receipt_digest,
        executor.target.binding_digest,
        hashlib.sha256(executor.read_algebra_json).hexdigest(),
        "primary",
        refs,
        ("string",),
        tuple((ref, "string") for ref in refs),
    )
    actor = Actor("fixture-user", kind=kind)
    app, deadline = (
        ArtifactRef(
            "fixture-app", "a" * 64 if composite == "v5" else "fixture-app-digest"
        ),
        time.monotonic() + 30,
    )
    scope = ExecutionScope(app, actor, "r", deadline, "l", "", "request-snapshot-1")
    request = SimpleNamespace(execute_get_many=AsyncMock())
    request_context = AsyncMock()
    request_context.__aenter__.return_value = request
    native = SimpleNamespace(
        schema=executor.native_table.source_digest,
        module="demo",
        read_profile=executor.read_profile,
        target_binding_digest=executor.target.binding_digest,
        artifact_digest=trust.artifact_digest,
        receipt_digest=trust.receipt_digest,
        algebra_json=executor.read_algebra_json,
        execute_read_v3=AsyncMock(),
        open_request=Mock(return_value=request_context),
    )
    policy = SessionPolicy({"fixture-user": "fixture_role"}, {}, "fixture_schema")

    def unused_factory(_identity: SessionIdentity) -> AbstractAsyncContextManager[Any]:
        raise AssertionError("the boundary test does not open a database lease")

    session = AsyncSession(unused_factory, policy)
    factory = AsyncMock(return_value=native)
    kwargs: dict[str, Any] = {"data_session": session, "authority": authority}
    bad_kwargs: tuple[tuple[dict[str, Any], str], ...] = ()
    if composite:
        provider_type: Any = GeneratedTableExecution
        kwargs.update({
            "read_routes": {"ordinary": ("demo", "Note")},
            "record_routes": {"inspect": root},
        })
        if composite == "v5":
            kwargs["connection_routes"] = _v5_connection_binding(
                native, request, executor, _source_root
            )
        bad_kwargs = (
            ({**kwargs, "read_routes": {"inspect": ("demo", "Note")}}, "disjoint"),
        )
    else:
        provider_type = GeneratedBatchExecution
        kwargs["roots"] = {"inspect": root}

    identity = SessionIdentity("person" if kind == "service" else kind, actor.subject)
    generated_scope = GeneratedScope(
        app, identity, "r", deadline, "l", "", "request-snapshot/1"
    )
    generated_call = GeneratedGetManyCall(
        "demo", "Note", "primary", (({"string": "n-1"},),), ("demo/id",)
    )
    bound = executor.bind_get_many(generated_call, generated_scope)
    request.execute_get_many.return_value = {
        "version": "umf.generated-key-batch-result/1",
        "sourceDigest": bound.source_digest,
        "bindingDigest": bound.target_digest,
        "module": "demo",
        "record": "Note",
        "keyId": "primary",
        "fields": [dict(field) for field in bound.fields],
        "items": [{"key": [{"string": "n-1"}], "values": [{"string": "n-1"}]}],
    }
    case = {
        "executor": executor,
        "_source_root": _source_root,
        "root": root,
        "actor": actor,
        "app": app,
        "deadline": deadline,
        "scope": scope,
        "request": request,
        "native": native,
        "factory": factory,
        "provider_type": provider_type,
        "provider_kwargs": kwargs,
        "bad_kwargs": bad_kwargs,
        "identity": identity,
        "generated_scope": generated_scope,
        "generated_call": generated_call,
        "bound": bound,
    }
    if composite == "v5":
        case["connection_calls"] = _connection_calls(scope, actor)
    return case


def _v5_connection_binding(
    native: Any, request: Any, executor: Any, note_root: Mapping[str, Any]
) -> dict[str, Any]:
    routes = _connection_routes(executor, note_root)
    native.connection_routes = routes
    request.execute_forward_connection = AsyncMock()
    native.prepared_connection_scopes = []

    def prepare(call: Any, **kwargs: Any) -> tuple[Any, Any, Any]:
        if call.after == "invalid-cursor":
            raise cast(Any, GeneratedNativeError)("INVALID_CURSOR")
        native.prepared_connection_scopes.append((kwargs["identity"], kwargs["scope"]))
        return call, kwargs["identity"], kwargs["scope"]

    native.prepare_forward_connection = Mock(side_effect=prepare)

    def execute(prepared: object) -> dict[str, object]:
        call = cast(tuple[object, object, object], prepared)[0]
        return connection_frame_fixture(call, routes, executor)

    request.execute_forward_connection.side_effect = execute
    return routes


def _connection_routes(executor: Any, _note_root: Mapping[str, Any]) -> dict[str, Any]:
    algebra = json.loads(executor.read_algebra_json)
    routes: dict[str, Any] = {}
    for operation, record, selected_fields in (
        ("Query.notes", "Note", ("demo/id", "demo/owner")),
        ("Query.tasks", "Task", ("demo/task_id", "demo/task_value")),
    ):
        root = algebra["roots"][f"demo/{record}"]
        outputs = {
            entry["fieldId"]: entry
            for entry in root["forwardConnection"]["fieldOutputs"]
        }
        body = {
            "version": "umf.allowed-connection-fields/1",
            "scalarCodecProfile": "fixture.scalar-codec/1",
            "fields": [
                {
                    "fieldId": field,
                    "sourceField": root["fields"][field]["sourceField"],
                    "output": outputs[field]["output"],
                    "scalar": outputs[field]["output"]["carrier"],
                    "nullable": outputs[field]["output"]["nullable"],
                }
                for field in selected_fields
            ],
        }
        api = cast(Any, generated_api)
        profile = api.AllowedConnectionFieldProfile.from_body(body)
        scope = api.GeneratedCursorScope(
            "fixture-app", "a" * 64, "b" * 64, operation, profile.digest
        )
        routes[operation] = api.GeneratedConnectionRoute("demo", record, scope, profile)
    return routes


def _connection_calls(
    scope: ExecutionScope, actor: Actor
) -> tuple[SelectedCallSpec, ...]:
    calls: list[SelectedCallSpec] = []
    for operation, fields, first in (
        ("Query.notes", (("demo", "owner"),), 2),
        ("Query.tasks", (("demo", "task_value"),), 2),
        ("Query.notes", (), 0),
        ("Query.notes", (), 1),
    ):
        call = OperationCall(operation, {}, actor, scope=scope)
        calls.append(
            SelectedCallSpec(call, Selection("connection", fields=fields, first=first))
        )
    return tuple(calls)


def prepared_connection_inputs(
    calls: tuple[SelectedCallSpec, ...], scope: ExecutionScope, actor: Actor
) -> tuple[
    tuple[SelectedCallSpec, ...],
    SelectedCallSpec,
    SelectedCallSpec,
]:
    bound = tuple(
        SelectedCallSpec(
            OperationCall(item.call.operation, {}, actor, scope=scope), item.selection
        )
        for item in calls
    )
    filtered = SelectedCallSpec(
        OperationCall(
            bound[0].call.operation,
            {"filter": {"owner": "value"}},
            actor,
            scope=scope,
        ),
        bound[0].selection,
    )
    bad_cursor = SelectedCallSpec(
        bound[0].call, replace(bound[0].selection, after="invalid-cursor")
    )
    return bound, filtered, bad_cursor


def connection_nodes(
    results: list[OperationOutcome],
) -> tuple[
    Mapping[str, object],
    Mapping[str, object],
    Mapping[str, object],
    Mapping[str, object],
]:
    def node(index: int) -> Mapping[str, object]:
        result = results[index].result
        edges = cast(list[Mapping[str, object]], result["edges"])
        return cast(Mapping[str, object], edges[0]["node"])

    return node(0), node(1), results[2].result, node(3)


def prepared_owners(native: Any, offset: int) -> tuple[list[object], list[object]]:
    entries = native.prepared_connection_scopes[offset:]
    return [entry[0] for entry in entries], [entry[1] for entry in entries]


def connection_frame_fixture(
    call: Any, routes: Mapping[str, Any], executor: Any
) -> dict[str, Any]:
    route = routes[call.operation_id]
    algebra = json.loads(executor.read_algebra_json)
    root = algebra["roots"][f"{call.module}/{call.record}"]
    key_id = root["primaryKeyId"]
    key_field = root["getMany"]["keyFields"][0]["fieldId"]
    key_value = "n-1" if call.record == "Note" else "t-1"
    field_rows: list[dict[str, object]] = []
    values = {}
    for descriptor in route.allowed_field_profile.body["fields"]:
        field_id = descriptor["fieldId"]
        values[field_id] = {"string": key_value if field_id == key_field else "value"}
    if call.first:
        field_rows = [
            {
                "cursor": f"{call.record}-cursor",
                "node": {
                    "key": {"keyId": key_id, "components": [{"string": key_value}]},
                    "fields": {
                        field: values[field] for field in call.fields or (key_field,)
                    },
                },
            }
        ]
    return {
        "version": "umf.generated-forward-connection-result/1",
        "sourceDigest": executor.native_table.source_digest,
        "bindingDigest": executor.target.binding_digest,
        "module": call.module,
        "record": call.record,
        "fields": [
            descriptor["sourceField"]
            for descriptor in route.allowed_field_profile.body["fields"]
            if descriptor["fieldId"] in (call.fields or (key_field,))
        ],
        "edges": field_rows,
        "pageInfo": {"hasNextPage": False, "hasPreviousPage": False},
    }


def _ordinary_read(base: dict[str, Any]) -> OperationCall:
    executor = base["executor"]
    source_root = base["_source_root"]
    predicates = cast(dict[str, dict[str, object]], source_root["predicates"])
    predicate = next(
        identity
        for identity, item in predicates.items()
        if item["fieldId"] == "demo/owner" and item["operator"] == "eq"
    )
    wire: dict[str, object] = {
        "version": "umf.generated-read-call/2",
        "root": {"module": "demo", "record": "Note"},
        "selection": None,
        "where": {
            "op": "atom",
            "predicateId": predicate,
            "values": [{"string": "n-1"}],
        },
        "orders": [],
        "limit": 10,
        "terminal": "all",
        "key": None,
    }
    native_scope = GeneratedScope(
        base["app"],
        base["identity"],
        "r-read",
        base["deadline"],
        "l-read",
        "",
        "statement",
    )
    read_call = GeneratedReadCallV2.from_mapping(wire)
    bound = executor.bind_read_v3(read_call, native_scope)
    examples = {
        "string": {"string": "n-1"},
        "boolean": {"boolean": True},
        "integer": {"integerToken": "1"},
        "decimal": {"decimalToken": "1"},
        "date": {"date": "2026-01-01"},
        "timestamp": {"timestamp": "2026-01-01T00:00:00.000000Z"},
        "uuid": {"uuid": "00000000-0000-0000-0000-000000000001"},
    }
    frame = {
        "version": "umf.generated-read-result/2",
        "kind": bound.result_kind,
        "terminal": "all",
        "sourceDigest": executor.native_table.source_digest,
        "module": "demo",
        "record": "Note",
        "columns": [
            {"field": dict(field), "output": dict(output)}
            for field, output in zip(bound.fields, bound.outputs, strict=True)
        ],
        "rows": [[examples[cast(str, output["carrier"])] for output in bound.outputs]],
        "cursor": None,
    }
    result = {"schema": executor.native_table.source_digest, "table": frame}
    base["native"].execute_read_v3 = AsyncMock(return_value=result)
    return OperationCall(
        "ordinary",
        {"read": wire},
        base["actor"],
        scope=replace(base["scope"], consistency="statement"),
    )


def batch_case(
    kind: Literal["person", "batch", "service"],
    authority: Any,
    composite: bool | str = False,
) -> dict[str, Any]:
    case = _provider_case(kind, authority, composite)
    case["read_call"] = _ordinary_read(case) if composite else None
    root, actor, scope = case["root"], case["actor"], case["scope"]
    selected_call = OperationCall("inspect", {}, actor, scope=scope)
    selection = Selection(
        "get_many",
        fields=(("demo", "id"),),
        keys=(SelectedKey(("demo", "Note"), "primary", ({"string": "n-1"},)),),
    )
    config = ExposureConfig(
        case["app"],
        "api-digest",
        root.source_digest,
        (),
        {
            "identity.codec": "lintel.node-id.string-key/1",
            "read.consistency": "request-snapshot-1",
        },
        (root,),
    )
    actions: list[tuple[Any, ...]] = []
    if composite:
        read_call = cast(OperationCall, case["read_call"])
        actions.extend([
            (
                "invoke",
                read_call,
                None,
                (
                    ("denied" if kind == "service" else "succeeded"),
                    case["native"].execute_read_v3.return_value
                    if kind != "service"
                    else {},
                ),
                None,
            ),
            (
                "invoke",
                replace(read_call, scope=scope),
                None,
                ("invalid", {}),
                None,
            ),
        ])
    selected_result = {
        "version": "batten.selected-result/1",
        "kind": "get_many",
        "items": [
            {
                "key": {
                    "record": ["demo", "Note"],
                    "keyId": "primary",
                    "components": [{"string": "n-1"}],
                },
                "fields": [{"field": ["demo", "id"], "value": {"string": "n-1"}}],
            }
        ],
    }
    actions.append((
        "open_error" if kind == "service" else "selected",
        selected_call,
        selection,
        None if kind == "service" else ("succeeded", selected_result),
        "snapshot" if kind == "service" else None,
    ))
    case.update({
        "selected_call": selected_call,
        "selection": selection,
        "config": config,
        "actions": tuple(actions),
    })
    case["expected_capture"] = (
        1,
        0 if kind == "service" or not composite else 1,
        0 if kind == "service" else 1,
        0 if kind == "service" else 1,
    )
    return case


def record_root_host(capabilities: Mapping[str, str]) -> Any:
    return SimpleNamespace(
        config=SimpleNamespace(selected_capabilities=capabilities),
        operations={"inspect": Operation("inspect", False, ("get_many",))},
    )
