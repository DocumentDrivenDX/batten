"""Public API3 staging keeps generated connections on the Host request owner."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, Literal, cast

import pytest
from api3_connection_fixture import (
    configured_api3_case,
    connection_intents,
    host_operations,
    request_scope,
)
from api3_connection_scenarios import (
    RequestObservation,
    RouteObservation,
    request_observation,
    result_observation,
    route_observation,
    session_workflow,
)
from batten.contracts import (
    Actor,
    HostConfig,
    HostServices,
)
from batten.lintel import LintelExecution
from batten.runtime import create_host
from lintel.ports import (
    Arguments,
    ConnectionIntent,
    ElementRef,
    ExecutionError,
    NodeKey,
    OperationRef,
)

from tests.runtime.test_lintel_host import Capture


@pytest.mark.parametrize("kind", ["person", "batch"])
@pytest.mark.parametrize(
    "mode",
    ["complete_then_replay", "ordinary_refusal", "alias_refusal", "aggregate_budget"],
)
async def test_generated_v5_host_prepares_mixed_roots_on_one_request(
    kind: Literal["person", "batch"],
    mode: Literal[
        "complete_then_replay", "ordinary_refusal", "alias_refusal", "aggregate_budget"
    ],
) -> None:
    configured = configured_api3_case(kind, mode)
    case = configured.case
    await configured.provider.prepare()
    host = create_host(
        HostConfig(
            case["app"], host_operations(), 8, 10, configured.provider.capabilities()
        ),
        HostServices(
            case["provider_kwargs"]["authority"], Capture(), configured.provider
        ),
    )
    execution = LintelExecution(
        host,
        configured.config,
        configured.executor.native_table,
        generated=configured.executor,
        connection_admission=configured.admission,
    )
    async with host:
        assert await host.admit(case["app"])
        authority = await host.open_scope(
            cast(Actor, case["actor"]),
            "prepared-connections",
            api_digest=configured.prepared.api_digest,
            consistency="request-snapshot-1",
        )
        lintel_scope = request_scope(configured.prepared, authority)
        intents = connection_intents(configured.prepared)
        (
            planned,
            steps,
            global_error,
            expected_connections,
            expected_get_many,
            expected_plan,
        ) = session_workflow(mode, intents)
        assert (
            mode != "aggregate_budget"
            or 4_300_000 < configured.admission.response_bytes
        )
        results: list[object] = []
        stages: list[str] = []
        with pytest.raises(ExecutionError, match=global_error):
            async with execution.session_planned(lintel_scope, planned) as session:
                for step in steps:
                    if step.method == "get_many":
                        pending: Awaitable[object] = session.get_many(
                            *cast(
                                tuple[
                                    OperationRef,
                                    tuple[NodeKey, ...],
                                    tuple[ElementRef, ...],
                                ],
                                step.arguments,
                            )
                        )
                    elif step.method == "connection":
                        pending = session.connection(
                            *cast(
                                tuple[
                                    OperationRef,
                                    Arguments,
                                    int,
                                    str | None,
                                    tuple[ElementRef, ...],
                                ],
                                step.arguments,
                            )
                        )
                    else:
                        pending = session.planned_connection(
                            *cast(tuple[ConnectionIntent], step.arguments)
                        )
                    if step.expected_error is None:
                        results.append(await pending)
                    else:
                        with pytest.raises(ExecutionError, match=step.expected_error):
                            await pending
                    stages.append(step.name)
        assert (
            stages,
            route_observation(configured.provider, configured.admission),
        ) == (
            [step.name for step in steps],
            RouteObservation(
                "96a3699160b47a5741e923d3fa134025318a20018b5563c46dde43873f7caf05",
                "96a3699160b47a5741e923d3fa134025318a20018b5563c46dde43873f7caf05",
            ),
        )
        observed_request = request_observation(case)
        assert observed_request == RequestObservation(
            1,
            expected_get_many,
            expected_connections,
            (id(case["request"]),) * expected_get_many,
            (id(case["request"]),) * expected_connections,
            (observed_request.prepared_identity_ids[0],) * expected_plan,
            (observed_request.prepared_scope_ids[0],) * expected_plan,
            observed_request.prepared_identity_ids[0],
            observed_request.prepared_scope_ids[0],
        )
        if mode == "complete_then_replay":
            observed_result = result_observation(results)
            assert observed_result.node_fields == ({},)
            assert observed_result.page_edge_counts == (1, 1, 0, 1, 1)
            assert observed_result.page_node_fields[3] == ({},)
            assert observed_result.page_record_refs == (
                ElementRef("demo", "Note"),
                ElementRef("demo", "Task"),
                ElementRef("demo", "Note"),
                ElementRef("demo", "Note"),
            )
            assert (
                observed_result.page_node_fields[4]
                == observed_result.page_node_fields[0]
            )
        if mode == "aggregate_budget":
            assert len(cast(Any, results[0]).edges) == 1
