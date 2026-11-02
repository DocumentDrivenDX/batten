---
ddx:
  id: SD-002
  type: solution-design
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
    - id: batten.architecture
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: ADR-015
      kind: informed_by
---

# SD-002-lintel-graphql-relay: Embed Lintel GraphQL and Relay access

**Feature**: [FEAT-002](../../01-frame/features/FEAT-002-operations-and-interfaces.md).
Owner direction on 2026-11-02 selects a separate Python/FastAPI Lintel runtime,
GraphQL + Relay rather than dual OpenAPI/GraphQL, and TypeScript client builds.
Lintel's packet lives in [DocumentDrivenDX/lintel](https://github.com/DocumentDrivenDX/lintel/blob/main/docs/helix/README.md).
The project name is provisional. This is integration design, not product code.

## Scope

Include Lintel in Batten's qualified platform runtime. Mount its GraphQL API
through public ASGI/host boundaries; build TypeScript Relay operations/fragments
from the same schema. UMF owns model meaning, Weft compilation, existing providers
native execution and Batten authority/resource custody. No private application
source is required. This refines FR-8/9 and ADR-015's public browser-client path.

## Requirements Mapping

| Requirement | Technical Capability | Component | Priority |
| --- | --- | --- | --- |
| FR-8/9 | Same declared command/query and gates through GraphQL | Lintel plus public Batten host | P0 |
| FR-32/33 | Async lifecycle and independent packaged dependency | Optional Batten integration | P0 |
| FR-42 | Qualified client/schema/runtime cohort | Platform build and acceptance | P0 |
| ADR-015 | Authored TypeScript app over public access | Relay artifacts/network adapter | P0 |

## Solution Approaches

Select a public Lintel adapter mounted at Batten composition. Pure Batten core
stays neutral; a module-owned adapter translates host capabilities and outcomes.
Putting GraphQL in core would couple every host to the framework. A standalone
Lintel service that bypasses Batten would lose admission/confirmation/attribution.
A Python API boundary avoids a separate TypeScript-to-Python gateway/sidecar.

## Domain Model

Reuse approved UMF model/operation identities, Batten actor/application context
and the provider's exact outcomes. Lintel projects GraphQL Node/connection/scalar
shapes and explicit exposure selection. Those are transport/client concepts, not
a competing UMF metamodel, authorization model or SQL language.

## System Decomposition

- Lintel owns projection, GraphQL/Relay adaptation and schema/client export.
- Batten host composition constructs the optional adapter and injects the Lintel
  router into the ASGI host. Generic core/ASGI modules do not discover or import it.
- Batten owns the proposed optional `batten.lintel` binding in this repository.
  It implements Lintel's neutral public execution ports through public Batten
  host invocation. Lintel imports no Batten package; generic Batten core imports
  neither Lintel nor GraphQL. This is one-way consumer integration, not mutual
  package coupling. Its exact API requires a contract and real import checks.
- Batten table/graph providers retain runtime execution; resolvers must not call
  raw providers around admission, permissions, confirmation or audit.
- Platform builds carry Python GraphQL dependencies and Relay client/build assets.
  Applications perform no pip/npm installation and no runtime dependency discovery.

## Technology Rationale

Python/FastAPI follows owner direction and the Databricks Apps embedding goal.
Strawberry is a reversible candidate for GraphQL/Relay schema construction;
Relay's compiler emits TypeScript operation/fragment artifacts. Pin and exercise
the actual interpreter/framework/compiler cohort before adopting it.

## Traceability

Lintel FR-1–12 and US-001–006 govern its component. Batten's existing public host
and feature gates remain authoritative when embedded. Acceptance must run one
installed Batten app from compiled Relay TypeScript in Chromium through GraphQL
to PostgreSQL 18, including refetch, arbitrary-edge continuation, batched expansion,
denial, exact values, uncertain write recovery and borrowed-resource shutdown.

## Concern Alignment

Public async I/O, neutral core, typed file settings, no new environment variables,
source/quality boundaries, minimal behavioral tests and host-enforced diagnostics
remain intact. A new framework is supplied by the optional platform dependency,
not installed by an application. No browser UI framework is selected here.

## Constraints & Assumptions

The local TablePort carries operation/inputs/phase/key/mutation but no explicit
connection/batch/selection metadata. The UMF adapter currently constructs a person
SessionIdentity; this does not establish service/batch authority. Required public
extensions must preserve true actor kinds and per-request native custody.

The published UMF 0.5.2 cohort references Weft 0.4.48; Batten's local candidate
pins 0.4.51. These versions must not be mixed into an invented qualified cohort.
No package/version/API name is frozen merely by appearing in this design.

## Risks

| Risk | Prob | Impact | Mitigation |
| --- | --- | --- | --- |
| Current paging does not supply Relay edge positions | Present gap | High | Upstream runtime capability; no offset fallback |
| Host invocation loses confirmation or identity | Unmeasured | High | Real public-boundary negative cases |
| Shared Relay cache mixes apps/actors | Unmeasured | High | Stable namespaces and scoped/cleared stores |
| Databricks app identity mistaken for caller identity | Unmeasured | High | Explicit host mapping and separately qualified deployment |

## Diagnostic Flow

Batten owns authoritative invocation/audit context. Lintel adds GraphQL operation,
projection/cohort and safe outcome context without logging variables or tokens.
Real OpenTelemetry receiver/correlation/privacy evidence is required at execution.
Exact telemetry surfaces and GraphQL/host mappings need contracts before source work.

## Schema Basis

Reuse current UMF 0.10 Records/Fields/Keys/Relationships and understood declared
commands/actions, plus the existing public Batten host/provider contracts. Lintel
must consume a supported neutral Python description rather than parse private
code or copy executable schema rules. Its pinned source inventory identifies the
inspected inputs. No new normative schema is introduced by this integration note.

## Gaps

Complete the Lintel projection/dynamic-schema, Relay native-read, host/outcome and
TypeScript build spikes before exact public contracts and source handoff. The
current Batten review gate remains for implementation/migration; this owner-directed
planning amendment does not assert source, installed, native or deployed acceptance.
