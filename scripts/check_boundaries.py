"""Import-boundary, public-API inventory and source-shape check."""

from __future__ import annotations

import json
from pathlib import Path

from boundary_checks import inspect
from boundary_model import sources


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads((root / "scripts/public-api.json").read_text())
    inspect(root, sources(root), inventory)
    print("Import boundaries and public API inventory are consistent.")


if __name__ == "__main__":
    main()
