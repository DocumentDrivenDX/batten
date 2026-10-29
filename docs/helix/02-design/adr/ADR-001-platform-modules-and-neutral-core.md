---
ddx:
  id: ADR-001
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

# ADR-001: Platform modules around an ontology-neutral core

## Problem

Combining declarations, platform implementations, and host construction makes
dependency boundaries hard to enforce. A neutral core must not acquire ontology
semantics merely because one installed module supplies ontology capabilities.

## Decision

Use the architecture's explicit module map and core-owned generic ports. Portable
contracts and runtime use the Python standard library. Platform modules own native
semantics, types, clients, and qualification. Concrete services are wired at the
embedding host's composition root or the development host.

Proposed defaults: Python 3.11 consumer floor with uv, Ruff, strict Pyright and
pytest; browser-compatible JavaScript with a TypeScript/Bun toolchain and
Playwright/Chromium verification. Native integration uses public UMF/Weft, Arras,
Tether, psycopg, Databricks SDK, gateway HTTPX/injected clients, FastAPI/ASGI, and
the MCP SDK only in their owning modules. Pydantic Settings and uvicorn belong
to host composition; `packaging` belongs to artifact tooling/verification. The
PostgreSQL helper is an explicit development dependency, pinned to PostgreSQL 18.

The ontology provider is a normal Batten platform module. Pure core handles
opaque component declarations, required capabilities, and generic dependencies.
It has no ontology type, query, registration, or storage-specific branch.
Application metadata cannot install or replace a privileged platform provider.

Exact dependency releases require a verified cohort. The proposal's reversible
risk is that an upstream public API or platform client lacks a required behavior;
qualification may refine the adapter surface, never justify a second engine in core.

## Why We Chose This

### Over exposing private host helpers

Public lifecycle/configuration/provider contracts let an independently installed
host work without application internals. Private helpers would retain the coupling
the boundary census identified.

### Over an ontology-aware universal core

Module-owned schemas keep ontology, tables, and agent sessions independent. Core
can order a dependency graph without understanding the provider's domain model.

## Consequences

**Good**: Every platform has an import owner and testable dependency closure.

**Trade-offs**: More package/API boundaries and explicit composition work; a
platform's domain-specific convenience surface belongs to its module.

**Drift signals to watch**: ontology imports in core, private source discovery,
vendor request types crossing core ports, or eager optional imports at the namespace root.

## Concern Impact

Select Python/uv and hexagonal architecture with the scoped browser and adapter
concerns. No private design system or deployment topology is selected.
