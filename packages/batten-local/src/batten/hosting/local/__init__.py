"""Explicit local composition; optional provider dependencies stay out of core."""

from __future__ import annotations

import math
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from batten.asgi import AppListing, create_app, create_registry
from batten.contracts import (
    Actor,
    ArtifactRef,
    Execution,
    HostConfig,
    HostServices,
    Operation,
)
from batten.runtime import create_host
from batten.tables import TablePort
from batten.umf_postgres.local import LocalTables, initialize
from starlette.applications import Starlette

from ._identity import LocalIdentities
from ._observations import LocalObservations
from ._server import ReadyServer


@dataclass(frozen=True)
class LocalApplication:
    listing: AppListing
    artifact: ArtifactRef
    model: Path
    assets: Path
    operations: tuple[Operation, ...]
    people: Mapping[str, Mapping[str, object]]
    native_people: dict[str, str]
    memberships: dict[str, list[str]]
    database: dict[str, object]
    execution: Callable[[TablePort, Mapping[str, str]], Execution]


@dataclass(frozen=True)
class LocalSettings:
    data: Path
    port: int
    max_concurrency: int
    timeout_seconds: float
    max_body_bytes: int
    max_sessions: int
    session_ttl_seconds: float

    def __post_init__(self) -> None:
        if any(
            type(value) is not int
            for value in (
                self.port,
                self.max_concurrency,
                self.max_body_bytes,
                self.max_sessions,
            )
        ):
            raise ValueError("integer local limits required")
        if any(
            type(value) not in (int, float) or not math.isfinite(value)
            for value in (self.timeout_seconds, self.session_ttl_seconds)
        ):
            raise ValueError("finite local deadlines required")
        if not self.data.is_absolute() or not 1024 <= self.port <= 65535:
            raise ValueError("absolute local data path and unprivileged port required")
        if (
            min(
                self.max_concurrency,
                self.timeout_seconds,
                self.max_body_bytes,
                self.max_sessions,
                self.session_ttl_seconds,
            )
            <= 0
        ):
            raise ValueError("explicit positive local limits required")


class LocalRuntime:
    def __init__(self, application: LocalApplication, settings: LocalSettings):
        self.application, self.settings = application, settings
        self.identities = LocalIdentities(
            application.people,
            max_sessions=settings.max_sessions,
            ttl_seconds=settings.session_ttl_seconds,
        )
        self.observations = LocalObservations(
            settings.data,
            application.artifact.id,
            timeout_ms=int(settings.timeout_seconds * 1000),
        )
        self.tables = LocalTables(
            settings.data,
            application.model,
            self.identities,
            self.observations.provider,
        )
        subjects = {
            role: subject for subject, role in application.native_people.items()
        }
        execution = application.execution(self.tables.provider, subjects)
        self.host = create_host(
            HostConfig(
                application.artifact,
                application.operations,
                settings.max_concurrency,
                settings.timeout_seconds,
            ),
            HostServices(self.identities, self.observations, execution, "owned"),
        )

    async def initialize(self) -> None:
        app = self.application
        await initialize(
            self.settings.data,
            app.model,
            app.database,
            app.native_people,
            app.memberships,
        )

    async def open(self) -> None:
        incident = uuid.uuid4().hex
        try:
            await self.observations.capture(
                Actor("system"), "startup", incident, "started", False
            )
            async with self.observations.scope(Actor("system"), "startup", incident):
                await self.tables.open()
            if self.tables.subjects != {
                role: subject
                for subject, role in self.application.native_people.items()
            }:
                raise ValueError("installed native identity profile changed")
            await self.observations.capture(
                Actor("system"), "startup", incident, "succeeded", False
            )
        except BaseException:
            await self.tables.aclose()
            await self.observations.aclose()
            raise

    def app(self) -> Starlette:
        return create_app(
            self.host,
            self.identities,
            self.application.assets,
            origin=f"http://127.0.0.1:{self.settings.port}",
            max_body_bytes=self.settings.max_body_bytes,
        )

    def asgi(self) -> Starlette:
        return create_registry(
            ((self.application.listing, self.app()),),
            origin=f"http://127.0.0.1:{self.settings.port}",
        )

    async def serve(self) -> None:
        import uvicorn

        server = ReadyServer(
            uvicorn.Config(
                self.asgi(),
                host="127.0.0.1",
                port=self.settings.port,
                proxy_headers=False,
                access_log=False,
                log_level="warning",
            )
        )
        await server.serve()

    async def aclose(self) -> None:
        report = await self.host.aclose()
        if report.state != "closed":
            raise RuntimeError("local host still draining; resources retained")
        await self.tables.aclose()
        await self.observations.aclose()


__all__ = ["LocalApplication", "LocalRuntime", "LocalSettings"]
