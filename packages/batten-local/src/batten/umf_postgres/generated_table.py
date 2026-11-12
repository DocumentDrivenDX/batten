"""Disjoint ordinary, Key-batch and planned connection routes on one binding."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from itertools import combinations
from types import MappingProxyType
from typing import cast

import umf_access.generated as generated_api
from batten.contracts import (
    ExecutionScope,
    Identity,
    OperationCall,
    OperationOutcome,
    SelectedCallSpec,
    SelectedRequestError,
    Selection,
    connection_routes_digest,
)
from umf_access.unified import AsyncSession, SessionIdentity
from umf_access_generated_executor import ExecutionScope as GeneratedScope
from umf_access_generated_executor import (
    GeneratedExecutor,
)

from ._generated_batch_routes import RecordRoot
from ._generated_connection import (
    GeneratedTablePlan,
    PlannedConnection,
    connection_fields,
    connection_preflight_error,
    connection_result,
    consume_connection,
    field_reference,
    issue_table_plan,
    native_connection_error,
    table_plan_from,
)
from ._generated_join import GeneratedJoinBinding, GeneratedJoinExecution
from ._generated_page import GeneratedPageBinding, GeneratedPageExecution
from ._generated_table_binding import GeneratedTableBinding
from ._generated_table_routes import ConnectionRoute as _ConnectionRoute
from ._read_binding import ReadBindingMetadata
from .generated_batch import GeneratedBatchBinding, GeneratedBatchExecution
from .generated_command import GeneratedCommandExecution
from .generated_read_v3 import GeneratedReadExecutionV3
from .generated_relationship import GeneratedRelationships

_PROFILE4 = "weft.generated-read-algebra/4"
_PROFILE5 = "weft.generated-read-algebra/5"
_PROFILE7 = "weft.generated-read-algebra/7"
_PROFILE8 = "weft.generated-read-algebra/8"
_MAX_PLANNED_CALLS = 256


class GeneratedTableExecution:
    """Route reads and both selected families through one held native request."""

    def __init__(
        self,
        executor: GeneratedExecutor,
        factory: Callable[[], Awaitable[GeneratedTableBinding]],
        *,
        data_session: AsyncSession,
        authority: Identity,
        read_routes: Mapping[str, tuple[str, str]],
        record_routes: Mapping[str, RecordRoot],
        connection_routes: Mapping[str, _ConnectionRoute] | None = None,
        page_routes: Mapping[str, tuple[str, str]] | None = None,
        joined_read_routes: Mapping[str, tuple[str, str, str, str]] | None = None,
        commands: GeneratedCommandExecution | None = None,
        relationships: GeneratedRelationships | None = None,
    ) -> None:
        profile = executor.read_profile
        routes = dict(connection_routes or {})
        pages = dict(page_routes or {})
        joined = dict(joined_read_routes or {})
        route_groups = (
            set(read_routes),
            set(record_routes) | routes.keys(),
            set(pages),
            set(joined),
            commands.operations if commands is not None else frozenset[str](),
            relationships.operations if relationships is not None else frozenset[str](),
        )
        if (
            profile not in {_PROFILE4, _PROFILE5, _PROFILE7, _PROFILE8}
            or not read_routes
            or not record_routes
            or any(left & right for left, right in combinations(route_groups, 2))
            or (profile == _PROFILE4 and (routes or pages))
            or (profile == _PROFILE5 and (not routes or pages))
            or (joined and profile != _PROFILE8)
        ):
            raise ValueError("disjoint generated routes and profile required")
        if any(
            type(operation) is not str
            or not operation
            or route.cursor_scope.host_operation_id != operation
            for operation, route in routes.items()
        ):
            raise ValueError("connection operation route differs")
        if any(
            (record_routes[operation].ref.module, record_routes[operation].ref.id)
            != (route.module, route.record)
            for operation, route in routes.items()
            if operation in record_routes
        ):
            raise ValueError("connection route differs from its Record route")
        if commands is not None and (
            type(commands) is not GeneratedCommandExecution
            or commands.artifact_digest != executor.trusted_artifact.artifact_digest
        ):
            raise ValueError("command routes differ from the admitted artifact")
        if relationships is not None and (
            type(relationships) is not GeneratedRelationships
            or relationships.artifact_digest
            != executor.trusted_artifact.artifact_digest
        ):
            raise ValueError("relationship routes differ from the admitted artifact")
        self._relationships = relationships
        self._commands = commands
        self._factory = factory
        self._native: GeneratedTableBinding | None = None
        self._factory_lock = asyncio.Lock()
        self._read_routes = MappingProxyType(dict(read_routes))
        self._record_routes = MappingProxyType(dict(record_routes))
        self._connection_routes = MappingProxyType(routes)
        self._page_routes = MappingProxyType(pages)
        self._joined_read_routes = MappingProxyType(joined)
        self._profile = profile
        self._connections_admitted = False
        self._connection_routes_digest: str | None = None
        self._plans: dict[str, GeneratedTablePlan] = {}
        self._read = GeneratedReadExecutionV3(
            cast(Callable[[], Awaitable[ReadBindingMetadata]], self._shared_factory),
            authority,
            executor,
            read_routes,
        )
        self._records = GeneratedBatchExecution(
            executor,
            cast(Callable[[], Awaitable[GeneratedBatchBinding]], self._shared_factory),
            data_session=data_session,
            authority=authority,
            roots=record_routes,
        )
        self._pages = (
            GeneratedPageExecution(
                executor,
                cast(
                    Callable[[], Awaitable[GeneratedPageBinding]], self._shared_factory
                ),
                authority,
                pages,
            )
            if pages
            else None
        )
        self._joined_reads: GeneratedJoinExecution | None = None
        if joined:
            self._joined_reads = GeneratedJoinExecution(
                executor,
                cast(
                    Callable[[], Awaitable[GeneratedJoinBinding]], self._shared_factory
                ),
                authority,
                joined,
            )

    async def _shared_factory(self) -> GeneratedTableBinding:
        async with self._factory_lock:
            if self._native is None:
                self._native = await self._factory()
            return self._native

    async def prepare(self) -> None:
        await self._read.prepare()
        await self._records.prepare()
        if self._connection_routes:
            native = await self._shared_factory()
            if native.read_profile not in {_PROFILE5, _PROFILE7, _PROFILE8} or dict(
                native.connection_routes
            ) != dict(self._connection_routes):
                raise ValueError("native connection routes differ from host pins")
            for route in self._connection_routes.values():
                key_id, wrappers, key_fields = self._records.connection_key_profile(
                    route.module, route.record
                )
                allowed = {
                    cast(str, item["fieldId"])
                    for item in cast(
                        tuple[Mapping[str, object], ...],
                        route.allowed_field_profile.body["fields"],
                    )
                }
                if (
                    not key_id
                    or wrappers != ("string",)
                    or not set(key_fields).issubset(allowed)
                ):
                    raise ValueError(
                        "connection Key is outside the admitted Field profile"
                    )
            first_route = next(iter(self._connection_routes.values()))
            scope_pins = first_route.cursor_scope
            route_rows = tuple(
                (
                    operation,
                    route.module,
                    route.record,
                    route.allowed_field_profile.digest,
                )
                for operation, route in self._connection_routes.items()
            )
            if any(
                (
                    route.cursor_scope.application_id,
                    route.cursor_scope.application_digest,
                    route.cursor_scope.api_digest,
                )
                != (
                    scope_pins.application_id,
                    scope_pins.application_digest,
                    scope_pins.api_digest,
                )
                for route in self._connection_routes.values()
            ):
                raise ValueError("connection route scopes differ")
            self._connection_routes_digest = connection_routes_digest(
                scope_pins.application_id,
                scope_pins.application_digest,
                scope_pins.api_digest,
                self._records.capabilities()["artifact.digest"],
                route_rows,
            )
            self._connections_admitted = True
        if self._pages is not None:
            await self._pages.prepare()
        if self._joined_reads is not None:
            await self._joined_reads.prepare()

    def capabilities(self) -> Mapping[str, str]:
        capabilities = dict(self._records.capabilities())
        if self._connections_admitted:
            capabilities["connection.forward"] = "edge-cursor-1"
            if self._connection_routes_digest is None:
                raise RuntimeError("connection route pin is unavailable")
            capabilities["connection.routes.digest"] = self._connection_routes_digest
        if self._pages is not None:
            capabilities.update(self._pages.capabilities())
        if self._joined_reads is not None:
            capabilities.update(self._joined_reads.capabilities())
        if self._commands is not None:
            capabilities.update(self._commands.capabilities())
        if self._relationships is not None:
            capabilities.update(self._relationships.capabilities())
        return MappingProxyType(capabilities)

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        if call.operation in self._read_routes:
            return await self._read.invoke(call)
        if self._pages is not None and call.operation in self._page_routes:
            return await self._pages.invoke(call)
        if (
            self._joined_reads is not None
            and call.operation in self._joined_read_routes
        ):
            return await self._joined_reads.invoke(call)
        if self._commands is not None and call.operation in self._commands.operations:
            return await self._commands.invoke(call)
        return OperationOutcome("invalid", "", {}, "unsupported")

    async def invoke_selected(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome:
        if selection.kind == "related_many" and self._relationships is not None:
            return await self._relationships.invoke(self._records, call, selection)
        if selection.kind != "connection":
            if call.operation not in self._record_routes:
                return OperationOutcome("invalid", "", {}, "unsupported")
            return await self._records.invoke_selected(call, selection)
        return await self._invoke_connection(call, selection)

    def prepare_selected(
        self, scope: ExecutionScope, calls: tuple[SelectedCallSpec, ...]
    ) -> object:
        if (
            not self._connections_admitted
            or type(scope) is not ExecutionScope
            or type(calls) is not tuple
            or not calls
            or len(calls) > _MAX_PLANNED_CALLS
        ):
            raise SelectedRequestError("invalid", "unsupported")
        identity, generated_scope = self._records.prepared_scope(scope)
        planned = tuple(
            self._prepare_connection(item, scope, identity, generated_scope)
            for item in calls
        )
        return issue_table_plan(self, scope, calls, identity, generated_scope, planned)

    def _prepare_connection(
        self,
        spec: SelectedCallSpec,
        scope: ExecutionScope,
        identity: SessionIdentity,
        generated_scope: GeneratedScope,
    ) -> PlannedConnection:
        call, selection = spec.call, spec.selection
        route = self._connection_routes.get(call.operation)
        cursor_scope = route.cursor_scope if route is not None else None
        if (
            route is None
            or call.scope is not scope
            or call.actor != scope.principal
            or call.phase != "invoke"
            or call.key is not None
            or call.confirmation is not None
            or bool(call.inputs)
            or call.actor.kind not in {"person", "batch"}
            or call.actor.delegation is not None
            or cursor_scope is None
            or cursor_scope.application_id != scope.application.id
            or cursor_scope.application_digest != scope.application.digest
            or cursor_scope.api_digest != scope.api_digest
            or selection.kind != "connection"
            or selection.keys
            or selection.parents
            or selection.target is not None
            or not 0 <= len(selection.fields) <= 8
            or type(selection.first) is not int
            or not 0 <= selection.first <= 100
        ):
            raise SelectedRequestError("invalid", "unsupported")
        key_id, key_wrappers, key_field_ids = self._records.connection_key_profile(
            route.module, route.record
        )
        if key_wrappers != ("string",):
            raise ValueError("connection Key profile is unsupported")
        native_fields = selection.fields
        if not native_fields:
            key_descriptor = next(
                (
                    field_reference(value)
                    for value in cast(
                        tuple[Mapping[str, object], ...],
                        route.allowed_field_profile.body["fields"],
                    )
                    if value["fieldId"] == key_field_ids[0]
                ),
                None,
            )
            if key_descriptor is None:
                raise SelectedRequestError("invalid", "unsupported")
            native_fields = (key_descriptor,)
        try:
            field_descriptors, field_ids = connection_fields(route, native_fields)
        except ValueError:
            raise SelectedRequestError("invalid", "unsupported") from None
        request_type = getattr(generated_api, "GeneratedForwardConnectionRequest", None)
        if not callable(request_type):
            raise ValueError("native generated connection API is unavailable")
        request = request_type(
            call.operation,
            route.module,
            route.record,
            field_ids,
            None,
            selection.first,
            selection.after,
        )
        native = self._native
        if native is None:
            raise ValueError("native connection binding is unavailable")
        try:
            native_plan = self._records.prepare_connection(
                request, identity, generated_scope
            )
        except Exception as error:
            raise connection_preflight_error(error, native.schema) from None
        return PlannedConnection(
            spec,
            native_plan,
            route.module,
            route.record,
            native.schema,
            native.target_binding_digest,
            key_id,
            key_wrappers,
            field_descriptors,
            field_ids,
        )

    @asynccontextmanager
    async def open_prepared_request(
        self, scope: ExecutionScope, prepared: object
    ) -> AsyncGenerator[None, None]:
        plan = table_plan_from(prepared, self, scope)
        if scope.lease_id in self._plans:
            raise ValueError("generated table plan is already active")
        completed = False
        async with self._records.open_prepared_request(
            scope,
            cast(SessionIdentity, plan.identity),
            cast(GeneratedScope, plan.generated_scope),
        ):
            self._plans[scope.lease_id] = plan
            try:
                yield
                completed = True
            finally:
                self._plans.pop(scope.lease_id, None)
                if completed and len(plan.used) != len(plan.items):
                    raise RuntimeError("planned connection calls were not consumed")

    def open_request(self, scope: ExecutionScope) -> AbstractAsyncContextManager[None]:
        return self._records.open_request(scope)

    async def _invoke_connection(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome:
        scope = call.scope
        plan = self._plans.get(scope.lease_id) if scope is not None else None
        if plan is None or scope is None or plan.scope is not scope:
            return OperationOutcome("invalid", "", {}, "unplanned_connection")
        match = consume_connection(plan, call, selection)
        if match is None:
            return OperationOutcome("invalid", "", {}, "unplanned_connection")
        _index, item = match
        if not await self._records.authorize_connection(call):
            return OperationOutcome("denied", "", {}, "denied")
        try:
            frame = await self._records.execute_connection(
                scope,
                cast(SessionIdentity, plan.identity),
                cast(GeneratedScope, plan.generated_scope),
                item.native,
            )
        except Exception as error:
            outcome = native_connection_error(error, item.source_digest)
            if outcome is None:
                raise
            return outcome
        translated = connection_result(frame, item)
        if translated is None:
            return OperationOutcome("unavailable", "", {}, "native_refused")
        return OperationOutcome("succeeded", "", translated)

    async def aclose(self) -> None:
        if self._plans:
            raise RuntimeError("prepared requests must close before provider")
        await self._records.aclose()
        await self._read.aclose()
        if self._pages is not None:
            await self._pages.aclose()
        if self._joined_reads is not None:
            await self._joined_reads.aclose()
        self._native = None
        self._connections_admitted = False


__all__ = ["GeneratedTableBinding", "GeneratedTableExecution"]
