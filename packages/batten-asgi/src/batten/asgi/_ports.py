"""Host-owned local identity interface."""

from collections.abc import Mapping
from typing import Protocol

from batten.contracts import Actor


class LocalSessions(Protocol):
    def resolve(self, cookie: str | None) -> Actor | None: ...

    def login(self, subject: str) -> str | None: ...

    def logout(self, cookie: str | None) -> None: ...

    def profile(self, actor: Actor) -> Mapping[str, object]: ...
