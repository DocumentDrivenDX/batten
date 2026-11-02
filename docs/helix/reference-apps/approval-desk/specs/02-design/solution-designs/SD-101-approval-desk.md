---
ddx:
  id: SD-101
  authoring:
    home: repo
  links:
    - id: FEAT-101
      kind: informed_by
    - id: ADR-016
      kind: informed_by
---

# SD-101-approval-desk: Native local approval workflow

**Feature**: [[FEAT-101-business-journey]]

## Scope

Implement the governed approval journey across a TypeScript browser, generic
Batten operation host, optional original UMF table adapter and dedicated local
PostgreSQL 18 database. SDK architecture, ADR-015/016 and CONTRACT-012 govern
cross-component boundaries. TD-101 owns story implementation details.

## Requirements Mapping

| Requirement | Technical Capability | Component | Priority |
| --- | --- | --- | --- |
| FR-1 authorized business journey | Submit, inspect, edit and independently decide | Original UMF model and app operations | P0 |
| FR-2 independent invariant | Pending expected-revision condition and different decision principal | Native command and row policy | P0 |
| FR-3 authority and original outcomes | Server-owned sessions, current authority, original native receipts | Host and UMF adapter | P0 |
| FR-4 surface/cohort parity | Same host and operations through installed CLI and browser | Local assembly and public transport | P0 |
| FR-5 local discovery | Visual registry entries and brand navigation | Optional ASGI registry | P0 |

Native database integrity governs concurrency. Local deadlines, body bounds and
session limits are explicit typed configuration. No production capacity or
latency budget is inferred; Erik supplies workload and acceptance budgets.

## Solution Approaches

**Selected: original platform integration.** UMF declares records, policy,
queries and conditional mutations; Weft plans native SQL. Batten owns public
operation dispatch and injected identity/capture services. Benefits are one
semantic authority and original-attempt recovery. Trade-off: the exact candidate
platform subset and installed cohort require explicit native evidence.

**Alternative: app-specific persistence.** Handwritten SQL and a separate receipt
store could demonstrate a form quickly but duplicate platform authority, policy
and recovery. Rejected under the native UMF owner ruling.

**Alternative: new declarative UI engine.** This would add an unqualified runtime
and vocabulary before the chosen TypeScript slice can prove the business journey.
ADR-015 selects authored TypeScript while preserving future ux-builder binding.

## Domain Model

A request holds its owner, summary, pending/approved/rejected state, opaque
revision and decision principal. A requester can own multiple requests. A reviewer
can inspect permitted requests and decide another person's pending request.
An invocation key identifies the original attempt; UMF owns its durable receipt.

### Business Rules

- **BR-1** — Independent decision: the decision principal differs from the owner.
- **BR-2** — Inspected state: decisions and edits require the current pending revision.
- **BR-3** — Current authority: each operation and observation uses the server-bound current actor.
- **BR-4** — Original outcome: uncertain work retains its original inputs and key.

## System Decomposition

| Component | Responsibility | Requirements | Interface / Design |
| --- | --- | --- | --- |
| TypeScript UI | Forms, permitted list, inspected detail and recovery control | FR-1/3 | CONTRACT-012; TD-101 |
| Approval operations | Validate business inputs and map native results | FR-1/2/4 | Public table port; TD-101 |
| Generic host | Admission, lifecycle, current identity, limits and capture outcomes | FR-3/4 | CONTRACT-001/012 |
| UMF PostgreSQL adapter | Delegate original wire, identity and native installation reference | FR-1/2/3 | Original UMF native table binding |
| Local composition | Explicit maintenance, stub sessions, loopback transport and safe capture | FR-3/4 | ADR-016, CONTRACT-012 |

The browser sends a declared operation to the ASGI adapter; the host resolves
current identity before business dispatch. The app calls the portable table
port. Original UMF executes under the configured native person role and policy.
The result returns through safe host capture. UI response loss observes the
same native receipt; it never triggers an automatic replacement mutation.

## Technology Rationale

Original UMF/Weft and psycopg preserve platform ownership. Starlette/Uvicorn are
optional HTTP transport dependencies selected by ADR-016. Bun builds the
TypeScript DOM application; no frontend framework is introduced. Playwright,
TypeScript checking and ESLint are development tools. pgserver provides the
explicit dedicated PostgreSQL 18 local environment.

## Traceability

| Requirement ID | Component | Design Element | Test Strategy |
| --- | --- | --- | --- |
| FR-1 | App/model/UI | Public declared operations | STP-101 native browser journey |
| FR-2 | Original UMF model | BR-1/2 native conditions | Stale decision and current independent approval |
| FR-3 | Host/native adapter | BR-3/4 | Foreign/anonymous denial and lost-response observation |
| FR-4 | Local composition | Installed browser/CLI closure | Same native data after restart |

## Concern Alignment

Native dependency ownership, async public I/O, explicit typed configuration,
authorization, durable effect knowledge and the existing test ratchet apply.
The app imports no native engine in business/UI code. Core imports no provider.
Local authentication and capture do not qualify remote login or OTLP delivery.
ADR-016 records selected optional dependencies; no other framework is selected.

## Constraints & Assumptions

Only fabricated people and records are used. Initialization explicitly creates a
new dedicated cluster; ordinary startup verifies its original installed model/head.
The first local adapter subset accepts one module and one table; it rejects
other installation shapes before database effects. The declared query bounds
remain visible; broader schemas need their own qualification.

## Risks

Candidate SDK/source divergence requires original packaging verification and
retained wheel/source hashes. Local stub identity remains loopback-only.
Native, installed, browser and deployed qualification remain distinct claims.

## Diagnostic Flow

The host owns operation spans and durable audit. Native connection instrumentation
creates linked database child spans under the same context. The local exporter
filters before durable capture, excluding SQL, request text and connection details.
Capture loss returns safe unavailable/uncertain outcomes. A real OTLP receiver and
fleet diagnostic budgets remain separate qualification work owned by Erik.

## Schema Basis

The authoritative `../models/approval.umf.json` composes original UMF core 0.10.0,
tables 0.1.0 and table-operation 0.1. TD-101 declares its `ddx.schemas` identity.
No new vocabulary or ORM is introduced. The pinned original compiler and actual
native/browser journey establish only the exercised local candidate subset.

## Local discovery

CONTRACT-012 defines explicit registration metadata and per-app routing.
`AppListing` and `create_registry` stay in the optional ASGI module. The local
assembly supplies the registered app instance; static previews contain fabricated
data and listing grants no business access. STP-101 maps US-101-AC6 to browser
proof of the loaded thumbnail, description, app URL, scoped cookie and return link.
