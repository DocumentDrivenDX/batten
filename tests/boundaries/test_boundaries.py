"""Positive and negative controls for the import-boundary checker."""

from __future__ import annotations

from pathlib import Path

import pytest
from boundary_checks import inspect

FORBIDDEN = [
    ("runtime/a.py", "import batten.databricks\n__all__ = []\n"),
    (
        "databricks/a.py",
        "from batten.storage._values import Hidden\n__all__ = []\n",
    ),
    ("storage/a.py", "import databricks.sdk\n__all__ = []\n"),
    ("runtime/a.py", "import psycopg\n__all__ = []\n"),
    ("tables/a.py", "import umf_access\n__all__ = []\n"),
    ("storage/a.py", "__all__ = ['unexpected']\n"),
    ("storage/a.py", "import praxis.database\n__all__ = []\n"),
    (
        "storage/a.py",
        "from os import getenv as read_setting\nread_setting('X')\n__all__ = []\n",
    ),
    (
        "storage/a.py",
        "import importlib as loader\nloader.import_module('x')\n__all__ = []\n",
    ),
    ("storage/a.py", "import os  # noqa: F401\n__all__ = []\n"),
]


def write(tmp_path: Path, name: str, relative: str, text: str) -> Path:
    path = tmp_path / name / "packages/example/src/batten" / relative
    path.parent.mkdir(parents=True)
    path.write_text(text)
    return path


def test_clean_module_passes(tmp_path: Path) -> None:
    path = write(tmp_path, "clean", "contracts/a.py", "__all__ = []\n")
    inspect(tmp_path / "clean", [path], {"batten.contracts.a": []})


@pytest.mark.parametrize(("relative", "text"), FORBIDDEN)
def test_forbidden_source_is_rejected(tmp_path: Path, relative: str, text: str) -> None:
    path = write(tmp_path, "bad", relative, text)
    with pytest.raises(ValueError):
        inspect(tmp_path / "bad", [path], {})


def test_import_cycle_is_rejected(tmp_path: Path) -> None:
    directory = tmp_path / "cycle/packages/example/src/batten/storage"
    directory.mkdir(parents=True)
    paths = [directory / "a.py", directory / "b.py"]
    paths[0].write_text("from . import b\n__all__ = []\n")
    paths[1].write_text("from . import a\n__all__ = []\n")
    with pytest.raises(ValueError, match="cycle"):
        inspect(
            tmp_path / "cycle", paths, {"batten.storage.a": [], "batten.storage.b": []}
        )
