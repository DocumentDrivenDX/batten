<!-- helix:publish audience=developer page=example-scheduled-digest kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/2e664952e5d782ef -->
<!-- helix:source docs/helix/reference-apps/scheduled-digest/specs/01-frame/prd.md sha256:1406dbec54dbf1aa -->
<!-- helix:source docs/helix/reference-apps/scheduled-digest/specs/01-frame/user-stories/US-110-journey.md sha256:e3465825a1ef9157 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Scheduled operational digest walkthrough

Specification walkthrough. Follow this journey as a schedule owner and authorized recipient. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, jobs, storage, messaging. These tags describe requested integration boundaries.

## 1. Define a bounded report

A schedule owner selects permitted fabricated report rows and a schedule occurrence.

## 2. Execute due work

Run the due occurrence with its original identity and bounded inputs.

## 3. Publish and inspect

Publish the report artifact and inspect its permitted reference and delivery status.

## 4. Compete for one occurrence

Have workers compete for the same occurrence, then lose a response. The original run and possible delivery outcome remain observable without a second business publication.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/scheduled-digest/specs/01-frame/user-stories/US-110-journey.md) or [choose another example](examples.md).
