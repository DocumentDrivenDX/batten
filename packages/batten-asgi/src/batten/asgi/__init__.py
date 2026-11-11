"""Optional loopback operation transport; no database or provider imports."""

from __future__ import annotations

import json
from pathlib import Path

from batten.runtime import Host
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles

from ._identities import LocalIdentities
from ._ports import LocalSessions
from ._registry import AppListing, registry_app
from ._routes import Routes
from .new_operations import (
    OperationIngress,
    operation_route,
)


def create_app(
    host: Host,
    sessions: LocalSessions,
    assets: Path,
    *,
    origin: str,
    max_body_bytes: int,
    additional_routes: tuple[BaseRoute, ...] = (),
    api_digest: str | None = None,
) -> Starlette:
    if not origin.startswith("http://127.0.0.1:") or max_body_bytes < 1:
        raise ValueError("explicit loopback origin and request bound required")
    routes = Routes(host, sessions, assets, max_body_bytes, api_digest=api_digest)
    app = Starlette(
        lifespan=routes.lifetime,
        routes=[
            Route("/", routes.index),
            Route("/api/session", routes.session),
            Route("/api/local-session", routes.login, methods=["POST"]),
            Route("/api/logout", routes.logout, methods=["POST"]),
            Route("/api/operations/{operation}", routes.invoke, methods=["POST"]),
            *additional_routes,
            Mount("/assets", StaticFiles(directory=assets, check_dir=False)),
        ],
    )
    return guarded(app, origin)


def create_registry(
    entries: tuple[tuple[AppListing, Starlette], ...], *, origin: str
) -> Starlette:
    if not origin.startswith("http://127.0.0.1:"):
        raise ValueError("explicit loopback origin required")
    return guarded(registry_app(entries), origin)


def guarded(app: Starlette, origin: str) -> Starlette:

    async def guard(request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.client is None or request.client.host not in {"127.0.0.1", "::1"}:
            return JSONResponse({"code": "denied"}, status_code=403)
        if request.headers.get("host") != origin.removeprefix("http://"):
            return JSONResponse({"code": "denied"}, status_code=403)
        if request.method != "GET" and request.headers.get("origin") != origin:
            return JSONResponse({"code": "denied"}, status_code=403)
        try:
            response = await call_next(request)
        except (ValueError, json.JSONDecodeError):
            response = JSONResponse({"status": "invalid"}, status_code=400)
        response.headers["content-security-policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        response.headers["cache-control"] = "no-store"
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["referrer-policy"] = "no-referrer"
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=guard)
    return app


__all__ = [
    "AppListing",
    "LocalIdentities",
    "LocalSessions",
    "OperationIngress",
    "create_app",
    "create_registry",
    "operation_route",
]
