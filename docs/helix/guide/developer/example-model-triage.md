<!-- helix:publish audience=developer page=example-model-triage kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/7f2fe6c6ca8ddd34 -->
<!-- helix:source docs/helix/reference-apps/model-triage/specs/01-frame/prd.md sha256:797429f398957b19 -->
<!-- helix:source docs/helix/reference-apps/model-triage/specs/01-frame/user-stories/US-108-journey.md sha256:cb2df85a8c83b356 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# AI-assisted inbox triage walkthrough

Specification walkthrough. Follow this journey as a triage analyst and automation owner. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, messaging, agents, models, actions. These tags describe requested integration boundaries.

## 1. Receive an inbox item

Receive fabricated work with a durable message identity.

## 2. Classify within budget

Request model assistance within the declared budget and preserve the original item identity.

## 3. Review the suggestion

An authorized human reviews the suggestion and applies a disposition. Inspect both the attributable business result and the settled delivery outcome.

## 4. Redeliver after response loss

Redeliver the same message after losing its processing response. Observe the original business result without applying the disposition twice.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/model-triage/specs/01-frame/user-stories/US-108-journey.md) or [choose another example](examples.md).
