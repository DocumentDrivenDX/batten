---
ddx:
  id: US-101
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: approval-desk.prd
      kind: derived_from
---

# US-101: Complete the approval desk journey

**Feature**: FEAT-101 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** requester and independent approver
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-001. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Submit a request, inspect its revision, approve or reject, then observe the final decision.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-101-AC1** — Given pending request owned by actor-a, when the actor performs the journey, then one approved request and attributable independent decision.
- [ ] **US-101-AC2** — Given the app's business invariant, when actors change the request after the approver opens it, then stale approval is refused and the newer request remains unchanged.
- [ ] **US-101-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-101-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-101-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

- [ ] **US-101-AC6** — Given the local runtime registry, when I open the approval desk card and later click the Batten brand, then I see the app description and visual thumbnail, enter its own URL, and return to the registry without gaining business authority from the listing.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-101-AC1 | pending request owned by actor-a | approve using the current revision | one approved request and attributable independent decision |
| Business invariant | US-101-AC2 | Same original fixture | change the request after the approver opens it | stale approval is refused and the newer request remains unchanged |
| Current authority | US-101-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-101-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-101-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,actions. Their presence requests support and grants no authority.

## Out of Scope

No money movement or authoritative accounting ledger. Full platform implementation is not authorized by this app story.
