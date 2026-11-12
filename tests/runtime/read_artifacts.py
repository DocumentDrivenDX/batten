"""Load a frozen fabricated generated artifact without a compiler dependency."""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from umf_access_generated_executor import (
    GeneratedExecutor,
    GeneratedFiles,
    GeneratedManifest,
    TargetBinding,
    TrustedArtifactRef,
    prepare_generated,
)


def read_executor(version: str = "v1") -> tuple[GeneratedExecutor, dict[str, object]]:
    if version in {"v7", "v7-rich"}:
        folder_name = (
            "generated-page7-rich"
            if version == "v7-rich"
            else "generated-page7-combined"
        )
        folder = Path(__file__).parent / "fixtures" / folder_name
        captured = {
            "manifest.json": (folder / "artifact/manifest.json").read_text(),
            "algebra/read.json": (folder / "artifact/algebra/read.json").read_text(),
            "native/native-table-source.json": (
                folder / "artifact/native/native-table-source.json"
            ).read_text(),
        }
        trust = json.loads((folder / "trusted-artifact.json").read_bytes())
        payload_digest = trust["payloadDigest"]
    else:
        name = {
            "v1": "generated_read_fixture.json",
            "v2": "generated_read_v2_fixture.json",
            "v3": "generated_read_v3_fixture.json",
            "v4": "generated_read_v4_fixture.json",
            "v5": "generated_read_v5_fixture.json",
        }[version]
        captured = json.loads(Path(__file__).with_name(name).read_bytes())["entries"]
        trust = json.loads(captured["trusted-artifact.json"])
        receipt = json.loads(captured["receipt.json"])
        payload_digest = receipt["payloadDigest"]
    manifest = GeneratedManifest.from_json(captured["manifest.json"])
    target = cast(Mapping[str, str], manifest.value["target"])
    executor = prepare_generated(
        manifest,
        GeneratedFiles.from_mapping({
            path: content.encode()
            for path, content in captured.items()
            if path not in {"manifest.json", "trusted-artifact.json", "receipt.json"}
        }),
        TrustedArtifactRef(
            trust["artifactId"],
            trust["artifactDigest"],
            trust["receiptDigest"],
            payload_digest,
            trust["sourceDigest"],
            trust["targetBindingDigest"],
            tuple(map(tuple, trust["inventory"])),
            trust["issuer"],
            trust["buildId"],
        ),
        TargetBinding(
            target["id"], target["profile"], target["version"], target["bindingDigest"]
        ),
    )

    return executor, json.loads(captured["algebra/read.json"])["roots"]["demo/Note"]
