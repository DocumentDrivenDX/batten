---
ddx:
  id: US-005
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: batten.prd
      kind: derived_from
    - id: CONTRACT-009
      kind: informed_by
---

# US-005: Discover and bind another application's service

**Feature:** [FEAT-009](../features/FEAT-009-composition-and-hosting.md)
**Feature Requirements:** CMP-17, CMP-23–29
**PRD Requirements:** FR-11, FR-15, FR-35, FR-37, FR-42, FR-44
**Priority:** P0

## Story

**As a** application author and host operator,
**I want** to discover permitted typed services and bind declared requirements,
**So that** applications interoperate through governed contracts and current access.

## Context

A fabricated customer-owner publishes a customer lookup interface. A review-queue
application references the same independently governed Customer type and declares
its lookup requirement. Batten's platform ontology relates applications, interfaces,
exports, requirements and bindings; it does not duplicate their business schemas.

## Walkthrough

1. The host bootstraps its registry and admits verified provider/consumer artifacts.
2. The author queries visible exports and their pinned native interface definitions.
3. The operator selects an export and supplies its qualified deployment binding.
4. The module produces bounded immutable evidence; pure assessment checks it.
5. The consumer invokes its scoped service with current actor/delegation authority.
6. A provider/deployment change identifies authorized dependents for reassessment.

## Acceptance Criteria

- [ ] **US-005-AC1** — Given shared Customer references, when artifacts are resolved, then exact native identity/digest is preserved and equal names/shapes with different identity do not substitute.
- [ ] **US-005-AC2** — Given visible and hidden services, when discovery or impact queries paginate, then only currently visible records/paths are disclosed; hidden and absent lookups have the same safe outcome.
- [ ] **US-005-AC3** — Given verified snapshot/artifacts/evidence, when assessment runs, then exact resolution is deterministic and no query, fetch, provider import or service start occurs.
- [ ] **US-005-AC4** — Given missing, ambiguous, incompatible, cyclic or relevant unknown dependencies, when resolved, then required dependencies refuse and optional absence remains inactive; explicit selection never bypasses compatibility or authority.
- [ ] **US-005-AC5** — Given forged exports/bindings, contradictory relationships, changed bytes or reused revision IDs, when admitted, then no application, service or authority is gained; original unknown content remains recoverable.
- [ ] **US-005-AC6** — Given a valid binding, when user or explicit delegated/background authority invokes it, then operation/target scope and current grants hold; metadata visibility, graph links and message headers confer no authority.
- [ ] **US-005-AC7** — Given cached bindings or catalog continuation, when authority, catalog, interface, provider or deployment changes, then stale use refuses/reassesses without automatic fallback or replay of possible effects.
- [ ] **US-005-AC8** — Given graph/table/API/messaging exports, when assessed and used, then each needs its exact qualified transport descriptor and semantic evidence; raw connections, arbitrary foreign writes and subscription provisioning through discovery refuse.
- [ ] **US-005-AC9** — Given registry bootstrap or explicit bindings, when installed/start occurs, then graph discovery uses the selected Arras module while core-only/headless closure remains ontology-free; root discovery never depends on resolving itself.
- [ ] **US-005-AC10** — Given deprecation, deployment relocation or retirement, when the host evaluates change, then interface identity survives relocation, exact dependents are identified within metadata permissions, and active bindings require explicit replacement/drain without retaining revoked authority.

## Edge Cases

A provider can be visible but unusable by the caller. A catalog row is never an
admission receipt. Self-contained metadata cannot establish live provider health.
Mutually referring semantic types are not necessarily startup cycles. Unknown
possible effects remain uncertain after binding replacement or cancellation.

## Test Scenarios

These are planned observations, not passing tests or new function allocations.
Extend existing behavior tables with canonical `@covers US-005-ACn` annotations;
keep each authorization/isolation invariant in one primary scenario.

| Criteria | Planned scenario / primary layer | Whole observable outcome |
| --- | --- | --- |
| AC1, AC4, AC5 | Existing composition resolution/unknown-preservation table | Exact identities/joins succeed; ambiguity, mismatch, forged revisions and unknown meaning refuse with preserved originals. |
| AC3 | Existing effect-free assessment scenario | Identical evidence produces identical plan; query/fetch/import/start observations remain empty. |
| AC2, AC6 | FLT-06 public provider authorization scenario | Visibility, invocation permission, delegation and revoked access remain distinct with no hidden paths/counts. |
| AC7, AC10 | Existing binding drift/upgrade/recovery scenarios | Changed continuation/binding refuses; relocation and retirement identify exact permitted dependents without replay. |
| AC8 | Transport profile conformance matrix | Descriptor/authority/consistency requirements hold per transport; reuse MSG/STO scenarios for guarantees they already own. |
| AC9 | Existing installed headless and lifecycle scenarios | Actual graph-host bootstrapping works; core-only imports no Arras/UMF engine and explicit bindings still verify evidence. |

## Dependencies

CONTRACT-001/002/003/004/009; ADR-001/002/013; native UMF model and exact public
Arras/transport cohort. Registry snapshot/visibility and async bridge require
native proof before discovery support claims. CONTRACT-007 owns messaging delivery;
platform asset ownership and outputs remain the
[platform asset contract](../../02-design/contracts/CONTRACT-008-platform-assets.md)'s
separate responsibility.

## Out of Scope

Product code, deployment, schema migration, choosing a registry database or new
broker, automatic dependency installation and a new ontology engine in core.
