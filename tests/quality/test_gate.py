"""Actual boundary-checker positive/negative controls, not an alternative parser."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from boundary_checks import inspect
from check_boundaries import check


def test_import_cycle_private_and_inventory_controls(tmp_path: Path) -> None:
    fixtures = [
        ("contracts/a.py", "__all__ = []\n", True),
        ("runtime/a.py", "import batten.databricks\n__all__ = []\n", False),
        (
            "databricks/a.py",
            "from batten.storage._values import Hidden\n__all__ = []\n",
            False,
        ),
        ("storage/a.py", "import databricks.sdk\n__all__ = []\n", False),
        ("storage/a.py", "__all__ = ['unexpected']\n", False),
        ("storage/a.py", "import praxis.database\n__all__ = []\n", False),
        (
            "storage/a.py",
            "from os import getenv as read_setting\nread_setting('X')\n__all__ = []\n",
            False,
        ),
        (
            "storage/a.py",
            "import importlib as loader\nloader.import_module('unknown')\n__all__ = []\n",
            False,
        ),
        (
            "databricks/a.py",
            "from databricks.sdk._internal import hidden\n__all__ = []\n",
            False,
        ),
    ]
    for i, (relative, text, allowed) in enumerate(fixtures):
        root = tmp_path / str(i)
        path = root / "packages/example/src/batten" / relative
        path.parent.mkdir(parents=True)
        path.write_text(text)
        if allowed:
            assert inspect(root, [path], {"batten.contracts.a": []}) == 0
        else:
            with pytest.raises(ValueError):
                inspect(root, [path], {})
    root = tmp_path / "cycle"
    directory = root / "packages/example/src/batten/storage"
    directory.mkdir(parents=True)
    paths = [directory / "a.py", directory / "b.py"]
    paths[0].write_text("from . import b\n__all__ = []\n")
    paths[1].write_text("from . import a\n__all__ = []\n")
    with pytest.raises(ValueError, match="cycle"):
        inspect(root, paths, {"batten.storage.a": [], "batten.storage.b": []})

    repository = tmp_path / "baseline"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    scripts = repository / "scripts"
    scripts.mkdir()
    (repository / "pyproject.toml").write_text(
        (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text()
    )
    (scripts / "public-api.json").write_text("{}")
    baseline = scripts / "quality-baseline.json"
    baseline.write_text(json.dumps({"initial_base": "wrong", "test_functions": 0}))
    with pytest.raises(ValueError, match="missing accepted baseline"):
        check(repository, "HEAD")
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "accepted baseline",
        ],
        check=True,
    )
    baseline.write_text(json.dumps({"initial_base": "wrong", "test_functions": 1}))
    with pytest.raises(ValueError, match="ceiling increased"):
        check(repository, "HEAD")
