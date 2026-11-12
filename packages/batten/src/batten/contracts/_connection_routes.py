"""Canonical metadata pin for an admitted set of generated connection routes."""

import json
import re
from collections.abc import Iterable
from hashlib import sha256

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def connection_routes_digest(
    application_id: str,
    application_digest: str,
    api_digest: str,
    artifact_digest: str,
    routes: Iterable[tuple[str, str, str, str]],
) -> str:
    """Hash immutable route pins using the Batten connection-routes/1 preimage."""
    pins = tuple(tuple(route) for route in routes)
    values = (application_id, application_digest, api_digest, artifact_digest)
    if any(not _valid_text(value) for value in values):
        raise ValueError("connection route scope pins require valid text")
    if any(
        len(route) != 4
        or any(not _valid_text(value) for value in route)
        or not _DIGEST.fullmatch(route[3])
        for route in pins
    ):
        raise ValueError("connection route pins require valid immutable rows")
    ordered = tuple(sorted(pins))
    if not ordered or len({route[0] for route in ordered}) != len(ordered):
        raise ValueError("connection routes require distinct Host operations")
    payload = {
        "version": "batten.connection-routes/1",
        "applicationId": application_id,
        "applicationDigest": application_digest,
        "apiDigest": api_digest,
        "artifactDigest": artifact_digest,
        "routes": [list(route) for route in ordered],
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8", errors="strict")
    return sha256(encoded).hexdigest()


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value:
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return False
    return True


__all__ = ["connection_routes_digest"]
