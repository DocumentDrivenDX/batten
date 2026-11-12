"""LocalRuntime against a real pgserver cluster (nightly)."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest
from approval_desk.cli import application
from batten.contracts import OperationCall
from batten.hosting.local import LocalRuntime, LocalSettings

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "examples/approval-desk/model/approval.umf.json"


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def runtime(tmp_path: Path) -> LocalRuntime:
    assets = tmp_path / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "index.html").write_text("<h1>app</h1>")
    (assets / "thumbnail.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    settings = LocalSettings(tmp_path / "data", free_port(), 4, 60.0, 16384, 16, 600.0)
    return LocalRuntime(application(MODEL, assets), settings)


async def test_initialize_open_call_and_close(tmp_path: Path) -> None:
    local = runtime(tmp_path)
    await local.initialize()
    assert (tmp_path / "data/deployment.json").is_file()
    await local.open()
    try:
        await local.host.start()
        assert await local.host.admit(local.application.artifact)
        cookie = local.identities.login("alex")
        actor = local.identities.resolve(cookie)
        assert actor is not None
        outcome = await local.host.invoke(OperationCall("list", {}, actor))
        assert outcome.status == "succeeded"
    finally:
        await local.aclose()
    assert await local.host.readiness() == "closed"


async def test_reinitializing_an_existing_data_directory_is_refused(
    tmp_path: Path,
) -> None:
    (tmp_path / "data").mkdir()
    with pytest.raises(ValueError, match="already exists"):
        await runtime(tmp_path).initialize()
