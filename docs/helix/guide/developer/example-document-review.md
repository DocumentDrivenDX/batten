<!-- helix:publish audience=developer page=example-document-review kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/5715af258a8ad5ba -->
<!-- helix:source docs/helix/reference-apps/document-review/specs/01-frame/prd.md sha256:182c987a77cdea67 -->
<!-- helix:source docs/helix/reference-apps/document-review/specs/01-frame/user-stories/US-105-journey.md sha256:326e9255af9f382d -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Assisted document review walkthrough

Specification walkthrough. Follow this journey as a reviewer and final decision owner. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, storage, agents, models, actions. These tags describe requested integration boundaries.

## 1. Provide a document

An authorized author uploads a fabricated document and requests bounded extraction.

## 2. Inspect the suggestions

A reviewer checks extracted facts against the original document and inspects provenance.

## 3. Correct and accept

Correct suggestions and accept the reviewed result. Accepted facts must retain document lineage and the human decision.

## 4. Challenge unsupported output

Introduce an unsupported assertion or unavailable model response. Unsupported suggestions remain unaccepted, and diagnostics disclose no private prompt or credentials.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/document-review/specs/01-frame/user-stories/US-105-journey.md) or [choose another example](examples.md).
