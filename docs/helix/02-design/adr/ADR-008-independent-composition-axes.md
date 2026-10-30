---
ddx:
  id: ADR-008
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: ADR-001
      kind: informed_by
    - id: ADR-003
      kind: informed_by
---

# ADR-008: Separate capability selection, hosting and placement

## Problem

Applications need selectable platform modules and several hosting environments.
Encoding every combination as a deployment type couples business meaning to
resources and makes optional provider dependencies mandatory.

## Decision

Represent application capability requirements, hosting profiles and execution
placement independently. Assess immutable metadata before loading code or starting
services. Hosts explicitly register installed providers and trusted factories;
application declarations cannot install them. CONTRACT-003/004 own the surfaces.

Native UMF application extensions describe application meaning. Portable core
accepts validated metadata projections and remains stdlib-only. `batten.umf` owns
UMF parsing/validation and native saga references; `batten.runtime` owns generic
assessment. `batten.hosting` owns typed profile resolution and selected-factory
composition through public APIs. Development/embedded hosts use this same boundary.

## Why We Chose This

### Over a preset for every platform combination

Independent axes preserve one application artifact across local, standalone and
embedded environments while keeping unsupported combinations explicit.

### Over automatic plugin discovery and dependency installation

Explicit installed metadata and host factory catalogs permit effect-free assessment
and enforce the already selected baked-in cohort/admission policy.

## Consequences

**Good:** Selectable dependency closure, inspectable refusal before effects and
consistent ownership/lifecycle across hosts.

**Trade-offs:** More explicit configuration; native metadata adapters must retain
source/evidence instead of replacing unknown meaning with a generic model.

**Drift signals to watch:** platform names becoming hosting modes, automatic
provider imports during assessment, hidden fallback placement, and UI dependencies in core.

## Assumptions

Provisional risk: the first supported public UMF cohort may lack a required
application-reference or saga executor surface. The native adapter must refuse
that capability until qualified. This is reversible and does not block a pure
metadata assessor, public lifecycle doubles or other independent applications.
Remote-worker syntax makes no transport/recovery claim; qualification precedes use.

## Concern Impact

Preserves hexagonal architecture, native platform ownership, typed files,
explicit cohort installation and boundary/test ratchets. No new runtime,
datastore or deployment provider is selected.
