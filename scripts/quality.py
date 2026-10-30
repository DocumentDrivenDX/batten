"""One quality recipe shared by local execution, hooks and CI."""

from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lint", action="store_true")
    args = parser.parse_args()
    commands = [
        [sys.executable, "scripts/check_boundaries.py", "--base", "HEAD"],
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
        ["pyright"],
        ["bun", "run", "lint"],
    ]
    if not args.lint:
        commands.append([sys.executable, "-m", "pytest"])
    for command in commands:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
