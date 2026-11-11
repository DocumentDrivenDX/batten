"""Build the approval desk web assets and wheels and install them into .cache/approval-runtime."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGES = ("batten", "batten-local")
FIND_LINKS = "https://github.com/DocumentDrivenDX/pgserver/releases/expanded_assets/pg18.6-pgv0.8.6-r2"


def run(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def assets(root: Path) -> None:
    """Bundle the TypeScript app into .cache/approval-ui, which the app wheel includes."""
    target = root / ".cache/approval-ui"
    target.mkdir(parents=True, exist_ok=True)
    source = root / "examples/approval-desk/web"
    run(
        [
            "bun",
            "build",
            str(source / "app.ts"),
            "--target=browser",
            "--format=esm",
            "--outdir",
            str(target),
        ],
        root,
    )
    for name in ("index.html", "style.css", "tokens.css", "thumbnail.svg"):
        (target / name).write_bytes((source / name).read_bytes())


def build(root: Path, project: Path, wheels: Path) -> Path:
    metadata = tomllib.loads((project / "pyproject.toml").read_text())["project"]
    run(
        [
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(wheels),
            str(project),
        ],
        root,
    )
    name = metadata["name"].replace("-", "_")
    return wheels / f"{name}-{metadata['version']}-py3-none-any.whl"


def constraints(root: Path, path: Path) -> None:
    lock = tomllib.loads((root / "uv.lock").read_text())
    path.write_text(
        "\n".join(
            p["name"] + "==" + p["version"]
            for p in lock["package"]
            if "registry" in p.get("source", {})
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--app-only", action="store_true", help="rebuild only the example app"
    )
    parser.add_argument(
        "--assets-only", action="store_true", help="only bundle the web assets"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    cache = root / ".cache"
    wheels = cache / "approval-wheels"
    runtime = cache / "approval-runtime"
    wheels.mkdir(parents=True, exist_ok=True)
    assets(root)
    if args.assets_only:
        return
    app = root / "examples/approval-desk"
    projects = (
        [app]
        if args.app_only
        else [
            *(root / "packages" / name for name in PACKAGES),
            app,
        ]
    )
    built = [str(build(root, project, wheels)) for project in projects]
    if not (runtime / "bin/python").exists():
        run(["uv", "venv", "--python", sys.executable, str(runtime)], root)
    pins = cache / "approval-constraints.txt"
    constraints(root, pins)
    reinstall = [
        arg
        for wheel in built
        for arg in ("--reinstall-package", Path(wheel).name.split("-")[0])
    ]
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(runtime / "bin/python"),
            "--prerelease=allow",
            "--constraint",
            str(pins),
            "--find-links",
            str(wheels),
            "--find-links",
            FIND_LINKS,
            *reinstall,
            *built,
        ],
        root,
    )
    print("Installed the approval desk into", runtime)


if __name__ == "__main__":
    main()
