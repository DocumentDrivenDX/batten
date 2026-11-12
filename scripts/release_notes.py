"""Print the CHANGELOG.md section for one version (used for GitHub Release notes)."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def section(changelog: str, version: str) -> str:
    match = re.search(
        rf"^## {re.escape(version)}\b.*?\n(.*?)(?=^## |\Z)", changelog, re.S | re.M
    )
    if match is None:
        raise SystemExit(f"CHANGELOG.md has no section for {version}")
    return match.group(1).strip() + "\n"


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.stdout.write(section((root / "CHANGELOG.md").read_text(), sys.argv[1]))


if __name__ == "__main__":
    main()
