---
ddx:
  id: US-105
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: document-review.prd
      kind: derived_from
---

# US-105: Complete the assisted document review journey

**Feature**: FEAT-105 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** reviewer and final decision owner
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-005. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Upload a fabricated document, request extraction, inspect provenance, correct suggestions and accept a reviewed result.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-105-AC1** — Given document with fabricated content and a bounded model request, when the actor performs the journey, then accepted facts retain original document and human decision provenance.
- [ ] **US-105-AC2** — Given the app's business invariant, when actors model returns an unsupported factual assertion or unavailable response, then unsupported suggestions remain unaccepted; failure exposes no private prompt or credentials.
- [ ] **US-105-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-105-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-105-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-105-AC1 | document with fabricated content and a bounded model request | extract suggestions then accept a corrected result | accepted facts retain original document and human decision provenance |
| Business invariant | US-105-AC2 | Same original fixture | model returns an unsupported factual assertion or unavailable response | unsupported suggestions remain unaccepted; failure exposes no private prompt or credentials |
| Current authority | US-105-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-105-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-105-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,storage,agents,models,actions. Their presence requests support and grants no authority.

## Out of Scope

No legal opinion, OCR engine or provider-independent model quality guarantee. Full platform implementation is not authorized by this app story.
