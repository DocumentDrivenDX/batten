"""UmfTableProvider adapts the table port to the UMF access contract."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from batten.contracts import Actor
from batten.tables import TablePort
from batten.umf_postgres import AuthenticatedTransport, create_umf_provider
from umf_access.unified import SessionIdentity


class Transport:
    def __init__(self, sent: list[dict[str, object]]) -> None:
        self.sent = sent

    async def execute(self, request: dict[str, object]) -> dict[str, object]:
        self.sent.append(request)
        return {"ok": True}


class Binding:
    schema = "approval_app"
    module = "approval"

    def __init__(self) -> None:
        self.identities: list[SessionIdentity] = []
        self.sent: list[dict[str, object]] = []

    def for_identity(self, identity: SessionIdentity) -> AuthenticatedTransport:
        self.identities.append(identity)
        return Transport(self.sent)


class Authority:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self.checked: list[tuple[str, str]] = []

    async def check(self, actor: Actor, operation: str) -> bool:
        self.checked.append((actor.subject, operation))
        return self.allowed


async def run(port: TablePort, **overrides: object) -> Mapping[str, object]:
    options: dict[str, object] = {"key": "k1", "phase": "invoke", "mutation": True}
    options.update(overrides)
    return await port.execute(
        Actor("alex"),
        "submit_request",
        {"summary": "x"},
        key=str(options["key"]),
        phase=str(options["phase"]),
        mutation=bool(options["mutation"]),
    )


async def test_prepare_builds_the_binding_once_and_close_drops_it() -> None:
    built: list[Binding] = []

    def factory() -> Binding:
        built.append(Binding())
        return built[-1]

    provider = create_umf_provider(factory, Authority(True))
    await provider.prepare()
    await provider.prepare()
    assert len(built) == 1
    await provider.aclose()
    with pytest.raises(RuntimeError, match="not prepared"):
        await run(provider)


async def test_execute_sends_the_original_access_request_as_the_person() -> None:
    binding, authority = Binding(), Authority(True)
    provider = create_umf_provider(lambda: binding, authority)
    await provider.prepare()
    assert await run(provider) == {"ok": True}
    assert authority.checked == [("alex", "tables.submit_request")]
    assert binding.identities == [SessionIdentity("person", "alex")]
    assert binding.sent == [
        {
            "contract": "umf.access/1",
            "schema": "approval_app",
            "kind": "table",
            "module": "approval",
            "operation": "submit_request",
            "call": {"kind": "single", "inputs": {"summary": "x"}},
            "phase": "invoke",
            "mutation": True,
            "idempotency_key": "k1",
        }
    ]


async def test_denied_actor_never_reaches_the_native_binding() -> None:
    binding = Binding()
    provider = create_umf_provider(lambda: binding, Authority(False))
    await provider.prepare()
    assert await run(provider) == {"error": {"code": "DENIED"}}
    assert binding.identities == [] and binding.sent == []
