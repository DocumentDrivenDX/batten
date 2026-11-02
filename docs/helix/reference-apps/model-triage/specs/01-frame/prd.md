---
ddx:
  id: model-triage.prd
  type: prd
  activity: frame
  authoring:
    home: repo
---

# AI-assisted inbox triage

## Summary

MA-008 is a fabricated enterprise reference app for a triage analyst and automation owner. It exercises
receive an inbox item, classify it within a budget, review the suggestion and apply an authorized disposition. Its purpose is to qualify a useful business journey
through Batten's platform integrations, rather than introduce a new engine.

## Problem and Goals

### Problem

Users need an attributable business result across data, permission and failure
boundaries. A successful component call alone cannot establish this workflow.

### Goals

- Complete the stated journey while preserving current access and original identity.
- Detect the app-specific business invariant: Delivery retries cannot repeat an accepted business disposition; a model suggestion cannot grant write authority.
- Reproduce denied, stale, duplicate, cancelled and uncertain outcomes independently
  of the host implementation.

### Non-Goals

No exactly-once external side-effect guarantee or autonomous high-impact decision.

## Users and Scope

The triage analyst and automation owner roles are assumed reference roles selected for this corpus, not
validated research personas. Erik owns real user validation and policy changes.
Business concepts: InboxItem, Classification, TriageDecision. All records and actors are fabricated.

## Requirements

### Must Have (P0)

- Complete the journey and enforce its app-specific business invariant.
- Apply shared authority, lifecycle and evidence obligations without disclosure.
- Qualify required native integrations and real UI outcomes before a support claim.

## Functional Requirements

### Subsystem: Governed business journey

Feature owner: FEAT-108.

- **FR-1** — Receive an inbox item, classify it within a budget, review the suggestion and apply an authorized disposition.
- **FR-2** — Delivery retries cannot repeat an accepted business disposition; a model suggestion cannot grant write authority.
- **FR-3** — Permission loss, stale inputs and interrupted work must preserve
  authorized visibility, actual effects and the original uncertain outcome.
- **FR-4** — Supported surfaces and candidate cohorts must preserve the same
  business semantics with attributable decisions and safe diagnostics.

## Acceptance Test Sketches

| Requirement | Scenario | Input | Expected Output |
| --- | --- | --- | --- |
| FR-1 | Main journey | fabricated inbox item with one durable message identity | one attributable disposition and a settled delivery outcome |
| FR-2 | Business boundary | redeliver after processing response loss | consumer observes original business result and does not apply the disposition twice |
| FR-3 | Foreign or revoked actor | Original fixture with changed authority | Safe refusal; no hidden data or new business effect |
| FR-4 | Alternate client/cohort | Same app and business inputs | Same authorized outcome or explicit unsupported refusal |

## Technical Context

Integration requirements: tables,messaging,agents,models,actions. These are corpus tags, not installable
module names or a claim that every adapter exists. Use UMF typed access with
PostgreSQL 18 for tables and Truss for graphs. Initial UI is a TypeScript browser
app under SDK ADR-015 and CONTRACT-005. No frontend framework is selected here.
Platform contracts are explicit dependencies in the test plan; original native
model/action packages require exact source and cohort qualification before build.

## Constraints, Assumptions, Dependencies

- Shared obligations in SDK CONTRACT-011 apply in full.
- Fixture states and role separation are conformance defaults, not production rules.
- Same local PostgreSQL instance does not imply one transaction across all services.
- Native authoring, host/client and required provider integrations precede app execution.

## Risks

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Fixture mistaken for a running app | Unmeasured | False support claim | Separate inventory from full execution qualification |
| UI or hook bypasses policy | Unmeasured | Unauthorized outcome | Public host boundary and server-side current authority checks |
| Backend changes business meaning | Unmeasured | Invalid result | Independent expectations and candidate-cohort replay |

## Open Questions

Erik supplies workload, latency/cost limits, real retention rules and production
policy. Those values block production qualification, not fabricated specification.

## Success Criteria

The governing story's positive and negative criteria pass through exact installed
native integrations and real client/host paths, with safe required telemetry.
The corpus inventory alone establishes none of those execution claims.
