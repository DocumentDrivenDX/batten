"""Run the README quickstart in a fresh virtual environment against built wheels.

Usage: smoke_install.py DIST_DIR

The quickstart block between the `quickstart` markers in README.md is executed
verbatim, with the wheels in DIST_DIR made visible to pip. The `serve` command is
started in the background and its registry page is fetched.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

PORT = 8820


def quickstart(readme: Path) -> list[str]:
    match = re.search(
        r"<!-- quickstart -->\s*```sh\n(.*?)```\s*<!-- /quickstart -->",
        readme.read_text(),
        re.S,
    )
    if match is None:
        raise SystemExit("README.md has no quickstart block")
    return [
        line
        for line in match.group(1).splitlines()
        if line.strip() and not line.startswith("#")
    ]


def script(lines: list[str], dist: Path) -> str:
    body = [f"export PIP_FIND_LINKS={dist}"]
    # `exec` makes the server the process we started, so terminate() stops it.
    body += [
        "exec " + line if line.startswith("batten-approval serve") else line
        for line in lines
    ]
    return "\n".join(["set -euo pipefail", *body])


def fetch_registry(process: subprocess.Popen[bytes]) -> str:
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise SystemExit(
                f"quickstart exited early with status {process.returncode}"
            )
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=5) as page:
                return page.read().decode()
        except OSError:
            time.sleep(1)
    raise SystemExit("approval desk did not answer on the quickstart port")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    dist = Path(sys.argv[1]).resolve()
    lines = quickstart(root / "README.md")
    if not lines or not lines[-1].startswith("batten-approval serve"):
        raise SystemExit("quickstart must end with batten-approval serve")
    with tempfile.TemporaryDirectory() as work:
        process = subprocess.Popen(["bash", "-c", script(lines, dist)], cwd=work)
        try:
            if "Approval desk" not in fetch_registry(process):
                raise SystemExit("registry page does not list the approval desk")
            print("quickstart OK: registry lists the approval desk")
        finally:
            process.terminate()
            process.wait(timeout=60)


if __name__ == "__main__":
    main()
