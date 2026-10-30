---
ddx:
  id: US-002
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: batten.prd
      kind: derived_from
---

# US-002: Bind one application to different hosts

**Feature:** [FEAT-009](../features/FEAT-009-composition-and-hosting.md)
**Feature Requirements:** CMP-07–09, CMP-12
**PRD Requirements:** FR-36
**Priority:** P0

## Story

**As a** Host integrator and operator,
**I want** to bind the same application to local and embedded profiles,
**So that** I can change its environment without changing application meaning.

## Context

The review application has the same digest in both environments. The local profile owns its fabricated identity and resources; the embedded profile borrows real host-provided services.

## Walkthrough

1. Supply the review application's exact artifacts and selected module metadata.
2. Select the explicit host profile and assess its capability bindings.
3. Inspect safe findings or proceed through the declared public boundary.
4. Observe the outcome and its evidence without changing the application meaning.

## Acceptance Criteria

- [ ] **US-002-AC1** — Given one application and local and embedded profiles, when assessed, then the application digest stays equal while resource ownership and bindings differ explicitly.
- [ ] **US-002-AC2** — Given an assessed plan whose cohort or profile changed, when start is requested, then drift is refused before any provider effect.
- [ ] **US-002-AC3** — Given dependency-ordered services and a later startup failure, when cleanup runs, then owned resources close in reverse order and borrowed services remain open.
- [ ] **US-002-AC4** — Given a cleanup timeout, when readiness and shutdown are observed, then retained resources remain visible without a false closed state.
- [ ] **US-002-AC5** — Given fabricated identity in a standalone or embedded profile, when assessed, then the deployment profile is refused.
- [ ] **US-002-AC6** — Given a separated worker without qualified transport capabilities, when assessed, then placement is refused rather than using an implicit local fallback.

## Edge Cases

Unknown required semantics block eligibility while preserving source content.
A host-profile change requires a new assessment; stale authorization grants no
continuing permission. Native and browser support need their own observations.

## Test Scenarios

Names below are planned evidence, not existing or passing tests. Each eventual
test must cite its criterion with the canonical `@covers US-002-AC1` syntax
using the matching criterion ID. Consolidate cases by observable behavior under
the first reviewed measured test ceiling; these names do not set that ceiling.

| Criterion | Planned scenario | Concrete assertion |
| --- | --- | --- |
| US-002-AC1 | `test_profile_portability` | equal app digest, distinct approved plans |
| US-002-AC2 | `test_plan_drift` | no prepare calls after drift |
| US-002-AC3 | `test_startup_cleanup` | complete observed cleanup order and borrowed lifetime |
| US-002-AC4 | `test_shutdown_uncertainty` | unsettled resources preserved |
| US-002-AC5 | `test_identity_boundary` | deployed profiles deny fabricated identity |
| US-002-AC6 | `test_remote_placement` | unsupported placement refused |

## Dependencies

FEAT-009; PRD FR-36; CONTRACT-004; CONTRACT-001/002. Exact dependency cohort and
public upstream APIs require integration evidence before their runtime claims.

## Out of Scope

Deployment, infrastructure provisioning, migration of existing consumers,
upstream saga implementation and claims of passing tests from metadata alone.
