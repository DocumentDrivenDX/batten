"""Fresh installed native application and browser process setup."""

from __future__ import annotations

import socket
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from approval_probe import AppProcess
from playwright.async_api import Browser, async_playwright


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def installed_app(
    tmp_path_factory: pytest.TempPathFactory,
) -> AsyncGenerator[tuple[AppProcess, Browser], None]:
    tmp_path = tmp_path_factory.mktemp("approval")
    root = Path(__file__).resolve().parents[2]
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    config = tmp_path / "local.toml"
    config.write_text(
        (root / "examples/approval-desk/local.toml")
        .read_text()
        .replace("port = 8820", f"port = {port}")
    )
    app = AppProcess(root, tmp_path / "data", config, f"http://127.0.0.1:{port}")
    await app.command("init")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            await app.start()
            yield app, browser
        finally:
            await browser.close()
            await app.stop()
