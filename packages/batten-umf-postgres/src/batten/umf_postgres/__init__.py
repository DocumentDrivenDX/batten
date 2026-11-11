"""Thin original-UMF transport adapter; compilation and persistence stay upstream."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Protocol

from batten.contracts import Actor, Identity
from umf_access.unified import SessionIdentity

if TYPE_CHECKING:
    from .generated_batch import (
        GeneratedBatchBinding,
        GeneratedBatchExecution,
        GeneratedBatchRequest,
    )
    from .generated_command import GeneratedCommandExecution, GeneratedCommandRoute
    from .generated_relationship import (
        GeneratedRelationshipRoute,
        GeneratedRelationships,
    )
    from .generated_table import GeneratedTableBinding, GeneratedTableExecution


def __getattr__(name: str) -> object:
    """Resolve generated exports only when the generated provider is selected."""
    if name in {
        "GeneratedBatchBinding",
        "GeneratedBatchExecution",
        "GeneratedBatchRequest",
    }:
        from . import generated_batch

        return getattr(generated_batch, name)
    if name in {"GeneratedCommandExecution", "GeneratedCommandRoute"}:
        from . import generated_command

        return getattr(generated_command, name)
    if name in {"GeneratedRelationshipRoute", "GeneratedRelationships"}:
        from . import generated_relationship

        return getattr(generated_relationship, name)
    if name in {"GeneratedTableBinding", "GeneratedTableExecution"}:
        from . import generated_table

        return getattr(generated_table, name)
    raise AttributeError(name)


class AuthenticatedTransport(Protocol):
    async def execute(self, request: dict[str, object]) -> dict[str, object]: ...


class NativeBinding(Protocol):
    schema: str
    module: str

    def for_identity(self, identity: SessionIdentity) -> AuthenticatedTransport: ...


class UmfTableProvider:
    def __init__(
        self,
        factory: Callable[[], Awaitable[NativeBinding]],
        authority: Identity,
    ):
        self._factory, self._authority = factory, authority
        self._native: NativeBinding | None = None

    async def prepare(self) -> None:
        if self._native is None:
            self._native = await self._factory()

    def _identity(self, actor: Actor) -> SessionIdentity | None:
        if actor.delegation is not None:
            return None
        if actor.kind == "person":
            return SessionIdentity("person", actor.subject)
        if actor.kind == "batch":
            return SessionIdentity("batch", actor.subject)
        return None

    async def execute(
        self,
        actor: Actor,
        operation: str,
        inputs: Mapping[str, object],
        *,
        key: str | None,
        phase: str,
        mutation: bool,
    ) -> Mapping[str, object]:
        if not await self._authority.check(actor, "tables." + operation):
            return {"error": {"code": "DENIED"}}
        native = self._native
        if native is None:
            raise RuntimeError("provider is not prepared")
        identity = self._identity(actor)
        if identity is None:
            return {"error": {"code": "AUTHORITY_UNSUPPORTED"}}
        request: dict[str, object] = {
            "contract": "umf.access/1",
            "schema": native.schema,
            "kind": "table",
            "module": native.module,
            "operation": operation,
            "call": {"kind": "single", "inputs": dict(inputs)},
            "phase": phase,
            "mutation": mutation,
            "idempotency_key": key,
        }
        return await native.for_identity(identity).execute(request)

    async def aclose(self) -> None:
        self._native = None


def create_umf_provider(
    factory: Callable[[], Awaitable[NativeBinding]],
    authority: Identity,
) -> UmfTableProvider:
    return UmfTableProvider(factory, authority)


__all__ = [
    "AuthenticatedTransport",
    "GeneratedBatchBinding",
    "GeneratedBatchExecution",
    "GeneratedBatchRequest",
    "GeneratedCommandExecution",
    "GeneratedCommandRoute",
    "GeneratedRelationshipRoute",
    "GeneratedRelationships",
    "GeneratedTableBinding",
    "GeneratedTableExecution",
    "NativeBinding",
    "UmfTableProvider",
    "create_umf_provider",
]
