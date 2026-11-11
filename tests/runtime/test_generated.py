"""Public generated provider preserves scope, exact input wires and safe outcomes."""

from contextlib import nullcontext
from dataclasses import replace
from typing import Literal, cast

import pytest
from batten.contracts import (
    OperationCall,
)
from batten.lintel._record_config import checked_record_roots
from batten.runtime import Host
from generated_batch_case import batch_case, record_root_host
from generated_provider_cases import (
    Authority,
    invalid_read_inputs,
    malformed_cases,
    scenario,
    wrong_root_call,
)
from umf_access.unified import SessionIdentity


@pytest.mark.parametrize(
    "profile",
    [
        "fixed",
        "read",
        "v2_all",
        "v3_all",
        "v3_all_complete",
        "v3_first",
        "v3_one",
        "v3_get",
        "v3_count",
        "v3_exists",
        "v4_batch",
        "v4_composite",
    ],
)
@pytest.mark.parametrize("kind", ["person", "batch", "service"])
async def test_generated_provider_preserves_exact_scope_and_read_profile(
    kind: Literal["person", "batch", "service"],
    profile: str,
) -> None:
    if profile in {"v4_batch", "v4_composite"}:
        case = batch_case(
            kind,
            Authority({"amount": {"string": "unchanged"}}),
            composite=profile == "v4_composite",
        )
        for bad_kwargs, message in case["bad_kwargs"]:
            with pytest.raises(ValueError, match=message):
                case["provider_type"](case["executor"], case["factory"], **bad_kwargs)
        provider, call = (
            case["provider_type"](
                case["executor"], case["factory"], **case["provider_kwargs"]
            ),
            cast(OperationCall, case["selected_call"]),
        )
        await provider.prepare()
        for _mode, call, selection, expected, error in case["actions"]:
            if error is not None:
                with pytest.raises(ValueError, match=error):
                    async with provider.open_request(case["scope"]):
                        pass
            else:
                async with (
                    provider.open_request(case["scope"])
                    if selection is not None
                    else nullcontext()
                ):
                    result = (
                        await provider.invoke_selected(call, selection)
                        if selection is not None
                        else await provider.invoke(call)
                    )
                assert (result.status, result.result) == expected
        assert (
            case["factory"].await_count,
            case["native"].execute_read_v3.await_count,
            case["request"].execute_get_many.await_count,
            case["native"].open_request.call_count,
        ) == case["expected_capture"]
        assert len(provider.capabilities()) == 8
        host = cast(Host, record_root_host(provider.capabilities()))
        assert case["root"].ref in checked_record_roots(
            host,
            case["config"],
            case["executor"].native_table,
            case["executor"],
        )
        with pytest.raises(ValueError, match="inventory"):
            checked_record_roots(
                host,
                replace(
                    case["config"],
                    record_roots=(replace(case["root"], receipt_digest="b" * 64),),
                ),
                case["executor"].native_table,
                case["executor"],
            )
    elif profile in {"read", "v2_all"}:
        with pytest.raises(ValueError, match="server-guarded"):
            scenario(profile)
        return
    else:
        native, provider, _inputs, expected, actor, scope, call = scenario(
            profile, kind
        )
        await provider.prepare()
        assert ((result := await provider.invoke(call)).status, len(native.calls)) == (
            "denied" if kind == "service" else "succeeded",
            0 if kind == "service" else 1,
        )
        capture = native.calls[0] if native.calls else None
        assert (
            capture is not None,
            capture[0]["call"] if capture else None,
            capture[1]
            == SessionIdentity(cast(Literal["person", "batch"], kind), actor.subject)
            if capture
            else False,
            capture[2].principal == capture[1] if capture else False,
            (capture[2].application, capture[2].request_id, capture[2].lease_id)
            if capture
            else None,
        ) == (
            kind != "service",
            {"kind": "single", "inputs": {"amount": expected}}
            if kind != "service"
            else None,
            kind != "service",
            kind != "service",
            (scope.application, scope.request_id, scope.lease_id)
            if kind != "service"
            else None,
        )
        for malformed in malformed_cases(profile, kind, result.result):
            native.response = malformed
            assert (
                (refused := await provider.invoke(call)).result,
                refused.code,
            ) == ({}, "native_refused")
        before, wrong_root = len(native.calls), wrong_root_call(profile, call)
        assert (
            (await provider.invoke(wrong_root)).status,
            len(native.calls),
        ) in (("invalid", before), ("denied", before))
        denial, limit, precondition, private = (
            {"schema": native.schema, "error": error}
            for error in (
                {"code": "DENIED"},
                {"code": "LIMIT_EXCEEDED"},
                {"code": "PRECONDITION_FAILED"},
                "private provider diagnostic",
            )
        )
        checks = invalid_read_inputs(
            call, actor, scope, kind, denial, limit, precondition, private
        )
        for invalid, response, statuses in checks:
            native.response = cast(dict[str, object] | None, response)
            assert (
                (refused := await provider.invoke(invalid)).status in statuses,
                refused.result,
            ) == (True, {})
    assert (
        await provider.aclose(),
        (await provider.invoke(call)).status != "succeeded",
    ) == (None, True)
