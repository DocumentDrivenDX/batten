---
ddx:
  id: US-004
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

# US-004: Bind UMF saga capabilities

**Feature:** [FEAT-009](../features/FEAT-009-composition-and-hosting.md)
**Feature Requirements:** CMP-03, CMP-10
**PRD Requirements:** FR-38
**Priority:** P0

## Story

**As a** Host integrator and operator,
**I want** to bind a declared UMF saga to a qualified executor,
**So that** application recovery retains upstream meaning across host placement.

## Context

UMF supplies saga declarations and qualification obligations. This Batten slice supplies metadata/capability binding; it cannot invent missing upstream execution semantics.

## Walkthrough

1. Supply the review application's exact artifacts and selected module metadata.
2. Select the explicit host profile and assess its capability bindings.
3. Inspect safe findings or proceed through the declared public boundary.
4. Observe the outcome and its evidence without changing the application meaning.

## Acceptance Criteria

- [ ] **US-004-AC1** — Given a saga reference without supported UMF vocabulary or executor, when assessed, then only the affected required component is ineligible and no fallback saga engine is selected.
- [ ] **US-004-AC2** — Given an exact qualified upstream declaration/profile/executor pairing, when bound, then its original identities and outcomes pass through without redefinition.
- [ ] **US-004-AC3** — Given an uncertain upstream effect, when observation or cancellation is requested, then Batten retains uncertainty and performs no new business invocation.

## Edge Cases

Unknown required semantics block eligibility while preserving source content.
A host-profile change requires a new assessment; stale authorization grants no
continuing permission. Native and browser support need their own observations.

## Test Scenarios

Names below are planned evidence, not existing or passing tests. Each eventual
test must cite its criterion with the canonical `@covers US-004-AC1` syntax
using the matching criterion ID. Consolidate cases by observable behavior under
the first reviewed measured test ceiling; these names do not set that ceiling.

| Criterion | Planned scenario | Concrete assertion |
| --- | --- | --- |
| US-004-AC1 | `test_saga_capability_refusal` | missing upstream support refuses |
| US-004-AC2 | `test_saga_binding_passthrough` | upstream identity and outcome retained |
| US-004-AC3 | `test_saga_uncertainty` | no synthetic rollback or duplicate invocation |

## Dependencies

FEAT-009; PRD FR-38; CONTRACT-003 and CONTRACT-004; CONTRACT-001/002. Exact dependency cohort and
public upstream APIs require integration evidence before their runtime claims.

## Out of Scope

Deployment, infrastructure provisioning, migration of existing consumers,
upstream saga implementation and claims of passing tests from metadata alone.
