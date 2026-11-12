"""Pure fixture builders for the captured strict API3 generated artifact."""

import json
from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, NamedTuple, cast

from batten.contracts import ArtifactRef, ExecutionScope, Operation
from batten.lintel import (
    ConnectionAdmission,
    ExposureConfig,
    ExposureRecordRoot,
    LintelExecution,
)
from batten.umf_postgres import GeneratedTableExecution
from generated_batch_case import batch_case
from lintel.ports import (
    ConnectionIntent,
    ElementRef,
    OperationRef,
    RequestScope,
)
from lintel.projection import (
    AdmittedPreparedApi,
    PreparedConnection,
    TrustedPreparedRef,
    load_prepared_api,
)
from umf_access.unified import AsyncSession, SessionIdentity, SessionPolicy
from umf_access_generated_executor import GeneratedExecutor


def prepared_api_inputs() -> tuple[bytes, TrustedPreparedRef]:
    folder = Path(__file__).with_name("fixtures")
    artifact = (folder / "prepared-api-v3-four-fields-proof.json").read_bytes()
    trusted = cast(
        dict[str, object],
        json.loads((folder / "prepared-api-v3-four-fields-trust.json").read_bytes()),
    )
    return artifact, TrustedPreparedRef(
        cast(str, trusted["artifactSha256"]),
        cast(str, trusted["artifactDigest"]),
        cast(str, trusted["application"]),
        cast(str, trusted["apiDigest"]),
        cast(str, trusted["exposureSha256"]),
        tuple(
            (item["identity"], item["sha256"])
            for item in cast(list[dict[str, str]], trusted["sources"])
        ),
        tuple(
            (pair[0], pair[1])
            for pair in cast(list[tuple[str, str]], trusted["capabilities"])
        ),
        cast(str, trusted["bindingProfile"]),
        cast(str, trusted["scalarCodecProfile"]),
        tuple(
            (pair[0], pair[1])
            for pair in cast(list[tuple[str, str]], trusted["limits"])
        ),
        cast(str, trusted["generatedRootsSha256"]),
        cast(str, trusted["generatedConnectionsSha256"]),
    )


def api3_case(
    kind: Literal["person", "batch"], authority: object
) -> tuple[
    dict[str, Any],
    GeneratedExecutor,
    AdmittedPreparedApi,
    ExposureConfig,
    ConnectionAdmission,
]:
    case = batch_case(kind, authority, composite="v5")
    executor = cast(GeneratedExecutor, case["executor"])
    prepared = load_prepared_api(*prepared_api_inputs())
    config = exposure_config(executor)
    admission = LintelExecution.prepare_connections(
        config, prepared, executor.native_table, executor
    )
    return case, executor, prepared, config, admission


class ConnectionAuthority:
    """Allow only the explicitly configured fixture operations."""

    async def check(self, actor: object, operation: str) -> bool:
        return operation in {"records.note", "records.task"}


def profile7_base_routes_case(kind: Literal["person", "batch"]) -> tuple[Any, Any]:
    """Prepare the issued v7 root with a protocol-only native binding double."""
    from generated_provider_cases import Native
    from read_artifacts import read_executor

    executor, _root = read_executor("v7")
    trust = executor.trusted_artifact
    native: Any = Native(executor)
    native.artifact_digest = trust.artifact_digest
    native.receipt_digest = trust.receipt_digest
    native.algebra_json = executor.read_algebra_json
    fields = (ElementRef("demo", "owner"),)
    root = ExposureRecordRoot(
        OperationRef("demo", "Note", "record"),
        "inspect",
        executor.native_table.source_digest,
        trust.artifact_digest,
        trust.receipt_digest,
        executor.target.binding_digest,
        sha256(executor.read_algebra_json).hexdigest(),
        "primary",
        fields,
        ("string",),
        tuple((field, "string") for field in fields),
    )

    def unused_factory(_identity: SessionIdentity) -> AbstractAsyncContextManager[Any]:
        raise AssertionError("base profile preparation must not open a native request")

    session = AsyncSession(
        unused_factory,
        SessionPolicy({"page7-fixture-user": "fixture_role"}, {}, "fixture_schema"),
    )

    async def factory() -> Any:
        return native

    provider = GeneratedTableExecution(
        executor,
        factory,
        data_session=session,
        authority=ConnectionAuthority(),
        read_routes={"ordinary": ("demo", "Note")},
        record_routes={"inspect": root},
    )
    return (
        provider,
        native,
    )


@dataclass(frozen=True)
class RouteMismatchCases:
    connection_provider: Any
    connection_native: Any
    page_provider: Any
    page_native: Any
    incomplete_page: Any
    incomplete_page_native: Any
    profile7_base_routes: Any
    profile7_base_native: Any


