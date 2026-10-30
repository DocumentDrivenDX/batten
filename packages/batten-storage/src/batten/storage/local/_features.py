"""Storage-specific capability requirements; generic core never interprets them."""

from __future__ import annotations

from batten.storage import Absent, Any, Condition, Digest, Matches


def required(
    operation: str,
    condition: Condition = Any(),
    digest: Digest | None = None,
    ranged: bool = False,
) -> frozenset[str]:
    result: set[str] = set()
    if isinstance(condition, Absent):
        result.add("create_only")
    if isinstance(condition, Matches):
        result.add(
            {
                "read": "conditional_read",
                "write": "conditional_replace",
                "delete": "conditional_delete",
            }[operation]
        )
    if digest is not None:
        result.add("verified_transfer")
    if ranged:
        result.add("read_range")
    return frozenset(result)
