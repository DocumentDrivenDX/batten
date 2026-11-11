"""Fabricated externally pinned artifact for public adapter boundary scenarios."""

import hashlib
import json

from umf_access_generated_executor import (
    AdmittedNativeTable,
    GeneratedFiles,
    GeneratedManifest,
    TargetBinding,
    TrustedArtifactRef,
    prepare_generated,
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def native_fixture() -> AdmittedNativeTable:
    """No executable program: this scenario tests host/port wiring, never SQL."""
    configuration: dict[str, object] = {
        "schema": "fabricated",
        "module": "fabricated",
        "ownerRole": "fixture_owner",
        "personRole": "fixture_person",
        "batchRole": "fixture_batch",
        "groupRoles": {},
    }
    native: dict[str, object] = {
        "version": "umf.native-table-source/1",
        "bundleDigest": "c" * 64,
        "sourceDigest": "b" * 64,
        "configurationDigest": digest(configuration),
        "configuration": configuration,
        "expectedCatalog": {"tables": [], "checks": []},
        "operations": [{"id": "inspect", "kind": "query"}],
    }
    program: dict[str, object] = {
        "status": "compiled",
        "version": "weft.table-operation/0.1",
        "module": "fabricated",
        "operation": "inspect",
        "binding": {"modelSha256": "b" * 64},
        "modelSha256": "b" * 64,
        "transport": {},
        "dbapiSql": "SELECT 1",
        "nativeDescriptionSql": "SELECT 1",
        "dbapiParameterOrder": [],
        "parameterSources": [],
        "outputs": [],
        "result": {"kind": "many"},
        "obligations": {},
    }
    exported: dict[str, object] = {
        "version": "weft.generated-query-program/1",
        "readiness": "export-only",
        "programDigest": digest(program),
        "program": program,
        "source": {
            "modelSha256": "b" * 64,
            "module": "fabricated",
            "operation": "inspect",
        },
        "target": {"id": "postgresql18", "modelSha256": "b" * 64},
        "parameterOrder": [],
        "parameters": [],
        "parameterSources": [],
        "outputs": [],
        "obligations": {},
        "template": {},
    }
    files = GeneratedFiles.from_mapping({
        "native/native-table-source.json": canonical(native),
        "programs/inspect.json": canonical(exported),
    })
    target = TargetBinding("postgresql18", "pg18/1", "18", "d" * 64)
    payload = {
        "version": "weft.generated-execution/1",
        "artifactId": "fabricated-app",
        "source": {
            "documentId": "fabricated",
            "coreVersion": "0.10.0",
            "sha256": "b" * 64,
            "moduleIds": ["fabricated"],
            "bundleInputDigest": "e" * 64,
        },
        "generator": {
            "umfDistribution": "umf-core",
            "umfVersion": "0.10.0",
            "umfSourceDigest": "1" * 64,
            "weftDistribution": "weft-sql",
            "weftVersion": "0.4.54",
            "weftSourceDigest": "2" * 64,
            "abi": "weft.generated-execution/1",
        },
        "executor": {
            "abiMajor": 1,
            "minMinor": 0,
            "maxMinor": 0,
            "packageId": "umf-access-generated-executor",
        },
        "target": {
            "id": target.id,
            "profile": target.profile,
            "version": target.version,
            "bindingDigest": target.binding_digest,
        },
        "algebra": {},
        "programs": {
            "inspect": {"kind": "query", "programPath": "programs/inspect.json"}
        },
        "inventory": dict(files.inventory),
    }
    payload_digest = digest(payload)
    manifest = {
        **payload,
        "provenance": {
            "receiptDigest": "3" * 64,
            "issuer": "fabricated-build",
            "buildId": "fixture",
        },
    }
    artifact_digest = digest(manifest)
    manifest["artifactDigest"] = artifact_digest
    trusted = TrustedArtifactRef(
        "fabricated-app",
        artifact_digest,
        "3" * 64,
        payload_digest,
        "b" * 64,
        target.binding_digest,
        files.inventory,
        "fabricated-build",
        "fixture",
    )
    executor = prepare_generated(
        GeneratedManifest.from_json(canonical(manifest)), files, trusted, target
    )
    return executor.native_table
