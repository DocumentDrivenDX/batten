"""Protocol fixture for the joined route mode in generated Host checks."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from types import SimpleNamespace
from typing import Any, Literal, cast

from batten.contracts import Actor, ArtifactRef, ExecutionScope, OperationCall
from batten.umf_postgres._generated_join import (
    GeneratedJoinBinding,
    GeneratedJoinExecution,
)
from generated_provider_cases import Authority
from umf_access_generated_executor import (
    GeneratedExecutor,
    GeneratedJoinedReadCall,
    GeneratedJoinedReadRoot,
)


async def joined_route_observation(
    kind: Literal["person", "batch"],
) -> tuple[object, ...]:
    """Exercise route pins, value frames and fixed refusals on one binding."""
    root = GeneratedJoinedReadRoot("root-key", "demo", "Task", "demo", "TaskNote")
    executor = cast(
        GeneratedExecutor,
        SimpleNamespace(
            read_profile="weft.generated-read-algebra/8",
            native_table=SimpleNamespace(source_digest="s" * 64),
            target=SimpleNamespace(binding_digest="b" * 64),
            trusted_artifact=SimpleNamespace(
                artifact_digest="a" * 64, receipt_digest="r" * 64
            ),
            read_algebra_json=b"{}",
            joined_read_roots=(root,),
        ),
    )
    frame: dict[str, object] = {"schema": "s" * 64, "table": {"rows": []}}
    native = SimpleNamespace(
        schema="s" * 64,
        module="demo",
        read_profile="weft.generated-read-algebra/8",
        target_binding_digest="b" * 64,
        artifact_digest="a" * 64,
        receipt_digest="r" * 64,
        algebra_json=b"{}",
        joined_read_roots=(root,),
        executions=[],
        response=frame,
    )

    def identity(call: GeneratedJoinedReadCall) -> str:
        return "call-digest" if call.root_record == "Task" else ""

    async def execute(
        call: GeneratedJoinedReadCall, *, identity: object, scope: object
    ) -> dict[str, object]:
        native.executions.append((call, identity, scope))
        return cast(dict[str, object], native.response)

    def validate(result: object, _call: GeneratedJoinedReadCall) -> bool:
        return result is native.response

    native.joined_read_identity = identity
    native.execute_joined_read = execute
    native.validate_joined_read_result = validate

    async def factory() -> Any:
        return native

    route = ("demo", "Task", "demo", "TaskNote")
    provider = GeneratedJoinExecution(
        executor,
        cast(Callable[[], Awaitable[GeneratedJoinBinding]], factory),
        Authority({"amount": {"string": "unchanged"}}),
        {"Query.joined": route},
    )
    await provider.prepare()
    actor = Actor("reviewer", kind=kind)
    scope = ExecutionScope(
        ArtifactRef("app", "d" * 64), actor, "request", 9999999999.0, "lease"
    )
    valid = GeneratedJoinedReadCall(
        "demo", "Task", "demo", "TaskNote", None, None, (), 10
    )
    wrong = GeneratedJoinedReadCall(
        "demo", "Other", "demo", "TaskNote", None, None, (), 10
    )
    outcomes = [
        await provider.invoke(
            OperationCall(
                "Query.joined", {"join": wrong.to_mapping()}, actor, scope=scope
            )
        ),
        await provider.invoke(
            OperationCall(
                "Query.joined", {"join": valid.to_mapping()}, actor, scope=scope
            )
        ),
    ]
    responses: tuple[Mapping[str, object], ...] = (
        {"schema": "s" * 64, "error": {"code": "UNSUPPORTED"}},
        {"schema": "s" * 64, "error": {"code": "CONFLICT"}},
        {"schema": "s" * 64, "diagnostic": "not a public frame"},
    )
    for response in responses:
        native.response = dict(response)
        outcomes.append(
            await provider.invoke(
                OperationCall(
                    "Query.joined", {"join": valid.to_mapping()}, actor, scope=scope
                )
            )
        )
    result = tuple(
        (outcome.status, outcome.code, outcome.result) for outcome in outcomes
    )
    await provider.aclose()
    return (*result, len(native.executions), frame)
