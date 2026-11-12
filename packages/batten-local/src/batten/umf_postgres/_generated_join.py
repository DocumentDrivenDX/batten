"""Optional required-inner joined reads over one verified ``/8`` artifact."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Protocol, cast

from batten.contracts import ExecutionScope, Identity, OperationCall, OperationOutcome
from umf_access.unified import GeneratedNativeError, SessionIdentity
from umf_access_generated_executor import (
    ExecutionScope as GeneratedScope,
)
from umf_access_generated_executor import (
    GeneratedExecutionError,
    GeneratedExecutor,
    GeneratedJoinedReadCall,
    GeneratedJoinedReadRoot,
)

from ._generated_values import native_read_refusal, read_refusal
from ._read_binding import ReadBindingMetadata

_PROFILE8 = "weft.generated-read-algebra/8"
_Route = tuple[str, str, str, str]


class GeneratedJoinBinding(ReadBindingMetadata, Protocol):
    """Public native operations needed by the joined-read route."""

    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def algebra_json(self) -> bytes: ...
    @property
    def joined_read_roots(self) -> tuple[GeneratedJoinedReadRoot, ...]: ...

    def joined_read_identity(self, call: GeneratedJoinedReadCall) -> str: ...
    def validate_joined_read_result(
        self, result: object, call: GeneratedJoinedReadCall
    ) -> bool: ...
    async def execute_joined_read(
        self,
        call: GeneratedJoinedReadCall,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]: ...


@dataclass(frozen=True)
class _Invocation:
    native: GeneratedJoinBinding
    call: GeneratedJoinedReadCall
    identity: SessionIdentity
    scope: GeneratedScope


class GeneratedJoinExecution:
    """Admit disjoint operations pinned to issuer-owned root/Relationship pairs."""

    def __init__(
        self,
        executor: GeneratedExecutor,
        factory: Callable[[], Awaitable[GeneratedJoinBinding]],
        authority: Identity,
        routes: Mapping[str, _Route],
    ) -> None:
        if (
            executor.read_profile != _PROFILE8
            or not routes
            or any(
                type(operation) is not str
                or not operation
                or type(route) is not tuple
                or len(route) != 4
                or any(type(part) is not str or not part for part in route)
                for operation, route in routes.items()
            )
        ):
            raise ValueError("generated joined-read profile and routes required")
        self._executor, self._factory, self._authority = executor, factory, authority
        self._routes = MappingProxyType(dict(routes))
        self._native: GeneratedJoinBinding | None = None
        self._roots: Mapping[str, _Route] = MappingProxyType({})

    async def prepare(self) -> None:
        if self._native is not None:
            return
        native = await self._factory()
        methods = (
            "joined_read_identity",
            "execute_joined_read",
            "validate_joined_read_result",
        )
        if any(not callable(getattr(native, method, None)) for method in methods):
            raise ValueError("native joined-read binding is incomplete")
        if (
            native.schema != self._executor.native_table.source_digest
            or native.read_profile != _PROFILE8
            or native.target_binding_digest != self._executor.target.binding_digest
            or native.artifact_digest != self._executor.trusted_artifact.artifact_digest
            or native.receipt_digest != self._executor.trusted_artifact.receipt_digest
            or native.algebra_json != self._executor.read_algebra_json
        ):
            raise ValueError(
                "native joined-read binding differs from verified artifact"
            )
        roots = self._executor.joined_read_roots
        if native.joined_read_roots != roots or len({
            (root.module, root.record, root.relationship_module, root.relationship_id)
            for root in roots
        }) != len(roots):
            raise ValueError("verified joined-read root inventory is ambiguous")
        issued = {
            (root.module, root.record, root.relationship_module, root.relationship_id)
            for root in roots
        }
        admitted: dict[str, _Route] = {}
        for operation, route in self._routes.items():
            if route not in issued or route[0] != native.module:
                raise ValueError("configured joined-read route is not verified")
            admitted[operation] = route
        self._native = native
        self._roots = MappingProxyType(admitted)

    def capabilities(self) -> Mapping[str, str]:
        if self._native is None or not self._roots:
            return MappingProxyType({})
        return MappingProxyType({"read.joined": "statement-1"})

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        refused = read_refusal(call)
        if refused is not None:
            return refused
        prepared = self._prepare(call.snapshot())
        if isinstance(prepared, OperationOutcome):
            return prepared
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        result = await prepared.native.execute_joined_read(
            prepared.call, identity=prepared.identity, scope=prepared.scope
        )
        if not prepared.native.validate_joined_read_result(result, prepared.call):
            return OperationOutcome("unavailable", "", {}, "native_refused")
        return _joined_outcome(result, prepared.native.schema)

    def _prepare(self, call: OperationCall) -> _Invocation | OperationOutcome:
        native = self._native
        route = self._roots.get(call.operation)
        if native is None or route is None:
            return OperationOutcome(
                "unavailable" if native is None else "invalid",
                "",
                {},
                "not_prepared" if native is None else "unsupported",
            )
        scope = cast(ExecutionScope, call.scope)
        try:
            if set(call.inputs) != {"join"}:
                raise ValueError("joined-read envelope differs")
            joined = GeneratedJoinedReadCall.from_mapping(call.inputs["join"])
            if (
                joined.root_module,
                joined.root_record,
                joined.relationship_module,
                joined.relationship_id,
            ) != route:
                raise ValueError("joined-read route differs")
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
            call_identity = native.joined_read_identity(joined)
            if type(call_identity) is not str or not call_identity:
                raise ValueError("joined-read identity is malformed")
        except GeneratedNativeError as error:
            return _joined_refusal(error.code, native.schema)
        except GeneratedExecutionError as error:
            return _joined_refusal(error.code, native.schema)
        except (ValueError, TypeError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        return _Invocation(native, joined, identity, generated_scope)

    async def aclose(self) -> None:
        self._native = None
        self._roots = MappingProxyType({})


def _joined_refusal(code: str, schema: str) -> OperationOutcome:
    outcomes = {
        "DENIED": ("denied", "denied"),
        "CONFLICT": ("precondition_failed", "precondition_failed"),
        "INVALID": ("invalid", "invalid"),
        "INVALID_CURSOR": ("invalid", "invalid_cursor"),
        "UNSUPPORTED": ("invalid", "unsupported"),
        "LIMIT_EXCEEDED": ("unavailable", "limit_exceeded"),
        "TOO_MANY_ROWS": ("unavailable", "limit_exceeded"),
        "SCHEMA_MISMATCH": ("unavailable", "schema_mismatch"),
        "PRECONDITION_FAILED": ("precondition_failed", "precondition_failed"),
        "BUSY": ("unavailable", "busy"),
    }
    if code in outcomes:
        status, reason = outcomes[code]
        return OperationOutcome(status, "", {}, reason)
    return native_read_refusal({"schema": schema, "error": {"code": code}}, schema)


def _joined_outcome(result: Mapping[str, object], schema: str) -> OperationOutcome:
    if set(result) == {"schema", "table"}:
        return OperationOutcome("succeeded", "", result)
    error = result.get("error")
    if isinstance(error, Mapping):
        error_mapping = cast(Mapping[str, object], error)
    else:
        error_mapping: Mapping[str, object] = {}
    if set(error_mapping) == {"code"}:
        value = error_mapping["code"]
        return _joined_refusal(cast(str, value), schema)
    return native_read_refusal(result, schema)


__all__ = ["GeneratedJoinBinding", "GeneratedJoinExecution"]
