"""Managed host adapters for the Note/Task gate."""

import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from contextlib import ExitStack

from gate import (
    HERE,
    SOURCE,
    command,
    copy_tree,
    read,
    require,
    response,
    sha,
    wait_for,
)


def json_call(*args, **kwargs):
    return response(*args, "-o", "json", **kwargs)


def environment(args, root, app, identity):
    host = args.workspace_host
    require(host and re.fullmatch(r"[a-zA-Z0-9.-]+", host), "workspace host required")
    require(
        args.workspace_id and args.workspace_id.isdecimal(), "workspace ID required"
    )
    origin = app["url"].rstrip("/")
    require(re.fullmatch(r"https://[a-zA-Z0-9.-]+", origin), "invalid app origin")
    variables = dict(
        APP_ORIGIN=origin,
        FIXTURE_SUBJECT_ID=str(identity["id"]),
        FIXTURE_WORKSPACE_HOST=host,
        FIXTURE_WORKSPACE_ID=args.workspace_id,
    )
    require(variables["FIXTURE_SUBJECT_ID"].isdecimal(), "invalid fixture subject")
    document = {
        "command": [
            "uv",
            "run",
            "--no-sync",
            "--offline",
            "--no-python-downloads",
            "python",
            "app_launcher.py",
        ],
        "env": [{"name": key, "value": value} for key, value in variables.items()],
    }
    (root / "app.yaml").write_text(json.dumps(document))
    return origin


def apps(args, packet, work, run_id):
    require(
        args.app and args.app.startswith("batten-qualification-"),
        "dedicated qualification app required",
    )
    tools = read(HERE / "toolchain-20261111.json")
    require(
        command("databricks", "--version", capture=True).strip()
        == tools["databricksCLI"],
        "Databricks CLI version differs",
    )
    profile = ("--profile", args.profile)
    cli = ("databricks", *profile)
    app = json_call(*cli, "apps", "get", args.app)
    require(
        app["compute_status"]["state"] == "STOPPED", "dedicated app must start stopped"
    )
    identity = json_call(*cli, "current-user", "me")
    username = identity["userName"]
    require(re.fullmatch(r"[A-Za-z0-9_.@+-]+", username), "invalid workspace username")
    remote = f"/Workspace/Users/{username}/batten-note-task-{run_id}"
    stage = work / "deployment"
    copy_tree(packet / "postgres", stage)
    copy_tree(packet / "apps", stage)
    origin = environment(args, stage, app, identity)
    # Load the pinned client without writing bytecode into the staged tree.
    spec = importlib.util.spec_from_file_location(
        "note_task_http", stage / "exercise.py"
    )
    require(spec is not None and spec.loader is not None, "missing pinned exercise")
    exercise = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(exercise)
    finally:
        sys.dont_write_bytecode = old
    with ExitStack() as cleanup:
        cleanup.callback(
            command, *cli, "workspace", "delete", remote, "--recursive", capture=True
        )
        command(*cli, "workspace", "import-dir", stage, remote, capture=True)
        cleanup.callback(stop_app, cli, args.app)
        command(*cli, "apps", "start", args.app, "--no-wait", capture=True)
        wait_for(lambda: idle_app(cli, args.app, "ACTIVE"), limit=480)
        wait_for(lambda: deploy_app(cli, args.app, remote), limit=480)
        token = json_call("databricks", "auth", "token", args.profile)["access_token"]
        result = replay_apps(stage, origin, token, exercise)
    stopped = json_call(*cli, "apps", "get", args.app)
    require(stopped["compute_status"]["state"] == "STOPPED", "Apps cleanup unverified")
    return {**result, "computeStopped": True, "workspaceSourceDeleted": True}


