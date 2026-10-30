---
ddx:
  id: US-001
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

# US-001: Assess application composition

**Feature:** [FEAT-009](../features/FEAT-009-composition-and-hosting.md)
**Feature Requirements:** CMP-01–06, CMP-11
**PRD Requirements:** FR-34, FR-35, FR-37
**Priority:** P0

## Story

**As a** Application author,
**I want** to select capabilities and inspect their resolved dependencies,
**So that** I can correct missing capabilities before starting the application.

## Context

A fabricated review queue references its native Review model, approve action and optional UI. The installed cohort is supplied as inert metadata, not imported to discover its contents.

## Walkthrough

1. Supply the review application's exact artifacts and selected module metadata.
2. Select the explicit host profile and assess its capability bindings.
3. Inspect safe findings or proceed through the declared public boundary.
4. Observe the outcome and its evidence without changing the application meaning.

## Acceptance Criteria

- [ ] **US-001-AC1** — Given exact compatible module descriptors and application artifacts, when assessment runs, then it returns a deterministic dependency order without importing providers or starting services.
- [ ] **US-001-AC2** — Given a missing, ambiguous or incompatible required provider, when assessed, then safe findings identify the unsatisfied requirement and no eligible plan is returned.
- [ ] **US-001-AC3** — Given a cyclic dependency or unsupported placement, when assessed, then the affected graph is refused without guessing a valid order.
- [ ] **US-001-AC4** — Given unknown application content, when exchanged and assessed, then bytes remain recoverable while relevant unknown semantics block eligibility.
- [ ] **US-001-AC5** — Given an absent optional UI module in a headless app, when installed and imported, then core and selected provider work without UI packages.
- [ ] **US-001-AC6** — Given a procedural hook naming an unreviewed handler, when assessed, then declaration content cannot authorize loading it.

## Edge Cases

Unknown required semantics block eligibility while preserving source content.
A host-profile change requires a new assessment; stale authorization grants no
continuing permission. Native and browser support need their own observations.

## Test Scenarios

Names below are planned evidence, not existing or passing tests. Each eventual
test must cite its criterion with the canonical `@covers US-001-AC1` syntax
using the matching criterion ID. Consolidate cases by observable behavior under
the first reviewed measured test ceiling; these names do not set that ceiling.

| Criterion | Planned scenario | Concrete assertion |
| --- | --- | --- |
| US-001-AC1 | `test_assessment_is_effect_free` | ordered metadata result; import/network/start spies remain untouched |
| US-001-AC2 | `test_capability_resolution` | table of missing/ambiguous/version outcomes |
| US-001-AC3 | `test_composition_constraints` | cycle and placement cases refuse |
| US-001-AC4 | `test_unknown_preservation` | preserved source and incomplete semantic finding |
| US-001-AC5 | `test_headless_installation` | wheel-only import succeeds with UI packages absent |
| US-001-AC6 | `test_handler_admission` | unreviewed handler refused before import |

## Dependencies

FEAT-009; PRD FR-34, FR-35, FR-37; CONTRACT-003; CONTRACT-001/002. Exact dependency cohort and
public upstream APIs require integration evidence before their runtime claims.

## Out of Scope

Deployment, infrastructure provisioning, migration of existing consumers,
upstream saga implementation and claims of passing tests from metadata alone.
