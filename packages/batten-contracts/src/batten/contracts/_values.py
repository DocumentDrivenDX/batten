"""Owned immutable snapshots of bounded transport values."""

import json
import math
from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol, cast


def _consume_text(value: str, budget: list[int]) -> None:
    if len(budget) > 1:
        if len(value) > budget[1]:
            raise ValueError("transport byte capacity exceeded")
        budget[1] -= len(value.encode("utf-8", errors="strict"))
        if budget[1] < 0:
            raise ValueError("transport byte capacity exceeded")


def _owned(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            key: _owned(item) for key, item in cast(Mapping[str, object], value).items()
        }
    if type(value) is tuple:
        return [_owned(item) for item in cast(tuple[object, ...], value)]
    return value


class StructuredKey(Protocol):
    def __init__(
        self,
        record: tuple[str, str],
        key_id: str,
        components: tuple[Mapping[str, object], ...],
    ) -> None: ...

    @property
    def record(self) -> tuple[str, str]: ...
    @property
    def key_id(self) -> str: ...
    @property
    def components(self) -> tuple[Mapping[str, object], ...]: ...


def _key_json(item: StructuredKey) -> dict[str, object]:
    return {"record": item.record, "keyId": item.key_id, "components": item.components}


def snapshot_transport(
    value: Mapping[str, object], key_type: type[StructuredKey]
) -> Mapping[str, object]:
    if not isinstance(cast(object, value), Mapping):
        raise ValueError("transport inputs require a mapping")
    frozen = freeze_value(value, [16_384, 8_388_608], key_type=key_type)

    def mapping(item: object) -> dict[str, object]:
        if type(item) is key_type:
            return _key_json(item)
        if isinstance(item, Mapping):
            return dict(cast(Mapping[str, object], item))
        raise ValueError("unsupported transport value")

    encoded = json.dumps(
        frozen,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        default=mapping,
    ).encode("utf-8", errors="strict")
    if len(encoded) > 8_388_608:
        raise ValueError("transport byte capacity exceeded")
    return cast(Mapping[str, object], _owned(frozen))


def _primitive(value: object, budget: list[int]) -> object:
    if type(value) is str:
        _consume_text(value, budget)
        return value
    if value is None or type(value) in {bool, int}:
        return value
    if type(value) is float and math.isfinite(value):
        return value
    raise ValueError("selection value is not a finite transport value")


def freeze_value(
    value: object,
    budget: list[int],
    depth: int = 0,
    *,
    key_type: type[StructuredKey] | None = None,
) -> object:

    budget[0] -= 1
    if budget[0] < 0 or depth > 32:
        raise ValueError("selection value exceeds limits")
    if key_type is not None and type(value) is key_type:
        key = cast(
            Mapping[str, object],
            freeze_value(
                _key_json(value),
                budget,
                depth + 1,
                key_type=key_type,
            ),
        )
        return key_type(
            cast(tuple[str, str], key["record"]),
            cast(str, key["keyId"]),
            cast(tuple[Mapping[str, object], ...], key["components"]),
        )
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for key, item in cast(Mapping[object, object], value).items():
            if not isinstance(key, str):
                raise ValueError("selection value requires string keys")
            _consume_text(key, budget)
            result[key] = freeze_value(item, budget, depth + 1, key_type=key_type)
        return MappingProxyType(result)
    if isinstance(value, (tuple, list)):
        return tuple(
            freeze_value(item, budget, depth + 1, key_type=key_type)
            for item in cast(tuple[object, ...] | list[object], value)
        )
    return _primitive(value, budget)