def deploy_app(cli, app, remote):
    result = subprocess.run(
        (*cli, "apps", "deploy", app, "--source-code-path", remote, "--timeout", "8m"),
        capture_output=True,
        text=True,
        timeout=510,
        check=False,
    )
    if result.returncode == 0:
        return True
    if "deployment in progress" in result.stderr:
        return None
    raise RuntimeError(
        f"Databricks deployment failed with exit code {result.returncode}"
    )


def idle_app(cli, app, compute):
    state = json_call(*cli, "apps", "get", app)
    if state["compute_status"]["state"] != compute:
        return None
    busy = {"IN_PROGRESS", "PENDING"}
    if any(
        (state.get(key) or {}).get("status", {}).get("state") in busy
        for key in ("active_deployment", "pending_deployment")
    ):
        return None
    return state


def stop_app(cli, app):
    def stop_when_idle():
        if idle_app(cli, app, "STOPPED"):
            return True
        if idle_app(cli, app, "ACTIVE"):
            command(*cli, "apps", "stop", app, "--no-wait", capture=True)
            return True
        return None

    wait_for(stop_when_idle, limit=480)
    wait_for(lambda: idle_app(cli, app, "STOPPED"), limit=330)


def replay_apps(stage, origin, token, exercise):
    def diagnostics():
        request = urllib.request.Request(
            origin + "/__fixture/diagnostics",
            headers={"Authorization": "Bearer " + token, "Origin": origin},
        )
        with urllib.request.urlopen(request, timeout=30) as reply:
            return json.load(reply)

    def gateway_ready():
        try:
            return diagnostics()
        except urllib.error.HTTPError as error:
            if error.code not in {502, 503, 504}:
                raise
            return None

    before = wait_for(gateway_ready, limit=150)
    require(
        not before["databaseLeases"] and all(before["compilerModulesAbsent"].values()),
        "Apps reader baseline differs",
    )
    verified = before["installedWheels"]
    require(
        verified["candidateImportsFromSitePackages"]
        and len(verified["wheelFilesVerified"]) == 5,
        "Apps did not load the candidate wheels",
    )
    for cohort in ("reader", "admin"):
        require(
            verified[f"{cohort}LockSha256"] == sha(stage / f"{cohort}.lock"),
            "Apps lock differs",
        )
    events = exercise.replay(origin, token=token)
    after = diagnostics()
    require(
        after["apiDigest"]
        == before["apiDigest"]
        == read(stage / "prepared-api.json")["apiDigest"],
        "Apps API digest differs",
    )
    opened = sorted(pid for phase, pid in after["databaseLeases"] if phase == "open")
    closed = sorted(pid for phase, pid in after["databaseLeases"] if phase == "close")
    require(
        opened == closed and len(opened) == 12 and len(events) == 12,
        "Apps replay coverage differs",
    )
    forward = events[-1]["response"]
    inspection = forward.pop("inspection")
    require(
        forward["compilerModulesAbsent"]
        and forward["preservedNotes"] == forward["preservedTasks"] == 6
        and inspection["generation"] == 2
        and inspection["headDigest"] == forward["head"],
        "Apps migration proof differs",
    )
    return dict(
        events=events,
        leases=len(opened),
        installedWheels=verified,
        compilerModulesAbsent=True,
        inspectedGeneration=2,
    )


