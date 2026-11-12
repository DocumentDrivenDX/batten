"""Portable operation ports; no platform library or native client crosses these."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Literal, Protocol, cast, runtime_checkable

from batten.contracts._connection_routes import connection_routes_digest
from batten.contracts._values import freeze_value, snapshot_transport


@dataclass(frozen=True)
class Actor:
    subject: str
    session: str | None = field(default=None, repr=False)
    kind: Literal["person", "service", "batch"] = "person"
    delegation: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    digest: str


@dataclass(frozen=True)
class Operation:
    id: str
    mutation: bool
    selection_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class SelectedKey:
    record: tuple[str, str]
    key_id: str
    components: tuple[Mapping[str, object], ...]

    def __post_init__(self) -> None:
        if (
            type(self.record) is not tuple
            or len(self.record) != 2
            or any(type(part) is not str or not part for part in self.record)
            or type(self.key_id) is not str
            or not self.key_id
        ):
            raise ValueError("selected key requires exact Record and Key identity")
        budget = [4096]
        components = tuple(freeze_value(item, budget) for item in self.components)
        if not all(isinstance(item, Mapping) for item in components):
            raise ValueError("selected key components require tagged mappings")
        object.__setattr__(self, "components", components)


@dataclass(frozen=True)
class Selection:
    kind: Literal["get_many", "connection", "related_many"]
    fields: tuple[tuple[str, str], ...] = ()
    keys: tuple[SelectedKey, ...] = ()
    parents: tuple[SelectedKey, ...] = ()
    target: tuple[str, str] | None = None
    first: int | None = None
    after: str | None = None


@dataclass(frozen=True)
class SelectedCallSpec:
    """Owned immutable call and selection for one prepared selected request."""

    call: OperationCall
    selection: Selection

    def __post_init__(self) -> None:
        if (
            type(self.call) is not OperationCall
            or type(self.selection) is not Selection
        ):
            raise ValueError("selected call spec requires contract values")
        call = self.call.snapshot()
        selection = self.selection
        if type(selection.fields) is not tuple or any(
            type(field) is not tuple
            or len(field) != 2
            or any(type(part) is not str or not part for part in field)
            for field in selection.fields
        ):
            raise ValueError("selected fields require immutable references")
        if len(selection.fields) > 1024:
            raise ValueError("selected fields exceed limits")
        if (
            type(selection.kind) is not str
            or (selection.first is not None and type(selection.first) is not int)
            or (selection.after is not None and type(selection.after) is not str)
        ):
            raise ValueError("selected call requires immutable selection values")
        if type(selection.keys) is not tuple or type(selection.parents) is not tuple:
            raise ValueError("selected keys require immutable tuples")
        if len(selection.keys) + len(selection.parents) > 4096:
            raise ValueError("selected keys exceed limits")
        keys = tuple(
            SelectedKey(key.record, key.key_id, key.components)
            for key in selection.keys
            if type(key) is SelectedKey
        )
        parents = tuple(
            SelectedKey(key.record, key.key_id, key.components)
            for key in selection.parents
            if type(key) is SelectedKey
        )
        if len(keys) != len(selection.keys) or len(parents) != len(selection.parents):
            raise ValueError("selected keys require contract values")
        target = (
            None
            if selection.target is None
            else tuple(selection.target)
            if type(selection.target) is tuple
            else selection.target
        )
        if target is not None and (
            type(target) is not tuple
            or len(target) != 2
            or any(type(part) is not str or not part for part in target)
        ):
            raise ValueError("selected target requires an immutable reference")
        object.__setattr__(self, "call", call)
        object.__setattr__(
            self,
            "selection",
            Selection(
                selection.kind,
                tuple(
                    cast(tuple[str, str], tuple(field)) for field in selection.fields
                ),
                keys,
                parents,
                target,
                selection.first,
                selection.after,
            ),
        )


@dataclass(frozen=True)
class ExecutionScope:
    application: ArtifactRef
    principal: Actor
    request_id: str
    deadline_monotonic: float
    lease_id: str
    api_digest: str | None = None
    consistency: str | None = None


@dataclass(frozen=True)
class OperationCall:
    operation: str
    inputs: Mapping[str, object]
    actor: Actor
    key: str | None = None
    phase: str = "invoke"
    scope: ExecutionScope | None = None
    confirmation: str | None = None

    def snapshot(self) -> OperationCall:
        """Own bounded JSON transport data before any asynchronous host gate."""
        return replace(self, inputs=snapshot_transport(self.inputs, SelectedKey))


@dataclass(frozen=True)
class OperationOutcome:
    status: str
    invocation: str
    result: Mapping[str, object]
    code: str | None = None


class SelectedRequestError(RuntimeError):
    """A selected request had a refusal; its earlier data cannot be released."""

    def __init__(self, status: str, code: str | None):
        super().__init__("selected request failed")
        self.status, self.code = status, code


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


@runtime_checkable
class SelectedExecution(Protocol):
    async def invoke_selected(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome: ...


@runtime_checkable
class RequestScopedSelectedExecution(SelectedExecution, Protocol):
    def capabilities(self) -> Mapping[str, str]: ...
    def open_request(
        self, scope: ExecutionScope
    ) -> AbstractAsyncContextManager[None]: ...


@runtime_checkable
class PreparedSelectedExecution(RequestScopedSelectedExecution, Protocol):
    def prepare_selected(
        self, scope: ExecutionScope, calls: tuple[SelectedCallSpec, ...]
    ) -> object: ...
    def open_prepared_request(
        self, scope: ExecutionScope, prepared: object
    ) -> AbstractAsyncContextManager[None]: ...


@dataclass(frozen=True)
class HostConfig:
    artifact: ArtifactRef
    operations: tuple[Operation, ...]
    max_concurrency: int
    timeout_seconds: float
    selected_capabilities: Mapping[str, str] = field(
        default_factory=lambda: dict[str, str]()
    )

    def __post_init__(self) -> None:
        values = dict(self.selected_capabilities)
        if any(
            type(key) is not str or type(value) is not str
            for key, value in values.items()
        ):
            raise ValueError("selected capability pins require strings")
        object.__setattr__(self, "selected_capabilities", MappingProxyType(values))


@dataclass(frozen=True)
class HostServices:
    identity: Identity
    observations: Observations
    execution: Execution
    ownership: str = "borrowed"
    monotonic: Callable[[], float] = field(default=time.monotonic, repr=False)


@dataclass(frozen=True)
class ShutdownReport:
    state: str
    retained_resources: tuple[str, ...]
    outcomes: tuple[str, ...]


__all__ = [
    "Actor",
    "ArtifactRef",
    "Execution",
    "ExecutionScope",
    "HostConfig",
    "HostServices",
    "Identity",
    "Observations",
    "Operation",
    "OperationCall",
    "OperationOutcome",
    "PreparedSelectedExecution",
    "RequestScopedSelectedExecution",
    "SelectedExecution",
    "SelectedKey",
    "SelectedCallSpec",
    "SelectedRequestError",
    "connection_routes_digest",
    "Selection",
    "ShutdownReport",
]
