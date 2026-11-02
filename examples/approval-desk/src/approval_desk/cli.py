"""Local entry point; business code receives only the public Batten table port."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import tomllib
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path

from batten.asgi import AppListing
from batten.contracts import ArtifactRef, Operation, OperationCall
from batten.hosting.local import LocalApplication, LocalRuntime, LocalSettings

from .operations import ApprovalOperations


def application(model: Path, assets: Path) -> LocalApplication:
    operations = tuple(
        Operation(name, name not in {"list", "get"})
        for name in ("list", "get", "submit", "edit", "decide")
    )
    ordinary = [
        "list",
        "get",
        "submit",
        "edit",
        "tables.list_requests",
        "tables.get_request",
        "tables.submit_request",
        "tables.edit_request",
    ]
    people = {
        subject: {
            "profile": {"name": name, "can_review": subject == "blake"},
            "operations": ordinary
            + (["decide", "tables.decide_request"] if subject == "blake" else []),
        }
        for subject, name in (("alex", "Alex"), ("blake", "Blake"), ("casey", "Casey"))
    }
    digest = hashlib.sha256(model.read_bytes())
    for path in sorted(assets.iterdir()):
        if path.is_file():
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
    digest.update(Path(__file__).with_name("operations.py").read_bytes())
    digest.update(Path(__file__).read_bytes())
    return LocalApplication(
        AppListing(
            "approval-desk",
            "Approval desk",
            "Submit a request, review its current revision, and keep an independent decision with the person who made it.",
            "thumbnail.svg",
        ),
        ArtifactRef("MA-001", digest.hexdigest()),
        model,
        assets,
        operations,
        people,
        {subject: "approval_" + subject for subject in people},
        {"reviewers": ["blake"]},
        {
            "module": "approval",
            "schema": "approval_app",
            "ownerRole": "approval_owner",
            "personRole": "approval_person",
            "batchRole": "approval_batch",
            "groupRoles": {"reviewers": "approval_reviewers"},
        },
        ApprovalOperations,
    )


async def run(args: argparse.Namespace) -> None:
    config = await asyncio.to_thread(lambda: tomllib.loads(args.config.read_text()))
    if set(config) != {
        "port",
        "max_concurrency",
        "timeout_seconds",
        "max_body_bytes",
        "max_sessions",
        "session_ttl_seconds",
    }:
        raise ValueError("unknown/missing local settings")
    definition = await asyncio.to_thread(
        application, args.model.resolve(), args.assets.resolve()
    )
    runtime = LocalRuntime(definition, LocalSettings(args.data.resolve(), **config))
    if args.command == "init":
        await runtime.initialize()
        print("Initialized fabricated PostgreSQL 18 approval workspace.")
        return
    await runtime.open()
    try:
        if args.command == "serve":
            print(
                f"Approval desk: http://127.0.0.1:{runtime.settings.port}", flush=True
            )
            await runtime.serve()
        else:
            await runtime.host.start()
            if not await runtime.host.admit(definition.artifact):
                raise RuntimeError("admission refused")
            cookie = runtime.identities.login(args.actor)
            actor = runtime.identities.resolve(cookie)
            if actor is None:
                raise ValueError("unknown local identity")
            outcome = await runtime.host.invoke(
                OperationCall(
                    args.operation, json.loads(args.inputs), actor, args.key, args.phase
                )
            )
            print(json.dumps(asdict(outcome)))
    finally:
        await runtime.aclose()


def main() -> None:
    resources = Path(str(files("approval_desk")))
    parser = argparse.ArgumentParser(
        description="Fabricated local approval app; no production authentication"
    )
    parser.add_argument("command", choices=["init", "serve", "call"])
    parser.add_argument("--data", type=Path, default=Path(".local/approval"))
    parser.add_argument("--config", type=Path, default=resources / "local.toml")
    parser.add_argument(
        "--model", type=Path, default=resources / "models/approval.umf.json"
    )
    parser.add_argument("--assets", type=Path, default=resources / "web")
    parser.add_argument("--actor", choices=["alex", "blake", "casey"], default="alex")
    parser.add_argument("--operation", default="list")
    parser.add_argument("--inputs", default="{}")
    parser.add_argument("--key")
    parser.add_argument("--phase", choices=["invoke", "observe"], default="invoke")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
