"""Explicit local-only stub identities; session references never come from app input."""

from __future__ import annotations

import copy
import math
import secrets
import time
from collections.abc import Mapping
from typing import cast

from batten.contracts import Actor


class LocalIdentities:
    def __init__(
        self,
        people: Mapping[str, Mapping[str, object]],
        *,
        max_sessions: int,
        ttl_seconds: float,
    ):
        if (
            type(max_sessions) is not int
            or max_sessions < 1
            or type(ttl_seconds) not in {int, float}
            or not math.isfinite(ttl_seconds)
            or ttl_seconds <= 0
        ):
            raise ValueError("finite positive local session limits required")
        self._people = copy.deepcopy(dict(people))
        self.max_sessions, self.ttl = max_sessions, ttl_seconds
        self.sessions: dict[str, tuple[str, float]] = {}
        self.revoked: set[str] = set()

    def login(self, subject: str) -> str | None:
        self.sessions = {
            key: value
            for key, value in self.sessions.items()
            if value[1] > time.monotonic()
        }
        if (
            subject not in self._people
            or subject in self.revoked
            or len(self.sessions) >= self.max_sessions
        ):
            return None
        cookie = secrets.token_urlsafe(32)
        self.sessions[cookie] = (subject, time.monotonic() + self.ttl)
        return cookie

    def resolve(self, cookie: str | None) -> Actor | None:
        value = self.sessions.get(cookie or "")
        if value is None or value[1] <= time.monotonic() or value[0] in self.revoked:
            return None
        return Actor(value[0], cookie)

    def logout(self, cookie: str | None) -> None:
        self.sessions.pop(cookie or "", None)

    def revoke(self, subject: str) -> None:
        self.revoked.add(subject)

    def profile(self, actor: Actor) -> Mapping[str, object]:
        profile = cast(Mapping[str, object], self._people[actor.subject]["profile"])
        return {**profile, "id": actor.subject}

    async def check(self, actor: Actor, operation: str) -> bool:
        resolved = self.resolve(actor.session)
        if resolved is None or resolved != actor:
            return False
        return operation in cast(list[str], self._people[actor.subject]["operations"])
