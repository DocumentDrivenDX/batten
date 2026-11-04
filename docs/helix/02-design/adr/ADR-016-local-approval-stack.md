---
ddx:
  id: ADR-016
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: ADR-015
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
---

# ADR-016: Assemble the local approval stack from existing public engines

## Problem

The first TypeScript app needs a running host and native typed persistence.
Building another ORM, HTTP server or rendering framework would expand its scope
and obscure the platform boundaries it is meant to exercise.

## Decision

Use the public UMF table deployment compiler and native async table binding over
psycopg/PostgreSQL 18. Application records and conditional commands are original
UMF declarations. Native compilation, RLS, receipts and outcome observation remain
upstream behavior. Use pgserver-pg18 only for explicit local maintenance/testing.

Keep generic host contracts/runtime stdlib-only. Optional table integration owns
UMF/psycopg dependencies; optional ASGI integration owns Starlette/Uvicorn. The
app supplies TypeScript DOM code and uses Bun for build-time transpilation, with
no new frontend framework. JavaScript Playwright is a development-only real-browser proof.
OpenTelemetry SDK instrumentation and safe durable local audit are host services;
local capture and actual OTLP receiver evidence remain distinguishable.

Use Python 3.13 for the upgraded local qualification environment: the current
PostgreSQL 18 helper publishes matching native wheels, and UMF Core/Codegen
support the interpreter. Portable library metadata retains its Python 3.11 floor;
qualification claims remain tied to their actually exercised interpreter.

Pin the assembled dependency cohort in the build lock and preserve original UMF
source digests. Local source dependencies may be used for candidate qualification;
they do not imply a published upstream release. No runtime package installation,
production identity, external infrastructure or implicit database upgrade occurs.

## Why We Chose This

### Over handwritten SQL persistence and migration generation

The upstream ORM owns typed declarations, native policy and original-attempt
recovery. Batten provides scoped integration and app-specific decisions.

### Over an additional frontend framework

A small authored TypeScript app can demonstrate the required journey through
public operations while preserving room for ux-builder integration.

## Consequences

**Good**: A real local vertical slice with separate generic, provider and UI layers.
**Trade-offs**: Candidate ORM subsets and installed/native/browser evidence must be
qualified explicitly. Local stub authentication confers no production support.
**Drift signals to watch**: Direct SQL in app code, platform dependencies in core,
provider credentials in browser code or treating local audit as OTLP qualification.

## Concern Impact

This selects optional ASGI and local native testing dependencies for the authorized
app build; it does not change the platform-neutral core or add a rendering engine.

## Local registry evolution

The owner selected a registry landing page after trying the first app. Keep its
listing metadata and HTTP presentation in the optional ASGI/local modules.
Explicit registered app instances compose under distinct URL prefixes; no new
discovery engine, frontend framework, native dependency or database table is
needed. Each local instance keeps independent sessions and provider bindings.
