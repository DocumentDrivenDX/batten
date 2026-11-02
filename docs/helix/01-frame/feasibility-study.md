---
ddx:
  id: batten.app-feasibility
  type: feasibility-study
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: informed_by
---

# Feasibility Study: Enterprise micro-apps

**Decision Deadline**: None supplied; Erik LaBianca owns prioritization.

## Executive Summary

### Project Overview

Batten targets governed internal applications that combine records, workflows,
documents, decisions and AI assistance. Its advantage is a shared platform and
permission/lifecycle contract, rather than a general replacement for every app stack.

### Recommendation

**Overall Assessment**: CONDITIONALLY FEASIBLE. **Decision**: CONDITIONAL GO.
Integrate existing platform capabilities and qualify complete reference journeys.
**Confidence**: Design fit is supported by the requirements; complete-app delivery
and operating capacity remain unqualified.

## Feasibility Assessment

### Technical

**Assessment**: HIGH RISK until the host/client and data integration cuts run.
Only the optional local storage backend has Batten implementation evidence.
No end-user app is established by that storage evidence alone.

| App class | Design fit | Required integration or boundary |
| --- | --- | --- |
| Intake, approvals, attestations, task/case queues | Strong | UMF table access over PostgreSQL 18, actions, authorization, TypeScript UI |
| Document review, attachment/evidence libraries | Strong | Above plus scoped object storage and row/blob recovery |
| Entity directories, relationships, impact/discovery tools | Strong | UMF typed graph access with Truss; Arras where ontology services are needed |
| AI extraction, triage, grounded answers, analyst assistants | Conditional | Tether and explicit model/search APIs; provenance, budgets and human approval |
| Reconciliation, scheduled reports, external job consoles | Conditional | Existing action/job/message capabilities, bounded work and durable recovery |
| Cross-app requests and workflow handoffs | Conditional | Governed discovery/binding, exact interfaces and independent consumer authority |
| Operational dashboards | Conditional | Bounded query/read models; not a new warehouse or unrestricted BI engine |
| Offline-first/mobile sync and live collaborative editors | Extension required | No selected sync/merge/presence capability or native mobile client |
| Hard real-time, safety-critical control or latency-guaranteed media | Outside the qualified design | No timing, certification or specialized runtime evidence |
| Heavy ETL, full-text/vector engine, unrestricted graph/SQL engine | Delegate | Existing platform jobs/engines; Batten supplies scoped orchestration and UI |
| Hostile third-party plugin marketplace | Excluded trust model | Trusted-code permission containment is not hostile-code isolation |
| Cross-service atomic commit or exactly-once external effects | Cannot promise | Requires exact native transaction evidence; sagas retain uncertainty |

An extension-required app can become a target after explicit contracts and native
qualification. It must not be silently implemented through unrestricted hooks.

### Business

**Assessment**: CONDITIONALLY FEASIBLE. Repeated workflow and integration patterns
fit the owner's enterprise micro-app goal. No market research, effort reduction or
return estimate is asserted. Erik supplies actual user validation and priorities.

### Operational

**Assessment**: HIGH RISK until exact cohorts pass. Hosts own identity, policy,
service binding and shared infrastructure. A local pgserver configuration must
use PostgreSQL 18, with table and Truss bindings explicitly separated even when
they share one instance. No startup-time migrations or automatic privilege grants.
Stub local identity is explicitly local and grants no production qualification.

### Resource

**Assessment**: HIGH RISK because capacity and delivery budgets are unknown.
Erik owns team allocation, workload, latency/cost budgets and delivery order.
Use existing UMF/PostgreSQL, UMF/Truss, Weft, Arras and Tether public capabilities;
rebuild neither ORM nor engines. Initial UI delivery is TypeScript under ADR-015.

## Risks

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Upstream capability mistaken for Batten integration | Unmeasured | Incorrect support claim | Exact installed/native cohort and app journey evidence |
| ORM paths have different transaction/policy limits | Unmeasured | Lost authorization or data | Preserve native restrictions and explicit refusal |
| A scripted AI fixture counted as model support | Unmeasured | Misleading qualification | Separate deterministic behavior from exact live API evidence |
| Twelve examples become twelve bespoke frameworks | Unmeasured | Duplicated runtime | Shared obligations and adapters; app-local business semantics |

## Alternatives

### Build thin integrations over the existing platform

Carry forward. Preserves native semantics and reduces duplicated machinery;
integration and cohort qualification are still required.

### Build new Batten ORMs and a UI compiler first

Reject. Duplicates existing owners and delays useful business journeys.

### Do Nothing / Delay

Reject for specification and gap tracking. Keep unsafe runtime support claims
blocked rather than waiting to define observable target behavior.

## Decision Framework

| Criterion | Status | Rationale |
| --- | --- | --- |
| Technical buildability | Risk | Suitable platform sources exist; Batten assembly is incomplete |
| Business value | Risk | Owner-selected patterns; user validation remains owner work |
| Operational supportability | Risk | Scope/policy/recovery must be qualified end to end |
| Compliance readiness | Risk | No domain certification or real regulated data is included |
| Resource availability | Risk | Owner has supplied no measured capacity or delivery budget |

## Next Steps

1. Maintain the reference-app corpus and its independent HELIX scopes.
2. Queue integrations by dependency and qualify a thin complete vertical slice.
3. Use the app workflow to pin native models, TypeScript UI, test oracles and cohorts.
