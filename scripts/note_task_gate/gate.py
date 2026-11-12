"""Run the pinned Note/Task release gate and emit a cleanup-aware receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import ExitStack
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = "7535ca6ecc10dd439ef48679183d05f3a6d36d5c25f7e5d9514294952d38a087"
PYTHON_IMAGE = "sha256:726d304906fa5eb468e5531e366548d1903286352f5adb54ef508ac01fbd80c6"
POSTGRES_IMAGE = (
    "sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336"
)


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def command(*args, cwd=None, env=None, timeout=300, capture=False):
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        timeout=timeout,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    ).stdout


def response(*args, **kwargs):
    return json.loads(command(*args, capture=True, **kwargs))


def verify(packet):
    pins = read(HERE / "packet-20261111.json")
    members = set()
    for path in packet.rglob("*"):
        relative = path.relative_to(packet).as_posix()
        require(not path.is_symlink(), f"packet symlink: {relative}")
        if path.is_file():
            members.add(relative)
            require(
                relative in pins and sha(path) == pins[relative],
                f"packet pin differs: {relative}",
            )
        else:
            require(path.is_dir(), f"invalid packet entry: {relative}")
    require(members == pins.keys(), "packet inventory is incomplete")
    for target in ("postgres", "workers"):
        require(
            sha(packet / target / "source.umf.json") == SOURCE, "UMF source differs"
        )
    return len(members)


def copy_tree(source, target):
    shutil.copytree(source, target, dirs_exist_ok=True)


def pg_results(directory):
    logs = directory / "logs"
    reader, admin, initial, host, forward = (
        read(logs / name)
        for name in (
            "reader-installed.json",
            "admin-installed.json",
            "initial-result.json",
            "host-result.json",
            "forward-result.json",
        )
    )
    require(host["status"] == forward["status"] == "pass", "PostgreSQL replay failed")
    require(
        all(item["compilerModulesAbsent"] for item in (reader, admin, host, forward)),
        "compiler present",
    )
    require(
        forward["preservedNotes"] == forward["preservedTasks"] == 6
        and forward["inspection"]["generation"] == 2
        and forward["inspection"]["headDigest"] == forward["head"],
        "forward proof differs",
    )
    require(
        host["leases"] == 12 and len(host["events"]) == 12,
        "host replay coverage differs",
    )
    forward.pop("inspection")
    return dict(
        reader=reader,
        administrator=admin,
        host=host,
        forward=forward,
        databaseVersion=initial["databaseVersion"],
        postgresStopped=True,
    )


def local(args, packet, work, target, run_id):
    copy_tree(packet / "postgres", work)
    copy_tree(packet / target, work)
    shutil.copyfile(HERE / "local.sh", work / "local.sh")
    if target == "macos":
        require(
            os.uname().sysname == "Darwin" and os.uname().machine == "arm64",
            "macOS arm64 required",
        )
        require(
            command(args.python, "--version", capture=True).strip() == "Python 3.11.17",
            "macOS CPython version differs",
        )
        require(
            command(args.pg_bin / "postgres", "--version", capture=True).strip()
            == "postgres (PostgreSQL) 18.6 (Homebrew)",
            "macOS PostgreSQL version differs",
        )
        tools = read(HERE / "toolchain-20261111.json")["macos"]
        executables = {
            "python": Path(args.python),
            "uv": args.uv,
            **{name: args.pg_bin / name for name in ("postgres", "initdb", "pg_ctl")},
        }
        for name, path in executables.items():
            require(
                path.is_file() and sha(path) == tools[name],
                f"macOS executable differs: {name}",
            )
        try:
            command(
                "bash", "local.sh", "macos", args.python, args.pg_bin, args.uv, cwd=work
            )
        finally:
            if (work / "pg-data/postmaster.pid").exists():
                command(
                    args.pg_bin / "pg_ctl",
                    "-D",
                    work / "pg-data",
                    "-m",
                    "fast",
                    "-w",
                    "stop",
                )
    else:
        network = f"note-task-{run_id}"
        db = f"{network}-pg"
        for image in (PYTHON_IMAGE, POSTGRES_IMAGE):
            require(
                command(
                    "docker",
                    "image",
                    "inspect",
                    image,
                    "--format",
                    "{{.Architecture}}",
                    capture=True,
                ).strip()
                == "arm64",
                "Linux image architecture differs",
            )
        with ExitStack() as cleanup:
            command("docker", "network", "create", "--internal", network, capture=True)
            cleanup.callback(command, "docker", "network", "rm", network, capture=True)
            command(
                "docker",
                "run",
                "--pull",
                "never",
                "--rm",
                "-d",
                "--name",
                db,
                "--network",
                network,
                "-e",
                "POSTGRES_HOST_AUTH_METHOD=trust",
                POSTGRES_IMAGE,
                capture=True,
            )
            cleanup.callback(command, "docker", "stop", db, capture=True)
            wait_for(
                lambda: command(
                    "docker",
                    "exec",
                    db,
                    "pg_isready",
                    "-h",
                    "127.0.0.1",
                    "-U",
                    "postgres",
                    capture=True,
                    timeout=10,
                ),
                limit=40,
            )
            runner = f"{network}-runner"
            cleanup.callback(remove_container, runner)
            command(
                "docker",
                "run",
                "--pull",
                "never",
                "--rm",
                "--name",
                runner,
                "--network",
                network,
                "-v",
                f"{work}:/input",
                "-e",
                f"FIXTURE_DATABASE_URI=host={db} dbname=postgres user=postgres",
                PYTHON_IMAGE,
                "bash",
                "-ec",
                "cp -R /input /replay; cd /replay; "
                "mkdir -p /input/logs; ln -s /input/logs logs; bash local.sh linux",
                timeout=240,
            )
    return pg_results(work)


def remove_container(name):
    running = command(
        "docker", "ps", "-aq", "--filter", f"name=^{name}$", capture=True
    ).strip()
    if running:
        command("docker", "rm", "-f", name, capture=True)


def wait_for(check, *, limit=240):
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        try:
            if result := check():
                return result
        except subprocess.CalledProcessError:
            pass
        time.sleep(5)
    raise TimeoutError("qualification readiness deadline exceeded")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target", choices=("verify", "macos", "linux", "apps", "workers", "all")
    )
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--uv", type=Path, default=Path(shutil.which("uv") or "uv"))
    parser.add_argument("--pg-bin", type=Path, default=Path("/opt/homebrew/bin"))
    parser.add_argument("--profile", default="aidev-cus")
    parser.add_argument("--app")
    parser.add_argument("--workspace-host")
    parser.add_argument("--workspace-id")
    parser.add_argument("--cloudflare-account")
    return parser.parse_args()


def main():
    require(not sys.flags.optimize, "qualification requires Python assertions")
    args = parse_args()
    packet = args.packet.resolve(strict=True)
    args.python = str(Path(args.python).resolve(strict=True))
    args.uv = args.uv.resolve()
    run_id = uuid.uuid4().hex[:12]
    targets = (
        ("macos", "linux", "apps", "workers")
        if args.target == "all"
        else (args.target,)
    )
    output = {
        "status": "running",
        "runId": run_id,
        "sourceSha256": SOURCE,
        "targets": {},
    }
    require(
        not args.receipt.resolve().is_relative_to(packet),
        "receipt must be outside the packet",
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    try:
        output["verifiedFiles"] = verify(packet)
        for target in targets:
            if target == "verify":
                continue
            with tempfile.TemporaryDirectory(prefix="ntg-", dir="/tmp") as directory:
                work = Path(directory)
                if target in {"macos", "linux"}:
                    result = local(args, packet, work, target, run_id)
                else:
                    import cloud

                    execute = cloud.apps if target == "apps" else cloud.workers
                    result = execute(args, packet, work, run_id)
                output["targets"][target] = result
        output["status"] = "pass"
    except BaseException as error:
        output["status"] = "failed"
        output["errorType"] = type(error).__name__
        raise
    finally:
        args.receipt.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    sys.modules["gate"] = sys.modules[__name__]

    def interrupted(_signal, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    main()
