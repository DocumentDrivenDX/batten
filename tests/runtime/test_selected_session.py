"""Selected resources are admitted independently and cleaned by their owner task."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager, nullcontext
from dataclasses import replace
from typing import cast

import pytest
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
    SelectedRequestError,
    Selection,
)
from batten.runtime import Host, create_host

from tests.runtime.test_lintel_host import Authority, Capture, Inspect

PINS = {"read.consistency": "request-snapshot-1", "binding": "fabricated-binding"}
REFUSALS = {
    "host_revoked": ("denied", "authority_revoked"),
    "admission_revoked": ("denied", "not_admitted"),
    "clock_expired": ("unavailable", "deadline_exceeded"),
}


class RequestInspect(Inspect):
    def __init__(
        self,
        mode: str,
        authority: Authority,
        clock: list[float],
        invalidate: Callable[[], Awaitable[bool]],
    ):
        self.mode, self.authority = mode, authority
        self.clock, self.invalidate = clock, invalidate
        self.calls = 0
        self.events: list[tuple[str, object]] = []
        self.prepared_calls: tuple[SelectedCallSpec, ...] | None = None
        self.prepared_scope: ExecutionScope | None = None
        self.release = asyncio.Event()
        self.started = asyncio.Event()

    def capabilities(self) -> Mapping[str, str]:
        return {
            **PINS,
            **({"extra": "unconfigured"} if self.mode == "extra" else {}),
            **({"binding": "different"} if self.mode == "mismatch" else {}),
        }

    def __getattribute__(self, name: str) -> object:
        if object.__getattribute__(self, "mode") == "prepared_missing" and name in {
            "prepare_selected",
            "open_prepared_request",
        }:
            raise AttributeError(name)
        return object.__getattribute__(self, name)

    def prepare_selected(
        self, scope: ExecutionScope, calls: tuple[SelectedCallSpec, ...]
    ) -> object:
        self.prepared_calls = calls
        self.prepared_scope = scope
        if self.mode == "prepared_replay":
            return (scope, calls, "replayed")
        if self.mode == "prepared_none":
            return None
        if self.mode == "prepared_clock_expired":
            self.clock[0] += 11
        return (scope, calls)

    @asynccontextmanager
    async def open_prepared_request(
        self, scope: ExecutionScope, prepared: object
    ) -> AsyncGenerator[None]:
        if prepared == (scope, self.prepared_calls, "replayed"):
            raise ValueError("prepared request was already consumed")
        assert prepared == (scope, self.prepared_calls)
        async with self.open_request(scope):
            yield

    @asynccontextmanager
    async def open_request(self, scope: ExecutionScope) -> AsyncGenerator[None]:
        self.events.append(("enter", asyncio.current_task()))
        if self.mode == "enter":
            raise RuntimeError("fabricated admission refusal")
        if self.mode == "cancel":
            raise asyncio.CancelledError
        if self.mode == "deadline":
            await self.release.wait()
        try:
            yield
        finally:
            if self.mode == "cleanup":
                while not self.release.is_set():
                    try:
                        await self.release.wait()
                    except asyncio.CancelledError:
                        self.events.append(("cancelled", asyncio.current_task()))
            self.events.append(("exit", asyncio.current_task()))

    async def invoke_selected(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome:
        self.calls += 1
        if self.calls == 2:
            if self.mode == "host_revoked":
                self.authority.revoked = True
            elif self.mode == "admission_revoked":
                await self.invalidate()
            elif self.mode == "clock_expired":
                self.clock[0] += 11
        if self.mode.startswith("active"):
            self.events.append(("read.enter", asyncio.current_task()))
            self.started.set()
            try:
                await self.release.wait()
            finally:
                self.events.append(("read.exit", asyncio.current_task()))
        return OperationOutcome("succeeded", "", {"selected": selection.kind})


def prepared_calls_for(
    mode: str, scope: ExecutionScope
) -> tuple[tuple[SelectedCallSpec, ...] | None, dict[str, object]]:
    owned_inputs: dict[str, object] = {"filter": {"key": "before"}}
    if not mode.startswith("prepared"):
        return None, owned_inputs
    call = OperationCall("inspect", owned_inputs, scope.principal, scope=scope)
    if mode == "prepared_wrong_scope":
        call = replace(call, scope=replace(scope))
    count = 257 if mode == "prepared_too_many_calls" else 1
    return tuple(
        SelectedCallSpec(call, Selection("get_many")) for _ in range(count)
    ), owned_inputs


def selected_refusal(
    mode: str,
) -> type[BaseException] | tuple[type[BaseException], ...]:
    if mode in {
        "missing",
        "extra",
        "mismatch",
        "wrong",
        "prepared_missing",
        "prepared_wrong_scope",
        "prepared_replay",
        "prepared_none",
        "prepared_clock_expired",
        "prepared_too_many_calls",
    }:
        return ValueError
    if mode == "prepared_denied":
        return SelectedRequestError
    if mode == "cancel":
        return asyncio.CancelledError
    if mode == "active_deadline":
        return RuntimeError, asyncio.CancelledError
    if mode == "deadline":
        return TimeoutError
    return RuntimeError


def selected_services(
    mode: str,
    artifact: ArtifactRef,
    authority: Authority,
    clock: list[float],
    invalidate: Callable[[], Awaitable[bool]],
) -> tuple[HostConfig, HostServices, RequestInspect]:
    authority.revoked = mode == "prepared_denied"
    execution = RequestInspect(mode, authority, clock, invalidate)
    config = HostConfig(
        artifact,
        (Operation("inspect", False, ("get_many",)),),
        1,
        0.25
        if mode in {"deadline", "active_deadline"}
        else 0.05
        if mode == "cleanup"
        else 10,
        {} if mode == "missing" else PINS,
    )
    services = HostServices(
        authority,
        Capture(),
        execution,
        monotonic=(lambda: clock[0])
        if mode in {"clock_expired", "prepared_clock_expired"}
        else time.monotonic,
    )
    return config, services, execution


@pytest.mark.parametrize(
    "mode",
    [
        "ready",
        "prepared",
        "prepared_denied",
        "prepared_missing",
        "prepared_wrong_scope",
        "prepared_replay",
        "prepared_none",
        "prepared_clock_expired",
        "prepared_too_many_calls",
        "missing",
        "extra",
        "mismatch",
        "wrong",
        "enter",
        "cancel",
        "deadline",
        "cleanup",
        "active",
        "active_deadline",
        "host_revoked",
        "admission_revoked",
        "clock_expired",
    ],
)
async def test_selected_session_admission_and_owner_cleanup(mode: str) -> None:
    """@covers HOST-04 @covers HOST-05 @covers generated request snapshot admission"""
    artifact, authority, clock = (
        ArtifactRef("fabricated", "digest"),
        Authority(),
        [time.monotonic()],
    )
    host_ref: dict[str, Host] = {}
    config, services, execution = selected_services(
        mode,
        artifact,
        authority,
        clock,
        lambda: host_ref["host"].admit(ArtifactRef("foreign", "digest")),
    )
    async with create_host(config, services) as host:
        host_ref["host"] = host
        assert await host.admit(artifact)
        scope = await host.open_scope(
            Actor("fabricated"),
            "request",
            api_digest="api",
            consistency="statement" if mode == "wrong" else "request-snapshot-1",
        )
        call = OperationCall("inspect", {}, scope.principal, scope=scope)
        assert (
            await host.invoke(replace(call, scope=replace(scope)))
        ).code == "scope_invalid"
        assert (
            mode == "wrong"
            or (await host.invoke(call)).code == "selected_session_inactive"
        )
        expected = selected_refusal(mode)
        invocation: Awaitable[OperationOutcome] | None = None
        with (
            nullcontext()
            if mode in {"ready", "active", "prepared"}
            else pytest.raises(expected)
        ) as refused:
            prepared_calls, inputs = prepared_calls_for(mode, scope)
            cast(dict[str, str], inputs["filter"])["key"] = "after"
            async with host.open_selected_session(
                scope,
                consistency="request-snapshot-1",
                calls=prepared_calls,
            ):
                for index in range(2 if mode in REFUSALS else 1):
                    invocation = (
                        host.invoke(call, selection=Selection("get_many"))
                        if mode == "active_deadline"
                        else asyncio.create_task(
                            host.invoke(call, selection=Selection("get_many"))
                        )
                    )
                    if mode == "active":
                        await execution.started.wait()
                    else:
                        outcome = await invocation
                        assert (
                            (outcome.status, outcome.result) == ("unavailable", {})
                            and outcome.code in {"timeout", "deadline_exceeded"}
                            if mode == "active_deadline"
                            else (outcome.status, outcome.code, outcome.result)
                            == (
                                (*REFUSALS[mode], {})
                                if index
                                else ("succeeded", None, {"selected": "get_many"})
                            )
                        )
                with pytest.raises(ValueError):
                    async with host.open_selected_session(
                        scope, consistency="request-snapshot-1"
                    ):
                        pass
        assert mode != "cleanup" or (await host.close_scope(scope)).state == "draining"
        execution.release.set()
        assert mode not in REFUSALS or (
            refused is not None
            and isinstance(refused.value, SelectedRequestError)
            and (refused.value.status, refused.value.code) == REFUSALS[mode]
        )
        if isinstance(invocation, asyncio.Task) and invocation.cancelled():
            with pytest.raises(asyncio.CancelledError):
                await invocation
        assert ((await host.close_scope(scope)).state, execution.calls) == (
            "closed",
            2
            if mode in REFUSALS
            else 1
            if mode in {"ready", "prepared", "cleanup", "active", "active_deadline"}
            else 0,
        )
        assert (
            mode == "prepared"
            and execution.prepared_calls is not None
            and cast(
                Mapping[str, object],
                execution.prepared_calls[0].call.inputs["filter"],
            )["key"]
            == "before"
            or mode in {"prepared_missing", "prepared_too_many_calls"}
            and execution.prepared_calls is None
            or mode not in {"prepared", "prepared_missing"}
        )
        if (
            mode
            in {"ready", "prepared", "cleanup", "active", "active_deadline"}
            | REFUSALS.keys()
        ):
            assert (
                execution.events[0][0] == "enter"
                and execution.events[-1][0] == "exit"
                and execution.events[0][1] is execution.events[-1][1]
            )
            assert not mode.startswith("active") or [
                event for event, _task in execution.events
            ] == ["enter", "read.enter", "read.exit", "exit"]
        else:
            assert [event for event, _task in execution.events] == (
                ["enter"] if mode in {"enter", "cancel", "deadline"} else []
            )
