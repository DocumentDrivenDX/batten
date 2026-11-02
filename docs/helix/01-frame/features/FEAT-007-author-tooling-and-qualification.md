---
ddx:
  id: FEAT-007
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
---

# FEAT-007: Author tooling and qualification

**Feature ID**: FEAT-007
**Priority**: P0
**Owner**: Erik LaBianca
**Covered PRD Subsystem(s)**: Author tooling and qualification
**Covered PRD Requirements**: FR-29–31, FR-47, FR-48
**Cross-Subsystem Rationale**: None; one authoring/qualification capability.

## Overview

Authors must target a governed Batten application, exercise its declared behavior
and obtain evidence that distinguishes intended meaning from actual execution.

## Ideal Future State

HELIX can frame, design and evolve any app in its own specification scope. The
same application semantics drive CLI and appropriate client conformance across
qualified hosts. Representative enterprise apps expose integration defects before
a platform upgrade affects consumers.

## Problem Statement

Component tests cannot prove whole business journeys. Duplicated app test stacks
and unscoped specs can conceal authority, recovery and compatibility defects.
Authors need explicit expectations and independently attributable evidence.

## Functional Areas

| Area | User question or job | Feature responsibility |
| --- | --- | --- |
| Authoring | What app am I changing? | Isolated specs, native authoring and reusable workflow |
| Qualification | Does the app preserve meaning? | CLI/native/client evidence and independent oracle |
| Corpus | What real patterns are covered? | Reference journeys, business invariants and integration matrix |

## Requirements

### Functional Requirements by Area

- **AUTHOR-01**: Tooling must preserve FR-31's complete author lifecycle and
  installed-artifact-only guide; reference apps have independent HELIX roots.
- **QUALIFY-01**: FR-29/30 evidence must preserve each actual layer, current inputs,
  required coverage, native qualification and safe refusal. Unsupported profiles
  and missing required execution must not become green skips.
- **QUALIFY-02**: FR-47's fully declarative behavior must have automatic CLI and
  property-based end-to-end qualification. Arbitrary procedural code requires
  explicit semantics and tests; authored TypeScript UI follows ADR-015.
- **CORPUS-01**: FR-48's enterprise library must combine shared platform obligations
  with distinct domain expectations and fabricated data. Each app remains a
  qualification target independently of the other apps' outcomes.

### Non-Functional Requirements

No new runtime dependency is introduced by inventory or workflow metadata. Source
quality ceilings remain enforced; the measured test-function ceiling cannot grow.
No latency or capacity target is invented; Erik supplies workload and budgets.
Every qualification result must bind exact application and platform inputs.

## User Stories

- [US-007: Target a reference app with HELIX](../user-stories/US-007-reference-app-workflow.md).
- Existing US-001–004 cover effect-free composition, profiles, UI and native sagas.

## Edge Cases and Error Handling

Wrong app scope, escaped paths and missing invariants fail authoring integrity.
Unknown native semantics, missing providers and stale runtime evidence refuse
qualification. A passing inventory is never a complete-app support claim.

## Constraints and Assumptions

The owner selects existing platform integrations and initial TypeScript apps.
Installed HELIX owns methodology; UMF owns models/actions and typed access.
Native/local/browser/deployed results remain distinct.

## Dependencies

CONTRACT-003/004/005/011, ADR-005/014/015 and existing platform public APIs.
The integration queue sequences runtime assembly without replacing upstream engines.

## Out of Scope

No second methodology catalog, ORM, query compiler, agent loop or UI framework.
This feature does not authorize production deployment, schema migration or grant changes.
