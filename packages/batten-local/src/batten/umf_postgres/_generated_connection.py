"""One-use prepared connection plans and their closed selected-result mapping."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from batten.contracts import (
    OperationCall,
    OperationOutcome,
    SelectedCallSpec,
    SelectedRequestError,
    Selection,
)
from umf_access.unified import GeneratedNativeError

from ._generated_table_routes import ConnectionRoute
from ._generated_values import native_read_refusal
from ._read_result import cell_size, result_sequence

_PLAN_ISSUER = object()


@dataclass(frozen=True)
class PlannedConnection:
    spec: SelectedCallSpec
    native: object
    module: str
    record: str
    source_digest: str
    binding_digest: str
    key_id: str
    key_wrappers: tuple[str, ...]
    field_descriptors: tuple[Mapping[str, object], ...]
    field_ids: tuple[str, ...]


class GeneratedTablePlan:
    """Nominal scope-bound plan; duplicate specs retain distinct occurrences."""

    def __init__(
        self,
        owner: object,
        scope: object,
        calls: tuple[SelectedCallSpec, ...],
        identity: object,
        generated_scope: object,
        items: tuple[PlannedConnection, ...],
        *,
        issuer: object,
    ):
        if issuer is not _PLAN_ISSUER:
            raise ValueError("generated table plan must be provider issued")
        self.owner, self.scope, self.calls = owner, scope, calls
        self.identity, self.generated_scope, self.items = (
            identity,
            generated_scope,
            items,
        )
        self.used: set[int] = set()
        self.opened = False


def issue_table_plan(
    owner: object,
    scope: object,
    calls: tuple[SelectedCallSpec, ...],
    identity: object,
    generated_scope: object,
    items: tuple[PlannedConnection, ...],
) -> GeneratedTablePlan:
    return GeneratedTablePlan(
        owner,
        scope,
        calls,
        identity,
        generated_scope,
        items,
        issuer=_PLAN_ISSUER,
    )


def table_plan_from(value: object, owner: object, scope: object) -> GeneratedTablePlan:
    if (
        type(value) is not GeneratedTablePlan
        or value.owner is not owner
        or value.scope is not scope
        or value.opened
    ):
        raise ValueError("generated table plan scope or issuer differs")
    value.opened = True
    return value


def consume_connection(
    plan: GeneratedTablePlan, call: OperationCall, selection: Selection
) -> tuple[int, PlannedConnection] | None:
    for index, item in enumerate(plan.items):
        if (
            index not in plan.used
            and item.spec.call == call
            and item.spec.selection == selection
        ):
            plan.used.add(index)
            return index, item
    return None


def connection_result(
    result: object, item: PlannedConnection, maximum: int = 8_388_608
) -> dict[str, object] | None:
    try:
        if not isinstance(result, Mapping):
            raise ValueError("native connection frame is not a mapping")
        frame = cast(Mapping[str, object], result)
        expected_refs = tuple(
            {
                "module": cast(
                    str, cast(Mapping[str, object], value["sourceField"])["module"]
                ),
                "element": cast(
                    str, cast(Mapping[str, object], value["sourceField"])["element"]
                ),
            }
            for value in item.field_descriptors
        )
        raw_page = frame.get("pageInfo")
        page = (
            cast(Mapping[str, object], raw_page)
            if isinstance(raw_page, Mapping)
            else None
        )
        if (
            set(frame)
            != {
                "version",
                "sourceDigest",
                "bindingDigest",
                "module",
                "record",
                "fields",
                "edges",
                "pageInfo",
            }
            or frame.get("version") != "umf.generated-forward-connection-result/1"
            or frame.get("sourceDigest") != item.source_digest
            or frame.get("bindingDigest") != item.binding_digest
            or frame.get("module") != item.module
            or frame.get("record") != item.record
            or list(result_sequence(frame["fields"])) != list(expected_refs)
            or page is None
            or set(page) != {"hasNextPage", "hasPreviousPage"}
            or type(page.get("hasNextPage")) is not bool
            or type(page.get("hasPreviousPage")) is not bool
        ):
            raise ValueError("native connection frame pins differ")
        edges = result_sequence(frame["edges"])
        if len(edges) > cast(int, item.spec.selection.first):
            raise ValueError("native connection page exceeds first")
        translated = _edges(edges, item)
        value: dict[str, object] = {
            "version": "batten.selected-result/1",
            "kind": "connection",
            "edges": translated,
            "hasNextPage": page["hasNextPage"],
            "hasPreviousPage": page["hasPreviousPage"],
        }
        if _json_size(value, maximum) > maximum:
            raise ValueError("selected connection result exceeds capacity")
        return value
    except (KeyError, ValueError, TypeError, UnicodeError):
        return None


def _json_size(value: object, maximum: int) -> int:
    encoder = json.JSONEncoder(
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        default=_json_default,
    )
    size = 0
    for chunk in encoder.iterencode(value):
        size += len(chunk.encode("utf-8", errors="strict"))
        if size > maximum:
            return size
    return size


def _json_default(value: object) -> object:
    if isinstance(value, Mapping):
        return dict(cast(Mapping[str, object], value))
    if type(value) is tuple:
        return list(cast(tuple[object, ...], value))
    raise TypeError("selected result contains a non-JSON value")


def _edges(
    edges: tuple[object, ...], item: PlannedConnection
) -> list[dict[str, object]]:
    seen: set[str] = set()
    output: list[dict[str, object]] = []
    selection = item.spec.selection
    for raw_edge in edges:
        edge = _mapping(raw_edge, {"cursor", "node"})
        cursor = edge["cursor"]
        if (
            type(cursor) is not str
            or not cursor
            or len(cursor.encode("utf-8")) > 2_000_000
        ):
            raise ValueError("native edge cursor differs")
        if cursor in seen:
            raise ValueError("native edge cursors are duplicated")
        seen.add(cursor)
        node = _mapping(edge["node"], {"key", "fields"})
        key = _mapping(node["key"], {"keyId", "components"})
        components = result_sequence(key["components"])
        if key["keyId"] != item.key_id or len(components) != len(item.key_wrappers):
            raise ValueError("native edge Key differs")
        for component, wrapper in zip(components, item.key_wrappers, strict=True):
            tagged = _mapping(component, {wrapper})
            if type(tagged[wrapper]) is not str:
                raise ValueError("native edge Key scalar differs")
        values = _mapping(node["fields"], set(item.field_ids))
        selected: dict[tuple[str, str], object] = {}
        for descriptor, field_id in zip(
            item.field_descriptors, item.field_ids, strict=True
        ):
            source = cast(Mapping[str, object], descriptor["sourceField"])
            reference = (cast(str, source["module"]), cast(str, source["element"]))
            cell_size(
                values[field_id], cast(Mapping[str, object], descriptor["output"])
            )
            selected[reference] = values[field_id]
        fields = [
            {"field": list(reference), "value": selected[reference]}
            for reference in selection.fields
        ]
        output.append({
            "cursor": cursor,
            "node": {
                "key": {
                    "record": [item.module, item.record],
                    "keyId": item.key_id,
                    "components": list(components),
                },
                "fields": fields,
            },
        })
    return output


def _mapping(value: object, members: set[str]) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("native connection object shape differs")
    mapping = cast(Mapping[str, object], value)
    if set(mapping) != members:
        raise ValueError("native connection object shape differs")
    return mapping


def connection_fields(
    route: ConnectionRoute, requested: tuple[tuple[str, str], ...]
) -> tuple[tuple[Mapping[str, object], ...], tuple[str, ...]]:
    body = route.allowed_field_profile.body
    descriptors = body.get("fields")
    if (
        body.get("version") != "umf.allowed-connection-fields/1"
        or type(descriptors) is not tuple
    ):
        raise ValueError("connection Field profile is unavailable")
    by_ref: dict[tuple[str, str], tuple[str, Mapping[str, object]]] = {}
    for raw in cast(tuple[object, ...], descriptors):
        item = cast(Mapping[str, object], raw)
        source = cast(Mapping[str, object], item["sourceField"])
        reference = (cast(str, source["module"]), cast(str, source["element"]))
        by_ref[reference] = (cast(str, item["fieldId"]), item)
    if len(set(requested)) != len(requested) or not set(requested).issubset(by_ref):
        raise ValueError("connection Fields exceed the admitted profile")
    chosen = tuple(by_ref[field] for field in requested)
    return tuple(item for _field_id, item in chosen), tuple(
        field_id for field_id, _item in chosen
    )


def field_reference(value: Mapping[str, object]) -> tuple[str, str]:
    source = cast(Mapping[str, object], value["sourceField"])
    return cast(str, source["module"]), cast(str, source["element"])


def connection_preflight_error(error: Exception, schema: str) -> SelectedRequestError:
    if type(error) is GeneratedNativeError:
        code = error.code
        if code == "UNSUPPORTED":
            return SelectedRequestError("invalid", "unsupported")
        refusal = native_read_refusal(
            {"schema": schema, "error": {"code": code}}, schema
        )
        return SelectedRequestError(refusal.status, refusal.code)
    return SelectedRequestError("unavailable", "native_refused")


def native_connection_error(error: Exception, schema: str) -> OperationOutcome | None:
    if type(error) is not GeneratedNativeError:
        return None
    code = error.code
    if code == "UNSUPPORTED":
        return OperationOutcome("invalid", "", {}, "unsupported")
    return native_read_refusal({"schema": schema, "error": {"code": code}}, schema)


__all__ = [
    "GeneratedTablePlan",
    "PlannedConnection",
    "connection_result",
    "consume_connection",
    "connection_fields",
    "connection_preflight_error",
    "issue_table_plan",
    "field_reference",
    "native_connection_error",
    "table_plan_from",
]
