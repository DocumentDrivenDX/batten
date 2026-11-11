"""Request parsing and public operation endpoints."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import cast

from batten.contracts import OperationCall
from batten.runtime import Host
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from ._ports import LocalSessions


async def body(request: Request, maximum: int) -> dict[str, object]:
    if (
        request.headers.get("content-type", "").split(";")[0].strip().lower()
        != "application/json"
    ):
        raise ValueError("JSON required")
    chunks = bytearray()
    async for chunk in request.stream():
        if len(chunks) + len(chunk) > maximum:
            raise ValueError("request too large")
        chunks.extend(chunk)
    value: object = json.loads(chunks)
    if not isinstance(value, dict):
        raise ValueError("object required")
    return cast(dict[str, object], value)


class Routes:
    def __init__(
        self, host: Host, sessions: LocalSessions, assets: Path, max_body_bytes: int
    ):
        self.host, self.sessions, self.assets, self.max_body_bytes = (
            host,
            sessions,
            assets,
            max_body_bytes,
        )

    @asynccontextmanager
    async def lifetime(self, app: Starlette) -> AsyncGenerator[None, None]:
        async with self.host:
            if not await self.host.admit(self.host.config.artifact):
                raise RuntimeError("app admission refused")
            yield

    async def index(self, request: Request) -> Response:
        return FileResponse(self.assets / "index.html")

    async def session(self, request: Request) -> Response:
        actor = self.sessions.resolve(request.cookies.get("batten_local"))
        return JSONResponse({
            "actor": dict(self.sessions.profile(actor)) if actor else None
        })

    async def login(self, request: Request) -> Response:
        value = await body(request, self.max_body_bytes)
        if set(value) != {"actor"} or not isinstance(value["actor"], str):
            return JSONResponse({"code": "invalid"}, status_code=400)
        self.sessions.logout(request.cookies.get("batten_local"))
        cookie = self.sessions.login(value["actor"])
        if cookie is None:
            return JSONResponse({"code": "denied"}, status_code=403)
        response = JSONResponse({"status": "succeeded"})
        response.set_cookie(
            "batten_local",
            cookie,
            httponly=True,
            samesite="strict",
            path=str(request.scope.get("root_path", "")) + "/api",
        )
        return response

    async def logout(self, request: Request) -> Response:
        self.sessions.logout(request.cookies.get("batten_local"))
        response = JSONResponse({"status": "succeeded"})
        response.delete_cookie(
            "batten_local", path=str(request.scope.get("root_path", "")) + "/api"
        )
        return response

    async def invoke(self, request: Request) -> Response:
        actor = self.sessions.resolve(request.cookies.get("batten_local"))
        if actor is None:
            return JSONResponse({"status": "denied", "code": "denied"}, status_code=403)
        value = await body(request, self.max_body_bytes)
        if not {"inputs"} <= set(value) <= {"inputs", "key", "phase"} or not isinstance(
            value["inputs"], dict
        ):
            return JSONResponse({"status": "invalid"}, status_code=400)
        key, phase = (value.get("key"), value.get("phase", "invoke"))
        if (
            key is not None
            and (not isinstance(key, str))
            or not isinstance(phase, str)
            or phase not in {"invoke", "observe"}
        ):
            return JSONResponse({"status": "invalid"}, status_code=400)
        call = OperationCall(
            request.path_params["operation"],
            cast(dict[str, object], value["inputs"]),
            actor,
            key,
            phase,
        )
        outcome = await self.host.invoke(call)
        codes = {
            "denied": 403,
            "invalid": 400,
            "precondition_failed": 409,
            "unavailable": 503,
            "uncertain": 202,
        }
        return JSONResponse(asdict(outcome), status_code=codes.get(outcome.status, 200))
