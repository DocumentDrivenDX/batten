"""Server-guarded Boolean/read-terminal adapter; all native meaning remains upstream."""

import json
from typing import Literal, Protocol, cast, runtime_checkable

from batten.contracts import ExecutionScope, OperationCall, OperationOutcome
from umf_access.unified import SessionIdentity
from umf_access_generated_executor import ExecutionScope as GeneratedScope
from umf_access_generated_executor import GeneratedExecutionError, GeneratedReadCallV2

from ._generated_values import native_read_refusal, read_refusal
from ._read_binding import ReadBindingMetadata
from ._read_result_v2 import valid_read_result_v2
from .generated_read import GeneratedReadExecution


@runtime_checkable
class GeneratedReadBindingV3(ReadBindingMetadata, Protocol):
    async def execute_read_v3(
        self,
        call: GeneratedReadCallV2,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]: ...


class GeneratedReadExecutionV3(GeneratedReadExecution):
    _read_profile = "weft.generated-read-algebra/3"
    _accepted_read_profiles = frozenset({
        "weft.generated-read-algebra/3",
        "weft.generated-read-algebra/4",
        "weft.generated-read-algebra/5",
        "weft.generated-read-algebra/7",
        "weft.generated-read-algebra/8",
    })

    async def prepare(self) -> None:
        await super().prepare()
        if not isinstance(self._native, GeneratedReadBindingV3):
            self._native = None
            raise ValueError("generated v3 native execution is unavailable")

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        refused = read_refusal(call)
        if refused is not None:
            return refused
        scope = cast(ExecutionScope, call.scope)
        identity = SessionIdentity(
            cast(Literal["person", "batch"], call.actor.kind), call.actor.subject
        )
        context = GeneratedScope(
            scope.application,
            identity,
            scope.request_id,
            scope.deadline_monotonic,
            scope.lease_id,
            scope.api_digest,
            scope.consistency,
        )
        try:
            inputs = call.snapshot().inputs
            if (
                set(inputs) != {"read"}
                or len(
                    json.dumps(
                        dict(inputs),
                        ensure_ascii=False,
                        allow_nan=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                )
                > self._maximum
            ):
                raise ValueError("generated v3 input envelope differs")
            read = GeneratedReadCallV2.from_mapping(inputs["read"])
            if self._routes.get(call.operation) != (read.module, read.record):
                raise ValueError("read operation differs from configured root")
            bound = self._executor.bind_read_v3(read, context)
        except (GeneratedExecutionError, ValueError, TypeError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        native = self._native
        if native is None:
            return OperationOutcome("unavailable", "", {}, "not_prepared")
        result = await cast(GeneratedReadBindingV3, native).execute_read_v3(
            read,
            identity=identity,
            scope=context,
        )
        if not valid_read_result_v2(result, native.schema, read, bound):
            return native_read_refusal(result, native.schema)
        return OperationOutcome("succeeded", "", result)


__all__ = ["GeneratedReadBindingV3", "GeneratedReadExecutionV3"]
