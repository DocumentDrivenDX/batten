"""Per-attempt safe metrics; correlation and native identity stay host-owned."""

from __future__ import annotations

import time
from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass
class Attempt:
    effect: str = "none"
    features: frozenset[str] = frozenset()
    started: float = field(default_factory=time.monotonic)
    metrics: dict[str, int | float | None] = field(
        default_factory=lambda: {
            "worker_calls": 0,
            "bytes_read": 0,
            "bytes_written": 0,
            "scanned_entries": 0,
            "returned_items": 0,
            "cache_hits": 0,
            "retry_attempts": 0,
            "native_requests": None,
        }
    )


CURRENT: ContextVar[Attempt | None] = ContextVar("batten_storage_attempt", default=None)


def count(name: str, amount: int) -> None:
    attempt = CURRENT.get()
    if attempt is not None:
        value = attempt.metrics.get(name, 0)
        if isinstance(value, (int, float)):
            attempt.metrics[name] = value + amount
