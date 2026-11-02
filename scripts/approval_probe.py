"""Installed application process setup; no business assertions live in fixtures."""

from __future__ import annotations

import asyncio
import json
import signal
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Browser, Page, expect


@dataclass
class AppProcess:
    root: Path
    data: Path
    config: Path
    url: str
    process: asyncio.subprocess.Process | None = None

    async def command(self, command: str, *args: str) -> str:
        process = await asyncio.create_subprocess_exec(
            str(self.root / ".cache/approval-runtime/bin/python"),
            "-I",
            "-m",
            "approval_desk.cli",
            command,
            "--data",
            str(self.data),
            "--config",
            str(self.config),
            *args,
            cwd=self.data.parent,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            async with asyncio.timeout(300):
                stdout, stderr = await process.communicate()
        finally:
            if process.returncode is None:
                process.send_signal(signal.SIGINT)
                await asyncio.shield(process.wait())
        if process.returncode:
            raise RuntimeError(stderr.decode())
        return stdout.decode()

    async def start(self) -> None:
        self.process = await asyncio.create_subprocess_exec(
            str(self.root / ".cache/approval-runtime/bin/python"),
            "-I",
            "-m",
            "approval_desk.cli",
            "serve",
            "--data",
            str(self.data),
            "--config",
            str(self.config),
            cwd=self.data.parent,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        if self.process.stdout is None:
            raise RuntimeError("missing process stream")
        lines: list[str] = []
        async with asyncio.timeout(90):
            while line := await self.process.stdout.readline():
                text = line.decode().strip()
                lines.append(text)
                if text.startswith("{") and json.loads(text).get("ready"):
                    return
        raise RuntimeError("\n".join(lines))

    async def stop(self) -> None:
        if self.process is not None and self.process.returncode is None:
            self.process.send_signal(signal.SIGINT)
            async with asyncio.timeout(45):
                await self.process.wait()


async def login_page(browser: Browser, url: str, actor: str) -> Page:
    page = await browser.new_page()
    await page.goto(url)
    await page.get_by_role("link", name="Open Approval desk", exact=True).click()
    await page.locator("#actor").select_option(actor)
    await expect(page.locator("#refresh")).to_be_enabled()
    return page


async def api(
    page: Page,
    operation: str,
    inputs: dict[str, str],
    *,
    key: str | None = None,
    phase: str = "invoke",
) -> dict[str, object]:
    return await page.evaluate(
        """async ({operation, inputs, key, phase}) => {
      const response = await fetch('./api/operations/' + operation, {method:'POST',
        headers:{'content-type':'application/json'}, body:JSON.stringify({inputs, ...(key ? {key} : {}), phase})});
      return {http:response.status, ...await response.json()};
    }""",
        {"operation": operation, "inputs": inputs, "key": key, "phase": phase},
    )
