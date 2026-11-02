<!-- helix:publish audience=developer page=example-data-reconciliation kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/8adb95f6e68931b0 -->
<!-- helix:source docs/helix/reference-apps/data-reconciliation/specs/01-frame/prd.md sha256:7b55be2d9e5eefa1 -->
<!-- helix:source docs/helix/reference-apps/data-reconciliation/specs/01-frame/user-stories/US-109-journey.md sha256:d6bdb101d8822381 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Data reconciliation workbench walkthrough

Specification walkthrough. Follow this journey as a data steward and reconciliation reviewer. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

tables, actions, jobs. These tags describe requested integration boundaries.

## 1. Capture source snapshots

A data steward compares two bounded fabricated snapshots containing a conflicting field.

## 2. Inspect the difference

Review the discrepancy and its original source lineage before proposing a resolution.

## 3. Approve and apply

A reconciliation reviewer approves the resolution and inspects its applied result.

## 4. Change a source before apply

Change one source after comparison. Applying the old repair must refuse stale inputs and preserve the newer source value.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/data-reconciliation/specs/01-frame/user-stories/US-109-journey.md) or [choose another example](examples.md).
