"""Read-only generated algebra provider behind the universal Batten host gates."""

from collections.abc import Awaitable, Callable, Mapping
from types import MappingProxyType
from typing import Literal, Protocol, cast

from batten.contracts import ExecutionScope, Identity, OperationCall, OperationOutcome
from umf_access.unified import SessionIdentity
from umf_access_generated_executor import (
    AdmittedNativeTable,
    GeneratedExecutionError,
    GeneratedExecutor,
    GeneratedReadCall,
)
from umf_access_generated_executor import ExecutionScope as GeneratedScope

from ._generated_values import native_read_refusal, read_refusal
from ._read_binding import ReadBindingMetadata
from ._read_result import valid_read_result
from ._read_wire import read_call


class GeneratedReadBinding(ReadBindingMetadata, Protocol):
    async def execute_read(
        self,
        call: GeneratedReadCall,
        *,
        identity: SessionIdentity,
        scope: GeneratedScope,
    ) -> dict[str, object]: ...


def _records(
    native: AdmittedNativeTable, read_profile: str | None
) -> frozenset[tuple[str, str]]:
    if type(native) is not AdmittedNativeTable:
        raise ValueError("verified native artifact required")
    version = "3" if read_profile == "weft.generated-read-algebra/8" else "2"
    if native.native_source["version"] != f"umf.native-table-source/{version}":
        raise ValueError(f"generated read requires native source version {version}")
    catalog = cast(Mapping[str, object], native.native_source["expectedCatalog"])
    records: set[tuple[str, str]] = set()
    for table in cast(tuple[Mapping[str, object], ...], catalog["tables"]):
        record = cast(Mapping[str, str], table["record"])
        records.add((record["module"], record["element"]))
    return frozenset(records)


class GeneratedReadExecution:
    _read_profile = "weft.generated-read-algebra/1"
    _accepted_read_profiles: frozenset[str] = frozenset()

    def __init__(
        self,
        factory: Callable[[], Awaitable[ReadBindingMetadata]],
        authority: Identity,
        executor: GeneratedExecutor,
        routes: Mapping[str, tuple[str, str]],
        *,
        max_input_bytes: int = 8_388_608,
    ):
        if executor.read_profile not in self._accepted_read_profiles:
            raise ValueError("server-guarded generated read profile required")
        admitted = executor.native_table
        records = _records(admitted, executor.read_profile)
        if not routes or any(
            type(name) is not str
            or not name
            or type(record) is not tuple
            or len(record) != 2
            or any(type(part) is not str for part in record)
            or record not in records
            for name, record in routes.items()
        ):
            raise ValueError("read routes differ from admitted Records")
        if type(max_input_bytes) is not int or max_input_bytes < 1:
            raise ValueError("positive input capacity required")
        self._factory, self._authority = factory, authority
        self._executor = executor
        self._routes = MappingProxyType(dict(routes))
        self._source, self._maximum = admitted.source_digest, max_input_bytes
        self._native: ReadBindingMetadata | None = None

    async def prepare(self) -> None:
        if self._native is None:
            native = await self._factory()
            if (
                native.schema != self._source
                or native.read_profile not in self._accepted_read_profiles
                or native.target_binding_digest != self._executor.target.binding_digest
                or any(record[0] != native.module for record in self._routes.values())
            ):
                raise ValueError("read binding differs from admitted artifact")
            self._native = native

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
            read = read_call(call.inputs, self._maximum)
            if self._routes.get(call.operation) != (read.module, read.record):
                raise ValueError("read operation differs from configured root")
            bound = self._executor.bind_read(read, context)
        except (GeneratedExecutionError, ValueError, TypeError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        native = self._native
        if native is None:
            return OperationOutcome("unavailable", "", {}, "not_prepared")
        result = await cast(GeneratedReadBinding, native).execute_read(
            read, identity=identity, scope=context
        )
        if not valid_read_result(result, native.schema, read, bound):
            return native_read_refusal(result, native.schema)
        return OperationOutcome("succeeded", "", result)

    async def aclose(self) -> None:
        self._native = None


__all__ = ["GeneratedReadBinding", "GeneratedReadExecution"]
