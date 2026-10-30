"""US-006-AC5/6: listing continuation and upload lifecycle whole outcomes."""

from __future__ import annotations

import pytest
from batten.storage import Any, Matches, StorageError
from batten.storage.local import LocalProvider, create_store
from conftest import Grant


async def test_listing_projection_and_progress(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    for key in ["a", "b", "folder/c", "folder/deep/d"]:
        await store.write(key, b"fabricated")
    cursor = None
    keys: list[str] = []
    prefixes: list[str] = []
    while True:
        page = await store.list(limit=2, cursor=cursor)
        keys.extend(item.key for item in page.items)
        prefixes.extend(page.common_prefixes)
        assert len(page.items) + len(page.common_prefixes) <= 2
        cursor = page.next_cursor
        if cursor is None:
            break
    assert sorted(keys) == ["a", "b"] and prefixes == ["folder/"]
    page = await store.list(prefix="folder/", recursive=True, detail="basic", limit=2)
    assert sorted(item.key for item in page.items) == ["folder/c", "folder/deep/d"]
    assert all(getattr(item, "size_bytes", None) is None for item in page.items)
    assert page.common_prefixes == ()


async def test_listing_scope_and_cursor_binding(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    for key in ["a", "b", "c"]:
        await store.write(key, b"fabricated")
    grant.hidden.add("b")
    page = await store.list(limit=1)
    assert page.next_cursor is not None
    with pytest.raises(StorageError, match="cursor_invalid"):
        await store.list(limit=2, cursor=page.next_cursor)
    stranger = Grant()
    stranger.identity = "other-fabricated-actor"
    with pytest.raises(StorageError, match="cursor_invalid"):
        await provider.bind(stranger).list(limit=1, cursor=page.next_cursor)
    found = [item.key for item in page.items]
    while page.next_cursor is not None:
        page = await store.list(limit=1, cursor=page.next_cursor)
        found.extend(item.key for item in page.items)
    assert sorted(found) == ["a", "c"]


async def test_upload_manifest_and_completion_condition(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    upload = await store.begin_upload("assembled")
    second = await store.write_part(upload.upload, 2, b"world")
    first = await store.write_part(upload.upload, 1, b"hello ")
    with pytest.raises(StorageError, match="upload_conflict"):
        await store.complete_upload(upload.upload, [second, first])
    parts = await store.list_parts(upload.upload, limit=2)
    assert [item.part_number for item in parts.items] == [1, 2]
    done = await store.complete_upload(upload.upload, [first, second])
    assert (await store.complete_upload(upload.upload, [first, second])) == done
    assert (await store.abort_upload(upload.upload)).outcome == "already_complete"
    async with store.open_read("assembled") as stream:
        assert b"".join([part async for part in stream]) == b"hello world"
    conflicting = await store.begin_upload(
        "assembled", condition=Matches(done.info.version)
    )
    part = await store.write_part(conflicting.upload, 1, b"stale")
    await store.write("assembled", b"new", condition=Any())
    with pytest.raises(StorageError, match="precondition_failed"):
        await store.complete_upload(conflicting.upload, [part])
    assert (await store.abort_upload(conflicting.upload)).outcome == "aborted"


async def test_upload_reattachment_restart_and_stale_parts(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    session = await store.begin_upload("resume")
    old = await store.write_part(session.upload, 1, b"old")
    current = await store.write_part(session.upload, 1, b"current")
    with pytest.raises(StorageError, match="upload_conflict"):
        await store.complete_upload(session.upload, [old])
    await store.aclose()
    await provider.aclose()
    restarted = create_store(provider.root, provider.limits)
    await restarted.prepare()
    rebound = restarted.bind(grant)
    assert (await rebound.upload_status(session.upload)).state == "open"
    receipt = await rebound.complete_upload(session.upload, [current])
    assert receipt.info.size_bytes == 7
    await restarted.aclose()


async def test_closed_handle_preserves_borrower_and_data(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    closed, borrower = provider.bind(grant), provider.bind(grant)
    await closed.write("keep", b"retained")
    await closed.aclose()
    with pytest.raises(StorageError, match="denied"):
        await closed.stat("keep")
    assert (await borrower.stat("keep")).size_bytes == 8
    session = await borrower.begin_upload("unpublished")
    await borrower.write_part(session.upload, 1, b"private")
    assert [item.key for item in (await borrower.list(limit=2)).items] == ["keep"]
    await borrower.abort_upload(session.upload)
    assert (await borrower.upload_status(session.upload)).state == "aborted"
    grant.features = {"multipart_upload", "create_only"}
    transient = await borrower.begin_upload("transient")
    await borrower.write_part(transient.upload, 1, b"temporary")
    await borrower.aclose()
    assert len(list((provider.root / "blobs").iterdir())) == 1
    with pytest.raises(StorageError, match="denied"):
        await provider.bind(grant).upload_status(transient.upload)
