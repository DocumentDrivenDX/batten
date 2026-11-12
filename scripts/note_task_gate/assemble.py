"""Assemble the immutable release packet from qualified build outputs."""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def copy(source: Path, target: Path, names: str) -> None:
    for name in names.split():
        src, dst = source / name, target / name
        if src.is_dir():
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
        else:
            shutil.copyfile(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("macos", "linux", "linux_wheels", "apps", "workers", "npm", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir()
    pg = out / "postgres"
    pg.mkdir()
    copy(
        args.macos,
        pg,
        """artifacts assets sdk host_app.py exercise.py fixtures
        apply_migration21.py apply_forward.py fixture-deployment.json forward.json
        bundle.json host-artifact-trust.json prepared-api.json prepared-trust.json
        source.umf.json writes.json macos_probe.py verify_installed.py""",
    )
    for host in ("macos", "linux", "apps", "workers"):
        (out / host).mkdir()
    copy(args.macos, out / "macos", "reader.lock admin.lock reader_wheels admin_wheels")
    copy(
        args.apps,
        out / "apps",
        """reader.lock admin.lock reader_wheels admin_wheels
        app_launcher.py reader_server.py verifier.py pyproject.toml uv.lock""",
    )
    apps = out / "apps" / "reader_server.py"
    server = apps.read_text()
    for key in ("ID", "HOST"):
        pattern = rf"(?m)^PINNED_WORKSPACE_{key} = ['\"][^'\"]+['\"]$"
        replacement = f"PINNED_WORKSPACE_{key} = os.environ['FIXTURE_WORKSPACE_{key}']"
        server, changed = re.subn(pattern, replacement, server)
        if changed != 1 and replacement not in server:
            raise ValueError(f"missing workspace fixture assignment: {key}")
    apps.write_text(server)
    linux = out / "linux"
    (linux / "reader_wheels").mkdir()
    lock = args.linux / "linux-candidate.lock"
    shutil.copyfile(lock, linux / "reader.lock")
    for line in lock.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        pin, digest = line.split()
        name, version = pin.split("==")
        pattern = f"{name.replace('-', '_')}-{version}-*.whl"
        candidates = [
            *args.linux.glob(f"candidate-wheels/{pattern}"),
            *args.linux_wheels.glob(pattern),
        ]
        expected = digest.split(":", 1)[1]
        match = next(
            w
            for w in candidates
            if hashlib.sha256(w.read_bytes()).hexdigest() == expected
        )
        shutil.copyfile(match, linux / "reader_wheels" / match.name)
    admin = {
        "annotated-types",
        "psycopg",
        "psycopg-binary",
        "pydantic",
        "pydantic-core",
        "typing-extensions",
        "typing-inspection",
        "umf-access",
    }
    (linux / "admin.lock").write_text(
        "".join(
            line + "\n"
            for line in lock.read_text().splitlines()
            if line.split("==")[0] in admin
        )
    )
    copy(
        args.workers,
        out / "workers",
        """main.py composition.py d1_binding.py d1_runtime.py
        fixture.py python_modules read.json write.json migration.json prepared-api.json
        successor.json source.umf.json successor.umf.json""",
    )
    copy(args.npm, out / "workers", "package.json package-lock.json")
    assert (pg / "source.umf.json").read_bytes() == (
        out / "workers/source.umf.json"
    ).read_bytes()
    files = {
        p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.rglob("*"))
        if p.is_file()
    }
    print(json.dumps(files, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
