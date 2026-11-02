---
ddx:
  id: US-106
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: entity-directory.prd
      kind: derived_from
---

# US-106: Complete the entity and relationship directory journey

**Feature**: FEAT-106 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** directory steward and scoped analyst
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-006. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Register an entity, link a related entity, traverse authorized relationships and update approved attributes.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-106-AC1** — Given permitted entity plus a separate hidden entity, when the actor performs the journey, then only authorized attributes and relationships are returned with their original model identity.
- [ ] **US-106-AC2** — Given the app's business invariant, when actors include a path through the hidden entity, then no hidden endpoint, property or count is disclosed.
- [ ] **US-106-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-106-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-106-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-106-AC1 | permitted entity plus a separate hidden entity | query the scoped entity and its permitted relationships | only authorized attributes and relationships are returned with their original model identity |
| Business invariant | US-106-AC2 | Same original fixture | include a path through the hidden entity | no hidden endpoint, property or count is disclosed |
| Current authority | US-106-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-106-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-106-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
graphs,actions. Their presence requests support and grants no authority.

## Out of Scope

No duplicated ontology/query engine; Truss remains the graph executor. Full platform implementation is not authorized by this app story.
