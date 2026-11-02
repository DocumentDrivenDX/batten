---
ddx:
  id: US-007
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-007
      kind: derived_from
---

# US-007: Target a reference app with HELIX

**Feature**: FEAT-007 — Author tooling and qualification
**Feature Requirements**: AUTHOR-01, CORPUS-01, QUALIFY-01
**PRD Requirements**: FR-29, FR-30, FR-31, FR-48
**Priority**: P0

## Story

**As a** Batten application author
**I want** to target an enterprise app's independent specification and conformance
**So that** changing its business rule cannot silently change SDK policy or another app.

## Context

The corpus supplies concrete business journeys through selected platform modules.
Its isolated HELIX scopes and evidence boundaries must hold before app runtime work.

## Walkthrough

1. The author opens a selected app and reads its scoped marker and instructions.
2. HELIX resolves installed templates and the shared Batten app workflow.
3. The author refines a business rule and its independent acceptance outcome.
4. Inventory validation checks the scope; runtime qualification requires actual evidence.

## Acceptance Criteria

- [ ] **US-007-AC1** — Given a selected app, when HELIX authors its requirements,
  then only that app's governed scope is selected and SDK dependencies remain explicit.
- [ ] **US-007-AC2** — Given a changed business rule, when conformance is allocated,
  then its distinct invariant remains traceable alongside shared platform obligations.
- [ ] **US-007-AC3** — Given a corrupt scope, duplicate identity or missing obligation,
  when the inventory is checked, then it fails without importing an app or provider.
- [ ] **US-007-AC4** — Given only specifications or component evidence, when complete
  app qualification is requested, then it refuses instead of reporting execution success.

## Edge Cases

A foreign app path never selects authority. A native integration that cannot
satisfy a required rule blocks that app's qualification without redefining the rule.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
| --- | --- | --- | --- | --- |
| Scope | US-007-AC1 | App-local marker | Resolve workflow and artifact paths | Independent app specs |
| Intent | US-007-AC2 | App-specific invariant | Inspect story/test allocation | Preserved domain expectation |
| Negative controls | US-007-AC3 | Corrupt inventory variants | Execute common checker | Failure without effects |
| Evidence boundary | US-007-AC4 | No complete app runner | Request strict qualification | Nonzero refusal |

## Dependencies

FEAT-007; CONTRACT-011; ADR-014/015; installed HELIX catalog.

## Out of Scope

Implementing complete app runtimes, a declarative UI compiler or new platform engines.
