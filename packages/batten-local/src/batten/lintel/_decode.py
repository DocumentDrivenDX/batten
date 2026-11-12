"""Strict safe projection of versioned provider outcomes into Lintel values."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import cast

from batten.lintel._config import ExposureOperation

from lintel.ports import (
    ConnectionPage,
    Edge,
    ElementRef,
    ExecutionError,
    NodeKey,
    NodeValue,
)


def object_value(value: object, keys: set[str]) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ExecutionError("INVALID")
    result = cast(Mapping[str, object], value)
    if set(result) != keys:
        raise ExecutionError("INVALID")
    return result


def sequence(value: object) -> tuple[object, ...]:
    if not isinstance(value, (tuple, list)):
        raise ExecutionError("INVALID")
    return tuple(cast(tuple[object, ...] | list[object], value))


def reference(value: object) -> ElementRef:
    parts = sequence(value)
    if len(parts) != 2 or not all(isinstance(item, str) and item for item in parts):
        raise ExecutionError("INVALID")
    return ElementRef(cast(str, parts[0]), cast(str, parts[1]))


def literal(value: object, wrapper: str | None = None) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or len(cast(Mapping[object, object], value)) != 1:
        raise ExecutionError("INVALID")
    result = cast(Mapping[object, object], value)
    name, inner = next(iter(result.items()))
    allowed = {
        "boolean",
        "string",
        "integerToken",
        "decimalToken",
        "uuid",
        "date",
        "timestamp",
    }
    if name not in allowed or (wrapper is not None and name != wrapper):
        raise ExecutionError("UNSUPPORTED")
    if type(inner) is not (bool if name == "boolean" else str):
        raise ExecutionError("INVALID")
    return MappingProxyType(dict(cast(Mapping[str, object], result)))


def key(value: object, exposure: ExposureOperation) -> NodeKey:
    item = object_value(value, {"record", "keyId", "components"})
    if reference(item["record"]) != exposure.record or item["keyId"] != exposure.key_id:
        raise ExecutionError("INVALID")
    components = sequence(item["components"])
    if len(components) != len(exposure.key_wrappers):
        raise ExecutionError("INVALID")
    return NodeKey(
        exposure.record,
        exposure.key_id,
        tuple(
            literal(part, wrapper)
            for part, wrapper in zip(components, exposure.key_wrappers, strict=True)
        ),
    )


def node(
    value: object, exposure: ExposureOperation, fields: tuple[ElementRef, ...]
) -> NodeValue:
    item = object_value(value, {"key", "fields"})
    values: dict[ElementRef, Mapping[str, object] | None] = {}
    for entry in sequence(item["fields"]):
        field = object_value(entry, {"field", "value"})
        ref = reference(field["field"])
        if ref not in fields or ref in values:
            raise ExecutionError("INVALID")
        values[ref] = (
            None
            if field["value"] is None and ref in exposure.nullable_fields
            else literal(field["value"], dict(exposure.field_wrappers)[ref])
        )
    if set(values) != set(fields):
        raise ExecutionError("INVALID")
    return NodeValue(key(item["key"], exposure), MappingProxyType(values))


def items(
    result: Mapping[str, object],
    kind: str,
    exposure: ExposureOperation,
    fields: tuple[ElementRef, ...],
    requested: tuple[NodeKey, ...],
) -> tuple[NodeValue | None, ...]:
    payload = object_value(result, {"version", "kind", "items"})
    if payload["version"] != "batten.selected-result/1" or payload["kind"] != kind:
        raise ExecutionError("INVALID")
    rows = sequence(payload["items"])
    if len(rows) != len(requested):
        raise ExecutionError("INVALID")
    values = tuple(None if row is None else node(row, exposure, fields) for row in rows)
    if kind == "get_many" and any(
        value is not None and value.key != expected
        for value, expected in zip(values, requested, strict=True)
    ):
        raise ExecutionError("INVALID")
    return values


def connection(
    result: Mapping[str, object],
    exposure: ExposureOperation,
    fields: tuple[ElementRef, ...],
    first: int,
) -> ConnectionPage:
    payload = object_value(
        result, {"version", "kind", "edges", "hasNextPage", "hasPreviousPage"}
    )
    if (
        payload["version"] != "batten.selected-result/1"
        or payload["kind"] != "connection"
        or type(payload["hasNextPage"]) is not bool
        or type(payload["hasPreviousPage"]) is not bool
    ):
        raise ExecutionError("INVALID")
    edges: list[Edge] = []
    for entry in sequence(payload["edges"]):
        edge = object_value(entry, {"cursor", "node"})
        cursor = edge["cursor"]
        if not isinstance(cursor, str) or not cursor:
            raise ExecutionError("INVALID_CURSOR")
        edges.append(Edge(cursor, node(edge["node"], exposure, fields)))
    if len(edges) > first or len({edge.cursor for edge in edges}) != len(edges):
        raise ExecutionError("INVALID")
    return ConnectionPage(
        tuple(edges),
        payload["hasNextPage"],
        payload["hasPreviousPage"],
    )
