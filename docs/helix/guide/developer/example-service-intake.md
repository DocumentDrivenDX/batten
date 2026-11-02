<!-- helix:publish audience=developer page=example-service-intake kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/a265097171b67cd7 -->
<!-- helix:source docs/helix/reference-apps/service-intake/specs/01-frame/prd.md sha256:9e32a07055839786 -->
<!-- helix:source docs/helix/reference-apps/service-intake/specs/01-frame/user-stories/US-102-journey.md sha256:3e1f077bd2964862 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Service intake and routing walkthrough

Specification walkthrough. Follow this journey as a requester and service coordinator. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, actions, messaging. These tags describe requested integration boundaries.

## 1. Submit once

A requester sends a fabricated service request with a stable submission identity.

## 2. Classify and route

A service coordinator classifies the intake and routes it to a queue they are permitted to use.

## 3. Acknowledge assignment

Inspect the current assignment and acknowledge it. Only permitted users should see the intake and assignment.

## 4. Recover a lost submission

Lose the response and inspect the original submission identity. The expected result is the original intake, without another record.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/service-intake/specs/01-frame/user-stories/US-102-journey.md) or [choose another example](examples.md).
