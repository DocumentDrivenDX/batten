"""Task-owned selected resources; context entry and exit share one task."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Protocol, cast

from batten.contracts import (
    ExecutionScope,
    HostConfig,
    HostServices,
    Operation,
    OperationOutcome,
    PreparedSelectedExecution,
    RequestScopedSelectedExecution,
    SelectedCallSpec,
    SelectedRequestError,
)
from batten.runtime._selection import selection_failure

_MAX_PREPARED_CALLS = 256


class _SelectedSessionHost(Protocol):
    config: HostConfig
    services: HostServices
    operations: dict[str, Operation]

    def scope_active(self, scope: ExecutionScope) -> bool: ...


def _prepared_execution(execution: object) -> bool:
    try:
        return (
            isinstance(execution, PreparedSelectedExecution)
            and callable(getattr(execution, "prepare_selected"))
            and callable(getattr(execution, "open_prepared_request"))
        )
    except AttributeError:
        return False


def _prepared_plan(
    host: _SelectedSessionHost,
    execution: RequestScopedSelectedExecution,
    scope: ExecutionScope,
    prepared: object | None,
) -> tuple[object | None, bool]:
    if prepared is None:
        return None, False
    raw_calls = cast(tuple[object, ...], prepared)
    if (
        not _prepared_execution(execution)
        or type(prepared) is not tuple
        or not prepared
        or len(raw_calls) > _MAX_PREPARED_CALLS
        or any(type(item) is not SelectedCallSpec for item in raw_calls)
    ):
        raise ValueError("prepared selected calls are unavailable")
    for item in cast(tuple[SelectedCallSpec, ...], prepared):
        if (
            item.call.scope is not scope
            or item.call.actor != scope.principal
            or item.call.operation not in host.operations
            or selection_failure(
                host.operations[item.call.operation], execution, item.selection
            )
            is not None
        ):
            raise ValueError("prepared selected calls are unavailable")
    plan = cast(PreparedSelectedExecution, execution).prepare_selected(
        scope, cast(tuple[SelectedCallSpec, ...], prepared)
    )
    return plan, True


async def _authorize_prepared_calls(
    host: _SelectedSessionHost,
    scope: ExecutionScope,
    calls: tuple[SelectedCallSpec, ...],
) -> None:
    deadline = scope.deadline_monotonic - host.services.monotonic()
    try:
        async with asyncio.timeout(deadline):
            for operation in dict.fromkeys(item.call.operation for item in calls):
                if not await host.services.identity.check(scope.principal, operation):
                    raise SelectedRequestError("denied", "denied")
    except TimeoutError:
        raise SelectedRequestError("unavailable", "deadline_exceeded") from None


async def _admit_selected_session(
    host: _SelectedSessionHost,
    scope: ExecutionScope,
    consistency: str,
    calls: tuple[SelectedCallSpec, ...] | None,
    resources: dict[str, SelectedSession],
) -> tuple[RequestScopedSelectedExecution, object | None, bool]:
    execution = host.services.execution
    if (
        consistency != "request-snapshot-1"
        or scope.consistency != consistency
        or not host.scope_active(scope)
        or not scope.api_digest
        or scope.lease_id in resources
        or not isinstance(execution, RequestScopedSelectedExecution)
        or host.config.selected_capabilities.get("read.consistency") != consistency
        or dict(execution.capabilities()) != dict(host.config.selected_capabilities)
    ):
        raise ValueError("selected request profile is unavailable")
    plan, prepared_selected = _prepared_plan(host, execution, scope, calls)
    if prepared_selected and (
        plan is None
        or not host.scope_active(scope)
        or dict(execution.capabilities()) != dict(host.config.selected_capabilities)
    ):
        raise ValueError("prepared selected request is unavailable")
    if calls is not None:
        await _authorize_prepared_calls(host, scope, calls)
        if not host.scope_active(scope) or scope.lease_id in resources:
            raise ValueError("prepared selected request is unavailable")
    return execution, plan, prepared_selected


@asynccontextmanager
async def open_selected_session(
    host: _SelectedSessionHost,
    scope: ExecutionScope,
    *,
    consistency: str,
    calls: tuple[SelectedCallSpec, ...] | None = None,
    resources: dict[str, SelectedSession],
    draining_scopes: set[str],
    drain_scope: Callable[[], Awaitable[bool]],
) -> AsyncGenerator[None]:
    execution, plan, prepared_selected = await _admit_selected_session(
        host, scope, consistency, calls, resources
    )
    resource = SelectedSession(
        execution,
        scope,
        scope.deadline_monotonic - host.services.monotonic(),
        drain_scope,
        plan,
        prepared_selected,
    )
    resources[scope.lease_id] = resource
    completed = False
    try:
        await resource.start()
        if not host.scope_active(scope) or not resource.active:
            raise RuntimeError("selected request scope expired")
        yield
        completed = True
    finally:
        draining_scopes.add(scope.lease_id)
        if not await asyncio.shield(resource.close(host.config.timeout_seconds)):
            draining_scopes.add(scope.lease_id)
            if completed:
                raise RuntimeError("selected request cleanup pending")
        elif not resource.failed:
            draining_scopes.discard(scope.lease_id)
        if resource.failed and completed:
            raise RuntimeError("selected request failed") from resource.failure
        if resource.refusal is not None and completed:
            raise resource.refusal


class SelectedSession:
    def __init__(
        self,
        execution: RequestScopedSelectedExecution,
        scope: ExecutionScope,
        timeout: float,
        drain: Callable[[], Awaitable[bool]],
        prepared: object | None = None,
        prepared_selected: bool = False,
    ):
        self._execution, self._scope, self._timeout = execution, scope, timeout
        self._prepared, self._prepared_selected = prepared, prepared_selected
        self._drain = drain
        self._ready, self._stop = asyncio.Event(), asyncio.Event()
        self._task: asyncio.Task[None] | None = None
        self.failed = False
        self.refusal: SelectedRequestError | None = None

    def record(self, outcome: OperationOutcome) -> None:
        if self.refusal is None and outcome.status != "succeeded":
            self.refusal = SelectedRequestError(outcome.status, outcome.code)

    @property
    def active(self) -> bool:
        return (
            self._task is not None
            and self._ready.is_set()
            and not self._task.done()
            and not self._stop.is_set()
        )

    @property
    def failure(self) -> BaseException | None:
        task = self._task
        if task is None or not task.done():
            return None
        return asyncio.CancelledError() if task.cancelled() else task.exception()

    async def _serve(self) -> None:
        try:
            async with asyncio.timeout(self._timeout):
                context = (
                    cast(
                        PreparedSelectedExecution, self._execution
                    ).open_prepared_request(self._scope, self._prepared)
                    if self._prepared_selected
                    else self._execution.open_request(self._scope)
                )
                async with context:
                    self._ready.set()
                    try:
                        await self._stop.wait()
                    finally:
                        await self._drain_calls()
        except BaseException:
            self.failed = True
            raise
        finally:
            self._ready.set()

    async def _drain_calls(self) -> None:
        while True:
            try:
                if await self._drain():
                    return
            except asyncio.CancelledError:
                self.failed = True

    async def start(self) -> None:
        self._task = asyncio.create_task(self._serve())
        self._task.add_done_callback(lambda _task: self._ready.set())
        await self._ready.wait()
        if self._task.done():
            self._task.result()
            raise RuntimeError("selected request closed before admission")

    async def close(self, timeout: float) -> bool:
        self._stop.set()
        task = self._task
        if task is None:
            return True
        _done, pending = await asyncio.wait({task}, timeout=timeout)
        if pending:
            task.cancel()
            return False
        if not task.cancelled():
            task.exception()
        return True
