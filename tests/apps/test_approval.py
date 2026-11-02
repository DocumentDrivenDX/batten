"""Real browser and native storage evidence for the first bounded local cohort."""

from __future__ import annotations

import json
import uuid
from typing import Any, cast

import pytest
from approval_probe import AppProcess, api, login_page
from playwright.async_api import Browser, Route, expect

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="module")]


async def test_approval_desk_native_browser_journey(
    installed_app: tuple[AppProcess, Browser],
) -> None:
    """@covers US-101-AC1 @covers US-101-AC2 @covers US-101-AC3
    @covers US-101-AC4 @covers US-101-AC5
    """
    app, browser = installed_app
    alex, blake, casey = [
        await login_page(browser, app.url, actor)
        for actor in ("alex", "blake", "casey")
    ]
    await expect(alex.locator("#empty")).to_be_visible()
    await alex.locator("#title").fill("Fabricated equipment request")
    await alex.locator("#submit").click()
    await expect(alex.locator("#requests strong")).to_have_text(
        "Fabricated equipment request"
    )
    await blake.locator("#refresh").click()
    await expect(blake.get_by_role("button", name="Approve request")).to_be_visible()
    await alex.locator("#edit-title").fill("Fabricated revised equipment request")
    await alex.get_by_role("button", name="Save changes").click()
    await expect(alex.locator("#requests strong")).to_have_text(
        "Fabricated revised equipment request"
    )
    await blake.get_by_role("button", name="Approve request").click()
    await expect(blake.locator("#notice")).to_contain_text("changed")
    await blake.locator("#refresh").click()
    await expect(blake.get_by_role("button", name="Approve request")).to_be_enabled()
    await blake.get_by_role("button", name="Approve request").click()
    await expect(blake.locator("#detail")).to_contain_text("Approved")
    final: Any = (await api(blake, "list", {}))["result"]
    assert [
        (row["owner"], row["state"], row["decided_by"], row["title"])
        for row in final["rows"]
    ] == [("alex", "approved", "blake", "Fabricated revised equipment request")]
    assert (await api(casey, "get", {"id": final["rows"][0]["id"]}))["result"] == {
        "rows": [],
        "cursor": None,
    }
    await alex.locator("#title").fill("Fabricated response loss")
    await alex.route("**/apps/approval-desk/api/operations/submit", lose_response)
    await alex.locator("#submit").click()
    await expect(alex.locator("#notice")).to_contain_text("response was lost")
    await alex.unroute("**/apps/approval-desk/api/operations/submit", lose_response)
    await alex.locator("#observe").click()
    await expect(alex.locator("#requests strong")).to_have_count(2)
    await expect(alex.locator("#observe")).to_be_hidden()
    assert (await api(casey, "list", {}))["result"] == {"rows": [], "cursor": None}
    assert (
        await api(
            blake,
            "submit",
            {"title": "Fabricated reviewer request"},
            key=uuid.uuid4().hex,
        )
    )["status"] == "succeeded"
    reviewer: Any = next(
        row
        for row in cast(
            dict[str, list[dict[str, str]]], (await api(blake, "list", {}))["result"]
        )["rows"]
        if row["owner"] == "blake"
    )
    for page, operation, inputs, expected in [
        (
            blake,
            "decide",
            {
                "id": reviewer["id"],
                "revision": reviewer["revision"],
                "decision": "approved",
            },
            "precondition_failed",
        ),
        (
            alex,
            "decide",
            {
                "id": final["rows"][0]["id"],
                "revision": final["rows"][0]["revision"],
                "decision": "approved",
            },
            "denied",
        ),
        (alex, "unknown", {}, "denied"),
        (
            alex,
            "submit",
            {"title": "Fabricated impersonation", "actor": "blake"},
            "invalid",
        ),
    ]:
        assert (await api(page, operation, inputs, key=uuid.uuid4().hex))[
            "status"
        ] == expected
    await app.stop()
    assert (
        (
            cli := json.loads(
                await app.command("call", "--actor", "blake", "--operation", "list")
            )
        )["status"]
        == "succeeded"
        and len(cli["result"]["rows"]) == 3
        and next(row for row in cli["result"]["rows"] if row["owner"] == "blake")[
            "state"
        ]
        == "pending"
    )
    await app.start()
    assert (await api(alex, "list", {}))["status"] == "denied"
    captures = "".join(
        (app.data / name).read_text() for name in ("audit.jsonl", "spans.jsonl")
    )
    assert (
        all(
            private not in captures
            for private in ("Fabricated", "postgresql://", "SELECT ")
        )
        and (
            spans := [
                json.loads(line)
                for line in (app.data / "spans.jsonl").read_text().splitlines()
            ]
        )
        and any(span["name"] == "database" for span in spans)
        and all(
            any(
                parent["name"] == "operation"
                and parent["span_id"] == span["parent_id"]
                and parent["trace_id"] == span["trace_id"]
                for parent in spans
            )
            for span in spans
            if span["name"] == "database"
        )
    )


async def test_registry_lists_visual_apps_and_brand_returns_home(
    installed_app: tuple[AppProcess, Browser],
) -> None:
    """@covers US-101-AC6: explicit local directory, app routing and session scope."""
    app, browser = installed_app
    page = await browser.new_page()
    await page.goto(app.url)
    card = page.get_by_role("link", name="Open Approval desk", exact=True)
    await expect(card).to_contain_text("independent decision")
    assert await card.locator("img").evaluate(
        "image => image.complete && image.naturalWidth > 0"
    )
    await card.click()
    await expect(page).to_have_url(app.url + "/apps/approval-desk/")
    await page.locator("#actor").select_option("alex")
    await expect(page.locator("#submit")).to_be_enabled()
    assert {
        cookie.get("path")
        for cookie in await page.context.cookies()
        if cookie.get("name") == "batten_local"
    } == {"/apps/approval-desk/api"}
    await page.get_by_role("link", name="Batten application registry").click()
    await expect(page).to_have_url(app.url + "/")
    await expect(
        page.get_by_role("heading", name="Applications", exact=True)
    ).to_be_visible()
    assert [
        (await page.request.get(app.url + path)).status
        for path in ("/apps/unregistered/", "/api/session")
    ] == [404, 404]
    await page.close()


async def lose_response(route: Route) -> None:
    await route.fetch()
    await route.abort("failed")
