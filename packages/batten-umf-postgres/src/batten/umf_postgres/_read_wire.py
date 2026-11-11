"""Exact portable data envelope for the upstream generated read binder."""

from collections.abc import Mapping
from typing import cast

from umf_access_generated_executor import GeneratedReadCall, GeneratedReadFilter

from ._generated_values import snapshot_inputs


def _object(value: object, keys: set[str]) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("read envelope must be a mapping")
    value = cast(Mapping[str, object], value)
    if set(value) != keys:
        raise ValueError("read envelope members differ")
    return value


def _array(value: object, maximum: int = 64) -> tuple[object, ...]:
    if not isinstance(value, (tuple, list)):
        raise ValueError("read list required")
    items = cast(tuple[object, ...] | list[object], value)
    if len(items) > maximum:
        raise ValueError("read list capacity exceeded")
    return tuple(items)


def _ids(value: object) -> tuple[str, ...]:
    items = _array(value)
    if any(type(item) is not str or not item for item in items):
        raise ValueError("read identity must be nonempty text")
    return cast(tuple[str, ...], items)


def _filter(value: object, maximum: int) -> GeneratedReadFilter:
    item = _object(value, {"predicate", "values"})
    predicate = _ids([item["predicate"]])[0]
    values = _array(item["values"], 1)
    copied = snapshot_inputs(
        {str(index): part for index, part in enumerate(values)}, maximum
    )
    return GeneratedReadFilter(predicate, tuple(copied.values()))


def read_call(inputs: Mapping[str, object], maximum: int) -> GeneratedReadCall:
    envelope = _object(inputs, {"read"})
    value = _object(
        envelope["read"], {"module", "record", "fields", "filters", "order", "limit"}
    )
    module, record = _ids([value["module"], value["record"]])
    selection = None if value["fields"] is None else _ids(value["fields"])
    orders = _ids(value["order"])
    filters = _array(value["filters"])
    limit = value["limit"]
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError("read row capacity exceeded")
    # Each scalar is bounded before copying; the aggregate is bounded as well.
    terms = tuple(_filter(item, maximum) for item in filters)
    size = sum(len(text.encode("utf-8")) for text in (module, record, *orders))
    size += sum(len(text.encode("utf-8")) for text in selection or ())
    for term in terms:
        size += len(term.predicate_id.encode("utf-8"))
        for literal in term.values:
            if literal is not None:
                for wrapper, scalar in cast(Mapping[str, object], literal).items():
                    size += len(wrapper.encode("utf-8")) + len(
                        str(scalar).encode("utf-8")
                    )
    if size > maximum:
        raise ValueError("read input capacity exceeded")
    return GeneratedReadCall(module, record, selection, terms, orders, limit)
