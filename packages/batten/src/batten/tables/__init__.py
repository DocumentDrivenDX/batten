"""Portable table port. Native UMF/driver imports belong to the optional adapter."""

from collections.abc import Mapping
from typing import Protocol

from batten.contracts import Actor


class TablePort(Protocol):
    async def prepare(self) -> None: ...
    async def execute(
        self,
        actor: Actor,
        operation: str,
        inputs: Mapping[str, object],
        *,
        key: str | None,
        phase: str,
        mutation: bool,
    ) -> Mapping[str, object]: ...
    async def aclose(self) -> None: ...


__all__ = ["TablePort"]
