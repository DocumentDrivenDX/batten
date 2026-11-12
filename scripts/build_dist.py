"""Build wheels and sdists for every distribution into dist/, with SHA256SUMS."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from check_versions import PROJECTS

APP = "examples/approval-desk"


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    dist = root / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    dist.mkdir()
    subprocess.run(
        [sys.executable, "scripts/prepare_approval.py", "--assets-only"],
        cwd=root,
        check=True,
    )
    for project in PROJECTS:
        # The app wheel force-includes generated web assets, so it has no sdist.
        kinds = ["--wheel"] if project == APP else ["--sdist", "--wheel"]
        subprocess.run(
            ["uv", "build", *kinds, "--out-dir", str(dist), str(root / project)],
            cwd=root,
            check=True,
        )
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in sorted(dist.iterdir())
        if path.suffix == ".whl" or path.name.endswith(".tar.gz")
    ]
    (dist / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