def route_mismatch_cases(kind: Literal["person", "batch"]) -> RouteMismatchCases:
    case, executor, _prepared, _config, _admission = api3_case(
        kind, ConnectionAuthority()
    )
    native = case["native"]
    native.connection_routes = {}
    connection_provider = case["provider_type"](
        executor, case["factory"], **case["provider_kwargs"]
    )
    from generated_provider_cases import page_route_scenario

    page = page_route_scenario(kind, ("demo", "Task"))
    incomplete = page_route_scenario(kind, missing_method="execute_ordinary_page")
    profile7_provider, profile7_native = profile7_base_routes_case(kind)
    return RouteMismatchCases(
        connection_provider,
        native,
        page.provider,
        page.native,
        incomplete.provider,
        incomplete.native,
        profile7_provider,
        profile7_native,
    )


def bind_api3_case(
    case: dict[str, Any], config: ExposureConfig, admission: ConnectionAdmission
) -> None:
    """Bind fake frames to immutable route metadata already derived from API3."""
    from generated_batch_case import connection_frame_fixture

    case["app"] = config.application
    case["native"].connection_routes = dict(admission.native_routes)
    case["provider_kwargs"]["connection_routes"] = admission.native_routes
    case["provider_kwargs"]["record_routes"] = {
        root.host_operation: root for root in config.record_roots
    }
    case["connection_call_trace"] = []

    def execute_forward_connection(prepared_call: object) -> dict[str, Any]:
        case["connection_call_trace"].append(case["request"])
        return connection_frame_fixture(
            cast(tuple[object, object, object], prepared_call)[0],
            admission.native_routes,
            case["executor"],
        )

    case["request"].execute_forward_connection.side_effect = execute_forward_connection
    result = {
        "version": "umf.generated-key-batch-result/1",
        "sourceDigest": case["executor"].native_table.source_digest,
        "bindingDigest": case["executor"].target.binding_digest,
        "module": "demo",
        "record": "Note",
        "keyId": "primary",
        "fields": [],
        "items": [{"key": [{"string": "n-1"}], "values": []}],
    }
    case["get_many_call_trace"] = []

    def execute_get_many(_call: object) -> dict[str, Any]:
        case["get_many_call_trace"].append(case["request"])
        return result

    case["request"].execute_get_many.side_effect = execute_get_many


def large_connection_frame(
    prepared_call: object, routes: Mapping[str, Any], executor: Any, size: int
) -> dict[str, Any]:
    from generated_batch_case import connection_frame_fixture

    call = cast(tuple[object, object, object], prepared_call)[0]
    frame = connection_frame_fixture(call, routes, executor)
    native_call = cast(Any, call)
    if native_call.first and native_call.fields:
        field = native_call.fields[0]
        edge = cast(dict[str, Any], cast(list[Any], frame["edges"])[0])
        node = cast(dict[str, Any], edge["node"])
        cast(dict[str, Any], node["fields"])[field] = {"string": "x" * size}
    return frame


def bind_large_connection_frames(
    case: dict[str, Any], admission: ConnectionAdmission, size: int
) -> None:
    def execute_forward_connection(prepared_call: object) -> dict[str, Any]:
        case["connection_call_trace"].append(case["request"])
        return large_connection_frame(
            prepared_call, admission.native_routes, case["executor"], size
        )

    case["request"].execute_forward_connection.side_effect = execute_forward_connection


class ConfiguredApi3Case(NamedTuple):
    case: dict[str, Any]
    executor: GeneratedExecutor
    prepared: AdmittedPreparedApi
    config: ExposureConfig
    admission: ConnectionAdmission
    provider: Any


def configured_api3_case(
    kind: Literal["person", "batch"], mode: str
) -> ConfiguredApi3Case:
    case, executor, prepared, config, admission = api3_case(kind, ConnectionAuthority())
    bind_api3_case(case, config, admission)
    if mode == "aggregate_budget":
        bind_large_connection_frames(case, admission, 4_300_000)
    provider = case["provider_type"](
        executor, case["factory"], **case["provider_kwargs"]
    )
    return ConfiguredApi3Case(case, executor, prepared, config, admission, provider)


def exposure_config(executor: GeneratedExecutor) -> ExposureConfig:
    trust = executor.trusted_artifact
    algebra_digest = sha256(executor.read_algebra_json).hexdigest()
    roots: list[ExposureRecordRoot] = []
    for record, host_operation in (("Note", "records.note"), ("Task", "records.task")):
        if record == "Note":
            exposed = tuple(
                ElementRef("demo", field)
                for field in ("amount", "enabled", "owner", "payload")
            )
        else:
            exposed = (ElementRef("demo", "task_value"),)
        roots.append(
            ExposureRecordRoot(
                OperationRef("demo", record, "record"),
                host_operation,
                executor.native_table.source_digest,
                trust.artifact_digest,
                trust.receipt_digest,
                executor.target.binding_digest,
                algebra_digest,
                "primary",
                exposed,
                ("string",),
                tuple(
                    (
                        field,
                        "decimalToken"
                        if field.element == "amount"
                        else "boolean"
                        if field.element == "enabled"
                        else "string",
                    )
                    for field in exposed
                ),
            )
        )
    return ExposureConfig(
        ArtifactRef(
            "fixture-app",
            "cab24da3fcf113acc7a59c4c58d1a3f65d9c8c33802e43129792a53eb1f0bc11",
        ),
        "bf0a7712a0175cce95280a7dcd0f150604dba7e44bfbdae35f7db3a84b6ac105",
        executor.native_table.source_digest,
        (),
        {
            "connection.forward": "edge-cursor-1",
            "read.consistency": "request-snapshot-1",
        },
        tuple(roots),
    )


