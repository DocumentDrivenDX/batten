---
ddx:
  id: US-002
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: batten.prd
      kind: derived_from
---

# US-002: Bind one application to different hosts

**Feature:** [FEAT-009](../features/FEAT-009-composition-and-hosting.md)
**Feature Requirements:** CMP-07–09, CMP-12–14, CMP-18–22
**PRD Requirements:** FR-36/46
**Priority:** P0

## Story

**As a** Host integrator and operator,
**I want** to bind the same application to local and embedded profiles,
**So that** I can change its environment without changing application meaning.

## Context

The review application has the same digest in both environments. The local profile owns its fabricated identity and resources; the embedded profile borrows real host-provided services.

## Walkthrough

1. Supply the review application's exact artifacts and selected module metadata.
2. Select the explicit host profile and assess its capability bindings.
3. Inspect safe findings or proceed through the declared public boundary.
4. Observe the outcome and its evidence without changing the application meaning.

## Acceptance Criteria

- [ ] **US-002-AC1** — Given one application and local and embedded profiles, when assessed, then the application digest stays equal while resource ownership and bindings differ explicitly.
- [ ] **US-002-AC2** — Given an assessed plan whose cohort or profile changed, when start is requested, then drift is refused before any provider effect.
- [ ] **US-002-AC3** — Given dependency-ordered services and a later startup failure, when cleanup runs, then owned resources close in reverse order and borrowed services remain open.
- [ ] **US-002-AC4** — Given a cleanup timeout, when readiness and shutdown are observed, then retained resources remain visible without a false closed state.
- [ ] **US-002-AC5** — Given fabricated identity in a standalone or embedded profile, when assessed, then the deployment profile is refused.
- [ ] **US-002-AC6** — Given a separated worker without qualified transport capabilities, when assessed, then placement is refused rather than using an implicit local fallback.

- [ ] **US-002-AC7** — Given local stub authentication and fabricated permitted/denied actors, when they invoke the same operation, then normal Batten and native permission checks enforce the respective outcomes without an implicit actor fallback.
- [ ] **US-002-AC8** — Given Truss and direct UMF table bindings in one local app, when both execute against the selected pgserver, then native observations identify the same server instance while each respects its own resource ownership.
- [ ] **US-002-AC9** — Given both consumers borrow a shared pgserver connection source, when one closes, then the other remains usable and only the instance owner may stop the server.
- [ ] **US-002-AC10** — Given an explicit Tether model API binding, when the recommendation runs, then the selected public adapter reaches that API under its configured profile and tool/approval restrictions.
- [ ] **US-002-AC11** — Given the selected model API is unavailable or incompatible, when the recommendation runs, then a safe failure remains visible without scripted-output or alternate-endpoint substitution.
- [ ] **US-002-AC12** — Given existing local records, when the host reloads declarations or restarts, then data is preserved and schema migration or fixture reset requires an explicit separate operation.

- [ ] **US-002-AC13** — Given managed packages, external outputs and a mixed dependency graph, when assessed, then exact source/contract pins and single ownership are checked without native imports or effects; cycles and unsupported meaning refuse.
- [ ] **US-002-AC14** — Given a reviewed deployment plan, when applied under current operator authority, then exact approved effects and durable request identity are retained; stale plans and conflicting owners refuse, and lost acknowledgements reconcile without blind replay.
- [ ] **US-002-AC15** — Given a deployed definition with absent outputs, stale external contracts, revoked access or failed readiness predicates, when preparation runs, then required resources block readiness and optional unavailable resources remain inactive without implicit provisioning.
- [ ] **US-002-AC16** — Given active persistent resources and external dependents, when start, reload, shutdown or removal runs, then no implicit apply, migration, grant or destruction occurs; approved destructive plans must resolve dependents first.

## Edge Cases

Unknown required semantics block eligibility while preserving source content.
A host-profile change requires a new assessment; stale authorization grants no
continuing permission. Native and browser support need their own observations.

## Test Scenarios

Names below are planned evidence, not existing or passing tests. Each eventual
test must cite its criterion with the canonical `@covers US-002-AC1` syntax
using the matching criterion ID. Consolidate cases by observable behavior under
the first reviewed measured test ceiling; these names do not set that ceiling.

| Criterion | Planned scenario | Concrete assertion |
| --- | --- | --- |
| US-002-AC1 | `test_profile_portability` | equal app digest, distinct approved plans |
| US-002-AC2 | `test_plan_drift` | no prepare calls after drift |
| US-002-AC3 | `test_startup_cleanup` | complete observed cleanup order and borrowed lifetime |
| US-002-AC4 | `test_shutdown_uncertainty` | unsettled resources preserved |
| US-002-AC5 | `test_identity_boundary` | deployed profiles deny fabricated identity |
| US-002-AC6 | `test_remote_placement` | unsupported placement refused |
| US-002-AC7 | `test_local_stub_authorization` | Permitted/denied fabricated actors traverse real gates; absent actor refuses. |
| US-002-AC8 | `test_shared_pgserver_native_bindings` | Truss and UMF-native operations use the same observed server; ownership/grants remain separate. |
| US-002-AC9 | `test_shared_pgserver_lifetime` | Closing a borrower preserves its peer; owner closes server last. |
| US-002-AC10 | `test_local_tether_model_binding` | Explicit scripted API fixture and separately supplied real API; invocation and tool/approval outcomes observed. |
| US-002-AC11 | `test_model_api_failure_is_explicit` | No alternate endpoint or fabricated successful result on provider failure. |
| US-002-AC12 | `test_local_reload_preserves_data` | Same native records after reload; no automatic schema changes or reset. |
| US-002-AC13 | Extend composition graph/unknown-source matrices | Managed/external/mixed source identities and owner conflicts produce deterministic outcomes without native effects. |
| US-002-AC14 | Deployment operation recovery matrix | Stale approval/state, concurrent apply and lost acknowledgements preserve the original operation and exact effects. |
| US-002-AC15 | Resource admission matrix | Definition-only deployment cannot pass initialization, schema, freshness or current-grant predicates. |
| US-002-AC16 | Extend lifecycle preservation matrix | No deployment authority during ordinary lifecycle; destruction respects retention and external dependents. |

## Dependencies

FEAT-009; PRD FR-36/46; CONTRACT-004/010; CONTRACT-001/002. Exact dependency cohort and
public upstream APIs require integration evidence before their runtime claims.

## Out of Scope

Executing live deployment, shared infrastructure provisioning, migration of existing consumers,
upstream saga implementation and claims of passing tests from metadata alone.
