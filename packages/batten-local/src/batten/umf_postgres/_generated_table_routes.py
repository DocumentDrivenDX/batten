"""Read-only protocols for immutable generated connection route values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class ConnectionCursorScope(Protocol):
    @property
    def application_id(self) -> str: ...

    @property
    def application_digest(self) -> str: ...

    @property
    def api_digest(self) -> str: ...

    @property
    def host_operation_id(self) -> str: ...

    @property
    def allowed_field_profile_digest(self) -> str: ...


class AllowedFieldProfile(Protocol):
    @property
    def body(self) -> Mapping[str, object]: ...

    @property
    def digest(self) -> str: ...


class ConnectionRoute(Protocol):
    @property
    def module(self) -> str: ...

    @property
    def record(self) -> str: ...

    @property
    def cursor_scope(self) -> ConnectionCursorScope: ...

    @property
    def allowed_field_profile(self) -> AllowedFieldProfile: ...


__all__ = ["AllowedFieldProfile", "ConnectionCursorScope", "ConnectionRoute"]
