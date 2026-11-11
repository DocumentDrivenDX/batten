"""Host-composed exposure pins joined to a verified native artifact inventory."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from batten.contracts import ArtifactRef
from batten.runtime import Host

from lintel.ports import ElementRef, OperationRef

from ._record_root import ExposureRecordRoot

if TYPE_CHECKING:
    from umf_access_generated_executor import AdmittedNativeTable

    from lintel.projection import AdmittedPreparedApi


@dataclass(frozen=True)
class ExposureOperation:
    ref: OperationRef
    host_operation: str
    selection_kinds: tuple[str, ...]
    record: ElementRef
    key_id: str
    fields: tuple[ElementRef, ...]
    key_wrappers: tuple[str, ...]
    field_wrappers: tuple[tuple[ElementRef, str], ...]
    related_target: ElementRef | None = None
    parent_record: ElementRef | None = None
    parent_key_id: str | None = None
    parent_key_wrappers: tuple[str, ...] = ()
    nullable_fields: tuple[ElementRef, ...] = ()


@dataclass(frozen=True)
class ExposureConfig:
    application: ArtifactRef
    api_digest: str
    source_digest: str
    operations: tuple[ExposureOperation, ...]
    capabilities: Mapping[str, str]
    record_roots: tuple[ExposureRecordRoot, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "capabilities", MappingProxyType(dict(self.capabilities))
        )


def checked_operations(
    host: Host, config: ExposureConfig, native: AdmittedNativeTable
) -> Mapping[OperationRef, ExposureOperation]:
    from umf_access_generated_executor import AdmittedNativeTable

    if (
        not isinstance(cast(object, native), AdmittedNativeTable)
        or config.application != host.config.artifact
        or config.source_digest != native.source_digest
        or not config.api_digest
    ):
        raise ValueError("exposure artifact pins differ")
    module = native.native_source["configuration"]
    if not isinstance(module, Mapping):
        raise ValueError("native configuration is absent")
    inventory = dict(native.operations)
    result: dict[OperationRef, ExposureOperation] = {}
    routes: set[str] = set()
    for exposed in config.operations:
        operation = host.operations.get(exposed.host_operation)
        kind = inventory.get(exposed.ref.id)
        if (
            exposed.ref in result
            or exposed.host_operation in routes
            or exposed.ref.module != module["module"]
            or exposed.ref.kind != "table"
            or operation is None
            or kind is None
            or operation.mutation != (kind not in {"query", "read"})
            or not set(exposed.selection_kinds).issubset(operation.selection_kinds)
            or len(set(exposed.fields)) != len(exposed.fields)
            or len(dict(exposed.field_wrappers)) != len(exposed.field_wrappers)
            or set(dict(exposed.field_wrappers)) != set(exposed.fields)
            or not set(exposed.nullable_fields).issubset(exposed.fields)
            or not exposed.key_id
        ):
            raise ValueError("exposure operation differs from admitted inventory")
        result[exposed.ref] = exposed
        routes.add(exposed.host_operation)
    return MappingProxyType(result)


def check_prepared_command_routes(
    host: Host,
    config: ExposureConfig,
    operations: Mapping[OperationRef, ExposureOperation],
    prepared: AdmittedPreparedApi | None,
) -> None:
    """Require every exposed command to join an admitted native Host mutation."""
    command_profile = any(
        key in config.capabilities for key in ("command.outcome", "command.observe")
    )
    if not command_profile:
        return
    if (
        prepared is None
        or prepared.api_digest != config.api_digest
        or not prepared.commands
    ):
        raise ValueError("prepared command profile requires admitted command metadata")
    for command in prepared.commands:
        route = operations.get(command.operation)
        if route is None or not host.operations[route.host_operation].mutation:
            raise ValueError(
                "prepared command does not match an admitted Host mutation"
            )
        expected = json.dumps(
            (command.operation.module, command.operation.id),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        if (
            host.config.selected_capabilities.get(
                f"command.operation/{route.host_operation}"
            )
            != expected
            or host.config.selected_capabilities.get("command.outcome") != "1"
            or host.config.selected_capabilities.get("command.observe") != "1"
        ):
            raise ValueError("prepared command differs from selected native Host route")


def check_prepared_relationship_routes(
    host: Host,
    config: ExposureConfig,
    operations: Mapping[OperationRef, ExposureOperation],
    prepared: AdmittedPreparedApi | None,
) -> None:
    if config.capabilities.get("relationship.batch") != "to-one-1":
        return
    if (
        prepared is None
        or prepared.api_digest != config.api_digest
        or not prepared.relationships
        or host.config.selected_capabilities.get("relationship.batch") != "to-one-1"
    ):
        raise ValueError("relationship requires an admitted prepared API and provider")
    for relationship in prepared.relationships:
        route = operations.get(relationship.operation)
        if (
            route is None
            or route.parent_record != relationship.source
            or route.related_target != relationship.target
            or route.record != relationship.target
            or "related_many" not in route.selection_kinds
        ):
            raise ValueError("prepared relationship differs from Host exposure")
        expected = json.dumps(
            (*relationship.relationship, *relationship.target),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        if (
            host.config.selected_capabilities.get(
                f"relationship.operation/{route.host_operation}"
            )
            != expected
        ):
            raise ValueError("prepared relationship differs from native Host route")
