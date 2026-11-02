"""Assemble an isolated pinned platform cohort, original SDK wheels and app assets."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

UMF_REVISION = "b12a489844f29947ee52115b90f4ccc5c8bc5032"
UMF_PATHS = [
    "src",
    "spec",
    "python",
    "scripts/codegen",
    "scripts/build-codegen.ts",
    "package.json",
    "bun.lock",
    "patches",
    ".helix.yml",
]


def run(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def upstream(root: Path, source: Path) -> Path:
    target = root / ".cache/approval-umf"
    ready = target / "batten-source.json"
    if ready.exists():
        if json.loads(ready.read_text())["revision"] != UMF_REVISION:
            raise ValueError("cached SDK source differs")
        return target
    target.mkdir(parents=True, exist_ok=True)
    if not (source / ".git").exists():
        source = root / ".cache/umf-source"
        source.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q"], source)
        run(
            [
                "git",
                "fetch",
                "--depth=1",
                "https://github.com/DocumentDrivenDX/umf.git",
                UMF_REVISION,
            ],
            source,
        )
    archive = subprocess.check_output(
        ["git", "archive", UMF_REVISION, *UMF_PATHS], cwd=source
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(target, filter="data")
    run(["bun", "install", "--frozen-lockfile", "--production"], target)
    run(["bun", "scripts/build-codegen.ts"], target)
    ready.write_text(
        json.dumps({
            "revision": UMF_REVISION,
            "source": "original public archive; rebuilt by original packaging script",
        })
    )
    return target


def assets(root: Path) -> Path:
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
    return target


def refresh_app(root: Path) -> None:
    runtime = root / ".cache/approval-runtime/bin/python"
    receipt_path = root / ".cache/approval-cohort.json"
    if not runtime.exists() or not receipt_path.exists():
        raise ValueError("prepare the complete platform cohort first")
    assets(root)
    wheels = root / ".cache/approval-wheels"
    run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--wheel",
            "--outdir",
            str(wheels),
            str(root / "examples/approval-desk"),
        ],
        root,
    )
    wheel = next(wheels.glob("novirhyza_batten_approval_desk-*.whl"))
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(runtime),
            "--no-deps",
            "--reinstall",
            str(wheel),
        ],
        root,
    )
    receipt = json.loads(receipt_path.read_text())
    receipt["wheels"][wheel.name] = hashlib.sha256(wheel.read_bytes()).hexdigest()
    receipt["model_sha256"] = hashlib.sha256(
        (
            root
            / "docs/helix/reference-apps/approval-desk/specs/02-design/models/approval.umf.json"
        ).read_bytes()
    ).hexdigest()
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        "Refreshed installed app; restart the local host to admit its new artifact digest."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--umf-source", type=Path)
    parser.add_argument("--app-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.app_only:
        refresh_app(root)
        return
    source = args.umf_source or root.parent / "umf"
    sdk = upstream(root, source)
    assets(root)
    wheels = root / ".cache/approval-wheels"
    wheels.mkdir(parents=True, exist_ok=True)
    projects = [
        sdk / "python/umf_access",
        sdk / "python/umf_codegen",
        *[
            root / "packages" / ("batten-" + name)
            for name in (
                "contracts",
                "runtime",
                "tables",
                "asgi",
                "umf-postgres",
                "local",
            )
        ],
        root / "examples/approval-desk",
    ]
    built: list[str] = []
    for index, project in enumerate(projects):
        name = tomllib.loads((project / "pyproject.toml").read_text())["project"][
            "name"
        ].replace("-", "_")
        matches = list(wheels.glob(name + "-*.whl"))
        if index < 2:
            if not matches:
                run(
                    [
                        "uv",
                        "build",
                        "--wheel",
                        "--project",
                        str(project),
                        "--out-dir",
                        str(wheels),
                    ],
                    root,
                )
        else:
            run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--wheel",
                    "--outdir",
                    str(wheels),
                    str(project),
                ],
                root,
            )
        built.append(str(next(wheels.glob(name + "-*.whl"))))
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
            "--no-deps",
            "--reinstall",
            *built[:2],
        ],
        root,
    )
    runtime = root / ".cache/approval-runtime"
    if not (runtime / "bin/python").exists():
        run(["uv", "venv", "--python", sys.executable, str(runtime)], root)
    constraints = root / ".cache/approval-constraints.txt"
    lock = tomllib.loads((root / "uv.lock").read_text())
    constraints.write_text(
        "\n".join(
            p["name"] + "==" + p["version"]
            for p in lock["package"]
            if "registry" in p.get("source", {})
        )
        + "\n"
    )
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(runtime / "bin/python"),
            "--constraint",
            str(constraints),
            "--find-links",
            str(wheels),
            "--find-links",
            "https://github.com/DocumentDrivenDX/pgserver/releases/expanded_assets/pg18.6-pgv0.8.6-r2",
            "--find-links",
            "https://github.com/DocumentDrivenDX/weft/releases/expanded_assets/v0.4.51",
            *[
                argument
                for project in projects
                for argument in (
                    "--reinstall-package",
                    tomllib.loads((project / "pyproject.toml").read_text())["project"][
                        "name"
                    ],
                )
            ],
            *built,
        ],
        root,
    )
    receipt = {
        "umf_revision": UMF_REVISION,
        "python": "3.11",
        "wheels": {
            Path(p).name: hashlib.sha256(Path(p).read_bytes()).hexdigest()
            for p in built
        },
        "model_sha256": hashlib.sha256(
            (
                root
                / "docs/helix/reference-apps/approval-desk/specs/02-design/models/approval.umf.json"
            ).read_bytes()
        ).hexdigest(),
        "packages": json.loads(
            subprocess.check_output(
                [
                    str(runtime / "bin/python"),
                    "-I",
                    "-c",
                    "import importlib.metadata,json; print(json.dumps({d.metadata['Name']: d.version for d in importlib.metadata.distributions()}))",
                ],
                text=True,
            )
        ),
    }
    (root / ".cache/approval-cohort.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(
        "Prepared original UMF/Weft/PostgreSQL 18 candidate and installed app artifacts; no schema applied."
    )


if __name__ == "__main__":
    main()
