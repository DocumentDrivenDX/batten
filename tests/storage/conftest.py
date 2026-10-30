"""Fabricated host bindings; no credentials, cloud services or runtime internals."""

from __future__ import annotations

import asyncio
import multiprocessing
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import fields
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from pathlib import Path

import pytest
import pytest_asyncio
from batten.storage import Limits, StorageError
from batten.storage.local import LocalProvider, create_store, initialize


class Grant:
    identity = "fabricated-actor/app/resource/profile"

    def __init__(self) -> None:
        self.allowed = True
        self.features: set[str] | None = None
        self.hidden: set[str] = set()
        self.sink_fails = False
        self.events: list[tuple[str, str, str]] = []

    async def check(self, operation: str, key: str, features: frozenset[str]) -> None:
        if (
            not self.allowed
            or key in self.hidden
            or self.features is not None
            and not features <= self.features
        ):
            raise StorageError("denied")

    async def observe(
        self,
        operation: str,
        code: str,
        effect: str,
        incident_id: str,
        metrics: Mapping[str, int | float | None],
    ) -> None:
        self.events.append((code, effect, incident_id))
        if self.sink_fails and code == "complete":
            raise RuntimeError("fabricated sink failure")


@pytest.fixture
def limits() -> Limits:
    values = {field.name: 4096 for field in fields(Limits)}
    values.update(
        max_object_bytes=65536,
        max_chunk_bytes=32,
        max_depth=8,
        max_page_items=2,
        max_scan_entries=4,
        max_active_transfers=4,
        max_active_uploads=4,
        max_parts=8,
        max_part_bytes=1024,
        max_parallel_parts=2,
        cursor_ttl_seconds=60,
        upload_ttl_seconds=60,
    )
    return Limits(**values)


@pytest_asyncio.fixture
async def local(
    tmp_path: Path, limits: Limits
) -> AsyncIterator[tuple[LocalProvider, Grant]]:
    root = tmp_path / "objects"
    await initialize(root)
    provider = create_store(root, limits)
    await provider.prepare()
    yield provider, Grant()
    await provider.aclose()


async def competing_write(
    root: Path, limits: Limits, version: str | None, body: bytes
) -> str:
    from batten.storage import Matches

    provider = create_store(root, limits)
    await provider.prepare()
    try:
        await provider.bind(Grant()).write("review", body, condition=Matches(version))
        return "complete"
    except StorageError as error:
        return error.code
    finally:
        await provider.aclose()


def process_writer(
    root: Path, limits: Limits, version: str | None, body: bytes, connection: Connection
) -> None:
    connection.send("ready")
    connection.recv()
    try:
        connection.send(asyncio.run(competing_write(root, limits, version, body)))
    finally:
        connection.close()


def process_results(root: Path, limits: Limits, version: str | None) -> list[str]:
    context = multiprocessing.get_context("fork")
    pairs = [context.Pipe() for _ in range(2)]
    processes = [
        context.Process(
            target=process_writer, args=(root, limits, version, body, pair[1])
        )
        for pair, body in zip(pairs, [b"first", b"second"])
    ]
    result: list[str] = []
    try:
        for process in processes:
            process.start()
        for parent, _child in pairs:
            if not parent.poll(30) or parent.recv() != "ready":
                raise TimeoutError("competing writer did not reach barrier")
        for parent, _child in pairs:
            parent.send("go")
        for parent, _child in pairs:
            if not parent.poll(30):
                raise TimeoutError("competing writer did not complete")
            result.append(str(parent.recv()))
    finally:
        close_processes(processes, pairs)
    return result


def close_processes(
    processes: Sequence[BaseProcess], pairs: list[tuple[Connection, Connection]]
) -> None:
    for process in processes:
        process.join(30)
        if process.is_alive():
            process.terminate()
            process.join()
    for parent, child in pairs:
        parent.close()
        child.close()
