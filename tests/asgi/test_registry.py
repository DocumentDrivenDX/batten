"""App registry: listing, routing and the loopback/origin guard."""

from __future__ import annotations

import pytest
from batten.asgi import AppListing, create_registry
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

ORIGIN = "http://127.0.0.1:8820"
LOOPBACK = ("127.0.0.1", 50000)


def listing(slug: str, title: str = "Title") -> AppListing:
    return AppListing(slug, title, "A fabricated app.", "thumb.svg")


def child(text: str) -> Starlette:
    async def home(request: Request) -> PlainTextResponse:
        return PlainTextResponse(text)

    async def post(request: Request) -> PlainTextResponse:
        return PlainTextResponse("posted")

    return Starlette(routes=[Route("/", home), Route("/post", post, methods=["POST"])])


def registry() -> Starlette:
    return create_registry(
        (
            (listing("alpha", "Alpha <desk>"), child("alpha home")),
            (listing("beta", "Beta"), child("beta home")),
        ),
        origin=ORIGIN,
    )


def client(app: Starlette, *, host: str = "127.0.0.1:8820") -> TestClient:
    return TestClient(app, base_url="http://" + host, client=LOOPBACK)


def test_index_lists_every_app_and_escapes_titles() -> None:
    with client(registry()) as http:
        page = http.get("/")
    assert page.status_code == 200
    assert "2 registered" in page.text
    assert 'href="/apps/alpha/"' in page.text and 'href="/apps/beta/"' in page.text
    assert "Alpha &lt;desk&gt;" in page.text and "<desk>" not in page.text


def test_each_app_is_mounted_under_its_slug_and_the_stylesheet_is_served() -> None:
    with client(registry()) as http:
        assert http.get("/apps/alpha/").text == "alpha home"
        assert http.get("/apps/beta/").text == "beta home"
        assert http.get("/apps/gamma/").status_code == 404
        assert http.get("/_batten/registry.css").status_code == 200


def test_responses_carry_security_headers() -> None:
    with client(registry()) as http:
        headers = http.get("/").headers
    assert "default-src 'self'" in headers["content-security-policy"]
    assert headers["cache-control"] == "no-store"
    assert headers["x-content-type-options"] == "nosniff"


def test_cross_origin_and_missing_origin_posts_are_refused() -> None:
    with client(registry()) as http:
        assert http.post("/apps/alpha/post").status_code == 403
        bad = http.post("/apps/alpha/post", headers={"origin": "http://evil.example"})
        assert bad.status_code == 403
        good = http.post("/apps/alpha/post", headers={"origin": ORIGIN})
        assert (good.status_code, good.text) == (200, "posted")


def test_wrong_host_header_and_non_loopback_peer_are_refused() -> None:
    with client(registry(), host="localhost:8820") as http:
        assert http.get("/").status_code == 403
    remote = TestClient(registry(), base_url=ORIGIN, client=("10.0.0.5", 1))
    with remote as http:
        assert http.get("/").status_code == 403


def test_duplicate_slugs_and_non_loopback_origin_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        create_registry(
            ((listing("a"), child("x")), (listing("a"), child("y"))), origin=ORIGIN
        )
    with pytest.raises(ValueError, match="loopback"):
        create_registry((), origin="http://example.com")


@pytest.mark.parametrize(
    ("slug", "title", "description", "thumbnail"),
    [
        ("Bad Slug", "t", "d", "a.svg"),
        ("ok", "", "d", "a.svg"),
        ("ok", "t" * 81, "d", "a.svg"),
        ("ok", "t", "d" * 301, "a.svg"),
        ("ok", "t", "d", "../escape.svg"),
        ("ok", "t", "d", "thumb.exe"),
    ],
)
def test_invalid_listings_are_rejected(
    slug: str, title: str, description: str, thumbnail: str
) -> None:
    with pytest.raises(ValueError):
        AppListing(slug, title, description, thumbnail)
