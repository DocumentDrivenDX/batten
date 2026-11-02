---
ddx:
  id: US-104
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: evidence-library.prd
      kind: derived_from
---

# US-104: Complete the evidence and attachment library journey

**Feature**: FEAT-104 — Governed business journey
**Feature Requirements**: Reference-app business journey.
**PRD Requirements**: FR-1, FR-2, FR-3, FR-4.
**Priority**: P0.

## Story

**As a** contributor and permitted reader
**I want** to complete the governed business journey
**So that** I can rely on its authorized result and recover safely after interruption.

## Context

This is application MA-004. Business rules below are explicit fabricated defaults.
They remain independent of whichever platform implementation is being qualified.

## Walkthrough

1. The actor opens permitted work and inspects its current state and revision.
2. The actor follows the journey: Upload fabricated evidence, verify bytes, link its immutable reference to a record and retrieve it.
3. The host checks current authority and original operation identity.
4. The actor observes the result, or reconciles the original uncertain attempt.

## Acceptance Criteria

- [ ] **US-104-AC1** — Given fabricated attachment with an original upload identity, when the actor performs the journey, then authorized retrieval returns the verified bytes and matching record reference.
- [ ] **US-104-AC2** — Given the app's business invariant, when actors interrupt between object publication and metadata confirmation, then published bytes are preserved and the original outcome is reconciled without blind upload replay.
- [ ] **US-104-AC3** — Given a foreign, anonymous or revoked actor, when they attempt the same operation or continuation, then no private result or unauthorized mutation is disclosed.
- [ ] **US-104-AC4** — Given response loss or cancellation, when the actor inspects original work, then actual effects and uncertainty remain attributable without a fresh blind command.
- [ ] **US-104-AC5** — Given the same business inputs on another supported surface or cohort, when the journey runs, then meaning and authority are preserved; unsupported required behavior refuses explicitly.

## Edge Cases

- Empty permitted data returns an authorized empty state, not hidden counts.
- Dependency failure exposes a safe outcome; a scripted replacement is not selected.
- Query and inspection do not mutate business records or retry uncertain commands.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Main journey | US-104-AC1 | fabricated attachment with an original upload identity | upload, verify and publish its reference | authorized retrieval returns the verified bytes and matching record reference |
| Business invariant | US-104-AC2 | Same original fixture | interrupt between object publication and metadata confirmation | published bytes are preserved and the original outcome is reconciled without blind upload replay |
| Current authority | US-104-AC3 | Fixture foreign actor | Attempt and continue work | Safe denial without disclosure |
| Lost response | US-104-AC4 | Original possibly effective attempt | Observe original identity | Actual or uncertain outcome, no blind replay |
| Cohort parity | US-104-AC5 | Same semantic inputs | Exercise supported client/host | Same meaning or explicit refusal |

## Dependencies

Local PRD FR-1–4; SDK CONTRACT-003/004/005/011. Native platform model/action
contracts must be selected before executable app construction. Corpus tags:
tables,storage,actions. Their presence requests support and grants no authority.

## Out of Scope

No claim of an atomic transaction across database rows and object storage. Full platform implementation is not authorized by this app story.
