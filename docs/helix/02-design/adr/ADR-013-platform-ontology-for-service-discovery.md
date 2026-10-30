---
ddx:
  id: ADR-013
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: FEAT-009
      kind: informed_by
    - id: ADR-001
      kind: informed_by
    - id: ADR-002
      kind: informed_by
---

# ADR-013: A Batten platform ontology for service discovery and binding

## Problem

Shared business types establish meaning but do not identify service providers,
consumer requirements or deployment bindings. Separate table/API/message
registries would fragment discovery and dependency impact assessment. Ontology
semantics in portable core would violate ADR-001's module boundary.

## Decision

Batten owns a small native UMF platform model: Application, ServiceInterface,
ServiceExport, ServiceRequirement and ServiceBinding. CONTRACT-009 owns their
semantics. Shared business types remain independently governed upstream artifacts.
A catalog is an authorized projection of these records and relationships.

The selected `batten.arras` module interprets the model through public Arras/UMF
interfaces and supplies inert resolution evidence and generic dependency edges.
Host composition bootstraps the registry explicitly and approves deployment
bindings. Pure core gains no ontology-specific types, branches or imports.
Core-only/headless hosts may consume explicit bindings without graph discovery.

Keep semantic interfaces separate from transport descriptors and deployment
resources. Exact immutable artifacts/revisions drive admission; current authority
and qualified provider bindings drive execution. Discovery visibility never grants
invocation access. Table, graph, API and messaging exports share this resolution
model while retaining separate transport guarantees.

## Why We Chose This

### Over a separate bespoke service registry

The same typed graph supports discovery, consumer dependencies and upgrade impact.
Batten avoids a second vocabulary and keeps ontology machinery upstream-owned.
A materialized index may accelerate queries but cannot become an independent
authority or bypass visibility and revision checks.

### Over inferring services from physical schemas

Tables cannot alone identify action contracts, shared semantic identity or message
delivery behavior. Explicit exports define which surfaces their owner supports;
private schemas and shared storage confer no integration rights.

### Over ontology types in portable core

Module-owned interpretation preserves optional dependencies and a generic runtime.
The host supplies a bounded pinned resolution to effect-free assessment; discovery
and root registry bootstrapping occur outside that assessment.

## Consequences

**Good**: One native model relates interfaces, exports, requirements and bindings.
Physical relocation preserves semantic identity; exact dependency pins identify
affected consumers during upgrades.

**Trade-offs**: Registry provenance, permission-filtered reads, revision integrity
and recovery need qualification. The host must bootstrap discovery without a
self-resolution cycle and preserve current authorization despite cached metadata.

**Drift signals to watch**: Graph links treated as grants; latest-version lookup;
raw cross-app connections; discovery provisioning subscriptions; a registry row
self-admitting its application; duplicated business types; ontology imports in core.

## Assumptions

Provisional risk: the public Arras provider can supply bounded authorized reads
and a coherent revision snapshot through an async-first Batten adapter. The
inspected synchronous surface does not prove those properties. An incompatible
API or missing snapshot/authority support invalidates that binding profile.
The module boundary and native model are reversible design choices; unsupported
profiles must refuse rather than acquire an unqualified core fallback.

Registry storage, scale thresholds, transport profile IDs and exact public cohort
remain qualification inputs. No database, broker or service mesh is selected here.

## Validation

**Result**: not tested with native services.
**Evidence**: CONTRACT-009 source receipt identifies inspected public definitions;
US-005 and TP-001 define required semantic, installed and native observations.
Structural checks alone cannot establish live discovery, binding or access behavior.
