<!-- helix:publish audience=developer page=example-case-tracker kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/c19320fbd5969cba -->
<!-- helix:source docs/helix/reference-apps/case-tracker/specs/01-frame/prd.md sha256:f27b09a20a126d83 -->
<!-- helix:source docs/helix/reference-apps/case-tracker/specs/01-frame/user-stories/US-103-journey.md sha256:da3963254c517cc0 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Case and task tracker walkthrough

Specification walkthrough. Follow this journey as a case owner and assigned worker. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, graphs, actions. These tags describe requested integration boundaries.

## 1. Open a case

A case owner opens a fabricated case and relates a required task to it.

## 2. Assign the task

Assign the work to a permitted worker and inspect both the task state and case revision.

## 3. Try early closure

Attempt to close the case while the required task is unfinished. The expected refusal preserves both current states.

## 4. Complete and close

The assigned worker completes the prerequisite. The owner closes the case and inspects its original task and decision lineage.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/case-tracker/specs/01-frame/user-stories/US-103-journey.md) or [choose another example](examples.md).