def workers(args, packet, work, run_id):
    account = args.cloudflare_account
    require(
        account and re.fullmatch(r"[a-f0-9]{32}", account),
        "explicit Cloudflare account required",
    )
    tools = read(HERE / "toolchain-20261111.json")
    for executable in ("node", "npm"):
        require(
            command(executable, "--version", capture=True).strip() == tools[executable],
            f"{executable} version differs",
        )
    copy_tree(packet / "workers", work)
    # npm's lock pins Wrangler and transitive integrity. Lifecycle scripts are disabled.
    command("npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund", cwd=work)
    wrangler = work / "node_modules/.bin/wrangler"
    env = {
        **os.environ,
        "CLOUDFLARE_ACCOUNT_ID": account,
        "WRANGLER_SEND_METRICS": "false",
    }

    def cf(*values, **options):
        return command(wrangler, *values, cwd=work, env=env, capture=True, **options)

    require(cf("--version").strip().endswith("4.157.0"), "Wrangler version differs")
    cf("d1", "list", "--json")
    name = f"batten-note-task-{run_id}"
    worker, workflow = f"{name}-worker", f"{name}-workflow"
    with ExitStack() as cleanup:
        cleanup.callback(cleanup_database, cf, name)
        created = cf("d1", "create", name)
        identifier = re.search(r'"database_id"\s*:\s*"([a-f0-9-]{36})"', created)
        require(identifier is not None, "D1 create did not report a database ID")
        config = dict(
            name=worker,
            account_id=account,
            main="main.py",
            compatibility_date="2026-11-04",
            compatibility_flags=["python_workers", "python_workflows"],
            workers_dev=False,
            preview_urls=False,
            d1_databases=[
                dict(binding="DB", database_name=name, database_id=identifier[1])
            ],
            workflows=[
                dict(
                    name=workflow,
                    binding="QUALIFICATION",
                    class_name="QualificationWorkflow",
                )
            ],
        )
        (work / "wrangler.json").write_text(json.dumps(config))
        cleanup.callback(cleanup_worker, cf, worker, workflow)
        cf("deploy")
        cf("workflows", "trigger", workflow, "--id", "qualification", "--json")
        result = wait_for(lambda: workflow_result(cf, workflow), limit=150)
        check_worker_result(work, result)
    return {
        **result,
        "workflowDeleted": True,
        "workerDeleted": True,
        "databaseDeleted": True,
    }


def cleanup_database(cf, name):
    databases = json.loads(cf("d1", "list", "--json"))
    if any(database["name"] == name for database in databases):
        cf("d1", "delete", name, "--skip-confirmation")
    require(
        not any(
            database["name"] == name
            for database in json.loads(cf("d1", "list", "--json"))
        ),
        "D1 cleanup unverified",
    )


def cleanup_worker(cf, worker, workflow):
    with ExitStack() as cleanup:
        cleanup.callback(cf, "delete", "--name", worker)
        cf("workflows", "delete", workflow)


def workflow_result(cf, workflow):
    state = json.loads(
        cf("workflows", "instances", "describe", workflow, "qualification", "--json")
    )
    if state["status"] in {"errored", "terminated"}:
        failed = [
            step.get("name") for step in state.get("steps", ()) if step.get("error")
        ]
        raise RuntimeError(f"Workers replay failed: {failed}")
    return state["output"] if state["status"] == "complete" else None


def check_worker_result(work, result):
    require(
        result["passed"]
        and result["compilerModulesAbsent"]
        and result["sourceSha256"] == SOURCE,
        "Workers runtime receipt differs",
    )
    for name, key in (
        ("read", "readSha256"),
        ("write", "writeSha256"),
        ("migration", "migrationSha256"),
    ):
        require(
            sha(work / f"{name}.json") == result[key], "Workers artifact pin differs"
        )
    require(
        read(work / "prepared-api.json")["apiDigest"] == result["apiDigest"],
        "Workers API differs",
    )
    requests, migration = result["requests"], result["migration"]
    require(
        requests["joinRows"] == 1
        and requests["relayPages"] == 2
        and all(
            requests[name]
            for name in (
                "relayReadback",
                "writeApplied",
                "observeRecovered",
                "invokeRetry",
                "ownerIsolation",
                "wrongApiRefused",
            )
        ),
        "Workers HTTP coverage differs",
    )
    require(
        migration["retainedNotes"] == migration["retainedTasks"] == 3
        and migration["retainedReceipts"] == 2
        and migration["foreignKeysValid"]
        and migration["recoveredLostReply"]
        and migration["staleReplayRefused"],
        "Workers migration proof differs",
    )
