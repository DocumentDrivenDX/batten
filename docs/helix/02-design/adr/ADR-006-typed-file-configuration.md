---
ddx:
  id: ADR-006
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
---

# ADR-006: Typed files are authoritative configuration

## Problem

Environment-driven configuration spreads deployment values and reader logic
across modules. The owner requires layered typed files, environment as a last
resort, and no new environment variables.

## Decision

The composition root resolves configuration once and injects immutable typed
values. Precedence is explicit call overrides, then the ordered file layers
(later layers override earlier ones), then already-supported host environment
fallback for absent fields, then declared defaults. A missing required value,
unknown key, or invalid value fails by field name without logging its value.

Portable contracts and runtime read neither files nor environment. The host uses
Pydantic Settings with an explicitly ordered file source; automatic environment
discovery and dotenv loading are disabled. A deployment may provide a reviewed
mapping to existing variables at its boundary. Batten introduces no environment
names and does not turn file keys into environment names by convention.

Resource addresses and approvals belong to host configuration. Plugin declarations
name requirements and typed application settings; secret references name purpose,
and the secret adapter obtains authorized values only for the call that needs them.

## Why We Chose This

### Over environment-first library defaults

Files provide reviewable layering, and an absent field can still use an explicit
host fallback. Environment cannot silently override a reviewed file.

### Over module-local readers

One resolved object makes provenance and rejection consistent and leaves tests
independent of ambient process state.

## Consequences

**Good**: Configuration precedence and ownership are explicit.

**Trade-offs**: Consuming hosts need a deliberate legacy/environment mapping;
the later migration plan must preserve their current visible settings behavior.

**Drift signals to watch**: inferred environment aliases, dotenv files, module-level
settings singletons, secret values in configuration output, or core I/O readers.

## Concern Impact

Overrides `python-uv` environment-first precedence and central automatic environment
loading. The owner's configuration ruling has precedence over those defaults.
