"""Ordinary Page calls over the verified combined generated read artifact."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Protocol, cast

from batten.contracts import (
    ExecutionScope,
    Identity,
    OperationCall,
    OperationOutcome,
)
from umf_access.unified import GeneratedNativeError, SessionIdentity
from umf_access_generated_executor import (
    ExecutionScope as GeneratedScope,
)
from umf_access_generated_executor import (
    GeneratedExecutionError,
    GeneratedExecutor,
    GeneratedOrdinaryPageCall,
    GeneratedOrdinaryPageRoot,
)

from ._generated_values import native_read_refusal, read_refusal
from ._read_binding import ReadBindingMetadata

_PROFILES = {"weft.generated-read-algebra/7", "weft.generated-read-algebra/8"}


class GeneratedPageBinding(ReadBindingMetadata, Protocol):
    """Public native adapter operations used by the Page route."""

    @property
    def ordinary_page_roots(self) -> tuple[GeneratedOrdinaryPageRoot, ...]: ...

    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def algebra_json(self) -> bytes: ...

    def ordinary_page_identity(self, call: GeneratedOrdinaryPageCall) -> bytes: ...

    def validate_ordinary_page_result(
        self, result: object, call: GeneratedOrdinaryPageCall
    ) -> bool: ...

    async def execute_ordinary_page(
        self,
        call: GeneratedOrdinaryPageCall,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]: ...


@dataclass(frozen=True)
class _PageInvocation:
    native: GeneratedPageBinding
    call: GeneratedOrdinaryPageCall
    identity: SessionIdentity
    scope: GeneratedScope


class GeneratedPageExecution:
    """Prepare operation-to-eligible-root pins and execute ordinary Pages."""

    def __init__(
        self,
        executor: GeneratedExecutor,
        factory: Callable[[], Awaitable[GeneratedPageBinding]],
        authority: Identity,
        routes: Mapping[str, tuple[str, str]],
    ) -> None:
        if (
            executor.read_profile not in _PROFILES
            or not routes
            or any(
                type(operation) is not str
                or not operation
                or type(root) is not tuple
                or len(root) != 2
                or any(type(part) is not str or not part for part in root)
                for operation, root in routes.items()
            )
        ):
            raise ValueError("combined generated Page profile required")
        self._executor, self._factory, self._authority = executor, factory, authority
        self._routes = MappingProxyType(dict(routes))
        self._roots: Mapping[str, str] = MappingProxyType({})
        self._native: GeneratedPageBinding | None = None

    async def prepare(self) -> None:
        if self._native is not None:
            return
        native = await self._factory()
        if any(
            not callable(getattr(native, method, None))
            for method in (
                "ordinary_page_identity",
                "execute_ordinary_page",
                "validate_ordinary_page_result",
            )
        ):
            raise ValueError("native Page binding is incomplete")
        if (
            native.schema != self._executor.native_table.source_digest
            or native.read_profile not in _PROFILES
            or native.target_binding_digest != self._executor.target.binding_digest
            or native.artifact_digest != self._executor.trusted_artifact.artifact_digest
            or native.receipt_digest != self._executor.trusted_artifact.receipt_digest
            or native.algebra_json != self._executor.read_algebra_json
        ):
            raise ValueError("native Page binding differs from verified artifact")
        verified_roots = self._executor.ordinary_page_roots
        native_roots = native.ordinary_page_roots
        if (
            len({root.root_id for root in verified_roots}) != len(verified_roots)
            or len({(root.module, root.record) for root in verified_roots})
            != len(verified_roots)
            or native_roots != verified_roots
        ):
            raise ValueError("verified Page root inventory is ambiguous")
        issued = {(root.module, root.record): root.root_id for root in verified_roots}
        admitted: dict[str, str] = {}
        for operation, root in self._routes.items():
            root_id = issued.get(root)
            if root_id is None or root[0] != native.module:
                raise ValueError("configured Page route is not verified")
            admitted[operation] = root_id
        self._native = native
        self._roots = MappingProxyType(admitted)

    def capabilities(self) -> Mapping[str, str]:
        if self._native is None or not self._roots:
            return MappingProxyType({})
        return MappingProxyType({"page.ordinary": "statement-1"})

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        snapshot = call.snapshot()
        prepared = self._prepare(snapshot)
        if isinstance(prepared, OperationOutcome):
            return prepared
        if not await self._authority.check(snapshot.actor, snapshot.operation):
            return OperationOutcome("denied", "", {}, "denied")
        result = await prepared.native.execute_ordinary_page(
            prepared.call, identity=prepared.identity, scope=prepared.scope
        )
        if not prepared.native.validate_ordinary_page_result(result, prepared.call):
            return native_read_refusal(result, prepared.native.schema)
        return OperationOutcome("succeeded", "", result)

    def _prepare(self, call: OperationCall) -> _PageInvocation | OperationOutcome:
        refused = read_refusal(call)
        if refused is not None:
            return refused
        native = self._native
        route_root = self._roots.get(call.operation)
        if native is None or route_root is None:
            return OperationOutcome(
                "unavailable" if native is None else "invalid",
                "",
                {},
                "not_prepared" if native is None else "unsupported",
            )
        scope = cast(ExecutionScope, call.scope)
        try:
            if set(call.inputs) != {"page"}:
                raise ValueError("Page input envelope differs")
            page = GeneratedOrdinaryPageCall.from_mapping(call.inputs["page"])
            if page.root_id != route_root:
                raise ValueError("Page root differs from configured route")
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
            page_identity = native.ordinary_page_identity(page)
            if type(page_identity) is not bytes or len(page_identity) != 32:
                raise ValueError("Page identity is malformed")
        except GeneratedNativeError as error:
            return _page_native_refusal(error.code, native.schema)
        except GeneratedExecutionError as error:
            return _page_native_refusal(error.code, native.schema)
        except (ValueError, TypeError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        return _PageInvocation(native, page, identity, generated_scope)

    async def aclose(self) -> None:
        self._native = None
        self._roots = MappingProxyType({})


__all__ = ["GeneratedPageBinding", "GeneratedPageExecution"]


def _page_native_refusal(code: str, schema: str) -> OperationOutcome:
    if code == "UNSUPPORTED":
        return OperationOutcome("invalid", "", {}, "unsupported")
    return native_read_refusal({"schema": schema, "error": {"code": code}}, schema)
