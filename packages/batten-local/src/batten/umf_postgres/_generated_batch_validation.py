"""Join selected Record exposure pins to the issued generated algebra."""

from collections.abc import Mapping
from typing import cast

from ._generated_batch_routes import RecordRoute

_WRAPPERS = {
    "boolean": "boolean",
    "string": "string",
    "integer": "integerToken",
    "decimal": "decimalToken",
    "date": "date",
    "timestamp": "timestamp",
    "uuid": "uuid",
}


def source_ref(value: object) -> tuple[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("issued Field reference differs")
    ref = cast(Mapping[str, object], value)
    if set(ref) != {"module", "element"}:
        raise ValueError("issued Field reference differs")
    module, element = ref["module"], ref["element"]
    if type(module) is not str or not module or type(element) is not str or not element:
        raise ValueError("issued Field reference differs")
    return module, element


def key_wrapper(field: Mapping[str, object]) -> str:
    codec = field.get("codec")
    if not isinstance(codec, Mapping):
        raise ValueError("issued Key codec differs")
    codec_map = cast(Mapping[str, object], codec)
    if codec_map.get("profile") != "weft.query-codec-instructions/1":
        raise ValueError("issued Key codec differs")
    steps = codec_map.get("steps")
    if type(steps) is not list:
        raise ValueError("issued Key codec differs")
    step_items = cast(list[object], steps)
    if len(step_items) != 4:
        raise ValueError("issued Key codec differs")
    first = step_items[0]
    if not isinstance(first, Mapping):
        raise ValueError("issued Key codec differs")
    first_map = cast(Mapping[str, object], first)
    if (
        first_map.get("op") != "require-exact-wrapper"
        or first_map.get("nullable") is not False
        or type(first_map.get("wrapper")) is not str
    ):
        raise ValueError("issued Key codec differs")
    return cast(str, first_map["wrapper"])


def check_root(issued: Mapping[str, object], root: RecordRoute) -> None:
    key_id = root.primary_key_id
    batch = issued.get("getMany")
    batch_map = (
        cast(Mapping[str, object], batch) if isinstance(batch, Mapping) else None
    )
    key_fields = batch_map.get("keyFields") if batch_map is not None else None
    if (
        issued.get("primaryKeyId") != key_id
        or batch_map is None
        or batch_map.get("keyId") != key_id
        or type(key_fields) is not list
        or not key_fields
        or tuple(
            key_wrapper(cast(Mapping[str, object], item))
            for item in cast(list[object], key_fields)
        )
        != root.key_wrappers
        or any(wrapper not in set(_WRAPPERS.values()) for wrapper in root.key_wrappers)
    ):
        raise ValueError("Record primary Key differs from issued algebra")
    fields = issued.get("fields")
    if not isinstance(fields, Mapping):
        raise ValueError("Record Fields are unavailable")
    issued_fields: dict[tuple[str, str], tuple[str, Mapping[str, object]]] = {}
    for field_id, value in cast(Mapping[str, object], fields).items():
        item = cast(Mapping[str, object], value)
        issued_fields[source_ref(item.get("sourceField"))] = (field_id, item)
    exposed = root.fields
    wrappers = dict(root.field_wrappers)
    if (
        len(set(exposed)) != len(exposed)
        or len(wrappers) != len(root.field_wrappers)
        or set(wrappers) != set(exposed)
        or not set(exposed).issubset(issued_fields)
    ):
        raise ValueError("Record exposed Fields differ from issued algebra")
    for ref in exposed:
        output = cast(Mapping[str, object], issued_fields[ref][1]["output"])
        if wrappers[ref] != _WRAPPERS.get(cast(str, output["carrier"])):
            raise ValueError("Record Field codec differs from issued output")


__all__ = ["check_root", "key_wrapper", "source_ref"]
