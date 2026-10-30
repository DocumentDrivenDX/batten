"""Semantic import graph and source shape checks."""

from __future__ import annotations

import ast
import io
import sys
import tokenize
from pathlib import Path

from boundary_model import ROOTS, VENDORS, exports, imports, module, owner


def edge(source: str, target: str, symbol: str) -> None:
    current = owner(source)
    if target.split(".")[0] == "praxis":
        raise ValueError(f"{source}: private host dependency")
    if target.startswith("batten."):
        destination = owner(target)
        if current != "tools" and destination != current:
            if destination not in ROOTS[current]:
                raise ValueError(f"{source}: forbidden import {target}")
            if any(p.startswith("_") for p in target.split(".")) or symbol.startswith(
                "_"
            ):
                raise ValueError(f"{source}: private export {target}.{symbol}")
    elif current != "tools":
        top = target.split(".")[0]
        if top in {"importlib", "runpy", "subprocess"}:
            raise ValueError(
                f"{source}: process/loader needs an explicit reviewed boundary"
            )
        if top not in sys.stdlib_module_names and top not in VENDORS.get(
            current, set()
        ):
            raise ValueError(f"{source}: undeclared vendor {target}")
        if top in VENDORS.get(current, set()) and (
            symbol.startswith("_")
            or any(part.startswith("_") for part in target.split("."))
        ):
            raise ValueError(f"{source}: private platform API")


def effects(tree: ast.AST, name: str) -> None:
    aliases: dict[str, str] = {}
    for statement in ast.walk(tree):
        if isinstance(statement, ast.Import):
            aliases.update(
                (entry.asname or entry.name, entry.name) for entry in statement.names
            )
        if isinstance(statement, ast.ImportFrom) and statement.module:
            aliases.update(
                (entry.asname or entry.name, statement.module + "." + entry.name)
                for entry in statement.names
            )
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and aliases.get(node.id) in {
            "os.environ",
            "os.getenv",
            "sys.path",
            "importlib.import_module",
        }:
            raise ValueError(f"{name}: aliased ambient access or loader")
        if isinstance(node, ast.Call):
            fn = ast.unparse(node.func)
            head, *tail = fn.split(".")
            fn = ".".join([aliases.get(head, head), *tail])
            if fn in {"__import__", "eval", "exec"} or fn.endswith("import_module"):
                raise ValueError(f"{name}: undeclared dynamic loader")
        if isinstance(node, ast.Attribute):
            text = ast.unparse(node)
            head, *tail = text.split(".")
            text = ".".join([aliases.get(head, head), *tail])
            if text in {"sys.path", "os.environ", "os.getenv"}:
                raise ValueError(f"{name}: ambient configuration/path mutation")


def cycles(graph: dict[str, set[str]]) -> None:
    visited: set[str] = set()
    active: set[str] = set()

    def visit(name: str) -> None:
        if name in active:
            raise ValueError(f"dependency cycle: {name}")
        if name in visited:
            return
        active.add(name)
        for dependency in graph.get(name, set()):
            visit(dependency)
        active.remove(name)
        visited.add(name)

    for name in graph:
        visit(name)


def suppressions(path: Path) -> None:
    for token in tokenize.generate_tokens(io.StringIO(path.read_text()).readline):
        if token.type == tokenize.COMMENT and any(
            x in token.string for x in ("noqa", "type: ignore", "pyright: ignore")
        ):
            raise ValueError(f"{path}: rule suppression")


def inspect(root: Path, paths: list[Path], inventory: dict[str, list[str]]) -> int:
    python = [p for p in paths if p.suffix == ".py"]
    trees = {module(p, root): ast.parse(p.read_text()) for p in python}
    graph: dict[str, set[str]] = {}
    count = 0
    for path in paths:
        maximum = 488 if "tests" in path.parts else 500
        if len(path.read_text().splitlines()) > maximum:
            raise ValueError(f"source line ceiling: {path}")
    for path in python:
        name = module(path, root)
        suppressions(path)
        tree = trees[name]
        owner(name)
        effects(tree, name)
        graph[name] = set()
        for target, symbol in imports(tree, name, path.name == "__init__.py"):
            edge(name, target, symbol)
            dependency = target + "." + symbol
            resolved = dependency if dependency in trees else target
            if resolved in trees:
                graph[name].add(resolved)
        declared = exports(tree)
        if name.startswith("batten.") and (
            path.name == "__init__.py" or not path.stem.startswith("_")
        ):
            if declared is None or sorted(declared) != sorted(inventory.get(name, [])):
                raise ValueError(f"missing or mismatched public inventory: {name}")
        count += sum(
            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name.startswith("test_")
            for n in ast.walk(tree)
        )
    cycles(graph)
    return count
