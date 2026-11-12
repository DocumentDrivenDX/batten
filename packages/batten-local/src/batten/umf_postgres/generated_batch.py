"""Request-scoped selected primary-Key batches over issued UMF read artifacts."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Protocol, cast

from batten.contracts import (
    ExecutionScope,
    Identity,
    OperationCall,
    OperationOutcome,
    Selection,
)
from umf_access import unified as native_runtime
from umf_access.unified import AsyncSession, SessionIdentity
from umf_access_generated_executor import (
    BoundKeyBatchProgram,
    GeneratedExecutionError,
    GeneratedExecutor,
    GeneratedGetManyCall,
)
from umf_access_generated_executor import (
    ExecutionScope as GeneratedScope,
)

from ._generated_batch_routes import RecordRoot, RecordRoute, snapshot_route
from ._generated_batch_validation import check_root, key_wrapper, source_ref
from ._generated_values import native_read_refusal
from ._key_batch_result import selected_batch_result

_PROFILES = frozenset({
    "weft.generated-read-algebra/4",
    "weft.generated-read-algebra/5",
    "weft.generated-read-algebra/7",
    "weft.generated-read-algebra/8",
})
_CONSISTENCY = "request-snapshot-1"
_GENERATED_CONSISTENCY = "request-snapshot/1"


class GeneratedBatchRequest(Protocol):
    async def execute_get_many(
        self, call: GeneratedGetManyCall
    ) -> dict[str, object]: ...


class GeneratedBatchBinding(Protocol):
    schema: str
    module: str

    @property
    def read_profile(self) -> str | None: ...
    @property
    def target_binding_digest(self) -> str: ...
    @property
    def artifact_digest(self) -> str: ...
    @property
    def receipt_digest(self) -> str: ...
    @property
    def algebra_json(self) -> bytes: ...
    def open_request(
        self,
        identity: SessionIdentity,
        scope: GeneratedScope,
        *,
        data_session: AsyncSession,
    ) -> AbstractAsyncContextManager[GeneratedBatchRequest]: ...


class _GeneratedConnectionRequest(Protocol):
    async def execute_forward_connection(
        self, prepared: object
    ) -> dict[str, object]: ...


@dataclass(frozen=True)
class _Request:
    host_scope: ExecutionScope
    identity: SessionIdentity
    generated_scope: GeneratedScope
    native_request: GeneratedBatchRequest


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class GeneratedBatchExecution:
    """Bind selected calls to one host-issued request snapshot and UMF v4 root."""

    def __init__(
        self,
        executor: GeneratedExecutor,
        factory: Callable[[], Awaitable[GeneratedBatchBinding]],
        *,
        data_session: AsyncSession,
        authority: Identity,
        roots: Mapping[str, RecordRoot],
    ) -> None:
        if (
            executor.read_profile not in _PROFILES
            or type(data_session) is not AsyncSession
            or not roots
            or any(type(name) is not str or not name for name in roots)
        ):
            raise ValueError("verified v4 batch profile required")
        self._executor, self._factory = executor, factory
        self._profile = executor.read_profile
        self._data_session, self._authority = data_session, authority
        self._roots = MappingProxyType({
            operation: snapshot_route(operation, root)
            for operation, root in roots.items()
        })
        self._native: GeneratedBatchBinding | None = None
        self._requests: dict[str, _Request] = {}
        self._opening: set[str] = set()
        self._lock = asyncio.Lock()
        self._algebra = cast(dict[str, object], json.loads(executor.read_algebra_json))
        self._algebra_digest = _digest(executor.read_algebra_json)
        self._source = executor.native_table.source_digest
        self._target = executor.target.binding_digest
        trust = executor.trusted_artifact
        self._artifact, self._receipt = trust.artifact_digest, trust.receipt_digest
        roots_rows: list[list[str]] = []
        algebra_roots = self._algebra.get("roots")
        if not isinstance(algebra_roots, Mapping):
            raise ValueError("verified Record roots are unavailable")
        algebra_roots_map = cast(Mapping[str, object], algebra_roots)
        for operation, root in self._roots.items():
            module, record = root.module, root.record
            if (
                operation != root.host_operation
                or root.source_digest != self._source
                or root.artifact_digest != self._artifact
                or root.receipt_digest != self._receipt
                or root.binding_digest != self._target
                or root.algebra_sha256 != self._algebra_digest
            ):
                raise ValueError("Record route provenance differs")
            matches = [
                item
                for value in algebra_roots_map.values()
                for item in (cast(Mapping[str, object], value),)
                if (item.get("module"), item.get("record")) == (module, record)
            ]
            if len(matches) != 1:
                raise ValueError("Record route is absent from issued algebra")
            check_root(matches[0], root)
            roots_rows.append([operation, module, record, root.primary_key_id])
        roots_rows.sort()
        self._records_digest = _digest(
            json.dumps(roots_rows, ensure_ascii=False, separators=(",", ":")).encode()
        )

    def connection_key_profile(
        self, module: str, record: str
    ) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        roots = cast(Mapping[str, object], self._algebra["roots"])
        matches = [
            cast(Mapping[str, object], value)
            for value in roots.values()
            if isinstance(value, Mapping)
            and (
                cast(Mapping[str, object], value).get("module"),
                cast(Mapping[str, object], value).get("record"),
            )
            == (module, record)
        ]
        if len(matches) != 1:
            raise ValueError("connection Record is absent from issued algebra")
        root = matches[0]
        batch = root.get("getMany")
        if not isinstance(batch, Mapping):
            raise ValueError("connection Key profile is unavailable")
        key_fields = cast(Mapping[str, object], batch).get("keyFields")
        key_id = root.get("primaryKeyId")
        if type(key_id) is not str or type(key_fields) is not list or not key_fields:
            raise ValueError("connection Key profile differs")
        key_descriptors = tuple(
            cast(Mapping[str, object], field)
            for field in cast(list[object], key_fields)
        )
        wrappers = tuple(key_wrapper(field) for field in key_descriptors)
        if cast(Mapping[str, object], batch).get("keyId") != key_id:
            raise ValueError("connection Key identity differs")
        field_ids = tuple(cast(str, field["fieldId"]) for field in key_descriptors)
        return key_id, wrappers, field_ids

    def capabilities(self) -> Mapping[str, str]:
        return MappingProxyType({
            "read.consistency": _CONSISTENCY,
            "read.profile": self._profile,
            "source.digest": self._source,
            "binding.digest": self._target,
            "algebra.digest": self._algebra_digest,
            "artifact.digest": self._artifact,
            "receipt.digest": self._receipt,
            "records.digest": self._records_digest,
        })

    async def prepare(self) -> None:
        if self._native is not None:
            return
        native = await self._factory()
        if (
            native.schema != self._source
            or native.read_profile != self._profile
            or native.target_binding_digest != self._target
            or native.artifact_digest != self._artifact
            or native.receipt_digest != self._receipt
            or native.algebra_json != self._executor.read_algebra_json
            or any(root.module != native.module for root in self._roots.values())
        ):
            raise ValueError("native batch binding differs from verified artifact")
        self._native = native

    @asynccontextmanager
    async def open_request(self, scope: ExecutionScope) -> AsyncGenerator[None, None]:
        identity, generated_scope = self.prepared_scope(scope)
        async with self.open_prepared_request(scope, identity, generated_scope):
            yield

    def prepared_scope(
        self, scope: ExecutionScope
    ) -> tuple[SessionIdentity, GeneratedScope]:
        native = self._native
        actor = scope.principal if type(scope) is ExecutionScope else None
        if (
            native is None
            or actor is None
            or actor.kind not in {"person", "batch"}
            or actor.delegation is not None
            or scope.consistency != _CONSISTENCY
            or not math.isfinite(scope.deadline_monotonic)
            or time.monotonic() >= scope.deadline_monotonic
        ):
            raise ValueError("host request snapshot is unavailable")
        identity = SessionIdentity(
            cast(Literal["person", "batch"], actor.kind), actor.subject
        )
        generated_scope = GeneratedScope(
            scope.application,
            identity,
            scope.request_id,
            scope.deadline_monotonic,
            scope.lease_id,
            scope.api_digest,
            _GENERATED_CONSISTENCY,
        )
        return identity, generated_scope

    def prepare_connection(
        self,
        request: object,
        identity: SessionIdentity,
        generated_scope: GeneratedScope,
    ) -> object:
        native = self._native
        if native is None or not callable(
            getattr(native, "prepare_forward_connection", None)
        ):
            raise ValueError("native connection profile is unavailable")
        return cast(
            Callable[..., object], getattr(native, "prepare_forward_connection")
        )(request, identity=identity, scope=generated_scope)

    async def execute_connection(
        self,
        scope: ExecutionScope,
        identity: SessionIdentity,
        generated_scope: GeneratedScope,
        prepared: object,
    ) -> dict[str, object]:
        context = self._requests.get(scope.lease_id)
        execute = (
            getattr(context.native_request, "execute_forward_connection", None)
            if context is not None
            else None
        )
        if (
            context is None
            or context.host_scope is not scope
            or context.identity is not identity
            or context.generated_scope is not generated_scope
            or not callable(execute)
        ):
            raise ValueError("prepared native request is inactive")
        connection_request = cast(_GeneratedConnectionRequest, context.native_request)
        return await connection_request.execute_forward_connection(prepared)

    async def authorize_connection(self, call: OperationCall) -> bool:
        return await self._authority.check(call.actor, call.operation)

    @asynccontextmanager
    async def open_prepared_request(
        self,
        scope: ExecutionScope,
        identity: SessionIdentity,
        generated_scope: GeneratedScope,
    ) -> AsyncGenerator[None, None]:
        native = self._native
        if (
            native is None
            or generated_scope.principal is not identity
            or generated_scope.application != scope.application
            or generated_scope.request_id != scope.request_id
            or generated_scope.lease_id != scope.lease_id
            or generated_scope.api_digest != scope.api_digest
            or generated_scope.consistency != _GENERATED_CONSISTENCY
        ):
            raise ValueError("prepared native request scope differs")
        async with self._lock:
            if scope.lease_id in self._requests or scope.lease_id in self._opening:
                raise ValueError("request lease is already open")
            self._opening.add(scope.lease_id)
        try:
            async with native.open_request(
                identity, generated_scope, data_session=self._data_session
            ) as request:
                async with self._lock:
                    self._opening.remove(scope.lease_id)
                    self._requests[scope.lease_id] = _Request(
                        scope, identity, generated_scope, request
                    )
                try:
                    yield
                finally:
                    async with self._lock:
                        self._requests.pop(scope.lease_id, None)
        finally:
            async with self._lock:
                self._opening.discard(scope.lease_id)

    async def invoke(self, call: OperationCall) -> OperationOutcome:
        return OperationOutcome("invalid", "", {}, "unsupported")

    async def invoke_selected(
        self, call: OperationCall, selection: Selection
    ) -> OperationOutcome:
        snapshot = call.snapshot()
        scope = snapshot.scope
        if self._invalid_selected(snapshot, selection) or scope is None:
            return OperationOutcome("invalid", "", {}, "unsupported")
        try:
            generated_call, context, bound = self._bound_selected(snapshot, selection)
        except (GeneratedExecutionError, KeyError, ValueError, TypeError, UnicodeError):
            return OperationOutcome("invalid", "", {}, "invalid")
        return await self._execute_selected(snapshot, generated_call, context, bound)

    def _invalid_selected(self, call: OperationCall, selection: Selection) -> bool:
        scope = call.scope
        return (
            selection.kind != "get_many"
            or scope is None
            or scope.principal != call.actor
            or call.phase != "invoke"
            or call.key is not None
            or call.confirmation is not None
            or call.actor.kind not in {"person", "batch"}
            or call.actor.delegation is not None
            or bool(call.inputs)
            or scope.consistency != _CONSISTENCY
        )

    def _bound_selected(
        self, call: OperationCall, selection: Selection
    ) -> tuple[GeneratedGetManyCall, _Request, BoundKeyBatchProgram]:
        scope = cast(ExecutionScope, call.scope)
        route = self._roots.get(call.operation)
        if route is None:
            raise ValueError("Record operation is not exposed")
        if not 1 <= len(selection.keys) <= 100 or len(selection.fields) > 8:
            raise ValueError("selected batch capacity differs")
        module, record = route.module, route.record
        keys: list[tuple[object, ...]] = []
        for key in selection.keys:
            if (key.record, key.key_id) != ((module, record), route.primary_key_id):
                raise ValueError("selected Key root differs")
            if len(key.components) != len(route.key_wrappers):
                raise ValueError("selected Key arity differs")
            for component, wrapper in zip(
                key.components, route.key_wrappers, strict=True
            ):
                if set(component) != {wrapper}:
                    raise ValueError("selected Key wrapper differs")
            keys.append(tuple(dict(component) for component in key.components))
        fields = self._field_ids(route, selection.fields)
        generated_call = GeneratedGetManyCall(
            module, record, route.primary_key_id, tuple(keys), fields
        )
        context = self._requests.get(scope.lease_id)
        if context is None or context.host_scope is not scope:
            raise ValueError("request snapshot is inactive")
        bound = self._executor.bind_get_many(generated_call, context.generated_scope)
        return generated_call, context, bound

    async def _execute_selected(
        self,
        call: OperationCall,
        generated_call: GeneratedGetManyCall,
        context: _Request,
        bound: BoundKeyBatchProgram,
    ) -> OperationOutcome:
        if not await self._authority.check(call.actor, call.operation):
            return OperationOutcome("denied", "", {}, "denied")
        native = self._native
        if native is None:
            return OperationOutcome("unavailable", "", {}, "not_prepared")
        try:
            frame = await context.native_request.execute_get_many(generated_call)
        except Exception as error:
            error_type = getattr(native_runtime, "GeneratedNativeError", None)
            code = getattr(error, "code", None)
            if (
                not isinstance(error_type, type)
                or type(error) is not error_type
                or type(code) is not str
                or code
                not in {
                    "DENIED",
                    "LIMIT_EXCEEDED",
                    "SCHEMA_MISMATCH",
                    "INVALID",
                    "UNSUPPORTED",
                    "PRECONDITION_FAILED",
                    "BUSY",
                }
            ):
                raise
            if code == "UNSUPPORTED":
                return OperationOutcome("invalid", "", {}, "unsupported")
            return native_read_refusal(
                {"schema": native.schema, "error": {"code": code}}, native.schema
            )
        translated = selected_batch_result(frame, bound)
        if translated is None:
            return OperationOutcome("unavailable", "", {}, "native_refused")
        return OperationOutcome("succeeded", "", translated)

    def _field_ids(
        self, root: RecordRoute, requested: tuple[tuple[str, str], ...]
    ) -> tuple[str, ...]:
        if len(requested) > 8 or len(set(requested)) != len(requested):
            raise ValueError("selected Field list differs")
        algebra_roots = cast(Mapping[str, object], self._algebra["roots"])
        module, record = root.module, root.record
        issued = next(
            cast(Mapping[str, object], item)
            for item in algebra_roots.values()
            if isinstance(item, Mapping)
            and (
                cast(Mapping[str, object], item).get("module"),
                cast(Mapping[str, object], item).get("record"),
            )
            == (module, record)
        )
        fields = cast(Mapping[str, object], issued["fields"])
        by_ref = {
            source_ref(cast(Mapping[str, object], value)["sourceField"]): field_id
            for field_id, value in fields.items()
        }
        exposed = set(root.fields)
        if not set(requested).issubset(exposed):
            raise ValueError("selected Fields are outside exposed Record root")
        return tuple(by_ref[field] for field in requested)

    async def aclose(self) -> None:
        async with self._lock:
            if self._requests:
                raise RuntimeError("request snapshots must close before provider")
            self._native = None


__all__ = [
    "GeneratedBatchBinding",
    "GeneratedBatchExecution",
    "GeneratedBatchRequest",
]
