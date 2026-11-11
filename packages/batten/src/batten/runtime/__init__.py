"""Generic local host lifecycle and dispatch, independent of native providers."""

from __future__ import annotations

import asyncio
import re
import uuid
from dataclasses import replace
from types import TracebackType

from batten.contracts import (
    ArtifactRef,
    HostConfig,
    HostServices,
    OperationCall,
    OperationOutcome,
    ShutdownReport,
)


class Host:
    def __init__(self, config: HostConfig, services: HostServices):
        if config.max_concurrency < 1 or config.timeout_seconds <= 0:
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
        self.active: set[asyncio.Task[object]] = set()

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

    async def _run(self, call: OperationCall, invocation: str) -> OperationOutcome:
        op = self.operations[call.operation]
        try:
            await self.services.observations.capture(
                call.actor, op.id, invocation, "started", op.mutation
            )
        except Exception:
            return OperationOutcome(
                "unavailable", invocation, {}, "capture_unavailable"
            )
        try:
            async with self.services.observations.scope(call.actor, op.id, invocation):
                result = await self.services.execution.invoke(call)
            if not await self.services.identity.check(call.actor, op.id):
                result = OperationOutcome(
                    "uncertain" if op.mutation else "denied",
                    invocation,
                    {},
                    "authority_revoked",
                )
        except asyncio.CancelledError:
            await self.services.observations.capture(
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
            await self.services.observations.capture(
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

    async def _refuse(
        self, call: OperationCall, invocation: str, status: str, code: str
    ) -> OperationOutcome:
        operation = self.operations.get(call.operation)
        try:
            await self.services.observations.capture(
                call.actor,
                operation.id if operation else "unknown",
                invocation,
                status,
                bool(operation and operation.mutation),
            )
        except Exception:
            return OperationOutcome(
                "unavailable", invocation, {}, "capture_unavailable"
            )
        return OperationOutcome(status, invocation, {}, code)

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        invocation = call.key or uuid.uuid4().hex
        if call.key is not None and not re.fullmatch(r"[a-f0-9-]{32,36}", call.key):
            return await self._refuse(call, uuid.uuid4().hex, "invalid", "invalid_key")
        if (
            self.state != "running"
            or not self.admitted
            or call.operation not in self.operations
        ):
            return await self._refuse(call, invocation, "denied", "not_admitted")
        if not await self.services.identity.check(call.actor, call.operation):
            return await self._refuse(call, invocation, "denied", "denied")
        if len(self.active) >= self.config.max_concurrency:
            return await self._refuse(call, invocation, "unavailable", "limit_exceeded")
        task = asyncio.current_task()
        if task is not None:
            self.active.add(task)
        try:
            async with asyncio.timeout(self.config.timeout_seconds):
                return await self._run(call, invocation)
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
            if task is not None:
                self.active.discard(task)

    async def aclose(self) -> ShutdownReport:
        if self.state == "closed":
            return ShutdownReport("closed", (self.config.artifact.id,), ())
        self.state, self.admitted = "draining", False
        tasks = self.active - {asyncio.current_task()}
        for task in tasks:
            task.cancel()
        if tasks:
            _done, pending = await asyncio.wait(
                tasks, timeout=self.config.timeout_seconds
            )
            if pending:
                return ShutdownReport(
                    "draining", (self.config.artifact.id,), ("cleanup_pending",)
                )
        if self.services.ownership == "owned":
            await self.services.execution.aclose()
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
