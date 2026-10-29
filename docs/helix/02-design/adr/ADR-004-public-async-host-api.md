---
ddx:
  id: ADR-004
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: batten.boundary-audit
      kind: informed_by
---

# ADR-004: Development and deployment use one public asynchronous host API

## Problem

Private application factories, worker constants, permission parsers, database
shutdown helpers, logging configuration, and import-path discovery prevent a
development host from being an independent consumer.

## Decision

Provide the public host lifecycle and injected-service boundary in CONTRACT-001.
Development hosting uses it exactly as another embedder does. The portable host
accepts typed configuration and service protocols, exposes admission/dispatch/
readiness, and owns only resources explicitly transferred to it.

Public I/O is asynchronous. Pure factories, declarations, and planners may be
synchronous. HTTP/ASGI and MCP adapters call the public host; neither discovers
or imports an embedding application. The development host constructs its own
logging/diagnostic sink and explicit loopback-only fabricated identity.

The embedding host supplies native credentials and identity through private
adapter-owned services; no raw connection or host credential reaches application
code, the browser bridge, or a worker. A separately declared application secret
is available only through its authorized secret port for the intended call.
Exact shutdown and borrowing semantics belong
to CONTRACT-001 and must be observed under cancellation.

## Why We Chose This

### Over publishing the current private helper modules

A public API states lifecycle and ownership invariants. Re-exporting private
helpers would expose application construction and mutable implementation state.

### Over a second fake development host

One lifecycle/admission implementation prevents the local host from proving a
different permission model. Doubles exercise service protocols, not another host.

## Consequences

**Good**: An installed local host can run without a consuming application's source.

**Trade-offs**: Embedders must supply explicit service bindings and resource ownership.
The local fabricated actor does not establish deployed identity qualification.

**Drift signals to watch**: source-checkout lookup, borrowed service shutdown,
global mutable settings, or an environment reader in core.

## Concern Impact

Applies async-first, modularity, typed configuration, and the cleanroom boundary.
