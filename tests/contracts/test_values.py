"""Value types shared by every host and provider."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from batten.contracts import (
    Actor,
    ArtifactRef,
    HostConfig,
    Operation,
    OperationCall,
    OperationOutcome,
)


def test_values_are_immutable_and_compare_by_content() -> None:
    artifact = ArtifactRef("app", "d1")
    assert artifact == ArtifactRef("app", "d1")
    assert artifact != ArtifactRef("app", "d2")
    assert len({artifact, ArtifactRef("app", "d1")}) == 1
    with pytest.raises(FrozenInstanceError):
        setattr(artifact, "digest", "d2")


def test_actor_session_is_not_printed() -> None:
    actor = Actor("alex", "secret-cookie")
    assert "secret-cookie" not in repr(actor)
    assert Actor("alex").session is None


def test_call_defaults_to_an_unkeyed_invoke() -> None:
    call = OperationCall("submit", {"summary": "x"}, Actor("alex"))
    assert (call.key, call.phase) == (None, "invoke")


def test_outcome_code_is_optional_and_config_keeps_operation_order() -> None:
    assert OperationOutcome("succeeded", "k", {}).code is None
    operations = (Operation("read", False), Operation("write", True))
    config = HostConfig(ArtifactRef("a", "d"), operations, 2, 1.5)
    assert [op.id for op in config.operations] == ["read", "write"]
    assert [op.mutation for op in config.operations] == [False, True]
