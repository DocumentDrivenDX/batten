"""Translate only an exact upstream Key batch frame into selected node slots."""

import json
from collections.abc import Mapping
from typing import Protocol, cast

from ._read_result import cell_size, result_sequence


class KeyBatchPins(Protocol):
    @property
    def source_digest(self) -> str: ...
    @property
    def target_digest(self) -> str: ...
    @property
    def root(self) -> Mapping[str, str]: ...
    @property
    def key_id(self) -> str: ...
    @property
    def keys(self) -> tuple[tuple[Mapping[str, object], ...], ...]: ...
    @property
    def fields(self) -> tuple[Mapping[str, object], ...]: ...
    @property
    def outputs(self) -> tuple[Mapping[str, object], ...]: ...


def selected_batch_result(
    result: Mapping[str, object], bound: KeyBatchPins, maximum: int = 8_388_608
) -> dict[str, object] | None:
    try:
        pins: dict[str, object] = {
            "version": "umf.generated-key-batch-result/1",
            "sourceDigest": bound.source_digest,
            "bindingDigest": bound.target_digest,
            "module": bound.root["module"],
            "record": bound.root["record"],
            "keyId": bound.key_id,
            "fields": [dict(field) for field in bound.fields],
        }
        if set(result) != set(pins) | {"items"} or any(
            result.get(key) != value for key, value in pins.items()
        ):
            raise ValueError("batch result provenance differs")
        slots = result_sequence(result["items"])
        if len(slots) != len(bound.keys):
            raise ValueError("batch slot count differs")
        translated: dict[str, object] = {
            "version": "batten.selected-result/1",
            "kind": "get_many",
            "items": [
                _slot(item, key, bound)
                for item, key in zip(slots, bound.keys, strict=True)
            ],
        }
        if (
            len(
                json.dumps(
                    translated,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
            > maximum
        ):
            raise ValueError("selected result capacity exceeded")
        return translated
    except (KeyError, ValueError, TypeError, UnicodeError):
        return None


def _slot(
    item: object, key: tuple[Mapping[str, object], ...], bound: KeyBatchPins
) -> dict[str, object] | None:
    if item is None:
        return None
    if not isinstance(item, Mapping):
        raise ValueError("batch slot must be a mapping")
    node = cast(Mapping[str, object], item)
    if set(node) != {"key", "values"} or list(result_sequence(node["key"])) != list(
        key
    ):
        raise ValueError("batch key differs from requested slot")
    values = result_sequence(node["values"])
    if len(values) != len(bound.outputs):
        raise ValueError("batch selected values differ")
    for value, output in zip(values, bound.outputs, strict=True):
        cell_size(value, output)
    return {
        "key": {
            "record": [bound.root["module"], bound.root["record"]],
            "keyId": bound.key_id,
            "components": [dict(component) for component in key],
        },
        "fields": [
            {"field": [field["module"], field["element"]], "value": value}
            for field, value in zip(bound.fields, values, strict=True)
        ],
    }
