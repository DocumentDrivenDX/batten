"""Owned OpenTelemetry provider and durable, redacted local audit capture."""

from __future__ import annotations

import asyncio
import fcntl
import json
import os
from collections.abc import AsyncGenerator, Callable, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
from typing import TypeVar

from batten.contracts import Actor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

_T = TypeVar("_T")


async def settled(work: Callable[[], _T]) -> _T:
    task = asyncio.create_task(asyncio.to_thread(work))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        await asyncio.shield(task)
        raise


def append(path: Path, frames: list[dict[str, object]]) -> None:
    content = b"".join(
        json.dumps(frame, separators=(",", ":")).encode() + b"\n" for frame in frames
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        offset = 0
        while offset < len(content):
            written = os.write(fd, content[offset:])
            if written <= 0:
                raise OSError("capture made no progress")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)


class SafeExporter(SpanExporter):
    def __init__(self, path: Path):
        self.path, self.failed = path, False
        self.pending: list[dict[str, object]] = []
        self.lock = Lock()

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        frames: list[dict[str, object]] = []
        for span in spans:
            context = span.context
            if context is None:
                self.failed = True
                return SpanExportResult.FAILURE
            attributes = span.attributes or {}
            safe = {
                key: attributes[key]
                for key in (
                    "batten.actor",
                    "batten.operation",
                    "batten.invocation",
                    "batten.application",
                )
                if key in attributes
            }
            frames.append({
                "type": "span",
                "name": "database"
                if span.kind == trace.SpanKind.CLIENT
                else "operation",
                "trace_id": format(context.trace_id, "032x"),
                "span_id": format(context.span_id, "016x"),
                "parent_id": format(span.parent.span_id, "016x")
                if span.parent
                else None,
                "attributes": safe,
                "start_ns": span.start_time,
                "end_ns": span.end_time,
            })
        with self.lock:
            if len(self.pending) + len(frames) > 2048:
                self.failed = True
                return SpanExportResult.FAILURE
            self.pending.extend(frames)
        return SpanExportResult.SUCCESS

    def flush(self) -> None:
        with self.lock:
            frames, self.pending = self.pending, []
        try:
            if frames:
                append(self.path, frames)
        except OSError:
            self.failed = True
            raise RuntimeError("required span capture unavailable") from None

    def shutdown(self) -> None:
        self.flush()


class LocalObservations:
    def __init__(self, data: Path, application: str, *, timeout_ms: int):
        self.path = data / "audit.jsonl"
        self.application, self.timeout = application, timeout_ms
        self.exporter = SafeExporter(data / "spans.jsonl")
        self.provider = TracerProvider(
            resource=Resource({"service.name": "batten-local"}),
            sampler=ALWAYS_ON,
            shutdown_on_exit=False,
        )
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer("batten.local", "0.1.0a1")

    @asynccontextmanager
    async def scope(
        self, actor: Actor, operation: str, invocation: str
    ) -> AsyncGenerator[None, None]:
        span = self.tracer.start_span(
            "batten.operation",
            attributes={
                "batten.actor": actor.subject,
                "batten.operation": operation,
                "batten.invocation": invocation,
                "batten.application": self.application,
            },
        )
        with trace.use_span(span, end_on_exit=False):
            try:
                yield
            finally:
                await settled(span.end)

    async def capture(
        self, actor: Actor, operation: str, invocation: str, status: str, mutation: bool
    ) -> None:
        frame: dict[str, object] = {
            "type": "audit",
            "application": self.application,
            "actor": actor.subject,
            "operation": operation,
            "invocation": invocation,
            "status": status,
            "mutation": mutation,
        }
        await settled(lambda: append(self.path, [frame]))
        await settled(self.exporter.flush)
        if self.exporter.failed:
            raise RuntimeError("required local capture unavailable")

    async def aclose(self) -> None:
        await settled(self.provider.shutdown)
