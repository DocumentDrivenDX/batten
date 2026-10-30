"""Common import/export/shape/test-budget gate, including bootstrap evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from boundary_checks import inspect
from boundary_model import sources
from check_policy import policy


def check(root: Path, base: str) -> int:
    subprocess.run(
        ["git", "rev-parse", "--verify", base],
        cwd=root,
        check=True,
        capture_output=True,
    )
    policy(root)
    baseline_path = root / "scripts/quality-baseline.json"
    baseline = json.loads(baseline_path.read_text())
    inventory = json.loads((root / "scripts/public-api.json").read_text())
    count = inspect(root, sources(root), inventory)
    if count > baseline["test_functions"]:
        raise ValueError(
            f"test count {count} exceeds measured ceiling {baseline['test_functions']}"
        )
    prior = subprocess.run(
        ["git", "show", f"{base}:scripts/quality-baseline.json"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if prior.returncode == 0:
        previous = json.loads(prior.stdout)
        if previous == baseline:
            parent = subprocess.run(
                ["git", "show", f"{base}^:scripts/quality-baseline.json"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if parent.returncode == 0:
                previous = json.loads(parent.stdout)
        if baseline["test_functions"] > previous["test_functions"]:
            raise ValueError("test ceiling increased")
    elif (
        baseline["initial_base"]
        != subprocess.check_output(
            ["git", "rev-parse", base], cwd=root, text=True
        ).strip()
    ):
        raise ValueError("missing accepted baseline")
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    print(
        f"Boundary/shape/census checks passed: {check(root, args.base)} behavior functions"
    )


if __name__ == "__main__":
    main()
