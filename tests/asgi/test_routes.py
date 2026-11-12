"""Operation endpoints and local sessions over a real Host with fake services."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from batten.asgi import create_app
from batten.contracts import (
    Actor,
    ArtifactRef,
    HostConfig,
    HostServices,
    Operation,
    OperationCall,
    OperationOutcome,
)
from batten.runtime import create_host
from starlette.testclient import TestClient

ORIGIN = "http://127.0.0.1:8820"
ARTIFACT = ArtifactRef("app", "digest")
JSON = {"origin": ORIGIN}
SECOND_KEY = "fedcba9876543210fedcba9876543210"


class Sessions:
    def __init__(self) -> None:
        self.cookies: dict[str, str] = {}

    def resolve(self, cookie: str | None) -> Actor | None:
        subject = self.cookies.get(cookie or "")
        return Actor(subject, cookie) if subject else None

    def login(self, subject: str) -> str | None:
        if subject != "alex":
            return None
        self.cookies["cookie-1"] = subject
        return "cookie-1"

    def logout(self, cookie: str | None) -> None:
        self.cookies.pop(cookie or "", None)

    def profile(self, actor: Actor) -> dict[str, object]:
        return {"id": actor.subject, "name": "Alex"}


class Allow:
    async def check(self, actor: Actor, operation: str) -> bool:
        return True


class Quiet:
    @asynccontextmanager
    async def scope(
        self, actor: Actor, operation: str, invocation: str
    ) -> AsyncGenerator[None, None]:
        yield

    async def capture(
        self, actor: Actor, operation: str, invocation: str, status: str, mutation: bool
    ) -> None:
        return None


class Echo:
    async def prepare(self) -> None:
        return None

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        return OperationOutcome(
            "succeeded", "x", {"operation": call.operation, "inputs": dict(call.inputs)}
        )

    async def aclose(self) -> None:
        return None


@pytest.fixture
def http(tmp_path: Path) -> TestClient:
    (tmp_path / "index.html").write_text("<h1>app</h1>")
    host = create_host(
        HostConfig(ARTIFACT, (Operation("echo", False),), 2, 1.0),
        HostServices(Allow(), Quiet(), Echo(), "owned"),
    )
    app = create_app(host, Sessions(), tmp_path, origin=ORIGIN, max_body_bytes=64)
    return TestClient(app, base_url=ORIGIN, client=("127.0.0.1", 1))


def login(http: TestClient) -> None:
    assert (
        http.post(
            "/api/local-session", json={"actor": "alex"}, headers=JSON
        ).status_code
        == 200
    )


def test_create_app_requires_a_loopback_origin_and_a_body_bound(tmp_path: Path) -> None:
    host = create_host(
        HostConfig(ARTIFACT, (), 1, 1.0), HostServices(Allow(), Quiet(), Echo())
    )
    with pytest.raises(ValueError):
        create_app(
            host, Sessions(), tmp_path, origin="http://example.com", max_body_bytes=1
        )
    with pytest.raises(ValueError):
        create_app(host, Sessions(), tmp_path, origin=ORIGIN, max_body_bytes=0)


def test_login_session_and_logout(http: TestClient) -> None:
    with http:
        assert http.get("/").text == "<h1>app</h1>"
        assert http.get("/api/session").json() == {"actor": None}
        denied = http.post(
            "/api/local-session", json={"actor": "mallory"}, headers=JSON
        )
        assert denied.status_code == 403
        login(http)
        assert http.get("/api/session").json()["actor"] == {
            "id": "alex",
            "name": "Alex",
        }
        assert http.post("/api/logout", headers=JSON).status_code == 200
        assert http.get("/api/session").json() == {"actor": None}


def test_operations_require_a_session(http: TestClient) -> None:
    with http:
        outcome = http.post("/api/operations/echo", json={"inputs": {}}, headers=JSON)
        assert (outcome.status_code, outcome.json()["code"]) == (403, "denied")


def test_operation_runs_through_the_host(http: TestClient) -> None:
    with http:
        login(http)
        body = {"inputs": {"n": 1}, "key": SECOND_KEY}
        outcome = http.post("/api/operations/echo", json=body, headers=JSON)
        assert outcome.status_code == 200
        assert outcome.json()["status"] == "succeeded"
        assert outcome.json()["invocation"] == SECOND_KEY
        assert outcome.json()["result"] == {"operation": "echo", "inputs": {"n": 1}}
        unknown = http.post("/api/operations/other", json={"inputs": {}}, headers=JSON)
        assert (unknown.status_code, unknown.json()["code"]) == (403, "not_admitted")


@pytest.mark.parametrize(
    "payload",
    [
        {"inputs": "text"},
        {"nothing": 1},
        {"inputs": {}, "extra": 1},
        {"inputs": {}, "key": 5},
        {"inputs": {}, "phase": "other"},
    ],
)
def test_malformed_operation_requests_are_invalid(
    http: TestClient, payload: dict[str, object]
) -> None:
    with http:
        login(http)
        outcome = http.post("/api/operations/echo", json=payload, headers=JSON)
        assert outcome.status_code == 400


def test_oversized_and_non_json_bodies_are_rejected(http: TestClient) -> None:
    with http:
        login(http)
        big = {"inputs": {"text": "x" * 200}}
        assert (
            http.post("/api/operations/echo", json=big, headers=JSON).status_code == 400
        )
        text = http.post("/api/operations/echo", content="{}", headers=JSON)
        assert text.status_code == 400
        array = http.post("/api/operations/echo", json=[1], headers=JSON)
        assert array.status_code == 400
