"""Exact terminal/frame shape checks around the upstream native G3 reader."""

import json
import re
from collections.abc import Mapping
from typing import cast

from umf_access_generated_executor import BoundReadProgramV2, GeneratedReadCallV2

from ._read_result import cell_size, check_rows, result_sequence


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("generated result mapping required")
    return cast(Mapping[str, object], value)


def valid_read_result_v2(
    result: Mapping[str, object],
    source: str,
    call: GeneratedReadCallV2,
    bound: BoundReadProgramV2,
    maximum: int = 8_388_608,
) -> bool:
    try:
        _check(result, source, call, bound, maximum)
    except (KeyError, ValueError, TypeError, UnicodeError):
        return False
    return True


def _check(
    result: Mapping[str, object],
    source: str,
    call: GeneratedReadCallV2,
    bound: BoundReadProgramV2,
    maximum: int,
) -> None:
    if set(result) != {"schema", "table"} or result["schema"] != source:
        raise ValueError("generated result envelope differs")
    frame = _mapping(result["table"])
    pins = {
        "version": "umf.generated-read-result/2",
        "kind": bound.result_kind,
        "terminal": call.terminal,
        "sourceDigest": source,
        "module": call.module,
        "record": call.record,
    }
    if bound.terminal != call.terminal or any(
        frame.get(key) != value for key, value in pins.items()
    ):
        raise ValueError("generated result terminal pins differ")
    if bound.result_kind == "scalar":
        _scalar(frame, pins, bound, maximum)
    else:
        _rows(frame, pins, bound, maximum)


def _scalar(
    frame: Mapping[str, object],
    pins: Mapping[str, object],
    bound: BoundReadProgramV2,
    maximum: int,
) -> None:
    if set(frame) != set(pins) | {"value"} or bound.scalar_output is None:
        raise ValueError("generated scalar result differs")
    value = frame["value"]
    used = cell_size(value, bound.scalar_output)
    if bound.terminal == "count":
        token = _mapping(value).get("integerToken")
        if type(token) is not str or re.fullmatch(r"0|[1-9][0-9]*", token) is None:
            raise ValueError("generated count result is not canonical nonnegative text")
    if (
        used + len(json.dumps(dict(pins), ensure_ascii=False).encode("utf-8")) + 128
        > maximum
    ):
        raise ValueError("generated scalar result capacity exceeded")


def _rows(
    frame: Mapping[str, object],
    pins: Mapping[str, object],
    bound: BoundReadProgramV2,
    maximum: int,
) -> None:
    if (
        set(frame) != set(pins) | {"columns", "rows", "cursor"}
        or frame["cursor"] is not None
    ):
        raise ValueError("generated row frame differs")
    columns = result_sequence(frame["columns"])
    expected = [
        {"field": dict(field), "output": dict(output)}
        for field, output in zip(bound.fields, bound.outputs, strict=True)
    ]
    if list(columns) != expected:
        raise ValueError("generated row columns differ")
    rows = result_sequence(frame["rows"])
    if bound.row_limit is None or len(rows) > bound.row_limit:
        raise ValueError("generated row count exceeds issued bound")
    if bound.cardinality == "exactly-one" and len(rows) != 1:
        raise ValueError("generated row count differs from exact terminal")
    empty = {
        "schema": frame["sourceDigest"],
        "table": {
            **pins,
            "columns": expected,
            "rows": [],
            "cursor": None,
        },
    }
    used = len(
        json.dumps(
            empty, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    )
    check_rows(rows, bound.outputs, used, maximum)
