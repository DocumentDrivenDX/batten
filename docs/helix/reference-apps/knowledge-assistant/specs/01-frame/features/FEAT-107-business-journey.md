---
ddx:
  id: FEAT-107
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: knowledge-assistant.prd
      kind: derived_from
---

# FEAT-107: Governed business journey

**Feature ID**: FEAT-107
**Priority**: P0
**Owner**: Erik LaBianca
**Covered PRD Subsystem(s)**: Governed business journey
**Covered PRD Requirements**: FR-1, FR-2, FR-3, FR-4
**Cross-Subsystem Rationale**: None; one app-specific journey.

## Overview

The app must complete its PRD's business journey through authorized platform
operations and preserve its independently stated business invariant.

## Ideal Future State

The actor can rely on the final result or safely reconcile original uncertain
work across supported surfaces, without rebuilding integration or policy.

## Problem Statement

Passing component calls do not prove this app's domain outcome. The PRD defines
its users, concepts and rule; the story owns its observable acceptance criteria.

## Requirements

- FR-1 must complete the specific app journey in the PRD.
- FR-2 must enforce the PRD's distinct business invariant.
- FR-3 must preserve current permission and actual/uncertain effects on failure.
- FR-4 must preserve meaning and attribution across qualified surfaces/cohorts.

### Non-Functional Requirements

No private provider access or client-derived authority. Bounded native work and
safe diagnostics follow SDK CONTRACT-011; Erik supplies production workload and
latency/cost budgets. No numeric operating target is assumed.

## User Stories

[US-107](../user-stories/US-107-journey.md) owns the acceptance criteria.

## Edge Cases and Error Handling

Foreign/revoked actors, changed inputs, interrupted commands and unavailable
providers retain the story's explicit safe outcomes. No silent scripted replacement.

## Constraints and Assumptions

Fabricated business defaults, native UMF data/actions, PostgreSQL 18/Truss when
required, and authored TypeScript UI. Exact platform subset needs qualification.

## Dependencies

Local PRD FR-1–4 and SDK CONTRACT-003/004/005/011 through explicit file references
in the app test plan. The app has no authority to modify those shared contracts.

## Out of Scope

New platform engines, privileged UI-side data access, production policy or deployment.
