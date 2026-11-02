<!-- helix:publish audience=developer page=example-knowledge-assistant kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/aca47475213fff14 -->
<!-- helix:source docs/helix/reference-apps/knowledge-assistant/specs/01-frame/prd.md sha256:ca8db4a12cb6f8a5 -->
<!-- helix:source docs/helix/reference-apps/knowledge-assistant/specs/01-frame/user-stories/US-107-journey.md sha256:b7075fe80f4d5408 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Grounded knowledge assistant walkthrough

Specification walkthrough. Follow this journey as a knowledge consumer and content owner. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, storage, agents, models, search. These tags describe requested integration boundaries.

## 1. Ask a question

A reader asks a question against fabricated sources with mixed visibility.

## 2. Retrieve permitted revisions

Retrieve only authorized sources and retain the exact source revisions used by the answer.

## 3. Inspect answer and citations

Read the grounded answer, its uncertainty and citations. Open a permitted citation to inspect the supporting material.

## 4. Revoke source access

Revoke access before reopening a citation. Citation access must refuse without revealing the hidden source content.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/knowledge-assistant/specs/01-frame/user-stories/US-107-journey.md) or [choose another example](examples.md).
