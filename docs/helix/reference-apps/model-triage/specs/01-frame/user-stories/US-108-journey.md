---
ddx:
  id: US-108
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: model-triage.prd
      kind: derived_from
---

# US-108: Complete the ai-assisted inbox triage journey

**Feature**: FEAT-108 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** triage analyst and automation owner
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-008. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Receive an inbox item, classify it within a budget, review the suggestion and apply an authorized disposition.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-108-AC1** — Given fabricated inbox item with one durable message identity, when the actor performs the journey, then one attributable disposition and a settled delivery outcome.
- [ ] **US-108-AC2** — Given the app's business invariant, when actors redeliver after processing response loss, then consumer observes original business result and does not apply the disposition twice.
- [ ] **US-108-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-108-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-108-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-108-AC1 | fabricated inbox item with one durable message identity | classify then approve its disposition | one attributable disposition and a settled delivery outcome |
| Business invariant | US-108-AC2 | Same original fixture | redeliver after processing response loss | consumer observes original business result and does not apply the disposition twice |
| Current authority | US-108-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-108-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-108-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,messaging,agents,models,actions. Their presence requests support and grants no authority.

## Out of Scope

No exactly-once external side-effect guarantee or autonomous high-impact decision. Full platform implementation is not authorized by this app story.
