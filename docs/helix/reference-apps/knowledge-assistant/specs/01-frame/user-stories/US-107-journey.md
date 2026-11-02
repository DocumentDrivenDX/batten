---
ddx:
  id: US-107
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: knowledge-assistant.prd
      kind: derived_from
---

# US-107: Complete the grounded knowledge assistant journey

**Feature**: FEAT-107 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** knowledge consumer and content owner
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-007. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Ask a question, retrieve authorized sources, inspect a grounded answer and open permitted citations.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-107-AC1** — Given question and fabricated sources with mixed visibility, when the actor performs the journey, then answer cites only available permitted source revisions and exposes uncertainty.
- [ ] **US-107-AC2** — Given the app's business invariant, when actors revoke source access before opening a citation, then citation access is refused without disclosing hidden source content.
- [ ] **US-107-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-107-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-107-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-107-AC1 | question and fabricated sources with mixed visibility | retrieve authorized evidence and produce an answer draft | answer cites only available permitted source revisions and exposes uncertainty |
| Business invariant | US-107-AC2 | Same original fixture | revoke source access before opening a citation | citation access is refused without disclosing hidden source content |
| Current authority | US-107-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-107-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-107-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,storage,agents,models,search. Their presence requests support and grants no authority.

## Out of Scope

No search/vector backend or accuracy level is implicitly selected. Full platform implementation is not authorized by this app story.
