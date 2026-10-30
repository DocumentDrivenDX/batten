---
ddx:
  id: ADR-009
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: derived_from
    - id: ADR-008
      kind: informed_by
---

# ADR-009: Preserve ux-builder authority behind an optional binding

## Problem

Batten needs usable UI defaults without creating another design system or copying
ux-builder's blueprint. Host-specific screen wiring would defeat application portability.

## Decision

Use optional ux-builder renderer adapters over a presentation-independent
operation/outcome boundary. The browser client is its first concrete binding;
a terminal client is a separately qualified design target.
ux-builder retains its original blueprint/design/component/theme/audit authority.
Batten owns references from controls to native UMF fields/actions and host-context
services under CONTRACT-005. Headless installations omit all UI dependencies.

Authors progress from manifests and native UMF/extensions to application-local
Python/TypeScript controls and hooks. Detailed local code is a normal extension
path using the supplied platform APIs and primitives. New third-party libraries
are exceptional platform extensions requiring explicit owner approval, a pinned
qualified closure and host admission. No application-driven installation is allowed.

ux-builder owns semantic control definitions, composition slots and presentation;
Batten preserves references and binds them to native operations. Renderer choice
is independent of hosting/placement. A browser-only control remains valid for
its declared surface without implying a terminal implementation.

## Why We Chose This

### Over generating a second Batten layout language

A reference binding connects existing authorities without maintaining competing
layout schemas or silently losing upstream design decisions.

### Over embedding host shell APIs in generated screens

The same client/context boundary can run locally, standalone or embedded; server
permissions and confirmation remain authoritative after the UI is generated.

## Consequences

**Good:** Reusable design workflow and UI defaults, portable client contracts,
independent headless installs and explicit server authorization proof.

**Trade-offs:** The adapter must qualify a pinned starter/blueprint/renderer/client
cohort, and SDK audit alone cannot prove host integration.

**Drift signals to watch:** copied blueprint schemas, application credentials in
assets, native types reconstructed from labels, eager UI dependencies or shell imports.

## Assumptions

Provisional risk: the published design-first flow and public outputs may require
an upstream extension to expose stable operation bindings. The first cohort proof
must establish the actual supported API. Semantic control definitions, local
implementation slots and terminal rendering may need upstream extensions; those
APIs are unknown and must be qualified before dependent source work. Adapter internals and package pins are
reversible; this does not block portable core or the effect-free assessor.

## Concern Impact

Adopts the owner's ux-builder integration and constrained extension requirements
across qualified presentation boundaries. It selects no second backend runtime and no deployed identity provider.
