---
ddx:
  id: US-111
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: access-attestation.prd
      kind: derived_from
---

# US-111: Complete the access review and attestation journey

**Feature**: FEAT-111 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** resource owner and independent reviewer
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-011. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Capture a scoped access snapshot, review assignments, attest or request removal and inspect the outcome.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-111-AC1** — Given fabricated resource grants and a named review snapshot, when the actor performs the journey, then signed-in reviewer decision retains snapshot and actor identity.
- [ ] **US-111-AC2** — Given the app's business invariant, when actors native grants change after snapshot capture, then decision remains bound to the old snapshot and live changes are explicitly reported.
- [ ] **US-111-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-111-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-111-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-111-AC1 | fabricated resource grants and a named review snapshot | review and attest the selected assignment | signed-in reviewer decision retains snapshot and actor identity |
| Business invariant | US-111-AC2 | Same original fixture | native grants change after snapshot capture | decision remains bound to the old snapshot and live changes are explicitly reported |
| Current authority | US-111-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-111-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-111-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,graphs,actions. Their presence requests support and grants no authority.

## Out of Scope

No identity-provider provisioning or automatic native grant change. Full platform implementation is not authorized by this app story.
