"""Reject disabled quality rules and increases to accepted shape ceilings."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

REQUIRED = {
    "E4",
    "E7",
    "E9",
    "F",
    "I",
    "C901",
    "PLR0911",
    "PLR0912",
    "PLR0915",
    "PLR0904",
}
CAPS = {
    "max-returns": 6,
    "max-branches": 9,
    "max-statements": 40,
    "max-public-methods": 15,
}


def policy(root: Path) -> None:
    config: dict[str, Any] = tomllib.loads((root / "pyproject.toml").read_text())
    lint = config["tool"]["ruff"]["lint"]
    if not REQUIRED <= set(lint["select"]):
        raise ValueError("required lint rules disabled")
    if any(
        lint.get(key)
        for key in (
            "ignore",
            "extend-ignore",
            "per-file-ignores",
            "extend-per-file-ignores",
        )
    ):
        raise ValueError("lint exceptions are forbidden")
    if lint["mccabe"]["max-complexity"] > 10:
        raise ValueError("complexity ceiling increased")
    if any(lint["pylint"][key] > limit for key, limit in CAPS.items()):
        raise ValueError("shape ceiling increased")
    if config["tool"]["pyright"]["typeCheckingMode"] != "strict":
        raise ValueError("strict typing disabled")
