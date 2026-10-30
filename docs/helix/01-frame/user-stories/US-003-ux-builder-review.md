---
ddx:
  id: US-003
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: derived_from
    - id: batten.prd
      kind: derived_from
---

# US-003: Review through a ux-builder interface

**Feature:** [FEAT-002](../features/FEAT-002-operations-and-interfaces.md)
**Feature Requirements:** UI-02–12
**PRD Requirements:** FR-39–41
**Priority:** P0

## Story

**As a** Application author,
**I want** to bind a ux-builder review screen to the declared approval operation,
**So that** users receive the same governed outcome in local and embedded hosts.

## Context

The review screen uses fabricated records and a deterministic agent double. Its blueprint and assets belong to ux-builder; Batten supplies operation bindings and authenticated host context.

## Walkthrough

1. Supply the review application's exact artifacts and selected module metadata.
2. Select the explicit host profile and assess its capability bindings.
3. Inspect safe findings or proceed through the declared public boundary.
4. Observe the outcome and its evidence without changing the application meaning.

## Acceptance Criteria

- [ ] **US-003-AC1** — Given the same review application under local and embedded profiles, when the user opens a record and approves it, then the same typed operation and server-authorized outcome occur.
- [ ] **US-003-AC2** — Given slow, denied, invalid and successful operation responses, when the user submits review, then each state presents an accessible outcome and a valid recovery path.
- [ ] **US-003-AC3** — Given an uncertain write outcome, when the user revisits its status, then the original invocation is reconciled without issuing a fresh approval.
- [ ] **US-003-AC4** — Given keyboard navigation and a confirmation dialog, when the user confirms or cancels, then focus and dismissal behave through the supplied host context.
- [ ] **US-003-AC5** — Given stale visible UI after authorization revocation, when a call or protected download is attempted, then the server denies access without disclosing data.
- [ ] **US-003-AC6** — Given altered assets or a binding to an undeclared operation, when admitted, then the UI refuses before invocation while retaining original blueprint bytes.
- [ ] **US-003-AC7** — Given the selected public ux-builder starter/design workflow and pinned cohort, when an author builds the screen, then its own lint/audit and Batten integration checks run independently.

- [ ] **US-003-AC8** — Given a review wizard containing grouped fields and an editable collection, when the reviewer moves backward after invalid input, then drafts and validation remain associated with their original fields/rows.
- [ ] **US-003-AC9** — Given a local detailed Python/TypeScript editor using supplied APIs, when the reviewer edits and submits a row, then the declared commit boundary and native operation outcome are preserved without an added third-party package.
- [ ] **US-003-AC10** — Given the same supported review interactions in browser and terminal, when the reviewer submits the same edit, then both surfaces preserve confirmation and the authorized operation outcome.
- [ ] **US-003-AC11** — Given a required browser-only detailed control, when terminal admission is requested, then admission refuses before operation effects and identifies the unsupported control safely.
- [ ] **US-003-AC12** — Given a local control importing an unapproved third-party package, when its artifact is assessed for admission, then it refuses without importing, fetching or installing that package.
- [ ] **US-003-AC13** — Given an explicitly approved and qualified platform extension, when a host admits its exact closure, then the control uses only its declared capabilities under the same server authorization.
- [ ] **US-003-AC14** — Given an editor with retained inputs, when its instance is torn down and another actor/resource opens it, then no previous instance data or active subscription is reused.


## Edge Cases

Unknown required semantics block eligibility while preserving source content.
A host-profile change requires a new assessment; stale authorization grants no
continuing permission. Native and browser support need their own observations.

## Test Scenarios

Names below are planned evidence, not existing or passing tests. Each eventual
test must cite its criterion with the canonical `@covers US-003-AC1` syntax
using the matching criterion ID. Consolidate cases by observable behavior under
the first reviewed measured test ceiling; these names do not set that ceiling.

| Criterion | Planned scenario | Concrete assertion |
| --- | --- | --- |
| US-003-AC1 | `review_approval_across_hosts` | browser journey and persisted outcome in both profiles |
| US-003-AC2 | `review_operation_states` | case table covers pending, denial, field error and success |
| US-003-AC3 | `review_uncertain_outcome` | same invocation identity; no duplicate effect |
| US-003-AC4 | `review_keyboard_confirmation` | focus restoration, cancellation and single authorized confirmation |
| US-003-AC5 | `review_revoked_access` | server refusal for both control and download |
| US-003-AC6 | `test_ui_integrity` | digest/target refusal and byte retention |
| US-003-AC7 | `test_ux_builder_cohort` | pinned build inputs and separately recorded evidence |

## Dependencies

FEAT-002; PRD FR-39; CONTRACT-005; CONTRACT-001/002. Exact dependency cohort and
public upstream APIs require integration evidence before their runtime claims.

## Out of Scope

Deployment, infrastructure provisioning, migration of existing consumers,
upstream saga implementation and claims of passing tests from metadata alone.
