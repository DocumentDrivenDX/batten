"""Generic local host lifecycle and dispatch, independent of native providers."""

from __future__ import annotations

import asyncio
import math
import re
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import replace
from types import TracebackType

from batten.contracts import (
    Actor,
    ArtifactRef,
    ExecutionScope,
    HostConfig,
    HostServices,
    Operation,
    OperationCall,
    OperationOutcome,
    SelectedCallSpec,
    SelectedExecution,
    Selection,
    ShutdownReport,
)
from batten.runtime._selected_session import SelectedSession, open_selected_session
from batten.runtime._selection import selection_failure, valid_selection


class _MutationAuthorityRevoked(Exception):
    pass


class Host:
    def __init__(self, config: HostConfig, services: HostServices):
        if (
            type(config.max_concurrency) is not int
            or config.max_concurrency < 1
            or type(config.timeout_seconds) not in {int, float}
            or not math.isfinite(config.timeout_seconds)
            or config.timeout_seconds <= 0
        ):
            raise ValueError("positive host limits required")
        operations = {op.id: op for op in config.operations}
        if len(operations) != len(config.operations) or services.ownership not in {
            "owned",
            "borrowed",
        }:
            raise ValueError("ambiguous operations or ownership")
        self.config, self.services, self.operations = config, services, operations
        self.state = "new"
        self.admitted = False
        self.active: dict[asyncio.Future[None], asyncio.Task[object]] = {}
        self._scopes: dict[str, ExecutionScope] = {}
        self._scope_calls: dict[
            str, dict[asyncio.Future[None], asyncio.Task[object]]
        ] = {}
        self._draining_scopes: set[str] = set()
        self._scope_resources: dict[str, SelectedSession] = {}

    async def start(self) -> None:
        if self.state == "running":
            return
        if self.state != "new":
            raise RuntimeError("host cannot restart")
        self.state = "starting"
        try:
            await self.services.execution.prepare()
        except BaseException:
            await self.aclose()
            raise
        self.state = "running"

    async def admit(self, artifact: ArtifactRef) -> bool:
        self.admitted = self.state == "running" and artifact == self.config.artifact
        return self.admitted

    async def readiness(self) -> str:
        return self.state

    async def open_scope(
        self,
        actor: Actor,
        request_id: str,
        *,
        deadline_monotonic: float | None = None,
        api_digest: str | None = None,
        consistency: str | None = None,
    ) -> ExecutionScope:
        if self.state != "running" or not self.admitted:
            raise RuntimeError("host is not admitted")
        now = self.services.monotonic()
        deadline = now + self.config.timeout_seconds
        if deadline_monotonic is not None:
            if not math.isfinite(deadline_monotonic):
                raise ValueError("invalid scope request")
            deadline = min(deadline, deadline_monotonic)
        if not request_id or not math.isfinite(deadline) or deadline <= now:
            raise ValueError("invalid scope request")
        if len(self._scopes) >= self.config.max_concurrency:
            raise RuntimeError("scope limit exceeded")
        scope = ExecutionScope(
            self.config.artifact,
            actor,
            request_id,
            deadline,
            uuid.uuid4().hex,
            api_digest,
            consistency,
        )
        self._scopes[scope.lease_id] = scope
        self._scope_calls[scope.lease_id] = {}
        return scope

    def scope_active(self, scope: ExecutionScope) -> bool:
        """Check this host's issued lease; operation authority is checked at dispatch."""
        return (
            self.state == "running"
            and self.admitted
            and self._scopes.get(scope.lease_id) is scope
            and scope.lease_id not in self._draining_scopes
            and scope.application == self.config.artifact
            and math.isfinite(scope.deadline_monotonic)
            and scope.deadline_monotonic > self.services.monotonic()
        )

    @asynccontextmanager
    async def open_selected_session(
        self,
        scope: ExecutionScope,
        *,
        consistency: str,
        calls: tuple[SelectedCallSpec, ...] | None = None,
    ) -> AsyncGenerator[None]:
        async with open_selected_session(
            self,
            scope,
            consistency=consistency,
            calls=calls,
            resources=self._scope_resources,
            draining_scopes=self._draining_scopes,
            drain_scope=lambda: self._drain_scope(scope),
        ):
            yield

    async def _drain_scope(self, scope: ExecutionScope) -> bool:
        self._draining_scopes.add(scope.lease_id)
        calls = {
            finished: task
            for finished, task in self._scope_calls.get(scope.lease_id, {}).items()
            if task is not asyncio.current_task()
        }
        for task in set(calls.values()):
            task.cancel()
        if calls:
            _done, pending = await asyncio.wait(
                calls, timeout=self.config.timeout_seconds
            )
            return not pending
        return True

    async def close_scope(self, scope: ExecutionScope) -> ShutdownReport:
        if self._scopes.get(scope.lease_id) is not scope:
            raise ValueError("scope is not issued by this host")
        if not await self._drain_scope(scope):
            return ShutdownReport(
                "draining", (self.config.artifact.id,), ("scope_cleanup_pending",)
            )
        resource = self._scope_resources.get(scope.lease_id)
        if resource is not None and not await resource.close(
            self.config.timeout_seconds
        ):
            return ShutdownReport(
                "draining", (self.config.artifact.id,), ("scope_cleanup_pending",)
            )
        self._scope_resources.pop(scope.lease_id, None)
        self._scope_calls.pop(scope.lease_id, None)
        self._scopes.pop(scope.lease_id, None)
        self._draining_scopes.discard(scope.lease_id)
        return ShutdownReport("closed", (), ())

    async def _capture(
        self,
        actor: Actor,
        operation: str,
        invocation: str,
        status: str,
        mutation: bool,
    ) -> None:
        async with asyncio.timeout(self.config.timeout_seconds):
            await self.services.observations.capture(
                actor, operation, invocation, status, mutation
            )

    async def _run(
        self, call: OperationCall, invocation: str, selection: Selection | None
    ) -> OperationOutcome:
        op = self.operations[call.operation]
        try:
            await self._capture(call.actor, op.id, invocation, "started", op.mutation)
        except Exception:
            return OperationOutcome(
                "unavailable", invocation, {}, "capture_unavailable"
            )
        try:
            async with self.services.observations.scope(call.actor, op.id, invocation):
                await self._check_mutation_authority(call, op)
                if selection is None:
                    result = await self.services.execution.invoke(call)
                elif isinstance(self.services.execution, SelectedExecution):
                    result = await self.services.execution.invoke_selected(
                        call, selection
                    )
                else:
                    return OperationOutcome(
                        "invalid", invocation, {}, "unsupported_selection"
                    )
            failure = await self._post_failure(call)
            if failure is not None:
                result = OperationOutcome(
                    "uncertain" if op.mutation else failure[0],
                    invocation,
                    {},
                    failure[1],
                )
        except _MutationAuthorityRevoked:
            result = OperationOutcome("denied", invocation, {}, "authority_revoked")
        except asyncio.CancelledError:
            await self._capture(
                call.actor,
                op.id,
                invocation,
                "uncertain" if op.mutation else "cancelled",
                op.mutation,
            )
            raise
        except Exception:
            result = OperationOutcome(
                "uncertain" if op.mutation else "unavailable",
                invocation,
                {},
                "provider_unavailable",
            )
        try:
            await self._capture(
                call.actor, op.id, invocation, result.status, op.mutation
            )
        except Exception:
            return OperationOutcome(
                "uncertain" if op.mutation else "unavailable",
                invocation,
                {},
                "capture_unavailable",
            )
        return replace(result, invocation=invocation)

    async def _check_mutation_authority(
        self, call: OperationCall, op: Operation
    ) -> None:
        if op.mutation and not await self.services.identity.check(call.actor, op.id):
            raise _MutationAuthorityRevoked

    async def _post_failure(self, call: OperationCall) -> tuple[str, str] | None:
        if not await self.services.identity.check(call.actor, call.operation):
            return "denied", "authority_revoked"
        return self._scope_limits(call)[1]

    async def _refuse(
        self, call: OperationCall, invocation: str, status: str, code: str
    ) -> OperationOutcome:
        operation = self.operations.get(call.operation)
        try:
            await self._capture(
                call.actor,
                operation.id if operation else "unknown",
                invocation,
                status,
                bool(operation and operation.mutation),
            )
        except Exception:
            return self._selected_result(
                call,
                OperationOutcome("unavailable", invocation, {}, "capture_unavailable"),
            )
        return self._selected_result(
            call, OperationOutcome(status, invocation, {}, code)
        )

    async def _admission_failure(self, call: OperationCall) -> tuple[str, str] | None:
        if (
            self.state != "running"
            or not self.admitted
            or call.operation not in self.operations
        ):
            return "denied", "not_admitted"
        if not await self.services.identity.check(call.actor, call.operation):
            return "denied", "denied"
        if self.state != "running" or not self.admitted:
            return "denied", "not_admitted"
        if len(self.active) >= self.config.max_concurrency:
            return "unavailable", "limit_exceeded"
        return None

    def _scope_limits(
        self, call: OperationCall
    ) -> tuple[float, tuple[str, str] | None]:
        timeout = self.config.timeout_seconds
        scope = call.scope
        if self.state != "running" or not self.admitted:
            return timeout, ("denied", "not_admitted")
        now = self.services.monotonic()
        if scope is None:
            failure = None if math.isfinite(now) else ("unavailable", "clock_invalid")
            return timeout, failure
        if (
            self._scopes.get(scope.lease_id) is not scope
            or scope.lease_id in self._draining_scopes
        ):
            return timeout, ("denied", "scope_invalid")
        if (
            scope.application != self.config.artifact
            or scope.principal != call.actor
            or not scope.request_id
            or not scope.lease_id
            or not math.isfinite(scope.deadline_monotonic)
        ):
            return timeout, ("denied", "scope_invalid")
        remaining = scope.deadline_monotonic - now
        if remaining <= 0 or not math.isfinite(remaining):
            code = "deadline_exceeded" if math.isfinite(remaining) else "clock_invalid"
            return timeout, ("unavailable", code)
        failure = None
        if scope.consistency == "request-snapshot-1" and (
            scope.lease_id not in self._scope_resources
            or not self._scope_resources[scope.lease_id].active
        ):
            failure = ("invalid", "selected_session_inactive")
        return min(timeout, remaining), failure

    async def _call_limits(
        self, call: OperationCall, selection: Selection | None
    ) -> tuple[float, tuple[str, str] | None]:
        failure = await self._admission_failure(call)
        timeout = self.config.timeout_seconds
        if failure is None:
            timeout, failure = self._scope_limits(call)
        if failure is None and selection is not None:
            failure = selection_failure(
                self.operations[call.operation], self.services.execution, selection
            )
        return timeout, failure

    async def invoke(
        self, call: OperationCall, *, selection: Selection | None = None
    ) -> OperationOutcome:
        invocation = call.key or uuid.uuid4().hex
        if selection is not None and not valid_selection(selection):
            return await self._refuse(call, invocation, "invalid", "invalid_selection")
        if call.key is not None and not re.fullmatch(r"[a-f0-9-]{32,36}", call.key):
            return await self._refuse(call, uuid.uuid4().hex, "invalid", "invalid_key")
        try:
            call = call.snapshot()
        except (ValueError, TypeError, UnicodeError):
            return await self._refuse(call, invocation, "invalid", "invalid_inputs")
        timeout, failure = self._scope_limits(call)
        deadline = self.services.monotonic() + timeout
        remaining = timeout
        if failure is None:
            try:
                async with asyncio.timeout(timeout):
                    timeout, failure = await self._call_limits(call, selection)
            except TimeoutError:
                failure = ("unavailable", "deadline_exceeded")
        if failure is None:
            remaining = deadline - self.services.monotonic()
            if not math.isfinite(remaining) or remaining <= 0:
                failure = ("unavailable", "deadline_exceeded")
            remaining = min(timeout, remaining)
        if failure is not None:
            result = await self._refuse(call, invocation, *failure)
        else:
            result = await self._dispatch(call, invocation, selection, remaining)
        return self._selected_result(call, result)

    def _selected_result(
        self, call: OperationCall, result: OperationOutcome
    ) -> OperationOutcome:
        scope = call.scope
        if scope is not None:
            resource = self._scope_resources.get(scope.lease_id)
            if (
                resource is not None
                and resource.active
                and self._scopes.get(scope.lease_id) is scope
            ):
                resource.record(result)
        return result

    async def _dispatch(
        self,
        call: OperationCall,
        invocation: str,
        selection: Selection | None,
        timeout: float,
    ) -> OperationOutcome:
        task = asyncio.current_task()
        finished = asyncio.get_running_loop().create_future()
        if task is not None:
            self.active[finished] = task
            if call.scope is not None:
                self._scope_calls[call.scope.lease_id][finished] = task
        try:
            async with asyncio.timeout(timeout):
                return await self._run(call, invocation, selection)
        except TimeoutError:
            return OperationOutcome(
                "uncertain"
                if self.operations[call.operation].mutation
                else "unavailable",
                invocation,
                {},
                "timeout",
            )
        finally:
            self.active.pop(finished, None)
            if call.scope is not None:
                self._scope_calls.get(call.scope.lease_id, {}).pop(finished, None)
            finished.set_result(None)

    async def aclose(self) -> ShutdownReport:
        if self.state == "closed":
            return ShutdownReport("closed", (self.config.artifact.id,), ())
        self.state, self.admitted = "draining", False
        current = asyncio.current_task()
        invocations = self.active.copy()
        tasks = set(invocations.values()) - {current}
        for task in tasks:
            task.cancel()
        pending_invocations = {
            completion
            for completion, task in invocations.items()
            if task is not current
        }
        if pending_invocations:
            _done, pending = await asyncio.wait(
                pending_invocations, timeout=self.config.timeout_seconds
            )
            if pending:
                return ShutdownReport(
                    "draining", (self.config.artifact.id,), ("cleanup_pending",)
                )
        if any(task is current for task in invocations.values()):
            return ShutdownReport(
                "draining", (self.config.artifact.id,), ("cleanup_pending",)
            )
        for resource in self._scope_resources.values():
            if not await resource.close(self.config.timeout_seconds):
                return ShutdownReport(
                    "draining", (self.config.artifact.id,), ("cleanup_pending",)
                )
        self._scope_resources.clear()
        if self.services.ownership == "owned":
            await self.services.execution.aclose()
        self._scopes.clear()
        self._scope_calls.clear()
        self._draining_scopes.clear()
        self.state = "closed"
        return ShutdownReport("closed", (self.config.artifact.id,), ())

    async def __aenter__(self) -> Host:
        await self.start()
        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if (await self.aclose()).state != "closed":
            raise RuntimeError("host cleanup pending")


def create_host(config: HostConfig, services: HostServices) -> Host:
    return Host(config, services)


__all__ = ["Host", "create_host"]
