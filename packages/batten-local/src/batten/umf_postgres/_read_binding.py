"""Host-only metadata shared by generated native read implementations."""

from typing import Protocol


class ReadBindingMetadata(Protocol):
    @property
    def schema(self) -> str: ...
    @property
    def module(self) -> str: ...
    @property
    def target_binding_digest(self) -> str: ...
    @property
    def read_profile(self) -> str | None: ...
