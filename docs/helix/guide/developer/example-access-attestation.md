<!-- helix:publish audience=developer page=example-access-attestation kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/ebdc24763524a4af -->
<!-- helix:source docs/helix/reference-apps/access-attestation/specs/01-frame/prd.md sha256:5812968b9124dd13 -->
<!-- helix:source docs/helix/reference-apps/access-attestation/specs/01-frame/user-stories/US-111-journey.md sha256:f6ece4bf831a4946 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Access review and attestation walkthrough

Specification walkthrough. Follow this journey as a resource owner and independent reviewer. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, graphs, actions. These tags describe requested integration boundaries.

## 1. Capture a review snapshot

A resource owner captures a named snapshot of scoped fabricated resource grants.

## 2. Review assignments

An independent reviewer inspects the captured assignments and their snapshot identity.

## 3. Record an attestation

Attest an assignment or request removal, retaining snapshot and reviewer identity. This workflow does not automatically change native grants.

## 4. Change a live grant

Change native grants after capture. The decision remains bound to the old snapshot while live changes are explicitly reported.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/access-attestation/specs/01-frame/user-stories/US-111-journey.md) or [choose another example](examples.md).
