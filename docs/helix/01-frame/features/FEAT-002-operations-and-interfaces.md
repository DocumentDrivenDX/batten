---
ddx:
  id: FEAT-002
  type: feature-specification
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: batten.concerns
      kind: informed_by
---

# FEAT-002: Operations and ux-builder interfaces

**Feature ID:** FEAT-002
**Priority:** P0
**Owner:** Erik LaBianca
**Covered PRD Subsystem(s):** Operations and interfaces
**Covered PRD Requirements:** FR-8, FR-9, FR-39–41, FR-47
**Cross-Subsystem Rationale:** One capability: expose the same governed operation through application interfaces.

## Overview

Applications must expose declared operations through host-contained UI and other
surfaces. The ux-builder integration must reuse its design workflow, components,
themes and audit tools while binding to native UMF meaning and Batten's public client.

## Ideal Future State

An author starts an application with ux-builder, designs the review journey and
binds a screen to the same typed operation used by tools and routes. Host changes
alter authentication and transport bindings without duplicating business logic.

## Problem Statement

Generic data-driven forms do not describe a complete review journey. Recreating
ux-builder's blueprint, layout and tokens in Batten would produce competing
sources of truth; binding generated UI directly to host internals would prevent portability.

## Functional Areas

| Area | Responsibility |
| --- | --- |
| Operation projection | Preserve FR-8/9 namespace, resource, gate, confirmation and adapter requirements. |
| UX integration | Resolve UI bindings, host context and cross-profile browser outcomes. |

## Requirements

- **UI-01:** Digest-covered screens/routes/views/downloads must preserve the full
  containment and declared-resource behavior in FR-8. Every surface must use the
  typed operation, permission and confirmation obligations of FR-9.
- **UI-02:** UI bindings must reference exact UMF model/action and Batten operation
  identities. Labels and display names must not resolve execution targets.
- **UI-03:** ux-builder must own blueprint structure, journeys, layout, tokens,
  themes and component semantics. Batten must preserve its original artifacts
  and add references/bindings rather than a second layout schema.
- **UI-04:** The same public client must support local, standalone and embedded
  hosts through explicit authenticated adapters. Server authorization remains
  decisive for every call, download and protected resource.
- **UI-05:** Controls must show loading, denial, input validation, success and
  uncertain outcomes with accessible recovery. An uncertain write must not be
  automatically reissued as a fresh business action.
- **UI-06:** Navigation, focus, confirmation and downloads must use the supplied
  host context without shell internals, raw credentials or ambient host discovery.
- **UI-07:** Headless installations must omit UI and ux-builder dependencies.
  A declared UI capability must refuse unsupported renderer/client combinations.
- **UI-08:** Starter/design-first integration must use a pinned supported public
  ux-builder cohort. Its build/lint/audit results and Batten's real browser/server
  authorization evidence must remain separately observable.

- **UI-09:** Authors start with declarative semantic controls, including wizard,
  grouped form and editable collection, and compose nested controls without
  rebuilding routine validation, state and recovery behavior.
- **UI-10:** Detailed application-local Python/TypeScript implementations may
  replace or fill declared control slots using supplied public APIs. Local code
  must preserve the control's operation, state, validation and authority contract.
- **UI-11:** Local customization must add no third-party packages, including
  bundled, vendored, remote or dynamically loaded substitutes. A new package
  requires an exceptional platform extension approved by the owner and admitted
  by the host against an exact qualified dependency closure.
- **UI-12:** Renderer selection is independent of hosting and placement. Browser
  and terminal implementations may differ in navigation and layout but must
  preserve declared semantic behavior. Each custom control declares its supported
  surfaces; a required unsupported control refuses before invocation.


### Non-Functional Requirements

Browser modules must execute without Bun/Node runtime globals. Cross-profile
browser verification must cover the same authored review journey and server
outcomes. Existing CONTRACT-002 shape/test policies apply; no UI timing or
accessibility support claim is established by configuration alone.

## User Stories

[US-003: Review through ux-builder](../user-stories/US-003-ux-builder-review.md)
owns the initial browser slice. Existing FR-8/9 adapter scope remains governed
by the PRD and needs subsequent story allocation before its implementation.
US-003 also allocates composition/custom-control and web/terminal comparison
criteria. It establishes no released upstream component or terminal support claim.

## Edge Cases and Error Handling

Expired authorization must deny a stale visible control. Unknown blueprint
content survives unchanged, but unsupported relevant binding meaning prevents
eligibility. Failed downloads and uncertain writes must remain visible rather
than appearing successful or causing silent retries.

## Constraints and Assumptions

The owner selected ux-builder integration. Exact public APIs and release cohort
remain a bounded upstream compatibility proof, not a settled runtime import claim.
Batten must not run the latest starter automatically or alter another project's tooling.

## Semantic verification obligation

FR-47 applies to every default fully declarative UI-and-hook composition.
Every interaction and hook must expose testable meaning after use-case refinement,
with complete CLI functionality and automatically generated property-based
end-to-end suites. CLI-only server checks cannot replace actual renderer behavior.
Candidate platform bindings must pass the same semantic conformance contract;
unsupported required meaning, missing coverage or changed outcomes blocks
qualification. Local procedural implementations require explicit test contracts
and must not inherit automatic coverage claims merely by occupying a semantic slot.

## Dependencies

FEAT-001/009; CONTRACT-001/003/005; ADR-009. The browser bridge remains independent
of a particular host shell; the optional ux-builder adapter owns its UI dependencies.

## Out of Scope

A Batten design system, blueprint fork, automatic UX inference from record fields,
client-owned authorization, publishing/deploying a generated application, and
claiming ux-builder audit alone proves Batten's server integration.
