"""Local settings, stub identities and audit capture; no database needed."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest
from batten.contracts import Actor
from batten.hosting.local import LocalSettings
from batten.hosting.local._identity import LocalIdentities
from batten.hosting.local._observations import LocalObservations

PEOPLE = {
    "alex": {"profile": {"name": "Alex"}, "operations": ["list", "submit"]},
    "blake": {"profile": {"name": "Blake"}, "operations": ["list", "decide"]},
}


def settings(tmp_path: Path, **overrides: Any) -> LocalSettings:
    values: dict[str, Any] = {
        "data": tmp_path,
        "port": 8820,
        "max_concurrency": 4,
        "timeout_seconds": 30.0,
        "max_body_bytes": 1024,
        "max_sessions": 8,
        "session_ttl_seconds": 60.0,
    }
    values.update(overrides)
    return LocalSettings(**values)


def test_valid_settings_are_accepted(tmp_path: Path) -> None:
    assert settings(tmp_path).port == 8820


@pytest.mark.parametrize(
    "bad",
    [
        {"port": 80},
        {"port": 70000},
        {"port": "8820"},
        {"max_concurrency": 0},
        {"max_body_bytes": -1},
        {"max_sessions": 0},
        {"timeout_seconds": 0.0},
        {"timeout_seconds": float("inf")},
        {"session_ttl_seconds": float("nan")},
        {"data": Path("relative/data")},
    ],
)
def test_invalid_settings_are_rejected(tmp_path: Path, bad: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        settings(tmp_path, **bad)


def test_login_resolves_to_the_actor_and_logout_ends_the_session() -> None:
    people = LocalIdentities(PEOPLE, max_sessions=4, ttl_seconds=60)
    cookie = people.login("alex")
    assert cookie is not None
    actor = people.resolve(cookie)
    assert actor is not None and actor == Actor("alex", cookie)
    assert people.profile(actor) == {"name": "Alex", "id": "alex"}
    people.logout(cookie)
    assert people.resolve(cookie) is None
    assert people.resolve(None) is None


def test_unknown_and_revoked_subjects_cannot_log_in() -> None:
    people = LocalIdentities(PEOPLE, max_sessions=4, ttl_seconds=60)
    assert people.login("mallory") is None
    cookie = people.login("blake")
    people.revoke("blake")
    assert people.resolve(cookie) is None
    assert people.login("blake") is None


def test_session_cap_and_expiry() -> None:
    people = LocalIdentities(PEOPLE, max_sessions=1, ttl_seconds=0.05)
    assert people.login("alex") is not None
    assert people.login("blake") is None
    time.sleep(0.1)
    assert people.login("blake") is not None


async def test_operation_checks_follow_the_session_and_the_grant() -> None:
    people = LocalIdentities(PEOPLE, max_sessions=4, ttl_seconds=60)
    cookie = people.login("alex")
    actor = Actor("alex", cookie)
    assert await people.check(actor, "submit")
    assert not await people.check(actor, "decide")
    assert not await people.check(Actor("blake", cookie), "list")
    assert not await people.check(Actor("alex", "forged"), "list")


async def test_capture_appends_a_redacted_audit_frame(tmp_path: Path) -> None:
    observations = LocalObservations(tmp_path, "app-1", timeout_ms=1000)
    actor = Actor("alex", "secret-cookie")
    await observations.capture(actor, "submit", "inv-1", "succeeded", True)
    await observations.aclose()
    (line,) = (tmp_path / "audit.jsonl").read_text().splitlines()
    frame = json.loads(line)
    assert frame == {
        "type": "audit",
        "application": "app-1",
        "actor": "alex",
        "operation": "submit",
        "invocation": "inv-1",
        "status": "succeeded",
        "mutation": True,
    }
    assert "secret-cookie" not in line
