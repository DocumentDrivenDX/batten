"""Host lifecycle, admission, outcomes and bounded concurrency, with fake services."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from batten.contracts import (
    Actor,
    ArtifactRef,
    HostConfig,
    HostServices,
    Operation,
    OperationCall,
    OperationOutcome,
)
from batten.runtime import Host, create_host

ARTIFACT = ArtifactRef("app-1", "digest-1")
ALEX = Actor("alex", "session-1")
KEY = "0123456789abcdef0123456789abcdef"
OPERATIONS = (Operation("read", False), Operation("write", True))


class Identity:
    def __init__(self) -> None:
        self.allowed = True
        self.after_run = True
        self.calls = 0

    async def check(self, actor: Actor, operation: str) -> bool:
        self.calls += 1
        # The first check admits the call; a later one models revocation mid-flight.
        return self.allowed if self.calls == 1 else self.after_run


class Observations:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []
        self.fail = False

    @asynccontextmanager
    async def scope(
        self, actor: Actor, operation: str, invocation: str
    ) -> AsyncGenerator[None, None]:
        yield

    async def capture(
        self, actor: Actor, operation: str, invocation: str, status: str, mutation: bool
    ) -> None:
        if self.fail:
            raise OSError("sink down")
        self.events.append((operation, status))


class Execution:
    def __init__(self) -> None:
        self.prepared = 0
        self.closed = 0
        self.fail_prepare = False
        self.error: Exception | None = None
        self.delay = 0.0
        self.running = 0
        self.peak = 0

    async def prepare(self) -> None:
        self.prepared += 1
        if self.fail_prepare:
            raise RuntimeError("cannot prepare")

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        self.running += 1
        self.peak = max(self.peak, self.running)
        try:
            await asyncio.sleep(self.delay)
            if self.error is not None:
                raise self.error
            return OperationOutcome("succeeded", "ignored", {"echo": call.operation})
        finally:
            self.running -= 1

    async def aclose(self) -> None:
        self.closed += 1


class Fixture:
    def __init__(
        self,
        *,
        max_concurrency: int = 2,
        timeout: float = 1.0,
        ownership: str = "owned",
    ) -> None:
        self.identity, self.observations = Identity(), Observations()
        self.execution = Execution()
        self.host = Host(
            HostConfig(ARTIFACT, OPERATIONS, max_concurrency, timeout),
            HostServices(self.identity, self.observations, self.execution, ownership),
        )

    async def running(self) -> Host:
        await self.host.start()
        assert await self.host.admit(ARTIFACT)
        return self.host


def call(operation: str, key: str | None = None) -> OperationCall:
    return OperationCall(operation, {}, ALEX, key)


@pytest.mark.parametrize(("concurrency", "timeout"), [(0, 1.0), (1, 0.0), (1, -1.0)])
def test_non_positive_limits_are_rejected(concurrency: int, timeout: float) -> None:
    with pytest.raises(ValueError, match="limits"):
        Fixture(max_concurrency=concurrency, timeout=timeout)


def test_duplicate_operations_and_unknown_ownership_are_rejected() -> None:
    services = HostServices(Identity(), Observations(), Execution())
    with pytest.raises(ValueError):
        create_host(
            HostConfig(ARTIFACT, (*OPERATIONS, OPERATIONS[0]), 1, 1.0), services
        )
    with pytest.raises(ValueError):
        Fixture(ownership="shared")


async def test_invoke_before_admission_is_refused() -> None:
    fixture = Fixture()
    await fixture.host.start()
    outcome = await fixture.host.invoke(call("read"))
    assert (outcome.status, outcome.code) == ("denied", "not_admitted")
    assert not await fixture.host.admit(ArtifactRef("app-1", "other"))
    assert await fixture.host.readiness() == "running"


async def test_successful_call_keeps_the_caller_key_and_records_both_phases() -> None:
    host = await Fixture().running()
    outcome = await host.invoke(call("read", KEY))
    assert (outcome.status, outcome.invocation) == ("succeeded", KEY)
    assert dict(outcome.result) == {"echo": "read"}
    observations = host.services.observations
    assert isinstance(observations, Observations)
    assert observations.events == [("read", "started"), ("read", "succeeded")]


async def test_unknown_operation_malformed_key_and_denied_actor_are_refused() -> None:
    fixture = Fixture()
    host = await fixture.running()
    unknown = await host.invoke(call("delete"))
    assert (unknown.status, unknown.code) == ("denied", "not_admitted")
    malformed = await host.invoke(call("read", "NOT A KEY"))
    assert (malformed.status, malformed.code) == ("invalid", "invalid_key")
    fixture.identity.allowed = False
    denied = await host.invoke(call("read"))
    assert (denied.status, denied.code) == ("denied", "denied")
    assert fixture.execution.peak == 0


@pytest.mark.parametrize(
    ("operation", "status"), [("read", "denied"), ("write", "uncertain")]
)
async def test_authority_revoked_during_a_call(operation: str, status: str) -> None:
    fixture = Fixture()
    fixture.identity.after_run = False
    outcome = await (await fixture.running()).invoke(call(operation))
    assert (outcome.status, outcome.code) == (status, "authority_revoked")


@pytest.mark.parametrize(
    ("operation", "status"), [("read", "unavailable"), ("write", "uncertain")]
)
async def test_provider_failure_never_claims_a_mutation_failed(
    operation: str, status: str
) -> None:
    fixture = Fixture()
    fixture.execution.error = RuntimeError("database gone")
    outcome = await (await fixture.running()).invoke(call(operation))
    assert (outcome.status, outcome.code) == (status, "provider_unavailable")


@pytest.mark.parametrize(
    ("operation", "status"), [("read", "unavailable"), ("write", "uncertain")]
)
async def test_timeout(operation: str, status: str) -> None:
    fixture = Fixture(timeout=0.05)
    fixture.execution.delay = 1.0
    outcome = await (await fixture.running()).invoke(call(operation))
    assert (outcome.status, outcome.code) == (status, "timeout")


async def test_unavailable_observation_sink_stops_the_call() -> None:
    fixture = Fixture()
    host = await fixture.running()
    fixture.observations.fail = True
    outcome = await host.invoke(call("write"))
    assert (outcome.status, outcome.code) == ("unavailable", "capture_unavailable")
    assert fixture.execution.peak == 0


async def test_concurrency_is_bounded_by_the_configured_limit() -> None:
    fixture = Fixture(max_concurrency=2)
    fixture.execution.delay = 0.05
    fixture.identity.after_run = True
    host = await fixture.running()
    outcomes = await asyncio.gather(*(host.invoke(call("read")) for _ in range(5)))
    statuses = sorted(o.status for o in outcomes)
    assert statuses == [
        "succeeded",
        "succeeded",
        "unavailable",
        "unavailable",
        "unavailable",
    ]
    assert {o.code for o in outcomes if o.status == "unavailable"} == {"limit_exceeded"}
    assert fixture.execution.peak == 2


async def test_close_reports_state_refuses_later_calls_and_honours_ownership() -> None:
    owned, borrowed = Fixture(ownership="owned"), Fixture(ownership="borrowed")
    for fixture in (owned, borrowed):
        host = await fixture.running()
        report = await host.aclose()
        assert (report.state, report.retained_resources) == ("closed", ("app-1",))
        refused = await host.invoke(call("read"))
        assert (refused.status, refused.code) == ("denied", "not_admitted")
        assert (await host.aclose()).state == "closed"
    assert (owned.execution.closed, borrowed.execution.closed) == (1, 0)


async def test_async_with_starts_and_closes_and_cannot_restart() -> None:
    fixture = Fixture()
    async with fixture.host as host:
        assert await host.readiness() == "running"
        await host.start()
        assert fixture.execution.prepared == 1
    assert await fixture.host.readiness() == "closed"
    with pytest.raises(RuntimeError, match="restart"):
        await fixture.host.start()


async def test_failed_prepare_closes_the_host_and_propagates() -> None:
    fixture = Fixture()
    fixture.execution.fail_prepare = True
    with pytest.raises(RuntimeError, match="cannot prepare"):
        await fixture.host.start()
    assert await fixture.host.readiness() == "closed"
    assert fixture.execution.closed == 1


async def test_close_cancels_in_flight_calls_and_marks_a_mutation_uncertain() -> None:
    fixture = Fixture(timeout=5.0)
    fixture.execution.delay = 5.0
    host = await fixture.running()
    task = asyncio.create_task(host.invoke(call("write")))
    await asyncio.sleep(0.05)
    assert (await host.aclose()).state == "closed"
    with pytest.raises(asyncio.CancelledError):
        await task
    assert fixture.observations.events[-1] == ("write", "uncertain")
