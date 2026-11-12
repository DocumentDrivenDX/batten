"""Pure value loaders for genuine prepared API4 and generated profile7 data."""

import hashlib
import json
from pathlib import Path

from batten.contracts import ArtifactRef
from batten.lintel import ExposureConfig, ExposureRecordRoot
from lintel.projection import AdmittedPreparedApi, TrustedPreparedRef, load_prepared_api
from read_artifacts import read_executor
from umf_access_generated_executor import GeneratedExecutor


def prepared_api4_inputs() -> tuple[bytes, TrustedPreparedRef]:
    folder = Path(__file__).parent / "fixtures/generated-page7-rich"
    artifact = (folder / "prepared-api-v4-rich-proof.json").read_bytes()
    trust = json.loads((folder / "prepared-api-v4-rich-trust.json").read_bytes())
    return artifact, TrustedPreparedRef(
        trust["artifactSha256"],
        trust["artifactDigest"],
        trust["application"],
        trust["apiDigest"],
        trust["exposureSha256"],
        tuple((item["identity"], item["sha256"]) for item in trust["sources"]),
        tuple(map(tuple, trust["capabilities"])),
        trust["bindingProfile"],
        trust["scalarCodecProfile"],
        tuple(map(tuple, trust["limits"])),
        trust["generatedRootsSha256"],
        trust["generatedConnectionsSha256"],
    )


def prepared_api4_exposure(
    prepared: AdmittedPreparedApi, executor: GeneratedExecutor
) -> ExposureConfig:
    trust = executor.trusted_artifact
    algebra_sha256 = hashlib.sha256(executor.read_algebra_json).hexdigest()
    host_ids = {"Note": "records.note", "Task": "records.task"}
    roots = tuple(
        ExposureRecordRoot(
            record.lookup,
            host_ids[record.type_name],
            executor.native_table.source_digest,
            trust.artifact_digest,
            trust.receipt_digest,
            executor.target.binding_digest,
            algebra_sha256,
            record.key_id,
            tuple(field.source for field in record.fields),
            ("string",),
            tuple(
                (
                    field.source,
                    "decimalToken" if field.scalar == "decimal" else field.scalar,
                )
                for field in record.fields
            ),
        )
        for record in prepared.records
    )
    return ExposureConfig(
        ArtifactRef(prepared.application, prepared.artifact_digest),
        prepared.api_digest,
        executor.native_table.source_digest,
        (),
        dict(prepared.capabilities),
        roots,
    )


def api4_constructor_case() -> tuple[
    AdmittedPreparedApi, GeneratedExecutor, ExposureConfig
]:
    executor, _root = read_executor("v7-rich")
    prepared = load_prepared_api(*prepared_api4_inputs())
    config = prepared_api4_exposure(prepared, executor)
    return prepared, executor, config
