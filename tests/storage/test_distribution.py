"""STO-09: wheel-only imports in a clean interpreter without platform packages."""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path


def test_installed_wheel_has_no_platform_dependencies(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    wheels = tmp_path / "wheels"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(wheels),
            str(root / "packages/batten-storage"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(wheels.glob("*.whl"))
    environment = tmp_path / "installed"
    venv.EnvBuilder(with_pip=False).create(environment)
    python = environment / "bin/python"
    subprocess.run(
        [
            "uv",
            "--cache-dir",
            str(tmp_path / "cache"),
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            "--no-index",
            str(wheel),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    probe = """
import importlib.metadata
import sys
import batten.storage
assert not any(n.startswith('batten.storage.local') for n in sys.modules)
assert not importlib.metadata.distribution('novirhyza-batten-storage').requires
import batten.storage.local
assert not any(n.split('.')[0] in {'databricks', 'psycopg', 'tether', 'umf', 'arras'} for n in sys.modules)
print('installed portable and local imports: no platform dependencies')
"""
    result = subprocess.run(
        [str(python), "-I", "-c", probe],
        check=True,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert "no platform dependencies" in result.stdout
