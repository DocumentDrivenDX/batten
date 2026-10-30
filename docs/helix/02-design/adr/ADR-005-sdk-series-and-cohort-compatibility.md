---
ddx:
  id: ADR-005
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-003
      kind: informed_by
---

# ADR-005: SDK series is independent of the embedding host release

## Problem

A plugin must declare the contract it uses without being rebuilt for every host
release. Separately installed modules also need explicit platform compatibility.

## Decision

A plugin declares `sdk` as the Batten contract's `MAJOR.MINOR` series. The host
admits equal major and plugin minor no greater than its supported minor. Required
module capabilities, manifest format, worker protocol, browser protocol, and
installed distribution constraints are checked separately before plugin execution.
Passing the series check alone never establishes complete compatibility.

The proposed first stable series is `1.0`; this assigns no published release and
claims no compatibility with another SDK's identically numbered series. Development
artifacts use explicit prerelease versions. A common Batten release cohort pins
exact wheel versions; the host reports its tested upstream platform cohort.

Optional compatible fields/methods can add a minor. Removal, changed meaning,
new required fields, or a narrower accepted input contract require a major.
Patch releases preserve contract semantics. Unknown required components refuse;
unknown optional extension content is retained, not executed or silently dropped.

Deprecation is announced for a minor before removal and includes a replacement;
removal still requires the major change. Later host-owned legacy compatibility
has its own consumer tests and does not alter Batten's native contract.

## Fleet upgrade qualification

PRD FR-42 makes safe dependency evolution a platform responsibility. Before a
candidate cohort qualifies, the platform must inventory affected applications
and declared integrations, run their required assertions and behavior coverage,
and verify required telemetry and protocol compatibility. Evidence must bind
exact candidate runtime, application and policy inputs; changing them invalidates
the result. A series match or a passing platform-only suite is insufficient.

The operator must be able to withhold a failing candidate and retain a qualified
cohort. Recovery must assess durable-state compatibility and preserve uncertain
external outcomes. There is no implicit schema/data rollback. Exact evidence
formats, required telemetry failure policy and rollout controls need contracts
before source implementation. No fleet upgrade has been qualified in this packet.

## Why We Chose This

### Over matching the host product version

Contract versions track application-facing meaning. A host release that changes
unrelated behavior should not invalidate every plugin.

### Over checking only SDK major/minor or dependency names

The selected capability and installed platform release may still be incompatible.
Independent wire/format/dependency checks make that refusal explicit.

## Consequences

**Good**: Authors know the contract series and capabilities their artifact needs.

**Trade-offs**: Release qualification must publish a real compatibility matrix;
cohort combinations outside it carry no support claim.

**Drift signals to watch**: importing code before metadata checks, name-only
dependency admission, or changing behavior under a patch without contract review.

## Concern Impact

Implements artifact admission, native-platform qualification, and cleanroom identity.
