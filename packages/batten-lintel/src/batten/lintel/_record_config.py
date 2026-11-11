"""Join explicit Record exposures to the upstream verifier's immutable metadata."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from batten.lintel._config import ExposureConfig, ExposureOperation
from batten.lintel._record_root import ExposureRecordRoot
from batten.runtime import Host

from lintel.ports import ElementRef, OperationRef

if TYPE_CHECKING:
    from umf_access_generated_executor import AdmittedNativeTable, GeneratedExecutor

_WRAPPERS = {
    "string": "string",
    "boolean": "boolean",
    "integer": "integerToken",
    "decimal": "decimalToken",
    "date": "date",
    "timestamp": "timestamp",
    "uuid": "uuid",
}


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("verified Record metadata is unavailable")
    return cast(Mapping[str, object], value)


def _sequence(value: object) -> tuple[object, ...]:
    if type(value) not in {list, tuple}:
        raise ValueError("verified Record sequence is unavailable")
    return tuple(cast(list[object] | tuple[object, ...], value))


def _reference(value: object) -> ElementRef:
    ref = _mapping(value)
    if set(ref) != {"module", "element"} or any(
        type(part) is not str or not part for part in ref.values()
    ):
        raise ValueError("verified Field reference differs")
    return ElementRef(cast(str, ref["module"]), cast(str, ref["element"]))


def _fields(root: Mapping[str, object], exposed: ExposureRecordRoot) -> None:
    fields = {
        _reference(item["sourceField"]): _mapping(item["output"])
        for value in _mapping(root["fields"]).values()
        for item in (_mapping(value),)
    }
    wrappers = dict(exposed.field_wrappers)
    if (
        len(set(exposed.fields)) != len(exposed.fields)
        or len(wrappers) != len(exposed.field_wrappers)
        or set(wrappers) != set(exposed.fields)
        or not set(exposed.fields).issubset(fields)
    ):
        raise ValueError("Record exposed Fields differ")
    for field in exposed.fields:
        output = fields[field]
        if wrappers[field] != _WRAPPERS.get(cast(str, output["carrier"])):
            raise ValueError("Record Field carrier differs")
    if set(exposed.nullable_fields) != {
        field for field in exposed.fields if fields[field]["nullable"] is True
    }:
        raise ValueError("Record Field presence differs")


def _key(root: Mapping[str, object], exposed: ExposureRecordRoot) -> None:
    batch = _mapping(root["getMany"])
    keys = tuple(_mapping(value) for value in _sequence(batch["keyFields"]))
    originals = tuple(
        _mapping(value)["fieldId"] for value in _sequence(root["primaryKey"])
    )
    wrappers = tuple(
        _mapping(_sequence(_mapping(component["codec"])["steps"])[0])
        for component in keys
    )
    if (
        batch["keyId"] != exposed.primary_key_id
        or root["primaryKeyId"] != exposed.primary_key_id
        or tuple(component["fieldId"] for component in keys) != originals
        or not 1 <= len(keys) <= 16
        or exposed.key_wrappers != ("string",) * len(keys)
        or any(
            step.get("op") != "require-exact-wrapper"
            or step.get("wrapper") != "string"
            or step.get("nullable") is not False
            for step in wrappers
        )
    ):
        raise ValueError(
            "Record primary Key differs from the selected string identity profile"
        )


def _required_record_read_profile(
    connection_lookups: Mapping[OperationRef, str] | None,
    connection_capabilities: Mapping[str, str] | None,
    connection_api_version: str | None,
) -> str | None:
    if connection_lookups is None:
        return "weft.generated-read-algebra/4"
    if connection_api_version == "lintel.prepared-api/3":
        profile = "weft.generated-read-algebra/5"
    elif connection_api_version == "lintel.prepared-api/4":
        profile = "weft.generated-read-algebra/7"
    elif connection_api_version == "lintel.prepared-api/5":
        profile = "weft.generated-read-algebra/8"
    else:
        return None
    if (
        connection_capabilities is None
        or connection_capabilities.get("read.profile") != profile
    ):
        return None
    return profile


def checked_record_roots(
    host: Host,
    config: ExposureConfig,
    native: AdmittedNativeTable,
    executor: GeneratedExecutor,
    *,
    connection_lookups: Mapping[OperationRef, str] | None = None,
    connection_capabilities: Mapping[str, str] | None = None,
    connection_api_version: str | None = None,
) -> Mapping[OperationRef, ExposureOperation]:
    from umf_access_generated_executor import is_verified_executor_for

    profile = (
        _required_record_read_profile(
            connection_lookups, connection_capabilities, connection_api_version
        )
        or ""
    )
    if (
        not is_verified_executor_for(executor, native)
        or executor.read_profile != profile
        or (
            connection_lookups is None
            and config.capabilities.get("identity.codec")
            != "lintel.node-id.string-key/1"
        )
        or config.capabilities.get("read.consistency") != "request-snapshot-1"
    ):
        raise ValueError("Record roots require the verified batch profile")
    trust = executor.trusted_artifact
    algebra_digest = hashlib.sha256(executor.read_algebra_json).hexdigest()
    routes = sorted(
        [item.host_operation, item.ref.module, item.ref.id, item.primary_key_id]
        for item in config.record_roots
    )
    required = {
        "read.consistency": "request-snapshot-1",
        "read.profile": executor.read_profile,
        "source.digest": native.source_digest,
        "binding.digest": executor.target.binding_digest,
        "algebra.digest": algebra_digest,
        "artifact.digest": trust.artifact_digest,
        "receipt.digest": trust.receipt_digest,
        "records.digest": hashlib.sha256(
            json.dumps(routes, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest(),
    }
    if any(
        host.config.selected_capabilities.get(key) != value
        for key, value in required.items()
    ):
        raise ValueError("Record roots differ from selected Host pins")
    if connection_lookups is not None and (
        connection_capabilities is None
        or any(
            host.config.selected_capabilities.get(key) != value
            for key, value in connection_capabilities.items()
        )
    ):
        raise ValueError("connection routes differ from selected Host pins")
    roots = tuple(
        _mapping(value)
        for value in _mapping(
            _mapping(json.loads(executor.read_algebra_json))["roots"]
        ).values()
    )
    operations: dict[OperationRef, ExposureOperation] = {}
    seen = {item.host_operation for item in config.operations} | set(
        dict(native.operations)
    )
    for exposed in config.record_roots:
        operation = host.operations.get(exposed.host_operation)
        matches = [
            root
            for root in roots
            if (root["module"], root["record"]) == (exposed.ref.module, exposed.ref.id)
        ]
        if (
            cast(str, exposed.ref.kind) != "record"
            or exposed.ref in operations
            or exposed.host_operation in seen
            or operation is None
            or operation.mutation
            or "get_many" not in operation.selection_kinds
            or (
                exposed.ref in (connection_lookups or {})
                and "connection" not in operation.selection_kinds
            )
            or len(matches) != 1
            or (
                exposed.source_digest,
                exposed.artifact_digest,
                exposed.receipt_digest,
                exposed.binding_digest,
                exposed.algebra_sha256,
            )
            != (
                native.source_digest,
                trust.artifact_digest,
                trust.receipt_digest,
                executor.target.binding_digest,
                algebra_digest,
            )
        ):
            raise ValueError("Record root differs from admitted inventory")
        _key(matches[0], exposed)
        _fields(matches[0], exposed)
        operations[exposed.ref] = ExposureOperation(
            exposed.ref,
            exposed.host_operation,
            ("get_many", "connection")
            if exposed.ref in (connection_lookups or {})
            else ("get_many",),
            ElementRef(exposed.ref.module, exposed.ref.id),
            exposed.primary_key_id,
            exposed.fields,
            exposed.key_wrappers,
            exposed.field_wrappers,
            nullable_fields=exposed.nullable_fields,
        )
        seen.add(exposed.host_operation)
    return MappingProxyType(operations)
