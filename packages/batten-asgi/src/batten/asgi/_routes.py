"""Request parsing and public operation endpoints."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from batten.runtime import Host
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from ._ports import LocalSessions
from .new_operations import OperationIngress, read_json_object


class Routes:
    def __init__(
        self,
        host: Host,
        sessions: LocalSessions,
        assets: Path,
        max_body_bytes: int,
        *,
        api_digest: str | None = None,
    ):
        self.host, self.sessions, self.assets, self.max_body_bytes = (
            host,
            sessions,
            assets,
            max_body_bytes,
        )

        async def resolve_actor(request: Request):
            return sessions.resolve(request.cookies.get("batten_local"))

        self.operations = OperationIngress(
            host,
            resolve_actor=resolve_actor,
            allowed_operations=tuple(
                operation_id
                for operation_id, operation in host.operations.items()
                if not operation.selection_kinds
            ),
            max_request_bytes=max_body_bytes,
            max_response_bytes=max_body_bytes,
            api_digest=api_digest,
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
        value = await read_json_object(request, self.max_body_bytes)
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
        return await self.operations.invoke(request)