def connection_intents(api: AdmittedPreparedApi) -> tuple[ConnectionIntent, ...]:
    note, task = api.generated_connections
    return (
        ConnectionIntent(
            "noteAlias",
            note.name,
            note.lookup,
            MappingProxyType({}),
            1,
            None,
            (ElementRef("demo", "owner"),),
        ),
        ConnectionIntent(
            "taskAlias",
            task.name,
            task.lookup,
            MappingProxyType({}),
            1,
            None,
            (ElementRef("demo", "task_value"),),
        ),
        ConnectionIntent(
            "emptyZero",
            note.name,
            note.lookup,
            MappingProxyType({}),
            0,
            None,
            (),
        ),
        ConnectionIntent(
            "emptyOne",
            note.name,
            note.lookup,
            MappingProxyType({}),
            1,
            None,
            (),
        ),
        ConnectionIntent(
            "noteAliasTwin",
            note.name,
            note.lookup,
            MappingProxyType({}),
            1,
            None,
            (ElementRef("demo", "owner"),),
        ),
    )


def refusal_intents(
    intents: tuple[ConnectionIntent, ...],
) -> tuple[tuple[ConnectionIntent, str], ...]:
    return (
        (
            replace(intents[0], response_key="badCursor", after="invalid-cursor"),
            "INVALID_CURSOR",
        ),
        (replace(intents[0], arguments={"filter": {}}), "UNSUPPORTED"),
    )


def escaped_profile_case(
    config: ExposureConfig,
) -> tuple[
    PreparedConnection,
    ExposureRecordRoot,
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    module, record = "demo/~module", "Note/Part~"
    lookup = OperationRef(module, record, "record")
    visible = ElementRef(module, "owner/id~")
    key = ElementRef(module, "id/~")
    visible_id = "demo~1~0module/owner~1id~0"
    key_id = "demo~1~0module/id~1~0"
    visible_output = {"carrier": "string", "nullable": False}
    key_output = {"carrier": "string", "nullable": False}
    field_rows: tuple[dict[str, object], ...] = (
        {
            "fieldId": visible_id,
            "sourceField": {"module": module, "element": visible.element},
            "output": visible_output,
            "scalar": "string",
            "nullable": False,
        },
        {
            "fieldId": key_id,
            "sourceField": {"module": module, "element": key.element},
            "output": key_output,
            "scalar": "string",
            "nullable": False,
        },
    )
    connection = PreparedConnection(
        lookup, "escaped", (visible,), key, "0" * 64, {"fields": list(field_rows)}
    )
    exposed = replace(config.record_roots[0], ref=lookup, fields=(visible,))
    root: dict[str, object] = {
        "fields": {
            visible_id: {"sourceField": {"module": module, "element": visible.element}},
            key_id: {"sourceField": {"module": module, "element": key.element}},
        },
        "forwardConnection": {
            "fieldOutputs": [
                {"fieldId": visible_id, "output": visible_output},
                {"fieldId": key_id, "output": key_output},
            ]
        },
        "primaryKey": [{"fieldId": key_id}],
    }
    good_profile: dict[str, object] = {
        "fields": [dict(field_rows[0]), dict(field_rows[1])]
    }
    bad_fields: list[dict[str, object]] = [dict(field_rows[0]), dict(field_rows[1])]
    bad_fields[0]["fieldId"] = "demo/~module/owner/id~"
    bad_profile: dict[str, object] = {"fields": bad_fields}
    return connection, exposed, root, good_profile, bad_profile


def budget_intents(
    intents: tuple[ConnectionIntent, ...],
) -> tuple[ConnectionIntent, ...]:
    return tuple(
        replace(intents[0], response_key=f"budget{index}") for index in range(3)
    )


def request_scope(api: AdmittedPreparedApi, authority: ExecutionScope) -> RequestScope:
    return RequestScope(
        api.application,
        api.api_digest,
        "query",
        authority,
        authority.request_id,
        authority.deadline_monotonic,
    )


def host_operations() -> tuple[Operation, ...]:
    return (
        Operation("records.note", False, ("get_many", "connection")),
        Operation("records.task", False, ("get_many", "connection")),
        Operation("ordinary", False),
    )
