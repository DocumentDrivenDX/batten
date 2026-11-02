---
ddx:
  id: US-102
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: service-intake.prd
      kind: derived_from
---

# US-102: Complete the service intake and routing journey

**Feature**: FEAT-102 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** requester and service coordinator
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-002. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Submit an intake form, classify it, route it to a permitted queue and acknowledge assignment.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-102-AC1** — Given fabricated request with a stable submission identity, when the actor performs the journey, then one intake and one current assignment visible only to permitted users.
- [ ] **US-102-AC2** — Given the app's business invariant, when actors repeat submission after its response is lost, then original result is observed without creating another intake.
- [ ] **US-102-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-102-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-102-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-102-AC1 | fabricated request with a stable submission identity | submit then route to a permitted team | one intake and one current assignment visible only to permitted users |
| Business invariant | US-102-AC2 | Same original fixture | repeat submission after its response is lost | original result is observed without creating another intake |
| Current authority | US-102-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-102-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-102-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,actions,messaging. Their presence requests support and grants no authority.

## Out of Scope

No arbitrary external ticket connector is assumed. Full platform implementation is not authorized by this app story.
