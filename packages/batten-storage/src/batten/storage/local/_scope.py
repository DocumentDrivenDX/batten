"""Per-invocation authority, deadlines and safe outcome capture."""

from __future__ import annotations

import asyncio
import errno
import time
import uuid
from collections.abc import Awaitable, Callable
from types import MappingProxyType
from typing import TypeVar

from batten.storage import Authority, StorageError

from ._observations import CURRENT, Attempt, count

T = TypeVar("T")


async def worker(
    function: Callable[..., T],
    *args: object,
    on_cancel: Callable[[T], None] | None = None,
    **kwargs: object,
) -> T:
    count("worker_calls", 1)
    task = asyncio.create_task(asyncio.to_thread(function, *args, **kwargs))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        try:
            result = await settle(task)
            if on_cancel is not None:
                await settle(asyncio.create_task(asyncio.to_thread(on_cancel, result)))
        except Exception:
            pass
        raise


async def settle(task: asyncio.Task[T]) -> T:
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            continue
    return task.result()


def translate(error: Exception, effect: str) -> StorageError:
    if isinstance(error, StorageError):
        return StorageError(
            error.code,
            "unknown" if effect == "unknown" else error.effect,
            error.incident_id,
        )
    code = "io_failure"
    if isinstance(error, FileNotFoundError):
        code = "not_found"
    if isinstance(error, OSError) and error.errno in {errno.ELOOP, errno.ENOTDIR}:
        code = "path_conflict"
    if isinstance(error, PermissionError):
        code = "denied"
    if isinstance(error, TimeoutError):
        code = "timeout"
    return StorageError(code, effect)


class Scope:
    def __init__(
        self, authority: Authority, timeout_ms: int, ready: Callable[[], bool]
    ):
        self.authority = authority
        self.timeout = timeout_ms / 1000
        self.ready = ready
        self.closed = False
        self.nonce = uuid.uuid4().hex
        self.closers: set[Callable[[], Awaitable[object]]] = set()
        self.tasks: dict[asyncio.Task[object], int] = {}

    async def authorize(
        self, operation: str, key: str, extra: frozenset[str] = frozenset()
    ) -> None:
        if self.closed or not self.ready():
            raise StorageError("denied")
        attempt = CURRENT.get()
        features: frozenset[str] = attempt.features if attempt else frozenset()
        await self.authority.check(operation, key, features | extra)

    async def permits(self, operation: str, key: str, feature: str) -> bool:
        try:
            await self.authorize(operation, key, frozenset({feature}))
        except StorageError as error:
            if error.code not in {"denied", "unsupported"}:
                raise
            return False
        return True

    async def capture(
        self, operation: str, code: str, effect: str, incident: str
    ) -> None:
        try:
            attempt = CURRENT.get()
            metrics = dict(attempt.metrics) if attempt else {}
            if attempt:
                metrics["duration_ms"] = (time.monotonic() - attempt.started) * 1000
            await self.authority.observe(
                operation, code, effect, incident, MappingProxyType(metrics)
            )
        except Exception:
            failure = StorageError("unavailable", effect, incident)
        else:
            return
        raise failure from None

    async def run(
        self,
        operation: str,
        key: str,
        action: Callable[[Attempt], Awaitable[T]],
        *,
        features: frozenset[str] = frozenset(),
    ) -> T:
        attempt = Attempt(features=features)
        token = CURRENT.set(attempt)
        incident = uuid.uuid4().hex
        task = asyncio.current_task()
        if task is not None:
            self.tasks[task] = self.tasks.get(task, 0) + 1
        try:
            try:
                async with asyncio.timeout(self.timeout):
                    await self.authorize(operation, key)
                    await self.capture(operation, "started", "none", incident)
                    result = await action(attempt)
                    await self.capture(operation, "complete", attempt.effect, incident)
                    return result
            except asyncio.CancelledError as cancellation:
                try:
                    await self.capture(operation, "cancelled", attempt.effect, incident)
                except StorageError as audit_loss:
                    cancellation.add_note(
                        f"Storage observation unavailable ({incident})"
                    )
                    raise cancellation from audit_loss
                raise
            except Exception as error:
                translated = translate(error, attempt.effect)
                failure = StorageError(translated.code, translated.effect, incident)
            await self.capture(
                operation, failure.code, failure.effect, failure.incident_id
            )
        finally:
            CURRENT.reset(token)
            if task is not None:
                self.tasks[task] -= 1
                if self.tasks[task] == 0:
                    del self.tasks[task]

        raise failure from None

    async def close(self) -> None:
        self.closed = True
        pending = set(self.tasks) - {asyncio.current_task()}
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        for close in tuple(self.closers):
            await close()
        self.closers.clear()
