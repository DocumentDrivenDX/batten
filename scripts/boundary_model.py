"""Import ownership and source inventory for the common gate."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import cast

ROOTS = {
    "contracts": (),
    "runtime": ("contracts",),
    "storage": ("contracts",),
    "storage.local": ("contracts", "storage"),
    "packaging": ("contracts",),
    "testing": ("contracts", "runtime"),
    "umf": ("contracts",),
    "hosting": ("contracts", "runtime"),
    "tables": ("contracts",),
    "workers": ("contracts", "runtime"),
    "postgres": ("contracts", "messaging"),
    "messaging": ("contracts",),
    "lakebase": ("contracts",),
    "platform": ("contracts",),
    "databricks": ("contracts", "storage", "platform"),
    "gateway": ("contracts",),
    "arras": ("contracts",),
    "tether": ("contracts",),
    "asgi": ("contracts",),
    "mcp": ("contracts",),
}
VENDORS = {
    "packaging": {"packaging"},
    "umf": {"umf_core", "umf_codegen", "umf_access"},
    "hosting": {"pydantic", "pydantic_settings"},
    "tables": {"umf_core", "umf_codegen", "umf_access", "weft"},
    "postgres": {"psycopg"},
    "lakebase": {"databricks"},
    "databricks": {"databricks"},
    "gateway": {"httpx"},
    "arras": {"arras", "umf_core", "umf_access"},
    "tether": {"tether"},
    "asgi": {"fastapi", "starlette"},
    "mcp": {"mcp"},
}


def sources(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({
        root / p
        for p in result.stdout.splitlines()
        if Path(p).suffix in {".py", ".js", ".mjs", ".ts"}
    })


def module(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    name = relative.split("/src/", 1)[-1].removesuffix(".py").replace("/", ".")
    return name.removesuffix(".__init__")


def owner(name: str) -> str:
    if not name.startswith("batten."):
        if name.startswith(("scripts.", "tests.", "docs.helix.site.")) or name in {
            "eslint.config"
        }:
            return "tools"
        raise ValueError(f"unclassified source: {name}")
    candidates = [
        key
        for key in ROOTS
        if name == "batten." + key or name.startswith("batten." + key + ".")
    ]
    if not candidates:
        raise ValueError(f"unclassified module: {name}")
    return max(candidates, key=len)


def imports(tree: ast.AST, name: str, package: bool) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    parent = name.split(".") if package else name.split(".")[:-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend((entry.name, "") for entry in node.names)
        if isinstance(node, ast.ImportFrom):
            parts = parent[: len(parent) - node.level + 1] if node.level else []
            target = ".".join(parts + ([node.module] if node.module else []))
            result.extend((target, entry.name) for entry in node.names)
    return result


def exports(tree: ast.AST) -> set[str] | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            value: object = ast.literal_eval(node.value)
            if not isinstance(value, (list, tuple)) or not all(
                isinstance(x, str) for x in cast(list[object], value)
            ):
                raise ValueError("export inventory must contain literal strings")
            return set(cast(list[str], value))
    return None
