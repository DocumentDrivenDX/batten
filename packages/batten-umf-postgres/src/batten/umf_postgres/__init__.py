"""Thin original-UMF transport adapter; compilation and persistence stay upstream."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from typing import Protocol

from batten.contracts import Actor, Identity
from umf_access.unified import SessionIdentity


class AuthenticatedTransport(Protocol):
    async def execute(self, request: dict[str, object]) -> dict[str, object]: ...


class NativeBinding(Protocol):
    schema: str
    module: str

    def for_identity(self, identity: SessionIdentity) -> AuthenticatedTransport: ...


class UmfTableProvider:
    def __init__(self, factory: Callable[[], NativeBinding], authority: Identity):
        self._factory, self._authority = factory, authority
        self._native: NativeBinding | None = None

    async def prepare(self) -> None:
        if self._native is None:
            self._native = await asyncio.to_thread(self._factory)

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
        return await native.for_identity(
            SessionIdentity("person", actor.subject)
        ).execute(request)

    async def aclose(self) -> None:
        self._native = None


def create_umf_provider(
    factory: Callable[[], NativeBinding], authority: Identity
) -> UmfTableProvider:
    return UmfTableProvider(factory, authority)


__all__ = [
    "AuthenticatedTransport",
    "NativeBinding",
    "UmfTableProvider",
    "create_umf_provider",
]
