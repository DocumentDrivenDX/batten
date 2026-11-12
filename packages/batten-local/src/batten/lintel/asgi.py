"""Host-owned ASGI scope custody for an independently mounted Lintel router."""

from __future__ import annotations

import asyncio
import math
import uuid
from collections.abc import Awaitable, Callable, Mapping
from typing import cast

from batten.contracts import Actor, ExecutionScope, ShutdownReport
from batten.runtime import Host
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from lintel.ports import ExecutionError, RequestScope

from ._response import BufferedResponse


class HostScopeIngress:
    def __init__(
        self,
        host: Host,
        *,
        api_digest: str,
        resolve_actor: Callable[[Request], Awaitable[Actor | None]],
        max_response_bytes: int,
        close_scope: Callable[[ExecutionScope], Awaitable[ShutdownReport]]
        | None = None,
    ):
        if (
            not api_digest
            or type(max_response_bytes) is not int
            or max_response_bytes < 1
        ):
            raise ValueError("explicit API and response bound required")
        self.host, self.api_digest = host, api_digest
        self.resolve_actor, self.maximum = resolve_actor, max_response_bytes
        self.close_scope = close_scope
        self._state_key = "batten.lintel." + uuid.uuid4().hex

    async def resolve_context(self, request: object, api_digest: str) -> RequestScope:
        if not isinstance(request, Request) or api_digest != self.api_digest:
            raise ExecutionError("API_MISMATCH")
        state: object = request.scope.get("state")
        authority: object = (
            cast(Mapping[str, object], state).get(self._state_key)
            if isinstance(state, Mapping)
            else None
        )
        if (
            type(authority) is not ExecutionScope
            or not self.host.scope_active(authority)
            or authority.api_digest != self.api_digest
            or authority.consistency != "request-snapshot-1"
        ):
            raise ExecutionError("API_MISMATCH")
        return RequestScope(
            authority.application.id,
            self.api_digest,
            "query",
            authority,
            authority.request_id,
            authority.deadline_monotonic,
        )

    def wrap(self, app: ASGIApp) -> ASGIApp:
        return _ScopedApp(self, app, self._state_key)


async def _error(
    code: str, scope: Scope, receive: Receive, send: Send, status: int = 503
) -> None:
    await JSONResponse(
        {"errors": [{"message": code, "extensions": {"code": code}}]},
        status_code=status,
    )(scope, receive, send)


class _ScopedApp:
    def __init__(self, ingress: HostScopeIngress, app: ASGIApp, state_key: str):
        self.ingress, self.app = ingress, app
        self._state_key = state_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            await self._http(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _http(self, scope: Scope, receive: Receive, send: Send) -> None:
        owner = self.ingress
        deadline = owner.host.services.monotonic() + owner.host.config.timeout_seconds
        authority: ExecutionScope | None = None
        response = BufferedResponse(owner.maximum)
        failure: str | None = None
        try:
            if not math.isfinite(deadline):
                raise ValueError("invalid request deadline")
            async with asyncio.timeout(owner.host.config.timeout_seconds):
                actor = await owner.resolve_actor(Request(scope, receive))
            if actor is None:
                await _error("DENIED", scope, receive, send, 401)
                return
            authority = await owner.host.open_scope(
                actor,
                uuid.uuid4().hex,
                deadline_monotonic=deadline,
                api_digest=owner.api_digest,
                consistency="request-snapshot-1",
            )
            request_scope = dict(scope)
            request_scope["state"] = {
                **scope.get("state", {}),
                self._state_key: authority,
            }
            remaining = authority.deadline_monotonic - owner.host.services.monotonic()
            async with asyncio.timeout(remaining):
                await self.app(request_scope, receive, response.capture)
        except TimeoutError:
            failure = "LIMIT_EXCEEDED"
        except Exception:
            failure = "BUSY"
        finally:
            if authority is not None:
                if not await _close_scope(owner, authority):
                    failure = "BUSY"
        if failure is not None or not response.complete:
            await _error(failure or "BUSY", scope, receive, send)
        else:
            await response.flush(send)


async def _close_scope(owner: HostScopeIngress, authority: ExecutionScope) -> bool:
    closer = owner.close_scope or owner.host.close_scope

    async def close() -> ShutdownReport:
        return await closer(authority)

    task = asyncio.create_task(close())
    cancellation: asyncio.CancelledError | None = None
    while True:
        try:
            report = await asyncio.shield(task)
            break
        except asyncio.CancelledError as error:
            cancellation = error
            if task.done():
                report = task.result()
                break
        except Exception:
            if cancellation is not None:
                raise cancellation
            return False
    if cancellation is not None:
        raise cancellation
    return report.state == "closed"


__all__ = ["HostScopeIngress"]
