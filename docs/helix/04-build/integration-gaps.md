---
ddx:
  id: batten.integration-queue
  type: implementation-plan
  activity: build
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: informed_by
    - id: CONTRACT-011
      kind: informed_by
    - id: ADR-015
      kind: informed_by
---

# Integration gaps for enterprise applications

## Scope

Close Batten assembly gaps by integrating the existing platform, then qualify
the reference apps through their public boundaries. Reuse the existing
composition, host, saga and ux-builder work items rather than create competing
engines. Governing scope: FR-29–31/47/48, CONTRACT-001/003/004/005/006/007/009/011,
ADR-001/002/005/009/014/015 and each selected reference app's test plan.

## Shared Constraints

UMF + PostgreSQL provides table ORM/typed access. UMF + Truss provides graph
ORM/typed access. Batten supplies capability binding, current authority,
attribution, lifecycle and cross-surface delivery. It must not reimplement these
ORMs, Weft's compiler, UMF actions/sagas, Arras ontology or Tether's agent loop.
PostgreSQL 18 only; an explicit local pgserver instance may serve table and
Truss bindings with separate scoped authority. Shared server does not establish
shared transactions or identity. Native schema changes remain separately authorized.

Initial UI delivery means a TypeScript app. Do not block useful app delivery on
building a declarative UI compiler. Keep ux-builder assets/tooling integration
available through qualified public APIs and isolate it from headless modules.
All browser calls pass through the public host client, never native providers.

Source inspection of UMF's typed-persistence integration evidence and Truss's
public Python documentation supports this integration direction; neither proves
Batten's installed/native cohort. UMF's source is b12a489844f29947ee52115b90f4ccc5c8bc5032;
Truss's inspected source is 14e16ce852381fd376da1d2187fc941683903ab2.
Their published/versioned compatibility sets must intersect explicitly; combining
the latest sources by name is not a qualified cohort.

## Implementation Slices

| Slice | Integration owner / approach | Work item | Depends On | Validation Gate |
| --- | --- | --- | --- | --- |
| INT-01 | Batten inert admission and metadata closure | batten-916449b0; cohort batten-9a5d7122 | Existing composition contracts | Effect-free assessment, native schema evidence and no private imports |
| INT-02 | Public host, scoped services and lifecycle | batten-2b9e6014 | INT-01 | Authenticated/local-stub distinction, current authority, safe audit/telemetry and ownership |
| INT-03 | UMF/PostgreSQL table ORM binding | batten-a77dd24d | INT-02 | Native PostgreSQL 18 actions/reads/bulk, row policy, stale writes and exact installed artifacts |
| INT-04 | UMF/Truss graph ORM binding | batten-e7af34e7 | INT-02 | Hidden graph endpoints/counts, native policy and original model identities |
| INT-05 | Public TypeScript client and local host | batten-39cb6fe0 | INT-02 | Same operation identity, server authority, navigation/download boundary and local pgserver configuration |
| INT-06 | Authored TypeScript app and ux-builder tooling | Existing batten-6e684a3f | INT-03/05 | Approval-desk browser journey, keyboard/focus and denied/uncertain results; no generated UI claim |
| INT-07 | Existing local storage binding; separate Volumes adapter | batten-8dd09b19 | INT-02/03 | Evidence-library row/blob reconciliation; exact local versus remote feature qualification |
| INT-08 | Native UMF action/saga binding | Existing batten-0b5cad5d | INT-01/02 | Original executor/profile/receipt semantics, uncertainty and unsupported refusal |
| INT-09 | Existing platform workers/jobs and schedules | batten-edc84420 | INT-02/08 | Scheduled-digest occurrence identity, concurrency, cancellation and attribution |
| INT-10 | PostgreSQL durable messages and consumer scopes | batten-e3665458 | INT-02/03 | Intake/triage delivery/retry/recovery without duplicate business effect |
| INT-11 | Tether, model API and scoped retrieval | batten-341346a4 | INT-02/03/05 | Document-review and knowledge provenance, budgets, human decisions and unavailable API |
| INT-12 | Arras/UMF service discovery and binding | batten-e50731a9 | INT-04/10 | Service-handoff exact interfaces, receiver authority and revocation/drift |
| INT-13 | Native action/CLI and app/browser evidence runner | batten-5fa3e526 | INT-01/02/03/05 | Independent oracle, broken-adapter controls, real client-host-provider observations and exact evidence |

INT-13 begins with the first vertical slice and grows through data-driven cases;
it must not wait until every adapter is implemented. Additional native source
gaps stay with the owning project and block only affected profiles. Diagnose the
specific missing public capability before proposing any replacement machinery.

## Execution Contract

The owner requested this queue and the reference-app workflow. These future
integration tasks have execution authorization off until a bounded build is
selected; source inspection and tracking are not platform delivery. Earlier local
storage authorization and implementation remain intact. No production apply,
secret access, schema migration, remote repository creation or commit is implied.
Token, time, staffing and spending budgets are unknown; Erik supplies them.
No reliable task billing meter is available. Include verification in each build.

## Continuation Evidence

Use ddx as the live tracker and `01-frame/work-items.jsonl` as its review export.
Current work is the independently scoped corpus and workflow task batten-4192222e.
Select approval-desk as the proposed first complete slice (INT-01/02/03/05/06/13),
then entity-directory for the graph path and evidence-library for row/blob recovery.
These are planning defaults, not fabricated production priorities or deadlines.

## Validation Plan

The common gate checks corpus integrity and existing source behavior. Missing
complete execution evidence fails strict qualification. For each integration,
reuse upstream behavioral evidence and test only the distinct Batten binding,
authority/lifecycle/attribution outcomes. Extend the measured suite through
parameterized cases without increasing the test-function ceiling. App domains
need independent expected results; storage unit tests cannot stand in for them.

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
| --- | --- | --- | --- |
| Upstream native feature is incomplete | Blocks a profile | Pin exact supported subset and queue upstream owner gap | Refuse the affected required app capability |
| Procedural UI becomes privileged integration glue | Policy bypass | Use public client/host, typed actions and server authority | Disable affected operation binding |
| Stateful upgrade changes meaning | Data/recovery risk | Requalify original app semantics and migration route | Use only verified native recovery |
| Duplicate test engines and hidden skips | False coverage | Reuse platform tooling and require independent negative controls | Withdraw affected qualification |

## Exit Criteria

An integration gap closes only with exact installed/native evidence and its
affected app's required client-host-provider journey. Complete-app qualification
requires all active obligations, safe required telemetry and candidate-cohort
replay. Inventory integrity, source inspection and component evidence remain
separate results, never substitutes for a required positive app execution.
