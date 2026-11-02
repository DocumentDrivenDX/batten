<!-- helix:publish audience=developer page=example-service-handoff kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/66e9cdbb0d23e750 -->
<!-- helix:source docs/helix/reference-apps/service-handoff/specs/01-frame/prd.md sha256:3adbe1d33ddfd218 -->
<!-- helix:source docs/helix/reference-apps/service-handoff/specs/01-frame/user-stories/US-112-journey.md sha256:d0a1df9e69f24ac3 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Cross-application service handoff walkthrough

Specification walkthrough. Follow this journey as a requesting user and receiving service owner. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

graphs, services, messaging, actions. These tags describe requested integration boundaries.

## 1. Discover a permitted export

A requesting user discovers an admitted receiving service export they may see.

## 2. Bind the exact interface

Resolve the exact host-approved interface and binding. Discovery alone supplies no authority.

## 3. Submit and observe

Submit a request and inspect receiver progress with original causal identity and receiver-scoped authority.

## 4. Revoke the binding

Revoke the binding or change the provider interface before invocation. Handoff must refuse without silently choosing another provider or replaying a command.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/service-handoff/specs/01-frame/user-stories/US-112-journey.md) or [choose another example](examples.md).
