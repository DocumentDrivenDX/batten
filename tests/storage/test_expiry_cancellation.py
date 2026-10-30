"""Native lifecycle boundaries using controlled clocks/events, never sleeps."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator

import pytest
from batten.storage import StorageError
from batten.storage.local import LocalProvider
from conftest import Grant


async def test_upload_and_cursor_expiry(
    local: tuple[LocalProvider, Grant], monkeypatch: pytest.MonkeyPatch
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    session = await store.begin_upload("expires")
    await store.write_part(session.upload, 1, b"expiry staging")
    await store.write("one", b"1")
    await store.write("two", b"2")
    page = await store.list(limit=1)
    assert page.next_cursor is not None
    wall, monotonic = time.time(), time.monotonic()
    monkeypatch.setattr(
        time, "time", lambda: wall + provider.limits.upload_ttl_seconds + 1
    )
    monkeypatch.setattr(
        time, "monotonic", lambda: monotonic + provider.limits.cursor_ttl_seconds + 1
    )
    assert (await store.upload_status(session.upload)).state == "expired"
    with pytest.raises(StorageError, match="upload_expired"):
        await store.write_part(session.upload, 1, b"too late")
    with pytest.raises(StorageError, match="cursor_expired"):
        await store.list(limit=1, cursor=page.next_cursor)
    fresh = await store.begin_upload("fresh")
    assert fresh.state == "open"
    assert len(list((provider.root / "blobs").iterdir())) == 2


async def test_cancellation_closes_staging_without_publishing(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    started = asyncio.Event()
    hold = asyncio.Event()

    async def source() -> AsyncIterator[bytes]:
        yield b"partial"
        started.set()
        await hold.wait()
        yield b"rest"

    transfer = asyncio.create_task(store.write("cancelled", source()))
    await started.wait()
    transfer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await transfer
    with pytest.raises(StorageError, match="not_found"):
        await store.stat("cancelled")
    assert any(code == "cancelled" for code, _effect, _incident in grant.events)
    assert list((provider.root / "blobs").iterdir()) == []

    started.clear()
    session = await store.begin_upload("abort-active")
    transfer = asyncio.create_task(store.write_part(session.upload, 1, source()))
    await started.wait()
    assert (await store.abort_upload(session.upload)).outcome == "unknown"
    hold.set()
    with pytest.raises(StorageError, match="upload_conflict"):
        await transfer
    assert (await store.upload_status(session.upload)).state == "aborted"
    assert list((provider.root / "blobs").iterdir()) == []
