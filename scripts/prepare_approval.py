"""Assemble an isolated pinned platform cohort, original SDK wheels and app assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

UMF_RELEASE = "umf-v0.5.8"
UMF_WHEELS = {
    "umf_access-0.1.0.dev8-py3-none-any.whl": "1a21c1ddd59f6b23e9f0b33228280564af0e96bb4d13699b89616d5143e4fd23",
    "umf_codegen-0.1.0a5-py3-none-any.whl": "36a6f7e0ab92feb9cb20ed8842cc3c1f073cdd3ff2c4edff137c1fcbc3ace158",
}


def run(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def upstream_wheels(wheels: Path) -> list[str]:
    wheels.mkdir(parents=True, exist_ok=True)
    urls = {
        name: f"https://github.com/DocumentDrivenDX/umf/releases/download/{UMF_RELEASE}/{name}"
        for name in UMF_WHEELS
    }
    result: list[str] = []
    for name, digest in UMF_WHEELS.items():
        path = wheels / name
        if not path.exists():
            from urllib.request import urlopen

            with urlopen(urls[name], timeout=60) as response:
                path.write_bytes(response.read())
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"upstream wheel digest mismatch: {name}")
        result.append(str(path))
    return result


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
    parser.add_argument("--app-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.app_only:
        refresh_app(root)
        return
    assets(root)
    wheels = root / ".cache/approval-wheels"
    wheels.mkdir(parents=True, exist_ok=True)
    built = upstream_wheels(wheels)
    projects = [
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
    for project in projects:
        metadata = tomllib.loads((project / "pyproject.toml").read_text())["project"]
        name = metadata["name"].replace("-", "_")
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
        built.append(str(wheels / f"{name}-{metadata['version']}-py3-none-any.whl"))
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
        "umf_release": UMF_RELEASE,
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
