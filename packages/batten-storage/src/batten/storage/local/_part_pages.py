"""Opaque, scoped, expiring continuation for accepted upload-part observations."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from batten.storage import Limits, PartPage, PartReceipt, StorageError, UploadRef

from ._scope import Scope


@dataclass
class Position:
    scope: Scope
    upload: UploadRef
    revision: str
    limit: int
    offset: int
    expiry: float


class PartPages:
    def __init__(self, limits: Limits):
        self.limits = limits
        self.positions: dict[str, Position] = {}

    def page(
        self,
        scope: Scope,
        upload: UploadRef,
        revision: str,
        parts: list[PartReceipt],
        token: str | None,
        limit: int,
    ) -> PartPage:
        offset = 0
        if token is not None:
            position = self.positions.get(token)
            if (
                position is None
                or position.scope is not scope
                or position.upload != upload
            ):
                raise StorageError("cursor_invalid")
            if position.expiry <= time.monotonic():
                del self.positions[token]
                raise StorageError("cursor_expired")
            if position.revision != revision or position.limit != limit:
                raise StorageError("cursor_invalid")
            offset = position.offset
            del self.positions[token]
        items = tuple(parts[offset : offset + limit])
        future = None
        if offset + limit < len(parts):
            self.prune()
            if len(self.positions) >= self.limits.max_active_transfers:
                raise StorageError("limit_exceeded")
            future = uuid.uuid4().hex
            if len(future.encode()) > self.limits.max_cursor_bytes:
                raise StorageError("limit_exceeded")
            self.positions[future] = Position(
                scope,
                upload,
                revision,
                limit,
                offset + limit,
                time.monotonic() + self.limits.cursor_ttl_seconds,
            )
        return PartPage(items, future)

    def prune(self) -> None:
        for token, position in tuple(self.positions.items()):
            if position.expiry <= time.monotonic() or position.scope.closed:
                del self.positions[token]

    async def close_scope(self, scope: Scope) -> None:
        for token, position in tuple(self.positions.items()):
            if position.scope is scope:
                del self.positions[token]
