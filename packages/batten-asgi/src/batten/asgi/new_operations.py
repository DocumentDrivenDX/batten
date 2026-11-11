"""Bounded standalone HTTP calls to prebound public Host operations."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import asdict, replace
from typing import cast

from batten.contracts import (
    Actor,
    ExecutionScope,
    Operation,
    OperationCall,
    OperationOutcome,
    ShutdownReport,
)
from batten.runtime import Host
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

ActorResolver = Callable[[Request], Awaitable[Actor | None]]
ScopeCloser = Callable[[ExecutionScope], Awaitable[ShutdownReport]]


class _CapacityExceeded(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object member")
        result[key] = value
    return result


def _invalid_constant(value: str) -> object:
    raise ValueError(f"invalid JSON constant: {value}")


def _validate_json_tree(
    value: object, *, maximum_values: int = 16_384, maximum_depth: int = 32
) -> None:
    pending: list[tuple[object, int]] = [(value, 0)]
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if nodes > maximum_values or depth > maximum_depth:
            raise _CapacityExceeded("JSON structure exceeds limits")
        if type(current) is dict:
            mapping = cast(dict[str, object], current)
            pending.extend((item, depth + 1) for item in mapping.values())
        elif type(current) is list:
            pending.extend((item, depth + 1) for item in cast(list[object], current))


async def read_json_object(
    request: Request, maximum: int, *, operation_envelope: bool = False
) -> dict[str, object]:
    if (
        request.headers.get("content-type", "").split(";")[0].strip().lower()
        != "application/json"
    ):
        raise ValueError("JSON required")
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > maximum:
            raise _CapacityExceeded("request capacity exceeded")
        data.extend(chunk)
    try:
        value: object = json.loads(
            data, object_pairs_hook=_unique_object, parse_constant=_invalid_constant
        )
        if operation_envelope and type(value) is dict:
            # Allow four values for the outer envelope while independently
            # checking the Host input snapshot; object keys are not value nodes.
            envelope = cast(dict[str, object], value)
            _validate_json_tree(envelope, maximum_values=16_388, maximum_depth=34)
            inputs = envelope.get("inputs")
            if type(inputs) is dict:
                _validate_json_tree(cast(dict[str, object], inputs))
        else:
            _validate_json_tree(value)
    except RecursionError as error:
        raise _CapacityExceeded("JSON structure exceeds limits") from error
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return cast(dict[str, object], value)


def _call_values(
    value: dict[str, object], operation: str, actor: Actor
) -> OperationCall:
    if not {"inputs"} <= set(value) <= {"inputs", "key", "phase", "confirmation"}:
        raise ValueError("operation envelope invalid")
    inputs, key, phase = value["inputs"], value.get("key"), value.get("phase", "invoke")
    confirmation = value.get("confirmation")
    if (
        type(inputs) is not dict
        or (
            confirmation is not None
            and (type(confirmation) is not str or phase != "invoke")
        )
        or (key is not None and type(key) is not str)
        or type(phase) is not str
        or phase not in {"invoke", "observe"}
    ):
        raise ValueError("operation envelope invalid")
    return OperationCall(
        operation,
        cast(dict[str, object], inputs),
        actor,
        key,
        phase,
        confirmation=cast(str | None, confirmation),
    )


def _response(payload: object, status: int, maximum: int) -> Response:
    try:
        response = JSONResponse(payload, status_code=status)
    except (RecursionError, TypeError, ValueError):
        return Response(status_code=503)
    if len(response.body) <= maximum:
        return response
    unavailable = JSONResponse({"status": "unavailable"}, status_code=503)
    if len(unavailable.body) <= maximum:
        return unavailable
    return Response(status_code=503)


def _status_code(outcome: OperationOutcome) -> int:
    return {
        "denied": 403,
        "invalid": 400,
        "precondition_failed": 409,
        "unavailable": 503,
        "uncertain": 202,
    }.get(outcome.status, 200)


async def _close_scope(
    host: Host,
    closer: ScopeCloser,
    scope: ExecutionScope,
    pending_tasks: dict[str, asyncio.Task[ShutdownReport]],
) -> ShutdownReport:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + host.config.timeout_seconds
    cancellation: asyncio.CancelledError | None = None
    report = ShutdownReport("draining", (), ("scope_cleanup_pending",))
    while report.state == "draining" and loop.time() < deadline:
        task = _cleanup_task(pending_tasks, scope, closer)
        completed, interrupted = await _wait_cleanup(task, deadline, loop)
        cancellation = cancellation or interrupted
        if not completed:
            break
        report = _cleanup_result(task)
        await asyncio.sleep(0)
    if cancellation is not None:
        raise cancellation
    return report


def _cleanup_task(
    pending: dict[str, asyncio.Task[ShutdownReport]],
    scope: ExecutionScope,
    closer: ScopeCloser,
) -> asyncio.Task[ShutdownReport]:
    task = pending.get(scope.lease_id)
    if task is not None:
        return task

    async def close() -> ShutdownReport:
        return await closer(scope)

    task = asyncio.create_task(close())
    pending[scope.lease_id] = task

    def reap(done: asyncio.Task[ShutdownReport]) -> None:
        try:
            done.exception()
        except asyncio.CancelledError:
            pass
        if pending.get(scope.lease_id) is done:
            pending.pop(scope.lease_id, None)

    task.add_done_callback(reap)
    return task


async def _wait_cleanup(
    task: asyncio.Task[ShutdownReport], deadline: float, loop: asyncio.AbstractEventLoop
) -> tuple[bool, asyncio.CancelledError | None]:
    try:
        done, _pending = await asyncio.wait(
            (task,), timeout=max(0.0, deadline - loop.time())
        )
    except asyncio.CancelledError as error:
        return False, error
    return bool(done), None


def _cleanup_result(task: asyncio.Task[ShutdownReport]) -> ShutdownReport:
    try:
        return task.result()
    except BaseException:
        return ShutdownReport("failed", (), ("scope_cleanup_failed",))


class OperationIngress:
    """Standalone Host scope owner for a fixed set of ordinary operations."""

    def __init__(
        self,
        host: Host,
        *,
        resolve_actor: ActorResolver,
        allowed_operations: Iterable[str],
        max_request_bytes: int,
        max_response_bytes: int,
        close_scope: ScopeCloser | None = None,
        api_digest: str | None = None,
    ):
        if (
            not callable(resolve_actor)
            or type(max_request_bytes) is not int
            or max_request_bytes < 1
            or type(max_response_bytes) is not int
            or max_response_bytes < 1
        ):
            raise ValueError("resolver and finite request/response limits required")
        if api_digest is not None and re.fullmatch(r"[0-9a-f]{64}", api_digest) is None:
            raise ValueError("invalid operation API digest")
        self.api_digest = api_digest
        operation_ids = tuple(allowed_operations)
        if any(
            type(operation_id) is not str or not operation_id
            for operation_id in operation_ids
        ) or len(set(operation_ids)) != len(operation_ids):
            raise ValueError("unique prebound operations required")
        self.operations = self._bind_operations(host, operation_ids)
        self.host, self.resolve_actor = host, resolve_actor
        self.maximum_request, self.maximum_response = (
            max_request_bytes,
            max_response_bytes,
        )
        self.close_scope = close_scope or host.close_scope
        self._pending_cleanup: dict[str, asyncio.Task[ShutdownReport]] = {}

    @staticmethod
    def _bind_operations(
        host: Host, operation_ids: tuple[str, ...]
    ) -> dict[str, Operation]:
        bound: dict[str, Operation] = {}
        for operation_id in operation_ids:
            operation = host.operations.get(operation_id)
            if operation is None or operation.selection_kinds:
                raise ValueError("only declared ordinary operations may be routed")
            bound[operation_id] = operation
        return bound

    async def invoke(self, request: Request) -> Response:
        try:
            async with asyncio.timeout(self.host.config.timeout_seconds):
                return await self._invoke(request)
        except TimeoutError:
            return _response({"status": "unavailable"}, 503, self.maximum_response)

    async def _invoke(self, request: Request) -> Response:
        actor = await self._actor(request)
        if isinstance(actor, Response):
            return actor
        parsed = await self._call(request, actor)
        if isinstance(parsed, Response):
            return parsed
        call, operation = parsed
        if (
            operation.mutation
            and self.api_digest is not None
            and request.headers.getlist("x-lintel-api") != [self.api_digest]
        ):
            return _response(
                {"status": "precondition_failed"}, 412, self.maximum_response
            )
        scope = await self._open_scope(actor)
        if isinstance(scope, Response):
            return scope
        outcome = await self._execute(call, operation, scope)
        if isinstance(outcome, Response):
            return outcome
        return self._encode(outcome)

    async def _actor(self, request: Request) -> Actor | Response:
        try:
            actor = await self.resolve_actor(request)
        except Exception:
            return _response({"status": "unavailable"}, 503, self.maximum_response)
        if type(actor) is not Actor:
            return _response({"status": "denied"}, 401, self.maximum_response)
        return actor

    async def _call(
        self, request: Request, actor: Actor
    ) -> tuple[OperationCall, Operation] | Response:
        try:
            value = await read_json_object(
                request, self.maximum_request, operation_envelope=True
            )
            operation_id = request.path_params["operation"]
            operation = self.operations.get(operation_id)
            if operation is None:
                raise ValueError("operation is not routed")
            call = _call_values(value, operation_id, actor)
        except _CapacityExceeded:
            return _response({"status": "limited"}, 413, self.maximum_response)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError, RecursionError):
            return _response({"status": "invalid"}, 400, self.maximum_response)
        return call, operation

    async def _open_scope(self, actor: Actor) -> ExecutionScope | Response:
        try:
            scope = await self.host.open_scope(
                actor, uuid.uuid4().hex, api_digest=self.api_digest
            )
        except (RuntimeError, ValueError):
            return _response({"status": "unavailable"}, 503, self.maximum_response)
        return scope

    async def _execute(
        self, call: OperationCall, operation: Operation, scope: ExecutionScope
    ) -> OperationOutcome:
        failed = False
        outcome: OperationOutcome | None = None
        try:
            outcome = await self.host.invoke(replace(call, scope=scope))
        except asyncio.CancelledError:
            raise
        except Exception:
            failed = True
        finally:
            try:
                cleanup = await _close_scope(
                    self.host, self.close_scope, scope, self._pending_cleanup
                )
            except Exception:
                cleanup = ShutdownReport("failed", (), ("scope_cleanup_failed",))
        if cleanup.state != "closed":
            return OperationOutcome(
                "uncertain" if operation.mutation else "unavailable",
                call.key or scope.request_id,
                {},
                "cleanup_pending",
            )
        if failed or outcome is None:
            return OperationOutcome(
                "uncertain" if operation.mutation else "unavailable",
                call.key or scope.request_id,
                {},
                "execution_failed",
            )
        return outcome

    def _encode(self, outcome: OperationOutcome) -> Response:
        try:
            return _response(
                asdict(outcome), _status_code(outcome), self.maximum_response
            )
        except (RecursionError, TypeError, ValueError):
            return _response({"status": "unavailable"}, 503, self.maximum_response)


def operation_route(ingress: OperationIngress) -> Route:
    """Build the stable POST route for an already composed operation ingress."""
    if type(ingress) is not OperationIngress:
        raise TypeError("OperationIngress required")
    return Route("/api/operations/{operation}", ingress.invoke, methods=["POST"])


__all__ = [
    "OperationIngress",
    "operation_route",
]
