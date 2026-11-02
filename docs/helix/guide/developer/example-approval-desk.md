<!-- helix:publish audience=developer page=example-approval-desk kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/01b0a28be3072a1f -->
<!-- helix:source docs/helix/reference-apps/approval-desk/specs/01-frame/prd.md sha256:0811410edd777ad4 -->
<!-- helix:source docs/helix/reference-apps/approval-desk/specs/01-frame/user-stories/US-101-journey.md sha256:f655241ab564f90e -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->
<!-- helix:source examples/approval-desk/README.md sha256:a532bd5d7719003f -->
<!-- helix:source examples/approval-desk/web/index.html sha256:288b5af40a12013e -->
<!-- helix:source examples/approval-desk/web/app.ts sha256:6c0aff047a0123a8 -->
<!-- helix:source docs/helix/05-deploy/runtime-release-0.1.0a1.md sha256:05463eb9e1a57115 -->

# Approval desk walkthrough

Runnable local preview. Follow this journey as a requester and independent approver. Use fabricated data throughout.

[Prepare and start the local app](https://github.com/DocumentDrivenDX/batten/blob/main/examples/approval-desk/README.md) before following these steps. The preview uses loopback development identities and PostgreSQL 18; production authentication and broader fleet qualification remain separate.

## Capabilities in this journey

tables, actions. These tags describe requested integration boundaries.

## 1. Open the local registry

Follow the run instructions to prepare the exact Python 3.11 cohort and explicitly initialize a new fabricated database. Start the host, open its root registry and choose Approval desk.

## 2. Submit as Alex

Choose Alex in Local identity. Enter a fabricated summary in Request summary and select Submit for review. Select the pending request to inspect its current revision.

## 3. Revise before deciding

As Alex, change the pending summary and select Save changes. The requester can edit but cannot approve their own request.

## 4. Review as Blake

Switch to Blake, the independent reviewer. Refresh and inspect the current request before selecting Approve request or Reject request. A decision based on an older revision must refuse.

## 5. Inspect the original outcome

Confirm the final state and decision identity. If a response is lost, use Check original outcome with the retained attempt rather than submitting a fresh command. The Batten brand returns to the registry.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/approval-desk/specs/01-frame/user-stories/US-101-journey.md) or [choose another example](examples.md).
