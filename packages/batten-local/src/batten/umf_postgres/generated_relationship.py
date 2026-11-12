"""Bound one-hop lookups through two authorized batches in the same snapshot."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, cast

from batten.contracts import (
    Identity,
    OperationCall,
    OperationOutcome,
    SelectedKey,
    Selection,
)
from umf_access_generated_executor import GeneratedExecutor

from ._generated_batch_routes import RecordRoot
from .generated_batch import GeneratedBatchExecution


@dataclass(frozen=True, slots=True)
class GeneratedRelationshipRoute:
    relationship: tuple[str, str]
    parent_operation: str
    target_operation: str


@dataclass(frozen=True, slots=True)
class _Route:
    declaration: GeneratedRelationshipRoute
    source_field: tuple[str, str]
    target: tuple[str, str]
    target_key: str


class GeneratedRelationships:
    def __init__(
        self,
        executor: GeneratedExecutor,
        roots: Mapping[str, RecordRoot],
        routes: Mapping[str, GeneratedRelationshipRoute],
        authority: Identity,
    ) -> None:
        if not routes or executor.read_profile != "weft.generated-read-algebra/8":
            raise ValueError("admitted /8 relationship inventory required")
        rows = cast(
            tuple[Mapping[str, Any], ...],
            executor.native_table.native_source["relationships"],
        )
        inventory = {
            (row["logicalIdentity"]["module"], row["logicalIdentity"]["id"]): row
            for row in rows
            if row["status"] == "admitted"
        }
        self._routes = MappingProxyType({
            name: _admit(route, roots, inventory[route.relationship])
            for name, route in routes.items()
        })
        self._authority = authority
        self.artifact_digest = executor.trusted_artifact.artifact_digest

    @property
    def operations(self) -> frozenset[str]:
        return frozenset(self._routes)

    def capabilities(self) -> Mapping[str, str]:
        return {
            "relationship.batch": "to-one-1",
            **{
                f"relationship.operation/{name}": json.dumps(
                    (*route.declaration.relationship, *route.target),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                for name, route in self._routes.items()
            },
        }

    async def invoke(
        self,
        records: GeneratedBatchExecution,
        call: OperationCall,
        selection: Selection,
    ) -> OperationOutcome:
        route = self._routes.get(call.operation)
        if (
            route is None
            or selection.kind != "related_many"
            or selection.target != route.target
            or not 1 <= len(selection.parents) <= 100
        ):
            return OperationOutcome("invalid", "", {}, "unsupported")
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        parents = await records.invoke_selected(
            replace(call, operation=route.declaration.parent_operation),
            Selection("get_many", (route.source_field,), keys=selection.parents),
        )
        if parents.status == "denied":
            return _result([None] * len(selection.parents))
        if parents.status != "succeeded":
            return parents
        keys = _target_keys(parents.result, route)
        return await _targets(records, call, selection, route, keys)


def _admit(
    route: GeneratedRelationshipRoute,
    roots: Mapping[str, RecordRoot],
    row: Mapping[str, Any],
) -> _Route:
    parent, target = roots[route.parent_operation], roots[route.target_operation]
    binding = row["binding"]
    declaration = row["declaration"]
    target_record = (target.ref.module, target.ref.id)
    if (
        tuple(binding["sourceRecord"]) != (parent.ref.module, parent.ref.id)
        or tuple(binding["targetRecord"]) != target_record
        or declaration["target"][0]["key"] != target.primary_key_id
        or target.key_wrappers != ("string",)
        or len(binding["pairs"]) != 1
    ):
        raise ValueError("relationship differs from admitted Record roots")
    field = binding["pairs"][0]["sourceField"]
    source_field = (cast(str, field["module"]), cast(str, field["element"]))
    if not any(
        (ref.module, ref.element) == source_field and wrapper == "string"
        for ref, wrapper in parent.field_wrappers
    ):
        raise ValueError("relationship source Key field is outside the Record route")
    return _Route(route, source_field, target_record, target.primary_key_id)


def _target_keys(
    result: Mapping[str, object], route: _Route
) -> list[SelectedKey | None]:
    keys: list[SelectedKey | None] = []
    for row in cast(list[Any], result["items"]):
        value = row["fields"][0]["value"] if row is not None else None
        keys.append(
            None
            if value is None
            else SelectedKey(route.target, route.target_key, (value,))
        )
    return keys


async def _targets(
    records: GeneratedBatchExecution,
    call: OperationCall,
    selection: Selection,
    route: _Route,
    keys: list[SelectedKey | None],
) -> OperationOutcome:
    present = tuple(key for key in keys if key is not None)
    items: list[object] = [None] * len(keys)
    if present:
        targets = await records.invoke_selected(
            replace(call, operation=route.declaration.target_operation),
            Selection("get_many", selection.fields, keys=present),
        )
        if targets.status == "denied":
            return _result(items)
        if targets.status != "succeeded":
            return targets
        rows = iter(cast(list[object], targets.result["items"]))
        items = [next(rows) if key is not None else None for key in keys]
    return _result(items)


def _result(items: list[object]) -> OperationOutcome:
    return OperationOutcome(
        "succeeded",
        "",
        {"version": "batten.selected-result/1", "kind": "related_many", "items": items},
    )


__all__ = ["GeneratedRelationshipRoute", "GeneratedRelationships"]
