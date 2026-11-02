"""Explicit local application directory; listing never grants app authority."""

from __future__ import annotations

import re
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from html import escape
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles


@dataclass(frozen=True)
class AppListing:
    slug: str
    title: str
    description: str
    thumbnail: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", self.slug):
            raise ValueError("invalid registered app slug")
        if (
            not 1 <= len(self.title.strip()) <= 80
            or not 1 <= len(self.description.strip()) <= 300
        ):
            raise ValueError("bounded app title and description required")
        if not re.fullmatch(
            r"[a-zA-Z0-9][a-zA-Z0-9_.-]*\.(png|jpg|webp|svg)", self.thumbnail
        ):
            raise ValueError("packaged thumbnail filename required")


def card(entry: AppListing) -> str:
    path = "/apps/" + entry.slug + "/"
    return (
        f'<a class="app-card" href="{path}" aria-label="Open {escape(entry.title, quote=True)}">'
        f'<div class="preview"><img src="{path}assets/{escape(entry.thumbnail, quote=True)}" alt="" width="640" height="360"></div>'
        '<div class="card-body"><span class="category">APPLICATION</span>'
        f'<h2>{escape(entry.title)}<span aria-hidden="true">↗</span></h2>'
        f'<p>{escape(entry.description)}</p><span class="open">Open app <span aria-hidden="true">→</span></span></div></a>'
    )


def registry_app(entries: tuple[tuple[AppListing, Starlette], ...]) -> Starlette:
    if len({entry.slug for entry, _ in entries}) != len(entries):
        raise ValueError("duplicate registered app slug")
    cards = "".join(card(entry) for entry, _ in entries)
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Applications · Batten</title><link rel="stylesheet" href="/_batten/registry.css"></head>'
        '<body><header><a class="brand" href="/" aria-label="Batten application registry">'
        '<span aria-hidden="true">▥</span> batten</a><span class="workspace">● Local workspace</span></header>'
        '<main><p class="eyebrow">YOUR LOCAL WORKSPACE</p><h1>Small apps. Useful work.</h1>'
        '<p class="intro">A place for the tools that move a little work forward.<br>Choose an application to get started.</p>'
        f'<div class="section-heading"><h2>Applications</h2><span>{len(entries)} registered</span></div>'
        f'<section class="apps" aria-label="Registered applications">{cards}</section>'
        "<footer>Batten · Local application registry</footer></main></body></html>"
    )

    async def index(request: Request) -> HTMLResponse:
        return HTMLResponse(page)

    @asynccontextmanager
    async def lifetime(app: Starlette) -> AsyncGenerator[None, None]:
        async with AsyncExitStack() as stack:
            for _entry, child in entries:
                await stack.enter_async_context(child.router.lifespan_context(child))
            yield

    return Starlette(
        lifespan=lifetime,
        routes=[
            Route("/", index),
            Mount(
                "/_batten",
                StaticFiles(
                    directory=Path(__file__).with_name("assets"), check_dir=False
                ),
            ),
            *[Mount("/apps/" + entry.slug, app=child) for entry, child in entries],
        ],
    )
