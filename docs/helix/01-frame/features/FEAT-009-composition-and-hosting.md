---
ddx:
  id: FEAT-009
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

# FEAT-009: Composition and hosting

**Feature ID:** FEAT-009
**Priority:** P0
**Owner:** Erik LaBianca
**Covered PRD Subsystem(s):** Composition and hosting
**Covered PRD Requirements:** FR-34–38, FR-43–44
**Cross-Subsystem Rationale:** One capability: assess and bind an application to an explicitly selected host/provider closure.

## Overview

Authors must compose native application declarations without committing them to
one deployment. Hosts must supply selected, independently installed providers
through the public lifecycle contract. UMF owns declarations and saga semantics;
Batten owns application composition, capability assessment and host binding.

## Ideal Future State

An author declares a fabricated AI review queue once. An operator can explain
its dependencies, select a headless or UI-enabled installation, and choose local,
standalone or embedded hosting without rewriting its business meaning.
Unsupported combinations are visible before application code or services start.
The platform supplies the complete selected runtime cohort, allowing hundreds of
applications to share declarative services with explicit limits and attribution.
Applications integrate through declared graph API capabilities and future defined
interfaces; the shared deployment does not grant access between them.

## Problem Statement

A platform wheel split alone does not specify how a host resolves capabilities,
rejects ambiguous providers or preserves application meaning across environments.
Conflating platform choice and process placement makes optional integrations
mandatory and hides lifetime/authority differences between hosts.

## Functional Areas

| Area | Author/operator question | Responsibility |
| --- | --- | --- |
| Declarations | What does this application require? | Native metadata references and inert procedural hook identities. |
| Selection | Which modules satisfy those needs? | Explicit cohort, compatibility, graph and placement assessment. |
| Binding | Who owns execution and resources? | Host profiles, service ownership and upstream executor integration. |

## Requirements

- **CMP-01:** Installed modules must expose inert, versioned capability and
  dependency descriptors. Selecting a module must not install dependencies at runtime.
- **CMP-02:** Applications must require capability interfaces rather than concrete
  deployment products, while allowing an explicit provider selection where meaning differs.
- **CMP-03:** UMF must remain the authority for model, value and action semantics.
  Batten application extensions must reference them without copying their schemas.
- **CMP-04:** Procedural hooks must reference reviewed handler identities and
  scoped capabilities; declarations must not execute code or confer authority.
- **CMP-05:** Effect-free assessment must reject missing/ambiguous providers,
  incompatible pins, cycles, unsupported placements and relevant unknown semantics.
- **CMP-06:** Optional unavailable capabilities must remain explicitly inactive.
  No operation may require an inactive capability and still be marked eligible.
- **CMP-07:** Application intent, hosting environment and execution placement must
  vary independently within supported combinations. Host profiles must preserve
  explicit identity, provider, resource and ownership bindings.
- **CMP-08:** Start must require the assessed immutable plan and matching trusted
  bindings, rechecking drift before effects. Readiness remains a live lifecycle
  result, separate from static eligibility and native qualification.
- **CMP-09:** Failed startup must clean owned resources in reverse dependency
  order and retain incomplete cleanup outcomes. Borrowed resources remain host-owned.
- **CMP-10:** UMF saga definitions must bind only to explicitly qualified upstream
  executor interfaces. Batten must preserve their outcomes, identity and uncertainty;
  no fallback saga semantics or new orchestration engine may be introduced here.
- **CMP-11:** Headless installations must import without UI, HTTP or unrelated
  platform packages. Optional wheels and convenience groups must retain that closure.
- **CMP-12:** Local fabricated identity must be explicit and rejected by standalone
  and embedded profiles. Separated-worker support must name qualified transport,
  custody and recovery evidence independently of profile syntax.

- **CMP-15:** Application delivery must consume the complete qualified runtime
  without pip/npm installation, consistent with FR-23/42 qualification.
- **CMP-16:** Shared hosting must enforce per-application/owner scope, resource
  limits, concurrency, fairness, attribution and independent lifecycle control.
  The target is hundreds of applications; support claims require measured workloads.
- **CMP-17:** Graph API interactions must name declared capabilities and authorized
  targets, recheck current grants, and expose interface/dependency identities for
  upgrade assessment. Relationships must not become grants or private data access.
  Future integration mechanisms require separate exact contracts.

### Non-Functional Requirements

Assessment must be deterministic for identical immutable inputs and have no
provider/application import, service start, network or environment-read effects.
Unknown content must survive exchange without unreported loss. Native and
browser claims require their own evidence. Erik LaBianca and host owners supply
numeric runtime/size budgets. Hundreds of applications is the owner's scale
objective; measured capacity, workload assumptions and timing budgets remain open.

## User Stories

- [US-001: Assess composition](../user-stories/US-001-assess-composition.md).
- [US-002: Bind host profiles](../user-stories/US-002-bind-host-profiles.md).
- [US-004: Bind UMF sagas](../user-stories/US-004-bind-umf-sagas.md).

## Edge Cases and Error Handling

A cycle must not be repaired by guessing an order. Missing required UMF saga
support prevents that component's eligibility without blocking independent apps.
A host profile cannot replace an artifact digest while retaining an old plan.
Optional absence is observable and cannot be used for a silently broken control.

## Constraints and Assumptions

Native UMF and typed files are owner decisions. The companion extension names
and first structural profile in CONTRACT-003 are proposed defaults. Exact public
UMF/Weft/Arras/Tether package cohorts remain integration-proof dependencies.
This packet authorizes specification and tracking only, not migration or source code.

## Dependencies

FEAT-001/008; CONTRACT-001/002/003/004; ADR-001/003/005/006/008.
UMF owns saga syntax and executor obligations; host owners supply qualified bindings.

## Out of Scope

Infrastructure provisioning, choosing a workflow engine, implementing sagas,
automatic module discovery/installation, implicit legacy compatibility, or
asserting every deployment/placement combination is already supported.
