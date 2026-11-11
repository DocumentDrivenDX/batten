"""Neutral Lintel calls translated exclusively through public Batten dispatch."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import replace
from typing import TYPE_CHECKING, NoReturn, cast

from batten.contracts import ExecutionScope, OperationCall, SelectedKey, Selection
from batten.lintel import _decode
from batten.lintel._command import command_result
from batten.lintel._config import ExposureOperation
from batten.lintel._failure import failure
from batten.runtime import Host

from lintel.ports import (
    Arguments,
    CommandResult,
    ConnectionPage,
    ElementRef,
    ExecutionError,
    ExecutionErrorCode,
    NodeKey,
    NodeValue,
    OperationRef,
)

if TYPE_CHECKING:
    from lintel.ports import ConnectionIntent


def selected_key(value: NodeKey) -> SelectedKey:
    return SelectedKey(
        (value.record.module, value.record.element),
        value.key_id,
        tuple(_decode.literal(component) for component in value.components),
    )


def checked_keys(
    keys: tuple[NodeKey, ...], exposure: ExposureOperation
) -> tuple[NodeKey, ...]:
    return tuple(
        _decode.key(
            {
                "record": value.record,
                "keyId": value.key_id,
                "components": value.components,
            },
            exposure,
        )
        for value in keys
    )


def _arguments(values: Arguments) -> Mapping[str, object]:
    return {
        name: selected_key(value)
        if isinstance(value, NodeKey)
        else (None if value is None else _decode.literal(value))
        for name, value in values.items()
    }


class Session:
    def __init__(
        self,
        host: Host,
        scope: ExecutionScope,
        kind: str,
        operations: Mapping[OperationRef, ExposureOperation],
        *,
        planned_intents: tuple[ConnectionIntent, ...] = (),
        connection_operations: Mapping[OperationRef, str] | None = None,
        result_budget: int | None = None,
        planned_mode: bool = False,
    ):
        self.host, self.scope, self.kind, self.operations = (
            host,
            scope,
            kind,
            operations,
        )
        self.active = True
        self._planned = list(planned_intents)
        self._planned_used: set[int] = set()
        self._connection_operations = connection_operations or {}
        self._budget_limit = result_budget
        self._planned_mode = planned_mode
        self._budget_used = 0
        self._budget_failed = False
        self._selected_failure: ExecutionError | None = None
        self._selected_lock = asyncio.Lock()

    def ensure_budget(self) -> None:
        if self._budget_failed:
            raise ExecutionError("LIMIT_EXCEEDED")
        if self._selected_failure is not None:
            raise self._selected_failure

    def _remember_failure(self, error: ExecutionError) -> None:
        if self._planned_mode and self._selected_failure is None:
            self._selected_failure = error

    def _refuse(self, code: ExecutionErrorCode) -> NoReturn:
        error = ExecutionError(code)
        self._remember_failure(error)
        raise error

    @property
    def budget_exceeded(self) -> bool:
        return self._budget_failed

    def _charge(self, result: Mapping[str, object]) -> None:
        if self._budget_limit is None:
            return
        remaining = self._budget_limit - self._budget_used
        encoder = json.JSONEncoder(
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=_json_default,
        )
        size = 0
        for chunk in encoder.iterencode(dict(result)):
            size += len(chunk.encode("utf-8", errors="strict"))
            if size > remaining:
                self._budget_failed = True
                self._refuse("LIMIT_EXCEEDED")
        if size > remaining:
            self._budget_failed = True
            self._refuse("LIMIT_EXCEEDED")
        self._budget_used += size

    def _exposure(
        self, operation: OperationRef, fields: tuple[ElementRef, ...] = ()
    ) -> ExposureOperation:
        if not self.active or not self.host.scope_active(self.scope):
            self._refuse("DENIED")
        exposure = self.operations.get(operation)
        if (
            exposure is None
            or len(set(fields)) != len(fields)
            or not set(fields).issubset(exposure.fields)
        ):
            self._refuse("UNSUPPORTED")
        return exposure

    async def _dispatch(
        self,
        exposure: ExposureOperation,
        values: Mapping[str, object],
        selection: Selection,
    ) -> Mapping[str, object]:
        if selection.kind not in exposure.selection_kinds:
            self._refuse("UNSUPPORTED")
        result = await self.host.invoke(
            OperationCall(
                exposure.host_operation, values, self.scope.principal, scope=self.scope
            ),
            selection=selection,
        )
        if result.status != "succeeded":
            error = failure(result.status, result.code)
            self._remember_failure(error)
            raise error
        return result.result

    async def get_many(
        self,
        operation: OperationRef,
        keys: tuple[NodeKey, ...],
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        try:
            exposure = self._exposure(operation, fields)
            keys = checked_keys(keys, exposure)
            selection = Selection(
                "get_many",
                tuple((field.module, field.element) for field in fields),
                tuple(selected_key(value) for value in keys),
            )
            async with self._selected_lock:
                self.ensure_budget()
                result = await self._dispatch(exposure, {}, selection)
                self._charge(result)
                return _decode.items(result, "get_many", exposure, fields, keys)
        except ExecutionError as error:
            self._remember_failure(error)
            raise

    async def connection(
        self,
        operation: OperationRef,
        arguments: Arguments,
        first: int,
        after: str | None,
        fields: tuple[ElementRef, ...],
    ) -> ConnectionPage:
        if self._planned_mode:
            self._refuse("UNSUPPORTED")
        try:
            exposure = self._exposure(operation, fields)
            selection = Selection(
                "connection",
                tuple((field.module, field.element) for field in fields),
                first=first,
                after=after,
            )
            async with self._selected_lock:
                self.ensure_budget()
                result = await self._dispatch(
                    exposure, _arguments(arguments), selection
                )
                self._charge(result)
                return _decode.connection(result, exposure, fields, first)
        except ExecutionError as error:
            self._remember_failure(error)
            raise

    async def planned_connection(self, intent: ConnectionIntent) -> ConnectionPage:
        if not self.active or not self._planned_mode:
            self._refuse("UNSUPPORTED")
        index = next(
            (
                position
                for position, planned in enumerate(self._planned)
                if position not in self._planned_used and planned == intent
            ),
            None,
        )
        if index is None:
            self._refuse("UNSUPPORTED")
        self._planned_used.add(index)
        try:
            operation = self._connection_operations.get(intent.lookup)
            exposure = self._exposure(intent.lookup, intent.fields)
            if operation != exposure.host_operation:
                self._refuse("UNSUPPORTED")
            selection = Selection(
                "connection",
                tuple((field.module, field.element) for field in intent.fields),
                first=intent.first,
                after=intent.after,
            )
            async with self._selected_lock:
                self.ensure_budget()
                result = await self._dispatch(exposure, {}, selection)
                self._charge(result)
                return _decode.connection(result, exposure, intent.fields, intent.first)
        except ExecutionError as error:
            self._remember_failure(error)
            raise

    async def related_many(
        self,
        operation: OperationRef,
        parents: tuple[NodeKey, ...],
        target: ElementRef,
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        exposure = self._exposure(operation, fields)
        if target != exposure.related_target:
            raise ExecutionError("UNSUPPORTED")
        if exposure.parent_record is None or exposure.parent_key_id is None:
            raise ExecutionError("UNSUPPORTED")
        parents = checked_keys(
            parents,
            replace(
                exposure,
                record=exposure.parent_record,
                key_id=exposure.parent_key_id,
                key_wrappers=exposure.parent_key_wrappers,
            ),
        )
        selection = Selection(
            "related_many",
            tuple((field.module, field.element) for field in fields),
            parents=tuple(selected_key(value) for value in parents),
            target=(target.module, target.element),
        )
        async with self._selected_lock:
            self.ensure_budget()
            result = await self._dispatch(exposure, {}, selection)
            self._charge(result)
            return _decode.items(result, "related_many", exposure, fields, parents)

    async def _command(
        self,
        operation: OperationRef,
        values: Arguments,
        invocation_key: str,
        phase: str,
        confirmation: str | None,
    ) -> CommandResult:
        exposure = self._exposure(operation)
        if phase == "invoke" and self.kind != "mutation":
            raise ExecutionError("DENIED")
        if not self.host.operations[exposure.host_operation].mutation:
            raise ExecutionError("UNSUPPORTED")
        result = await self.host.invoke(
            OperationCall(
                exposure.host_operation,
                _arguments(values),
                self.scope.principal,
                invocation_key,
                phase,
                self.scope,
                confirmation,
            )
        )
        if result.status == "uncertain":
            return CommandResult(
                "unknown", invocation_key, "unknown", (), None, None, None
            )
        if result.status != "succeeded":
            raise failure(result.status, result.code)
        try:
            if result.invocation != invocation_key:
                raise ExecutionError("INVALID")
            return command_result(result.result, exposure, invocation_key, phase)
        except ExecutionError:
            return CommandResult(
                "unknown", invocation_key, "unknown", (), None, None, None
            )

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult:
        return await self._command(
            operation, arguments, invocation_key, "invoke", confirmation
        )

    async def observe(
        self, operation: OperationRef, arguments: Arguments, invocation_key: str
    ) -> CommandResult:
        return await self._command(
            operation, arguments, invocation_key, "observe", None
        )


def _json_default(value: object) -> object:
    if isinstance(value, Mapping):
        return dict(cast(Mapping[str, object], value))
    if type(value) is tuple:
        return list(cast(tuple[object, ...], value))
    raise TypeError("selected result contains a non-JSON value")
