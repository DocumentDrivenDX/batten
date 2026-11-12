"""Reject unsupported selected reads before provider acquisition or effects."""

from typing import cast

from batten.contracts import Operation, SelectedExecution, SelectedKey, Selection


def _reference(value: object) -> bool:
    return (
        isinstance(value, tuple)
        and len(cast(tuple[object, ...], value)) == 2
        and all(
            isinstance(item, str) and bool(item)
            for item in cast(tuple[object, ...], value)
        )
    )


def _key(value: object) -> bool:
    return (
        isinstance(value, SelectedKey)
        and _reference(value.record)
        and isinstance(cast(object, value.key_id), str)
        and bool(value.key_id)
    )


def valid_selection(value: object) -> bool:
    if not isinstance(value, Selection):
        return False
    fields, keys, parents = value.fields, value.keys, value.parents
    return (
        isinstance(cast(object, value.kind), str)
        and value.kind in {"get_many", "connection", "related_many"}
        and type(fields) is tuple
        and len(fields) <= 1024
        and all(_reference(item) for item in fields)
        and type(keys) is tuple
        and type(parents) is tuple
        and len(keys) + len(parents) <= 4096
        and all(_key(item) for item in (*keys, *parents))
        and (value.target is None or _reference(value.target))
        and (value.after is None or isinstance(cast(object, value.after), str))
    )


def selection_failure(
    operation: Operation, execution: object, selection: Selection
) -> tuple[str, str] | None:
    if (
        operation.mutation
        or selection.kind not in operation.selection_kinds
        or not isinstance(execution, SelectedExecution)
    ):
        return "invalid", "unsupported_selection"
    if selection.kind == "get_many":
        valid = (
            not selection.parents
            and selection.target is None
            and selection.first is None
            and selection.after is None
        )
    elif selection.kind == "connection":
        valid = (
            not selection.keys
            and not selection.parents
            and selection.target is None
            and type(selection.first) is int
            and selection.first >= 0
        )
    elif selection.kind == "related_many":
        valid = (
            not selection.keys
            and selection.target is not None
            and selection.first is None
            and selection.after is None
        )
    else:
        valid = False
    return None if valid else ("invalid", "invalid_selection")
