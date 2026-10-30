"""Native local behavior: US-006-AC1/2/3/4, STO-01/02/03/04/05/07/10/13/15."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import replace
from pathlib import Path

import pytest
from batten.storage import Absent, Any, Digest, Matches, StorageError
from batten.storage.local import LocalProvider, create_store, initialize
from conftest import Grant, process_results


@pytest.mark.parametrize("body", [b"", b"Fabricated review", b"fabricated" * 1000])
async def test_roundtrip_and_reload(
    local: tuple[LocalProvider, Grant], body: bytes
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    written = await store.write("reviews/demo.txt", body)
    assert written.info.size_bytes == len(body)
    assert (await store.stat(written.info.key)).version == written.info.version
    async with store.open_read(written.info.key) as stream:
        assert b"".join([chunk async for chunk in stream]) == body
    await store.aclose()
    other = provider.bind(grant)
    assert (await other.stat(written.info.key)).version == written.info.version
    await provider.aclose()
    reloaded = create_store(provider.root, provider.limits)
    await reloaded.prepare()
    assert (await reloaded.bind(grant).stat(written.info.key)).size_bytes == len(body)
    assert (await reloaded.bind(grant).delete(written.info.key)).outcome == "deleted"
    assert (await reloaded.bind(grant).delete(written.info.key)).outcome == "absent"
    await reloaded.aclose()


async def test_authority_precedes_existence_and_continuation(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    await store.write("demo.txt", b"x" * 64)
    async with store.open_read("demo.txt") as stream:
        assert len(await anext(stream.__aiter__())) == 32
        grant.allowed = False
        with pytest.raises(StorageError, match="denied"):
            await anext(stream.__aiter__())
    for key in ["demo.txt", "missing.txt"]:
        with pytest.raises(StorageError, match="denied"):
            await store.stat(key)
    assert grant.events[-1][0] == "denied"
    grant.allowed = True
    grant.features = set()
    with pytest.raises(StorageError, match="denied"):
        await store.write("requires-create", b"not consumed")
    with pytest.raises(StorageError, match="denied"):
        async with store.open_read("demo.txt", offset=1):
            pass
    grant.features = {"read_range"}
    async with store.open_read("demo.txt", offset=1) as ranged:
        await anext(ranged.__aiter__())
        grant.features.clear()
        with pytest.raises(StorageError, match="denied"):
            await anext(ranged.__aiter__())


async def test_key_and_root_containment(
    local: tuple[LocalProvider, Grant], tmp_path: Path
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    for key in [
        "../escape",
        "/absolute",
        "a//b",
        "a\\b",
        "a:b",
        "a/",
        "a/./b",
        "a\x00b",
    ]:
        with pytest.raises(StorageError, match="invalid_key"):
            await store.write(key, b"forbidden")
    for key in ["Case", "case", "caf\u00e9", "cafe\u0301", "%2e%2e"]:
        await store.write(key, key.encode())
        async with store.open_read(key) as content:
            assert b"".join([part async for part in content]) == key.encode()
    external = tmp_path / "external"
    external.mkdir()
    (provider.root / "objects" / "d657363617065").symlink_to(external)
    with pytest.raises(StorageError):
        await store.write("escape/file", b"forbidden")
    assert list(external.iterdir()) == []
    unmanaged = tmp_path / "unmanaged"
    unmanaged.mkdir()
    (unmanaged / "keep").write_bytes(b"keep")
    with pytest.raises(StorageError):
        await initialize(unmanaged)
    assert (unmanaged / "keep").read_bytes() == b"keep"


@pytest.mark.parametrize("processes", [False, True])
async def test_conditional_competing_publication(
    local: tuple[LocalProvider, Grant], processes: bool
) -> None:
    provider, grant = local
    stores = [provider.bind(grant), provider.bind(grant)]
    original_body = b"original" * 16
    original = await stores[0].write("review", original_body)
    condition = Matches(original.info.version)
    async with stores[0].open_read("review", condition=condition) as old:
        before = await anext(old.__aiter__())
        if processes:
            outcomes = await asyncio.to_thread(
                process_results, provider.root, provider.limits, original.info.version
            )
        else:
            results = await asyncio.gather(
                *(
                    s.write("review", data, condition=condition)
                    for s, data in zip(stores, [b"first", b"second"])
                ),
                return_exceptions=True,
            )
            outcomes = [
                result.code if isinstance(result, StorageError) else "complete"
                for result in results
            ]
        assert sorted(outcomes) == ["complete", "precondition_failed"]
        assert before + b"".join([part async for part in old]) == original_body
    async with stores[0].open_read("review") as stream:
        assert b"".join([part async for part in stream]) in {b"first", b"second"}
    with pytest.raises(StorageError, match="precondition_failed"):
        await stores[0].write("review", b"overwrite", condition=Absent())
    with pytest.raises(StorageError, match="precondition_failed"):
        await stores[0].delete("review", condition=condition)
    await stores[0].write("review", b"explicit", condition=Any())


async def test_range_pinning_and_eof(local: tuple[LocalProvider, Grant]) -> None:
    provider, grant = local
    store = provider.bind(grant)
    info = (await store.write("binary", b"0123456789")).info
    async with store.open_read(
        "binary", offset=2, length=4, condition=Matches(info.version)
    ) as stream:
        assert b"".join([part async for part in stream]) == b"2345"
        assert stream.selection.length == 4
    async with store.open_read("binary", offset=10) as stream:
        assert [part async for part in stream] == []
    with pytest.raises(StorageError, match="range_not_satisfiable"):
        async with store.open_read("binary", offset=11):
            pass
    await store.write("binary", b"changed", condition=Any())
    with pytest.raises(StorageError, match="precondition_failed"):
        async with store.open_read("binary", condition=Matches(info.version)):
            pass


async def test_stream_integrity_and_partial_close(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    body = b"x" * 64
    digest = Digest("sha256", hashlib.sha256(body).hexdigest())
    receipt = await store.write("verified", body, expected_digest=digest)
    assert receipt.verification is not None and receipt.verification.scope == "source"
    async with store.open_read("verified", expected_digest=digest) as stream:
        assert b"".join([part async for part in stream]) == body
        assert (
            stream.verification is not None and stream.verification.scope == "delivered"
        )
    async with store.open_read("verified", expected_digest=digest) as stream:
        await anext(stream.__aiter__())
    assert stream.verification is None
    wrong = Digest("sha256", hashlib.sha256(b"wrong").hexdigest())
    with pytest.raises(StorageError, match="integrity_mismatch"):
        await store.write("bad", body, expected_digest=wrong)
    with pytest.raises(StorageError, match="not_found"):
        await store.stat("bad")
    with pytest.raises(StorageError, match="integrity_mismatch"):
        async with store.open_read("verified", expected_digest=wrong) as stream:
            [part async for part in stream]


async def test_transfer_limits_preserve_destination(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    bounded = create_store(provider.root, replace(provider.limits, max_object_bytes=3))
    await bounded.prepare()
    store = bounded.bind(grant)
    await store.write("small", b"old")
    with pytest.raises(StorageError, match="limit_exceeded"):
        await store.write("small", b"larger", condition=Any())
    async with store.open_read("small") as stream:
        assert b"".join([part async for part in stream]) == b"old"
    await bounded.aclose()


async def test_observation_failure_retains_possible_effect(
    local: tuple[LocalProvider, Grant],
) -> None:
    provider, grant = local
    store = provider.bind(grant)
    grant.sink_fails = True
    with pytest.raises(StorageError, match="unavailable") as failure:
        await store.write("observed", b"published")
    assert failure.value.effect == "unknown"
    grant.sink_fails = False
    assert (await store.stat("observed")).size_bytes == 9
