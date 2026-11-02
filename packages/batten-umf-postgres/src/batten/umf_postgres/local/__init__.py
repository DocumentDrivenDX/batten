"""Local-only resource composition; ordinary startup never deploys schema."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, TypeVar, cast

import psycopg
from batten.contracts import Identity
from batten.umf_postgres import NativeBinding, UmfTableProvider, create_umf_provider
from opentelemetry.trace import TracerProvider
from pgserver.postgres_server import get_server
from umf_access.unified import (
    AsyncSession,
    NativeTableBinding,
    SessionIdentity,
    SessionPolicy,
    observe_table_head_async,
)

from ._deployment import initialize as initialize_sync

_T = TypeVar("_T")


async def settled(work: Callable[[], _T]) -> _T:
    task = asyncio.create_task(asyncio.to_thread(work))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        await asyncio.shield(task)
        raise


async def initialize(
    data: Path,
    model: Path,
    configuration: dict[str, object],
    people: dict[str, str],
    memberships: dict[str, list[str]],
) -> None:
    await settled(
        lambda: initialize_sync(data, model, configuration, people, memberships)
    )


class LocalTables:
    def __init__(
        self,
        data: Path,
        model: Path,
        authority: Identity,
        tracer_provider: TracerProvider | None = None,
    ):
        self.data, self.model, self.tracer_provider = data, model, tracer_provider
        self.server: Any = None
        self._uri = ""
        self._session: AsyncSession | None = None
        self.metadata: dict[str, Any] = {}
        self.provider = create_umf_provider(self._native, authority)

    async def open(self) -> None:
        await settled(self._open)
        await self.provider.prepare()
        if self._session is None:
            raise RuntimeError("native session was not prepared")
        await observe_table_head_async(
            self._session,
            SessionIdentity("person", next(iter(self.metadata["people"]))),
            self.metadata["bundle"],
            self.metadata["reference"],
        )

    def _open(self) -> None:
        if not (self.data / "pgdata/PG_VERSION").is_file():
            raise ValueError("explicit local initialization required")
        self.metadata = json.loads((self.data / "deployment.json").read_text())
        digest = hashlib.sha256(self.model.read_bytes()).hexdigest()
        if digest != self.metadata["bundle"]["sourceDigest"]:
            raise ValueError("installed model differs; startup never migrates")
        self.server = get_server(self.data / "pgdata", cleanup_mode="stop")
        self._uri = self.server.get_uri()

    @asynccontextmanager
    async def _connection(self, identity: SessionIdentity) -> AsyncGenerator[Any, None]:
        connection = await psycopg.AsyncConnection.connect(
            self._uri,
            application_name="batten."
            + self.metadata["bundle"]["configuration"]["module"]
            + "."
            + identity.subject,
        )
        try:
            if self.tracer_provider is not None:
                from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor

                connection = PsycopgInstrumentor.instrument_connection(
                    connection, tracer_provider=self.tracer_provider
                )
            yield connection
        finally:
            await connection.close()

    def _native(self) -> NativeBinding:
        metadata = self.metadata
        settings = SessionPolicy(
            metadata["people"],
            {},
            metadata["bundle"]["configuration"]["schema"],
            catalog_only=True,
        )
        session = AsyncSession(self._connection, settings)
        self._session = session
        material = (self.data / "host-material.bin").read_bytes()
        if len(material) != 64:
            raise ValueError("invalid local host material")
        return cast(
            NativeBinding,
            NativeTableBinding(
                session,
                metadata["bundle"],
                metadata["reference"],
                metadata["binding"],
                cursor_secret=material[:32],
                outcome_secret=material[32:],
            ),
        )

    @property
    def subjects(self) -> dict[str, str]:
        return {role: subject for subject, role in self.metadata["people"].items()}

    async def aclose(self) -> None:
        await self.provider.aclose()
        if self.server is not None:
            await settled(self.server.cleanup)
            self.server = None


__all__ = ["LocalTables", "UmfTableProvider", "initialize"]
