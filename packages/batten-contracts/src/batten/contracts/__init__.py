"""Portable operation ports; no platform library or native client crosses these."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Actor:
    subject: str
    session: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    digest: str


@dataclass(frozen=True)
class Operation:
    id: str
    mutation: bool


@dataclass(frozen=True)
class OperationCall:
    operation: str
    inputs: Mapping[str, object]
    actor: Actor
    key: str | None = None
    phase: str = "invoke"


@dataclass(frozen=True)
class OperationOutcome:
    status: str
    invocation: str
    result: Mapping[str, object]
    code: str | None = None


class Identity(Protocol):
    async def check(self, actor: Actor, operation: str) -> bool: ...


class Observations(Protocol):
    def scope(
        self, actor: Actor, operation: str, invocation: str
    ) -> AbstractAsyncContextManager[None]: ...
    async def capture(
        self, actor: Actor, operation: str, invocation: str, status: str, mutation: bool
    ) -> None: ...


class Execution(Protocol):
    async def prepare(self) -> None: ...
    async def invoke(self, call: OperationCall) -> OperationOutcome: ...
    async def aclose(self) -> None: ...


@dataclass(frozen=True)
class HostConfig:
    artifact: ArtifactRef
    operations: tuple[Operation, ...]
    max_concurrency: int
    timeout_seconds: float


@dataclass(frozen=True)
class HostServices:
    identity: Identity
    observations: Observations
    execution: Execution
    ownership: str = "borrowed"


@dataclass(frozen=True)
class ShutdownReport:
    state: str
    retained_resources: tuple[str, ...]
    outcomes: tuple[str, ...]


__all__ = [
    "Actor",
    "ArtifactRef",
    "Execution",
    "HostConfig",
    "HostServices",
    "Identity",
    "Observations",
    "Operation",
    "OperationCall",
    "OperationOutcome",
    "ShutdownReport",
]
