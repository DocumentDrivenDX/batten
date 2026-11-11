"""Optional Lintel transport adapter; every operation crosses Batten's host gates."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager, nullcontext
from types import MappingProxyType
from typing import TYPE_CHECKING, Protocol, cast

from batten.contracts import (
    ExecutionScope,
    OperationCall,
    SelectedCallSpec,
    SelectedRequestError,
    Selection,
)
from batten.lintel._config import (
    ExposureConfig,
    ExposureOperation,
    check_prepared_command_routes,
    check_prepared_relationship_routes,
    checked_operations,
)
from batten.lintel._connections import ConnectionAdmission, prepare_connection_admission
from batten.lintel._failure import failure, native_failure
from batten.lintel._record_config import checked_record_roots
from batten.lintel._record_root import ExposureRecordRoot
from batten.lintel._session import Session
from batten.runtime import Host

from lintel.ports import (
    ConnectionPage,
    ElementRef,
    ExecutionError,
    OperationRef,
    RequestScope,
    RequestSession,
)

if TYPE_CHECKING:
    from umf_access_generated_executor import AdmittedNativeTable, GeneratedExecutor

    from lintel.ports import ConnectionIntent


class _PlannedSession(RequestSession, Protocol):
    async def planned_connection(self, intent: ConnectionIntent) -> ConnectionPage: ...


def _native_inputs(
    host: Host,
    config: ExposureConfig,
    native: AdmittedNativeTable | None,
    generated: GeneratedExecutor | None,
    connection_admission: ConnectionAdmission | None,
) -> tuple[dict[OperationRef, ExposureOperation], ConnectionAdmission | None]:
    if native is None:
        raise ValueError("native artifact is required")
    operations = dict(checked_operations(host, config, native))
    if config.record_roots:
        if generated is None:
            raise ValueError("Record exposure requires a verified generated executor")
        if connection_admission is None:
            operations.update(checked_record_roots(host, config, native, generated))
        else:
            if connection_admission.prepared_api.version not in {
                "lintel.prepared-api/3",
                "lintel.prepared-api/4",
                "lintel.prepared-api/5",
            }:
                raise ValueError("prepared API connection admission differs")
            operations.update(
                checked_record_roots(
                    host,
                    config,
                    native,
                    generated,
                    connection_lookups=connection_admission.host_operation_by_lookup,
                    connection_capabilities=connection_admission.selected_capabilities,
                    connection_api_version=connection_admission.prepared_api.version,
                )
            )
    elif connection_admission is not None:
        raise ValueError("API connections require explicit Record roots")
    admission = cast(ConnectionAdmission | None, connection_admission)
    check_prepared_command_routes(
        host,
        config,
        operations,
        admission.prepared_api if admission is not None else None,
    )
    check_prepared_relationship_routes(
        host,
        config,
        operations,
        admission.prepared_api if admission is not None else None,
    )
    return operations, admission


class LintelExecution:
    def __init__(
        self,
        host: Host,
        config: ExposureConfig,
        native: AdmittedNativeTable | None = None,
        *,
        generated: GeneratedExecutor | None = None,
        connection_admission: ConnectionAdmission | None = None,
    ):
        operations, connection_admission = _native_inputs(
            host, config, native, generated, connection_admission
        )
        self._operations = MappingProxyType(operations)
        self._host, self._config = host, config
        self._connection_admission = connection_admission
        self._response_bytes = (
            connection_admission.response_bytes
            if connection_admission is not None
            else None
        )

    @staticmethod
    def prepare_connections(
        config: ExposureConfig,
        prepared_api: object,
        native: AdmittedNativeTable,
        executor: GeneratedExecutor,
    ) -> ConnectionAdmission:
        from lintel.projection import AdmittedPreparedApi

        if type(prepared_api) is not AdmittedPreparedApi:
            raise ValueError("API3 requires a publicly admitted prepared API")
        return prepare_connection_admission(config, prepared_api, native, executor)

    def capabilities(self) -> Mapping[str, str]:
        return self._config.capabilities

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[RequestSession]:
        authority = scope.authority
        if (
            not isinstance(authority, ExecutionScope)
            or not self._host.scope_active(authority)
            or scope.application != self._config.application.id
            or scope.api_digest != self._config.api_digest
            or scope.api_digest != authority.api_digest
            or scope.request_id != authority.request_id
            or scope.deadline_monotonic != authority.deadline_monotonic
            or scope.kind not in {"query", "mutation"}
        ):
            raise ExecutionError("API_MISMATCH")
        admission = self._connection_admission
        session = Session(
            self._host,
            authority,
            scope.kind,
            self._operations,
            connection_operations=(
                admission.host_operation_by_lookup if admission is not None else None
            ),
            result_budget=self._response_bytes,
            planned_mode=admission is not None,
        )
        resource = (
            self._host.open_selected_session(
                authority, consistency="request-snapshot-1"
            )
            if self._config.record_roots
            else nullcontext()
        )
        try:
            async with resource:
                try:
                    yield session
                finally:
                    session.active = False
            session.ensure_budget()
        except ExecutionError:
            raise
        except SelectedRequestError as error:
            raise failure(error.status, error.code) from None
        except Exception as error:
            try:
                session.ensure_budget()
            except ExecutionError as refusal:
                raise refusal from None
            raise native_failure(error) from None

    @asynccontextmanager
    async def session_planned(
        self, scope: RequestScope, intents: tuple[ConnectionIntent, ...]
    ) -> AsyncGenerator[_PlannedSession]:
        admission = self._connection_admission
        authority = scope.authority
        if admission is None or type(intents) is not tuple or not intents:
            raise ExecutionError("UNSUPPORTED")
        if len(intents) > admission.max_connections:
            raise ExecutionError("LIMIT_EXCEEDED")
        if not isinstance(authority, ExecutionScope):
            raise ExecutionError("API_MISMATCH")
        if not self._scope_matches(scope, authority):
            raise ExecutionError("API_MISMATCH")
        calls = _planned_calls(admission, intents, authority, self._operations)
        session = Session(
            self._host,
            authority,
            scope.kind,
            self._operations,
            planned_intents=intents,
            connection_operations=admission.host_operation_by_lookup,
            result_budget=admission.response_bytes,
            planned_mode=True,
        )
        try:
            async with self._host.open_selected_session(
                authority,
                consistency="request-snapshot-1",
                calls=calls,
            ):
                try:
                    yield session
                finally:
                    session.active = False
            session.ensure_budget()
        except ExecutionError:
            raise
        except SelectedRequestError as error:
            raise failure(error.status, error.code) from None
        except Exception as error:
            try:
                session.ensure_budget()
            except ExecutionError as refusal:
                raise refusal from None
            raise native_failure(error) from None

    def _scope_matches(self, scope: RequestScope, authority: object) -> bool:
        return (
            isinstance(authority, ExecutionScope)
            and self._host.scope_active(authority)
            and scope.application == self._config.application.id
            and scope.api_digest == self._config.api_digest == authority.api_digest
            and scope.request_id == authority.request_id
            and scope.deadline_monotonic == authority.deadline_monotonic
            and scope.kind == "query"
        )


def _planned_calls(
    admission: ConnectionAdmission,
    intents: tuple[ConnectionIntent, ...],
    authority: ExecutionScope,
    operations: Mapping[OperationRef, ExposureOperation],
) -> tuple[SelectedCallSpec, ...]:
    from lintel.ports import ConnectionIntent

    response_keys: set[str] = set()
    calls: list[SelectedCallSpec] = []
    for intent in intents:
        if type(intent) is not ConnectionIntent:
            raise ExecutionError("UNSUPPORTED")
        prepared = admission.prepared_by_name.get(intent.field_name)
        operation = admission.host_operation_by_lookup.get(intent.lookup)
        exposure = operations.get(intent.lookup)
        if (
            not intent.response_key
            or type(intent.field_name) is not str
            or type(intent.lookup) is not OperationRef
            or intent.response_key in response_keys
            or prepared is None
            or prepared.lookup != intent.lookup
            or intent.lookup.kind != "record"
            or operation is None
            or exposure is None
            or exposure.host_operation != operation
            or intent.arguments
            or type(intent.first) is not int
            or not 0 <= intent.first <= admission.max_page
            or not _valid_cursor(intent.after, admission.cursor_bytes)
            or type(intent.fields) is not tuple
            or any(type(field) is not ElementRef for field in intent.fields)
            or len(set(intent.fields)) != len(intent.fields)
            or not set(intent.fields).issubset(prepared.field_refs)
            or not set(intent.fields).issubset(exposure.fields)
        ):
            raise ExecutionError("UNSUPPORTED")
        response_keys.add(intent.response_key)
        calls.append(
            SelectedCallSpec(
                OperationCall(operation, {}, authority.principal, scope=authority),
                Selection(
                    "connection",
                    fields=tuple(
                        (field.module, field.element) for field in intent.fields
                    ),
                    first=intent.first,
                    after=intent.after,
                ),
            )
        )
    return tuple(calls)


def _valid_cursor(value: str | None, maximum: int) -> bool:
    if value is None:
        return True
    if type(value) is not str:
        return False
    try:
        return len(value.encode("utf-8")) <= maximum
    except UnicodeEncodeError:
        return False


__all__ = [
    "ExposureConfig",
    "ExposureOperation",
    "ExposureRecordRoot",
    "ConnectionAdmission",
    "LintelExecution",
    "prepare_connection_admission",
]
