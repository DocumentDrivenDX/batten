"""Native provider port for generated table reads."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from umf_access.unified import AsyncSession, SessionIdentity
from umf_access_generated_executor import ExecutionScope as GeneratedScope
from umf_access_generated_executor import (
    GeneratedOrdinaryPageCall,
    GeneratedOrdinaryPageRoot,
)

from ._generated_table_routes import ConnectionRoute as _ConnectionRoute


class _GeneratedTableRequest(Protocol):
    async def execute_get_many(self, call: object) -> dict[str, object]: ...
    async def execute_forward_connection(
        self, prepared: object
    ) -> dict[str, object]: ...


class GeneratedTableBinding(Protocol):
    """One source/profile-bound native table adapter for all generated routes."""

    @property
    def connection_routes(self) -> Mapping[str, _ConnectionRoute]: ...
    @property
    def schema(self) -> str: ...
    @property
    def module(self) -> str: ...
    @property
    def target_binding_digest(self) -> str: ...
    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def algebra_json(self) -> bytes: ...
    @property
    def read_profile(self) -> str | None: ...

    def open_request(
        self,
        identity: SessionIdentity,
        scope: GeneratedScope,
        *,
        data_session: AsyncSession,
    ) -> AbstractAsyncContextManager[_GeneratedTableRequest]: ...

    def prepare_forward_connection(
        self,
        request: object,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> object: ...

    @property
    def ordinary_page_roots(self) -> tuple[GeneratedOrdinaryPageRoot, ...]: ...

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
