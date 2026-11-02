"""Validate reference-app inventory, never substitute metadata for app execution."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, cast

OBLIGATIONS = {
    "AUTH",
    "IDENTITY",
    "COMMANDS",
    "LIFECYCLE",
    "LIMITS",
    "PARITY",
    "OBSERVABILITY",
}
FIELDS = {"id", "slug", "root", "ui", "modules", "story", "obligations"}


def inside(root: Path, value: str) -> Path:
    path = root / value
    if Path(value).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("corpus path escapes repository")
    return path


def app(root: Path, value: dict[str, Any], workflow: Path) -> None:
    if set(value) != FIELDS or not re.fullmatch(r"MA-\d{3}", value["id"]):
        raise ValueError("invalid application inventory fields or ID")
    if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", value["slug"]):
        raise ValueError("invalid application slug")
    if value["root"] != "docs/helix/reference-apps/" + value["slug"]:
        raise ValueError("application root mismatch")
    if value["ui"] not in {"typescript", "headless"}:
        raise ValueError("invalid application UI delivery")
    tags(value)
    directory = inside(root, value["root"])
    marker = json.loads((directory / ".helix.yml").read_text())
    if marker["flows"] != [{"id": "helix", "root": "specs/"}]:
        raise ValueError("application HELIX scope mismatch")
    binding = marker["x-batten-app"]
    if (
        binding["id"] != value["id"]
        or (directory / binding["workflow"]).resolve() != workflow.resolve()
    ):
        raise ValueError("application workflow binding mismatch")
    documents(directory, value)


def tags(value: dict[str, Any]) -> None:
    for key in ("modules", "obligations"):
        raw: object = value[key]
        if not isinstance(raw, list):
            raise ValueError("integration/obligation tags must be arrays")
        entries = cast(list[object], raw)
        if (
            not entries
            or any(not isinstance(x, str) or not x for x in entries)
            or len(set(entries)) != len(entries)
        ):
            raise ValueError("invalid or duplicate integration/obligation tags")
    if set(value["obligations"]) != OBLIGATIONS:
        raise ValueError("missing or unknown shared obligation")
    if not re.fullmatch(r"US-\d{3}", value["story"]):
        raise ValueError("invalid story identity")


def documents(directory: Path, value: dict[str, Any]) -> None:
    for path, kind in (
        ("01-frame/prd.md", "prd"),
        (
            f"01-frame/features/FEAT-{value['story'].split('-')[1]}-business-journey.md",
            "feature-specification",
        ),
        (f"01-frame/user-stories/{value['story']}-journey.md", "user-stories"),
        ("03-test/test-plan.md", "test-plan"),
    ):
        text = (directory / "specs" / path).read_text()
        if not text.startswith("---\n") or f"type: {kind}\n" not in text:
            raise ValueError("missing governed application artifact")
    story = directory / "specs/01-frame/user-stories" / (value["story"] + "-journey.md")
    text = story.read_text()
    if any(f"**{value['story']}-AC{i}**" not in text for i in range(1, 6)):
        raise ValueError("missing application acceptance criterion")
    if "specs/" not in (directory / "AGENTS.md").read_text():
        raise ValueError("missing application scope instructions")
    fixture = json.loads((directory / "fixtures.json").read_text())
    if fixture["application"] != value["id"] or not fixture["record"]["id"].startswith(
        "fabricated-"
    ):
        raise ValueError("fixture identity mismatch")
    if fixture["actors"]["permitted"] == fixture["actors"]["foreign"]:
        raise ValueError("foreign actor is not distinct")


def inventory(root: Path) -> int:
    catalog = json.loads((root / "docs/helix/reference-apps/catalog.json").read_text())
    if set(catalog) != {"version", "workflow", "apps"} or catalog["version"] != 1:
        raise ValueError("invalid corpus version or fields")
    workflow = inside(root, catalog["workflow"])
    if not workflow.is_file() or not catalog["apps"]:
        raise ValueError("missing workflow or apps")
    seen: set[str] = set()
    roots: set[str] = set()
    for value in catalog["apps"]:
        if value["id"] in seen or value["root"] in roots:
            raise ValueError("duplicate app identity or root")
        app(root, value, workflow)
        seen.add(value["id"])
        roots.add(value["root"])
    actual = {
        str(path.parent.relative_to(root))
        for path in (root / "docs/helix/reference-apps").glob("*/.helix.yml")
    }
    if actual != roots:
        raise ValueError("unregistered or missing application scope")
    return len(seen)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-execution", action="store_true")
    args = parser.parse_args()
    count = inventory(Path(__file__).resolve().parents[1])
    print(f"Reference-app inventory only: {count} scoped specifications validated")
    if args.require_execution:
        parser.exit(
            1,
            "Complete app execution is unqualified: trusted runner/host/client/provider evidence required\n",
        )


if __name__ == "__main__":
    main()
