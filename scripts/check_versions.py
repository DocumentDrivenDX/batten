"""Fail unless every distribution has one version, equal to the tag when given."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

PROJECTS = (
    "packages/batten",
    "packages/batten-storage",
    "packages/batten-local",
    "examples/approval-desk",
)


def versions(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for project in PROJECTS:
        metadata = tomllib.loads((root / project / "pyproject.toml").read_text())
        found[metadata["project"]["name"]] = metadata["project"]["version"]
    return found


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    found = versions(root)
    unique = set(found.values())
    if len(unique) != 1:
        raise SystemExit(f"versions differ: {found}")
    (version,) = unique
    if len(sys.argv) > 1 and sys.argv[1] != "v" + version:
        raise SystemExit(f"tag {sys.argv[1]} does not match version {version}")
    print(version)


if __name__ == "__main__":
    main()
