"""Compose admitted prepared connection metadata into native and Host routes."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from batten.contracts import connection_routes_digest
from batten.lintel._config import ExposureConfig
from batten.lintel._record_root import ExposureRecordRoot

from lintel.ports import ElementRef, OperationRef

_READ_PROFILES = {
    "lintel.prepared-api/3": "weft.generated-read-algebra/5",
    "lintel.prepared-api/4": "weft.generated-read-algebra/7",
    "lintel.prepared-api/5": "weft.generated-read-algebra/8",
}
_CONNECTION_PROFILE = "connection.forward=edge-cursor-1"

if TYPE_CHECKING:
    from umf_access.generated import GeneratedConnectionRoute
    from umf_access_generated_executor import AdmittedNativeTable, GeneratedExecutor

    from lintel.projection import AdmittedPreparedApi, PreparedConnection


@dataclass(frozen=True, slots=True)
class ConnectionAdmission:
    """Prepared API admission and native routes, ready before Host creation."""

    prepared_api: AdmittedPreparedApi
    native_routes: Mapping[str, GeneratedConnectionRoute]
    prepared_by_name: Mapping[str, PreparedConnection]
    host_operation_by_lookup: Mapping[OperationRef, str]
    max_connections: int
    max_page: int
    cursor_bytes: int
    response_bytes: int
    selected_capabilities: Mapping[str, str]


def prepare_connection_admission(
    config: ExposureConfig,
    prepared_api: AdmittedPreparedApi,
    native: AdmittedNativeTable,
    executor: GeneratedExecutor,
) -> ConnectionAdmission:
    """Join prepared roots to opaque Host operation IDs before constructing Host."""

    _check_admission_pins(config, prepared_api, native, executor)
    roots = {root.ref: root for root in config.record_roots}
    if len(roots) != len(config.record_roots):
        raise ValueError("prepared API Record root references are duplicated")
    limits = _mapping(prepared_api.host_profile.get("limits"))
    max_aliases = _positive_limit(limits.get("maxAliases"))
    max_fields = _positive_limit(limits.get("maxFieldOccurrences"))
    max_page = _positive_limit(limits.get("maxPage"))
    cursor_bytes = _positive_limit(limits.get("cursorBytes"))
    response_bytes = _positive_limit(limits.get("responseBytes"))
    prepared_connections = prepared_api.generated_connections
    if not prepared_connections or len(prepared_connections) > min(
        max_aliases, max_fields
    ):
        raise ValueError("prepared API connection count exceeds admitted limits")
    algebra_roots = _mapping(
        _mapping(json.loads(executor.read_algebra_json)).get("roots")
    )
    native_operations = {operation for operation, _kind in native.operations}
    config_operations = {item.host_operation for item in config.operations}
    routes: dict[str, GeneratedConnectionRoute] = {}
    by_name: dict[str, PreparedConnection] = {}
    operation_by_lookup: dict[OperationRef, str] = {}
    route_pins: list[tuple[str, str, str, str]] = []
    for connection in prepared_connections:
        route, root = _connection_route(
            config,
            connection,
            roots,
            algebra_roots,
            native_operations,
            config_operations,
            routes,
            by_name,
        )
        routes[root.host_operation] = route
        by_name[connection.name] = connection
        operation_by_lookup[connection.lookup] = root.host_operation
        route_pins.append((
            root.host_operation,
            connection.lookup.module,
            connection.lookup.id,
            connection.profile_digest,
        ))
    route_pins.sort()
    selected_capabilities = _generated_pins(config, native, executor, route_pins)
    return ConnectionAdmission(
        prepared_api,
        MappingProxyType(routes),
        MappingProxyType(by_name),
        MappingProxyType(operation_by_lookup),
        min(max_aliases, max_fields),
        max_page,
        cursor_bytes,
        response_bytes,
        MappingProxyType(selected_capabilities),
    )


def _check_admission_pins(
    config: ExposureConfig,
    prepared_api: AdmittedPreparedApi,
    native: AdmittedNativeTable,
    executor: GeneratedExecutor,
) -> None:
    from umf_access_generated_executor import (
        AdmittedNativeTable,
        is_verified_executor_for,
    )

    from lintel.projection import AdmittedPreparedApi

    if (
        type(prepared_api) is not AdmittedPreparedApi
        or type(native) is not AdmittedNativeTable
        or not is_verified_executor_for(executor, native)
        or prepared_api.version not in _READ_PROFILES
        or executor.read_profile != _READ_PROFILES.get(prepared_api.version)
        or any(
            _connection_read_profile(connection, prepared_api.version)
            != _READ_PROFILES[prepared_api.version]
            for connection in prepared_api.generated_connections
        )
        or config.application.id != prepared_api.application
        or config.api_digest != prepared_api.api_digest
        or config.source_digest != native.source_digest
        or config.capabilities.get("connection.forward") != "edge-cursor-1"
        or dict(prepared_api.capabilities).get("connection.forward") != "edge-cursor-1"
        or dict(prepared_api.capabilities).get("read.consistency")
        != "request-snapshot-1"
        or config.source_digest
        not in {digest for _identity, digest in prepared_api.source_digests}
    ):
        raise ValueError("prepared API connection admission pins differ")


def _connection_route(
    config: ExposureConfig,
    connection: PreparedConnection,
    roots: Mapping[OperationRef, ExposureRecordRoot],
    algebra_roots: Mapping[str, object],
    native_operations: set[str],
    config_operations: set[str],
    routes: Mapping[str, GeneratedConnectionRoute],
    by_name: Mapping[str, PreparedConnection],
) -> tuple[GeneratedConnectionRoute, ExposureRecordRoot]:
    from umf_access.generated import (
        AllowedConnectionFieldProfile,
        GeneratedConnectionRoute,
        GeneratedCursorScope,
    )

    from lintel.projection import PreparedConnection, allowed_field_profile_to_dict

    if type(connection) is not PreparedConnection:
        raise ValueError("prepared API connection metadata type differs")
    root = roots.get(connection.lookup)
    if (
        connection.lookup.kind != "record"
        or root is None
        or connection.name in by_name
        or root.host_operation in routes
        or root.host_operation in native_operations
        or root.host_operation in config_operations
    ):
        raise ValueError(
            "prepared API connection does not join one exposed Record root"
        )
    algebra_root = algebra_roots.get(
        connection_root_id(connection.lookup.module, connection.lookup.id)
    )
    if not isinstance(algebra_root, Mapping):
        raise ValueError(
            "prepared API connection Record is absent from generated algebra"
        )
    profile_body = allowed_field_profile_to_dict(connection)
    profile = AllowedConnectionFieldProfile.from_body(profile_body)
    if profile.digest != connection.profile_digest:
        raise ValueError("prepared API allowed Field profile digest differs")
    validate_connection_profile(
        connection, root, cast(Mapping[str, object], algebra_root), profile_body
    )
    route_scope = GeneratedCursorScope(
        config.application.id,
        config.application.digest,
        config.api_digest,
        root.host_operation,
        profile.digest,
    )
    return (
        GeneratedConnectionRoute(
            connection.lookup.module, connection.lookup.id, route_scope, profile
        ),
        root,
    )


def _generated_pins(
    config: ExposureConfig,
    native: AdmittedNativeTable,
    executor: GeneratedExecutor,
    connection_pins: list[tuple[str, str, str, str]],
) -> dict[str, str]:
    trust = executor.trusted_artifact
    algebra_digest = sha256(executor.read_algebra_json).hexdigest()
    records = sorted(
        [root.host_operation, root.ref.module, root.ref.id, root.primary_key_id]
        for root in config.record_roots
    )
    required = {
        "read.consistency": "request-snapshot-1",
        "read.profile": _required_read_profile(executor),
        "connection.forward": "edge-cursor-1",
        "source.digest": native.source_digest,
        "binding.digest": executor.target.binding_digest,
        "algebra.digest": algebra_digest,
        "artifact.digest": trust.artifact_digest,
        "receipt.digest": trust.receipt_digest,
        "records.digest": _digest(records),
        "connection.routes.digest": connection_routes_digest(
            config.application.id,
            config.application.digest,
            config.api_digest,
            trust.artifact_digest,
            tuple(connection_pins),
        ),
    }
    return required


def validate_connection_profile(
    connection: PreparedConnection,
    exposed: ExposureRecordRoot,
    root: Mapping[str, object],
    profile: Mapping[str, object],
) -> None:
    raw_fields = profile.get("fields")
    if type(raw_fields) is not list:
        raise ValueError("prepared API allowed Field profile is unavailable")
    entries = tuple(cast(list[object], raw_fields))
    by_id: dict[str, Mapping[str, object]] = {}
    by_source: dict[ElementRef, str] = {}
    for value in entries:
        item = _mapping(value)
        field_id = item.get("fieldId")
        source = _mapping(item.get("sourceField"))
        module, element = source.get("module"), source.get("element")
        if (
            type(field_id) is not str
            or type(module) is not str
            or type(element) is not str
        ):
            raise ValueError(
                "prepared API allowed Field descriptor differs from issued algebra"
            )
        reference = ElementRef(module, element)
        if field_id in by_id or reference in by_source:
            raise ValueError("prepared API allowed Field descriptors are duplicated")
        by_id[field_id] = item
        by_source[reference] = field_id
    visible = set(connection.field_refs)
    key_reference = connection.primary_key_field
    exposed_fields = set(exposed.fields)
    if (
        not visible.issubset(exposed_fields)
        or key_reference not in _primary_fields(root)
        or set(by_source) != visible | {key_reference}
        or len(by_source) != len(visible | {key_reference})
    ):
        raise ValueError(
            "prepared API connection Fields or Key differ from Record exposure"
        )
    fields = _mapping(root.get("fields"))
    forward = _mapping(root.get("forwardConnection"))
    outputs = {
        cast(str, item["fieldId"]): _mapping(item["output"])
        for value in cast(tuple[object, ...], forward["fieldOutputs"])
        for item in (_mapping(value),)
    }
    for field_id, item in by_id.items():
        issued = _mapping(fields.get(field_id))
        output = outputs.get(field_id)
        if (
            output is None
            or item.get("sourceField") != issued.get("sourceField")
            or item.get("output") != output
            or item.get("scalar") != output.get("carrier")
            or item.get("nullable") != output.get("nullable")
        ):
            raise ValueError(
                "prepared API allowed Field descriptor differs from issued algebra"
            )


def connection_root_id(module: str, record: str) -> str:
    """Build the issued algebra root key from escaped JSON Pointer components."""
    return f"{_escape_component(module)}/{_escape_component(record)}"


def _escape_component(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _primary_fields(root: Mapping[str, object]) -> tuple[ElementRef, ...]:
    fields = _mapping(root.get("fields"))
    result: list[ElementRef] = []
    for value in cast(tuple[object, ...], root["primaryKey"]):
        field_id = cast(str, _mapping(value)["fieldId"])
        field = _mapping(fields.get(field_id))
        source = _mapping(field["sourceField"])
        result.append(
            ElementRef(cast(str, source["module"]), cast(str, source["element"]))
        )
    return tuple(result)


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("prepared API connection metadata is unavailable")
    return cast(Mapping[str, object], value)


def _connection_read_profile(connection: object, api_version: str) -> object:
    profile = getattr(connection, "read_profile", None)
    if profile is None and api_version == "lintel.prepared-api/3":
        return "weft.generated-read-algebra/5"
    return profile


def _required_read_profile(executor: GeneratedExecutor) -> str:
    profile = executor.read_profile
    if type(profile) is not str or profile not in _READ_PROFILES.values():
        raise ValueError("generated connection read profile differs")
    return profile


def _positive_limit(value: object) -> int:
    if type(value) is not str or not value.isascii() or not value.isdecimal():
        raise ValueError("prepared API connection limit is unavailable")
    result = int(value)
    if result <= 0:
        raise ValueError("prepared API connection limit is unavailable")
    return result


def _digest(rows: list[list[str]]) -> str:
    return sha256(
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


__all__ = ["ConnectionAdmission", "prepare_connection_admission"]
