"""Generated native execution through issued host scopes and upstream guards."""

from collections.abc import Awaitable, Callable, Mapping
from typing import Literal, Protocol, cast

from batten.contracts import ExecutionScope, Identity, OperationCall, OperationOutcome
from umf_access.unified import SessionIdentity
from umf_access_generated_executor import ExecutionScope as GeneratedScope

from ._generated_values import native_read_refusal, read_refusal, snapshot_inputs


class GeneratedNativeBinding(Protocol):
    schema: str
    module: str

    async def execute(
        self,
        request: dict[str, object],
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]: ...


def _result_valid(
    result: Mapping[str, object], native: GeneratedNativeBinding, operation: str
) -> bool:
    table = result.get("table")
    if (
        set(result) != {"schema", "table"}
        or result.get("schema") != native.schema
        or not isinstance(table, Mapping)
    ):
        return False
    frame = cast(Mapping[str, object], table)
    common = {"kind", "version", "module", "operation", "sourceDigest"}
    fields = {"count"} if frame.get("kind") == "count" else {"rows", "cursor"}
    return (
        set(frame) == common | fields
        and frame.get("version") == "umf.table-read-result/0.1"
        and frame.get("module") == native.module
        and frame.get("operation") == operation
        and frame.get("sourceDigest") == native.schema
        and frame.get("kind") in ("count", "many", "one", "optional")
    )


class GeneratedUmfExecution:
    def __init__(
        self,
        factory: Callable[[], Awaitable[GeneratedNativeBinding]],
        authority: Identity,
        *,
        max_input_bytes: int = 8_388_608,
    ):
        if type(max_input_bytes) is not int or max_input_bytes < 1:
            raise ValueError("positive input capacity required")
        self._factory, self._authority = factory, authority
        self._max_input_bytes = max_input_bytes
        self._native: GeneratedNativeBinding | None = None

    async def prepare(self) -> None:
        if self._native is None:
            self._native = await self._factory()

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        refused = read_refusal(call)
        if refused is not None:
            return refused
        scope = cast(ExecutionScope, call.scope)
        try:
            inputs = snapshot_inputs(call.inputs, self._max_input_bytes)
        except (ValueError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        native = self._native
        if native is None:
            return OperationOutcome("unavailable", "", {}, "not_prepared")
        identity = SessionIdentity(
            cast(Literal["person", "batch"], call.actor.kind), call.actor.subject
        )
        generated_scope = GeneratedScope(
            scope.application,
            identity,
            scope.request_id,
            scope.deadline_monotonic,
            scope.lease_id,
            scope.api_digest,
            scope.consistency,
        )
        result = await native.execute(
            {
                "contract": "umf.access/1",
                "schema": native.schema,
                "kind": "table",
                "module": native.module,
                "operation": call.operation,
                "call": {"kind": "single", "inputs": inputs},
                "phase": call.phase,
                "mutation": False,
                "idempotency_key": call.key,
            },
            identity=identity,
            scope=generated_scope,
        )
        if not _result_valid(result, native, call.operation):
            return native_read_refusal(result, native.schema)
        return OperationOutcome("succeeded", "", result)

    async def aclose(self) -> None:
        self._native = None


__all__ = ["GeneratedNativeBinding", "GeneratedUmfExecution"]
