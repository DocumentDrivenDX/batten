"""Pure scenario and observation data for the API3 selected-session workflow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, cast

from api3_connection_fixture import budget_intents
from lintel.ports import Arguments, ConnectionIntent, ElementRef, NodeKey


@dataclass(frozen=True)
class SessionStep:
    name: str
    method: str
    arguments: tuple[object, ...]
    expected_error: str | None = None


@dataclass(frozen=True)
class RequestObservation:
    opened: int
    get_many_calls: int
    connection_calls: int
    get_many_trace_ids: tuple[int, ...]
    connection_trace_ids: tuple[int, ...]
    prepared_identity_ids: tuple[int, ...]
    prepared_scope_ids: tuple[int, ...]
    opened_identity_id: int
    opened_scope_id: int


@dataclass(frozen=True)
class RouteObservation:
    provider_digest: str
    admission_digest: str


@dataclass(frozen=True)
class ResultObservation:
    node_fields: tuple[Mapping[str, object] | None, ...]
    page_edge_counts: tuple[int, ...]
    page_node_fields: tuple[tuple[Mapping[str, object], ...], ...]
    page_record_refs: tuple[ElementRef, ...]


def request_observation(case: Mapping[str, Any]) -> RequestObservation:
    native = case["native"]
    request = case["request"]
    identities = [entry[0] for entry in native.prepared_connection_scopes]
    scopes = [entry[1] for entry in native.prepared_connection_scopes]
    opened = native.open_request.call_args
    return RequestObservation(
        native.open_request.call_count,
        request.execute_get_many.await_count,
        request.execute_forward_connection.await_count,
        tuple(id(value) for value in case["get_many_call_trace"]),
        tuple(id(value) for value in case["connection_call_trace"]),
        tuple(id(value) for value in identities),
        tuple(id(value) for value in scopes),
        id(opened.args[0]),
        id(opened.args[1]),
    )


def route_observation(provider: Any, admission: Any) -> RouteObservation:
    key = "connection.routes.digest"
    return RouteObservation(
        provider.capabilities()[key], admission.selected_capabilities[key]
    )


def result_observation(results: list[object]) -> ResultObservation:
    nodes = cast(tuple[Any | None, ...], results[0])
    pages = cast(list[Any], results[1:])
    return ResultObservation(
        tuple(node.fields if node is not None else None for node in nodes),
        tuple(len(page.edges) for page in pages),
        tuple(tuple(edge.node.fields for edge in page.edges) for page in pages),
        tuple(edge.node.key.record for page in pages for edge in page.edges),
    )


def session_workflow(
    mode: str, intents: tuple[ConnectionIntent, ...]
) -> tuple[
    tuple[ConnectionIntent, ...],
    tuple[SessionStep, ...],
    str,
    int,
    int,
    int,
]:
    if mode in {"complete", "complete_then_replay"}:
        steps = [
            SessionStep(
                "getMany",
                "get_many",
                (
                    intents[0].lookup,
                    (
                        NodeKey(
                            ElementRef(intents[0].lookup.module, intents[0].lookup.id),
                            "primary",
                            ({"string": "n-1"},),
                        ),
                    ),
                    (),
                ),
            )
        ]
        steps.extend(
            SessionStep(f"connection:{index}", "planned_connection", (intent,))
            for index, intent in enumerate(intents)
        )
        if mode == "complete_then_replay":
            steps.append(
                SessionStep(
                    "replay", "planned_connection", (intents[0],), "UNSUPPORTED"
                )
            )
        return intents, tuple(steps), "UNSUPPORTED", 5, 1, 5
    if mode == "ordinary_refusal":
        arguments: Arguments = MappingProxyType({})
        return (
            (intents[0],),
            (
                SessionStep(
                    "ordinary connection",
                    "connection",
                    (
                        intents[0].lookup,
                        arguments,
                        1,
                        None,
                        intents[0].fields,
                    ),
                    "UNSUPPORTED",
                ),
                SessionStep(
                    "post-refusal getMany",
                    "get_many",
                    (
                        intents[0].lookup,
                        (
                            NodeKey(
                                ElementRef(
                                    intents[0].lookup.module, intents[0].lookup.id
                                ),
                                "primary",
                                ({"string": "n-1"},),
                            ),
                        ),
                        (),
                    ),
                    "UNSUPPORTED",
                ),
            ),
            "UNSUPPORTED",
            0,
            0,
            1,
        )
    if mode == "alias_refusal":
        return (
            (intents[0],),
            (
                SessionStep(
                    "wrong response key",
                    "planned_connection",
                    (replace(intents[0], response_key="differentAlias"),),
                    "UNSUPPORTED",
                ),
                SessionStep(
                    "post-refusal getMany",
                    "get_many",
                    (
                        intents[0].lookup,
                        (
                            NodeKey(
                                ElementRef(
                                    intents[0].lookup.module, intents[0].lookup.id
                                ),
                                "primary",
                                ({"string": "n-1"},),
                            ),
                        ),
                        (),
                    ),
                    "UNSUPPORTED",
                ),
            ),
            "UNSUPPORTED",
            0,
            0,
            1,
        )
    budget = budget_intents(intents)
    return (
        budget,
        (
            SessionStep("first page", "planned_connection", (budget[0],)),
            SessionStep(
                "aggregate overrun",
                "planned_connection",
                (budget[1],),
                "LIMIT_EXCEEDED",
            ),
            SessionStep(
                "third dispatch refused",
                "planned_connection",
                (budget[2],),
                "LIMIT_EXCEEDED",
            ),
        ),
        "LIMIT_EXCEEDED",
        2,
        0,
        3,
    )
