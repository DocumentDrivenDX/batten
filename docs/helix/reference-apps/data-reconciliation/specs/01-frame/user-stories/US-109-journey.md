---
ddx:
  id: US-109
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: data-reconciliation.prd
      kind: derived_from
---

# US-109: Complete the data reconciliation workbench journey

**Feature**: FEAT-109 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** data steward and reconciliation reviewer
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-009. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Compare bounded source snapshots, inspect discrepancies, approve a resolution and inspect the applied result.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-109-AC1** — Given two fabricated source snapshots and a conflicting field, when the actor performs the journey, then approved difference resolves with original source lineage.
- [ ] **US-109-AC2** — Given the app's business invariant, when actors change a source after comparison and before apply, then repair refuses stale inputs and preserves the new source value.
- [ ] **US-109-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-109-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-109-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-109-AC1 | two fabricated source snapshots and a conflicting field | compare, review and conditionally apply a repair | approved difference resolves with original source lineage |
| Business invariant | US-109-AC2 | Same original fixture | change a source after comparison and before apply | repair refuses stale inputs and preserves the new source value |
| Current authority | US-109-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-109-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-109-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,actions,jobs. Their presence requests support and grants no authority.

## Out of Scope

Large transformations stay in existing platform jobs; no new ETL engine. Full platform implementation is not authorized by this app story.
