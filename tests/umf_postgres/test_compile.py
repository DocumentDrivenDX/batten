"""The approval model compiles with the released umf-codegen, without a database."""

from __future__ import annotations

from pathlib import Path

import pytest
from approval_desk.cli import application
from batten.umf_postgres.local._deployment import compile_model, raw_binding

MODEL = (
    Path(__file__).resolve().parents[2]
    / "examples/approval-desk/model/approval.umf.json"
)


def configuration(tmp_path: Path) -> dict[str, object]:
    return dict(application(MODEL, tmp_path).database)


def test_approval_model_compiles_to_a_bundle_and_an_initial_plan(
    tmp_path: Path,
) -> None:
    bundle, plan = compile_model(MODEL, configuration(tmp_path))
    assert bundle["configuration"]["schema"] == "approval_app"
    assert bundle["sourceDigest"] and bundle["bundleDigest"]
    assert plan["digest"]


def test_raw_binding_describes_the_single_request_table(tmp_path: Path) -> None:
    bundle, _plan = compile_model(MODEL, configuration(tmp_path))
    binding = raw_binding(bundle)
    assert binding["schema"] == "approval_app"
    assert binding["modelSha256"] == bundle["sourceDigest"]
    (table,) = binding["tables"]
    assert table["key"] and table["columns"]


def test_an_invalid_model_is_refused(tmp_path: Path) -> None:
    broken = tmp_path / "broken.umf.json"
    broken.write_text('{"modules": []}')
    with pytest.raises(ValueError, match="refused"):
        compile_model(broken, configuration(tmp_path))
