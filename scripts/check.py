"""The one check recipe shared by local runs and CI."""

from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lint", action="store_true", help="skip pytest")
    args = parser.parse_args()
    commands = [
        [sys.executable, "scripts/check_boundaries.py"],
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
        ["pyright"],
        ["bun", "run", "lint"],
        ["bun", "run", "typecheck"],
    ]
    if not args.lint:
        commands.append([sys.executable, "-m", "pytest", "-m", "not integration"])
    for command in commands:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
