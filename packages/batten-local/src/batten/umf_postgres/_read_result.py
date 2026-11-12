"""Bounded structural result gate; upstream native codecs own value semantics."""

import json
from collections.abc import Mapping
from typing import cast

from umf_access_generated_executor import BoundReadProgram, GeneratedReadCall

_WRAPPERS = {
    "boolean": "boolean",
    "string": "string",
    "integer": "integerToken",
    "decimal": "decimalToken",
    "float": "floatToken",
    "date": "date",
    "timestamp": "timestamp",
    "uuid": "uuid",
    "bits128": "bits128Hex",
}


def result_sequence(value: object) -> tuple[object, ...]:
    if not isinstance(value, (tuple, list)):
        raise ValueError("native result list required")
    return tuple(cast(tuple[object, ...] | list[object], value))


def cell_size(value: object, output: Mapping[str, object]) -> int:
    if value is None:
        if output["nullable"] is not True:
            raise ValueError("native result nullability differs")
        return 4
    wrapper = _WRAPPERS.get(cast(str, output["carrier"]))
    if not isinstance(value, Mapping):
        raise ValueError("native result literal required")
    literal = cast(Mapping[str, object], value)
    if wrapper is None or set(literal) != {wrapper}:
        raise ValueError("native result wrapper differs")
    scalar = literal[wrapper]
    expected = bool if wrapper == "boolean" else str
    if type(scalar) is not expected:
        raise ValueError("native result scalar differs")
    return len(
        json.dumps(
            {wrapper: scalar},
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def valid_read_result(
    result: Mapping[str, object],
    source: str,
    call: GeneratedReadCall,
    bound: BoundReadProgram,
    maximum: int = 8_388_608,
) -> bool:
    try:
        _check_result(result, source, call, bound, maximum)
    except (ValueError, KeyError, TypeError, UnicodeError):
        return False
    return True


def _check_result(
    result: Mapping[str, object],
    source: str,
    call: GeneratedReadCall,
    bound: BoundReadProgram,
    maximum: int,
) -> None:
    if set(result) != {"schema", "table"} or result["schema"] != source:
        raise ValueError("native envelope differs")
    raw = result["table"]
    if not isinstance(raw, Mapping):
        raise ValueError("native frame required")
    frame = cast(Mapping[str, object], raw)
    pins = {
        "version": "umf.generated-read-result/1",
        "kind": "many",
        "sourceDigest": source,
        "module": call.module,
        "record": call.record,
        "cursor": None,
    }
    if set(frame) != set(pins) | {"columns", "rows"} or any(
        frame[key] != value for key, value in pins.items()
    ):
        raise ValueError("native frame pins differ")
    columns = result_sequence(frame["columns"])
    expected = [
        {"field": dict(field), "output": dict(output)}
        for field, output in zip(bound.fields, bound.outputs, strict=True)
    ]
    if list(columns) != expected:
        raise ValueError("native columns differ")
    rows = result_sequence(frame["rows"])
    if len(rows) > call.limit:
        raise ValueError("native row capacity exceeded")
    empty = {"schema": source, "table": {**pins, "columns": expected, "rows": []}}
    used = len(
        json.dumps(
            empty, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    )
    check_rows(rows, bound.outputs, used, maximum)


def check_rows(
    rows: tuple[object, ...],
    outputs: tuple[Mapping[str, object], ...],
    used: int,
    maximum: int,
) -> None:
    if used > maximum:
        raise ValueError("native result capacity exceeded")
    for row_index, raw_row in enumerate(rows):
        row = result_sequence(raw_row)
        if len(row) != len(outputs):
            raise ValueError("native row arity differs")
        used += 2 + int(row_index > 0)
        for column_index, (value, output) in enumerate(zip(row, outputs, strict=True)):
            used += cell_size(value, output) + int(column_index > 0)
            if used > maximum:
                raise ValueError("native result capacity exceeded")
