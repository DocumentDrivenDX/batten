"""Public invocation scopes preserve actor attribution and refuse stale authority."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest
from batten.asgi import AppListing
from batten.contracts import (
    Actor,
    ArtifactRef,
    HostConfig,
    HostServices,
    Operation,
    OperationCall,
    OperationOutcome,
    SelectedKey,
    Selection,
)
from batten.hosting.local import LocalApplication, LocalRuntime, LocalSettings
from batten.lintel import ExposureConfig, ExposureOperation, LintelExecution
from batten.runtime import Host, create_host
from lintel.ports import ElementRef, ExecutionError, NodeKey, OperationRef, RequestScope
from starlette.types import ASGIApp, Message, Scope

from tests.runtime.artifacts import native_fixture


async def asgi_post(
    app: ASGIApp,
    path: str,
    body: bytes,
    *,
    headers: list[tuple[bytes, bytes]] | None = None,
    receive_observation: list[int] | None = None,
) -> tuple[int, bytes]:
    messages: list[Message] = [
        {"type": "http.request", "body": body, "more_body": False}
    ]
    response: list[Message] = []

    async def receive() -> Message:
        if receive_observation is not None:
            receive_observation.append(1)
        return messages.pop() if messages else {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        response.append(message)

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers or [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    status = next(
        message["status"]
        for message in response
        if message["type"] == "http.response.start"
    )
    payload = b"".join(
        cast(bytes, message.get("body", b""))
        for message in response
        if message["type"] == "http.response.body"
    )
    return cast(int, status), payload


class Authority:
    revoked = False
    inputs: dict[str, object] | None = None
    wait: asyncio.Event | None = None

    async def check(self, actor: Actor, operation: str) -> bool:
        if self.inputs is not None:
            cast(dict[str, object], self.inputs["value"])["nested"] = (
                "changed during authority"
            )
        if self.wait is not None:
            await self.wait.wait()
        return not self.revoked and operation == "inspect" and bool(actor.subject)


class Capture:
    def __init__(self) -> None:
        self.outcomes: list[tuple[str, str, str]] = []

    @asynccontextmanager
    async def scope(
        self, actor: Actor, operation: str, invocation: str
    ) -> AsyncGenerator[None]:
        yield

    async def capture(
        self, actor: Actor, operation: str, invocation: str, status: str, mutation: bool
    ) -> None:
        self.outcomes.append((actor.kind, actor.subject, status))


class Inspect:
    calls = 0

    async def prepare(self) -> None:
        pass

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        self.calls += 1
        return OperationOutcome(
            "succeeded",
            "",
            {
                "inputs": dict(call.inputs),
                "kind": call.actor.kind,
                "subject": call.actor.subject,
                "request": call.scope.request_id if call.scope else None,
            },
        )

    async def aclose(self) -> None:
        pass


class NestedInspect:
    def __init__(self) -> None:
        self.host: Host | None = None
        self.inner_started, self.inner_release = asyncio.Event(), asyncio.Event()
        self.outer_started, self.outer_release = asyncio.Event(), asyncio.Event()
        self.cancelled = asyncio.Event()
        self.closes = 0
        self.received: list[OperationCall] = []

    async def prepare(self) -> None:
        pass

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        self.received.append(call)
        mode = call.inputs.get("mode")
        if mode == "outer_capacity":
            await cast(Host, self.host).invoke(
                OperationCall("inspect", {"mode": "inner"}, call.actor)
            )
        elif mode == "inner":
            self.inner_started.set()
            await self.inner_release.wait()
        elif mode == "outer_drain":
            await cast(Host, self.host).invoke(
                OperationCall("inspect", {"mode": "inner_done"}, call.actor)
            )
            self.outer_started.set()
            try:
                await self.outer_release.wait()
            except asyncio.CancelledError:
                self.cancelled.set()
                while not self.outer_release.is_set():
                    try:
                        await asyncio.shield(self.outer_release.wait())
                    except asyncio.CancelledError:
                        pass
        return OperationOutcome("succeeded", "", {})

    async def aclose(self) -> None:
        self.closes += 1


class SelectedInspect(Inspect):
    def __init__(self, label: str | None = "fabricated") -> None:
        self.value: Mapping[str, object] | None = (
            None if label is None else {"string": label}
        )

    async def invoke_selected(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome:
        return OperationOutcome(
            "succeeded",
            "",
            {
                "version": "batten.selected-result/1",
                "kind": selection.kind,
                "items": [
                    None
                    if index == 1
                    else {
                        "key": {
                            "record": key.record,
                            "keyId": key.key_id,
                            "components": key.components,
                        },
                        "fields": [
                            {"field": field, "value": self.value}
                            for field in selection.fields
                        ],
                    }
                    for index, key in enumerate(selection.keys)
                ],
            },
        )


@pytest.fixture
def lintel_exposure() -> ExposureOperation:
    record, label = (
        ElementRef("fabricated", "record"),
        ElementRef("fabricated", "label"),
    )
    return ExposureOperation(
        OperationRef("fabricated", "inspect", "table"),
        "inspect",
        ("get_many",),
        record,
        "id",
        (label,),
        ("string",),
        ((label, "string"),),
        nullable_fields=(label,),
    )


@pytest.fixture
def lintel_key(lintel_exposure: ExposureOperation) -> NodeKey:
    return NodeKey(lintel_exposure.record, "id", ({"string": "fabricated-key"},))


@pytest.fixture
def local_runtime(tmp_path: Path) -> LocalRuntime:
    application = LocalApplication(
        AppListing(
            "fabricated", "Fabricated", "Fabricated authority fixture", "icon.svg"
        ),
        ArtifactRef("fabricated-app", "fabricated-digest"),
        tmp_path / "model.json",
        tmp_path,
        (Operation("inspect", False),),
        {"fabricated-actor": {"profile": {}, "operations": ["inspect"]}},
        {"fabricated-actor": "fixture_role"},
        {},
        {},
        lambda _tables, _subjects: Inspect(),
    )
    return LocalRuntime(application, LocalSettings(tmp_path, 8820, 2, 10, 1024, 4, 60))


@pytest.mark.parametrize(
    "execution", [Inspect(), SelectedInspect(), SelectedInspect(None)]
)
async def test_invocation_scope_preserves_authority_and_attribution(
    local_runtime: LocalRuntime,
    execution: Inspect,
    lintel_exposure: ExposureOperation,
    lintel_key: NodeKey,
) -> None:
    """@covers HOST-01 @covers HOST-04 @covers HOST-05"""
    artifact = ArtifactRef("fabricated-app", "fabricated-digest")
    authority, capture, clock = Authority(), Capture(), [1000.0]
    verified = Actor(
        "fabricated-actor", local_runtime.identities.login("fabricated-actor")
    )
    for candidate in (
        verified,
        replace(verified, kind="batch"),
        replace(verified, kind="service"),
        replace(verified, delegation="unverified-reference"),
    ):
        assert await local_runtime.host.services.identity.check(
            candidate, "inspect"
        ) == (candidate == verified)
    host = create_host(
        HostConfig(artifact, (Operation("inspect", False, ("get_many",)),), 2, 10),
        HostServices(authority, capture, execution, monotonic=lambda: clock[0]),
    )
    async with host:
        assert await host.admit(artifact)

        api = LintelExecution(
            host,
            ExposureConfig(artifact, "a" * 64, "b" * 64, (lintel_exposure,), {}),
            native_fixture(),
        )
        for kind in ("person", "batch", "service"):
            actor = Actor("fabricated-actor", kind=kind)
            scope = await host.open_scope(actor, kind, api_digest="a" * 64)
            authority.inputs = {
                "value": {"nested": "original"},
                "key": SelectedKey(
                    ("fabricated", "record"), "id", ({"string": "fabricated-key"},)
                ),
            }
            call = OperationCall("inspect", authority.inputs, actor, scope=scope)
            result = await host.invoke(call)
            assert result.status == "succeeded" and result.result == {
                "inputs": {
                    "value": {"nested": "original"},
                    "key": SelectedKey(
                        ("fabricated", "record"), "id", ({"string": "fabricated-key"},)
                    ),
                },
                "kind": kind,
                "subject": actor.subject,
                "request": kind,
            }
            async with api.session(
                RequestScope(
                    artifact.id,
                    "a" * 64,
                    "query",
                    scope,
                    kind,
                    scope.deadline_monotonic,
                )
            ) as session:
                if isinstance(execution, SelectedInspect):
                    rows = await session.get_many(
                        lintel_exposure.ref,
                        (lintel_key, lintel_key, lintel_key),
                        lintel_exposure.fields,
                    )
                    assert (
                        rows[0] == rows[2]
                        and rows[1] is None
                        and rows[0] is not None
                        and rows[0].fields
                        == {lintel_exposure.fields[0]: execution.value}
                    )
                else:
                    with pytest.raises(ExecutionError, match="UNSUPPORTED"):
                        await session.get_many(
                            lintel_exposure.ref, (lintel_key,), lintel_exposure.fields
                        )
            assert (
                await host.invoke(call, selection=Selection("connection", first=0))
            ).code == "unsupported_selection"
            invalid = (
                replace(scope, application=ArtifactRef("foreign", "different")),
                replace(scope, principal=replace(actor, subject="other")),
                replace(scope, lease_id=""),
                replace(scope, deadline_monotonic=float("nan")),
                replace(scope),
            )
            for candidate in invalid:
                assert not host.scope_active(candidate)
                outcome = await host.invoke(replace(call, scope=candidate))
                assert (outcome.status, outcome.code, outcome.result) == (
                    "denied",
                    "scope_invalid",
                    {},
                )
            for revoked, advance, status, code in (
                (True, 0, "denied", "denied"),
                (False, 11, "unavailable", "deadline_exceeded"),
            ):
                authority.revoked = revoked
                clock[0] += advance
                denied = await host.invoke(call)
                assert (denied.status, denied.code, denied.result) == (status, code, {})
            assert not host.scope_active(scope)
            assert (await host.close_scope(scope)).state == "closed" and (
                await host.invoke(call)
            ).code == "scope_invalid"
        scope = await host.open_scope(
            actor, "authority-timeout", deadline_monotonic=clock[0] + 0.01
        )
        before, authority.wait = execution.calls, asyncio.Event()
        outcome = await host.invoke(replace(call, scope=scope))
        assert (outcome.status, outcome.code, outcome.result, execution.calls) == (
            "unavailable",
            "deadline_exceeded",
            {},
            before,
        )
        assert (await host.close_scope(scope)).state == "closed" and [
            entry for entry in capture.outcomes if entry[2] == "succeeded"
        ] == [
            (kind, "fabricated-actor", "succeeded")
            for kind in ("person", "batch", "service")
            for _ in range(2 if isinstance(execution, SelectedInspect) else 1)
        ]
    assert (await host.invoke(call)).code == "not_admitted"


async def test_nested_invocations_count_and_drain_independently() -> None:
    artifact = ArtifactRef("nested-app", "nested-digest")
    executor = NestedInspect()
    host = create_host(
        HostConfig(artifact, (Operation("inspect", False),), 2, 1),
        HostServices(Authority(), Capture(), executor, ownership="owned"),
    )
    executor.host = host
    async with host:
        assert await host.admit(artifact)
        actor = Actor("nested-actor")
        wide_mapping = {"items": tuple(range(5_000))}
        page_wire_call = OperationCall("inspect", wide_mapping, actor)
        assert (await host.invoke(page_wire_call)).status == "succeeded"
        assert executor.received[-1].inputs == {"items": list(range(5_000))}
        provider_call_count = len(executor.received)
        oversized_call = OperationCall(
            "inspect", {"too_many": tuple(range(16_400))}, actor
        )
        refused = await host.invoke(oversized_call)
        assert (refused.status, refused.code) == ("invalid", "invalid_inputs")
        assert len(executor.received) == provider_call_count
        outer = asyncio.create_task(
            host.invoke(OperationCall("inspect", {"mode": "outer_capacity"}, actor))
        )
        await executor.inner_started.wait()
        limited = await host.invoke(OperationCall("inspect", {"mode": "idle"}, actor))
        assert (limited.status, limited.code) == ("unavailable", "limit_exceeded")
        executor.inner_release.set()
        assert (await outer).status == "succeeded"

        draining = asyncio.create_task(
            host.invoke(OperationCall("inspect", {"mode": "outer_drain"}, actor))
        )
        await executor.outer_started.wait()
        report = await host.aclose()
        assert report.state == "draining"
        assert executor.cancelled.is_set() and executor.closes == 0
        executor.outer_release.set()
        assert (await draining).status == "denied"
        assert (await host.aclose()).state == "closed"
        assert executor.closes == 1
