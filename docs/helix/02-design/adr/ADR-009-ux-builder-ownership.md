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

Use an optional ux-builder adapter over Batten's portable public browser client.
ux-builder retains its original blueprint/design/component/theme/audit authority.
Batten owns references from controls to native UMF fields/actions and host-context
services under CONTRACT-005. Headless installations omit all UI dependencies.

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
must establish the actual supported API. Adapter internals and package pins are
reversible; this does not block portable core or the effect-free assessor.

## Concern Impact

Adopts the owner's ux-builder integration requirement within the existing browser
boundary. It selects no second backend runtime and no deployed identity provider.
