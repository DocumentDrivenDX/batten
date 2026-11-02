---
ddx:
  id: US-112
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: service-handoff.prd
      kind: derived_from
---

# US-112: Complete the cross-application service handoff journey

**Feature**: FEAT-112 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** requesting user and receiving service owner
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-012. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Discover a permitted service, bind its exact interface, submit a request and observe receiving progress.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-112-AC1** — Given fabricated requester app and an admitted receiving export, when the actor performs the journey, then one attributable request with preserved causal identity and receiver-scoped authority.
- [ ] **US-112-AC2** — Given the app's business invariant, when actors revoke the binding or change the provider interface before invocation, then handoff refuses without choosing another provider or replaying the command.
- [ ] **US-112-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-112-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-112-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-112-AC1 | fabricated requester app and an admitted receiving export | resolve and invoke its exact approved interface | one attributable request with preserved causal identity and receiver-scoped authority |
| Business invariant | US-112-AC2 | Same original fixture | revoke the binding or change the provider interface before invocation | handoff refuses without choosing another provider or replaying the command |
| Current authority | US-112-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-112-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-112-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
graphs,services,messaging,actions. Their presence requests support and grants no authority.

## Out of Scope

No ambient service discovery or automatic authority propagation. Full platform implementation is not authorized by this app story.
