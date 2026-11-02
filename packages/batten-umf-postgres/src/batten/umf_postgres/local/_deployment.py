"""Explicit fabricated local installation using the original UMF compiler/ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import psycopg
from pgserver.postgres_server import get_server
from psycopg import sql
from umf_access.lifecycle import apply_table_migration
from umf_codegen import compile_table_deployment, compile_table_migration

JSON = dict[str, Any]


def compile_model(model: Path, configuration: Any) -> tuple[JSON, JSON]:
    compiled = compile_table_deployment(model.read_text(), configuration=configuration)
    if compiled["status"] != "compiled":
        raise ValueError("original UMF deployment compilation refused")
    bundle = compiled["bundle"]
    migration = compile_table_migration(
        migration_id="001", predecessor=None, previous_bundle=None, next_bundle=bundle
    )
    if migration["status"] != "compiled":
        raise ValueError("original UMF initial deployment plan refused")
    return bundle, migration["plan"]


def roles(
    admin: Any,
    configuration: JSON,
    people: dict[str, str],
    memberships: dict[str, list[str]],
) -> None:
    names = [
        configuration["ownerRole"],
        configuration["personRole"],
        configuration["batchRole"],
        *configuration["groupRoles"].values(),
        *people.values(),
    ]
    for role in names:
        admin.execute(
            sql.SQL(
                "CREATE ROLE {} NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION"
            ).format(sql.Identifier(role))
        )
    for role in people.values():
        admin.execute(
            sql.SQL("GRANT {} TO {} WITH INHERIT TRUE, SET FALSE").format(
                sql.Identifier(configuration["personRole"]), sql.Identifier(role)
            )
        )
    for group, subjects in memberships.items():
        for subject in subjects:
            admin.execute(
                sql.SQL("GRANT {} TO {} WITH INHERIT TRUE, SET FALSE").format(
                    sql.Identifier(configuration["groupRoles"][group]),
                    sql.Identifier(people[subject]),
                )
            )
    admin.execute(
        sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}").format(
            sql.Identifier(configuration["schema"]),
            sql.Identifier(configuration["ownerRole"]),
        )
    )


def raw_binding(bundle: JSON) -> JSON:
    model = json.loads(bundle["source"]["utf8"])
    if len(model["modules"]) != 1:
        raise ValueError("local installation slice requires one declared module")
    module = model["modules"][0]
    table = module["extensions"]["umf.tables"]["tables"][0]
    record_id = table["record"]["element"]
    record = next(e for e in module["elements"] if e["id"] == record_id)
    fields = {e["id"]: e for e in module["elements"] if e["kind"] == "field"}
    primary = next(key for key in record["keys"] if key.get("primary"))
    if len(module["extensions"]["umf.tables"]["tables"]) != 1:
        raise ValueError("local installation slice requires one declared table")
    return {
        "version": "umf.raw-read-binding/0.1",
        "schema": bundle["configuration"]["schema"],
        "modelJson": bundle["source"]["utf8"],
        "modelSha256": bundle["sourceDigest"],
        "tables": [
            {
                "logical": [module["namespace"], record["name"]],
                "native": table["name"],
                "key": [fields[ref["element"]]["name"] for ref in primary["fields"]],
                "columns": [
                    {
                        "logical": fields[c["field"]["element"]]["name"],
                        "native": c["name"],
                        "carrier": fields[c["field"]["element"]]["scalarType"],
                        "nullable": fields[c["field"]["element"]]["nullability"]
                        != "required",
                    }
                    for c in table["columns"]
                ],
            }
        ],
        "relationships": [],
        "nativeLifecycle": {
            "version": "umf.table-lifecycle/0.1",
            "module": module["id"],
            "configurationDigest": bundle["configurationDigest"],
            "deploymentDigest": bundle["bundleDigest"],
        },
    }


def initialize(
    data: Path,
    model: Path,
    configuration: JSON,
    people: dict[str, str],
    memberships: dict[str, list[str]],
) -> None:
    if data.exists():
        raise ValueError(
            "local data directory already exists; no implicit adoption/reset"
        )
    bundle, plan = compile_model(model, configuration)
    binding = raw_binding(bundle)
    data.mkdir(parents=True, mode=0o700)
    server = get_server(data / "pgdata", cleanup_mode="stop")
    try:
        with psycopg.connect(server.get_uri(), autocommit=True) as admin:
            if admin.info.server_version // 10000 != 18:
                raise ValueError("PostgreSQL 18 required")
            configuration = bundle["configuration"]
            roles(admin, configuration, people, memberships)
            with admin.transaction():
                admin.execute(
                    sql.SQL("SET LOCAL ROLE {}").format(
                        sql.Identifier(configuration["ownerRole"])
                    )
                )
                admin.execute("SET LOCAL search_path=pg_catalog")
                installed = apply_table_migration(
                    admin,
                    plan,
                    approved_digest=plan["digest"],
                    expected_head=None,
                    person_roles=tuple(people.values()),
                )
        metadata = {
            "version": 1,
            "people": people,
            "bundle": bundle,
            "reference": installed["installationReference"],
            "binding": binding,
        }
        (data / "deployment.json").write_text(json.dumps(metadata))
        fd = os.open(
            data / "host-material.bin", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(os.urandom(64))
    finally:
        server.cleanup()
