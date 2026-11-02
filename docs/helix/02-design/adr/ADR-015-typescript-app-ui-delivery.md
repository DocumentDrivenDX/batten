---
ddx:
  id: ADR-015
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: informed_by
    - id: ADR-009
      kind: informed_by
---

# ADR-015: TypeScript applications bridge the UI delivery gap

## Problem

Batten's declarative UI model is a target, while the owner wants useful apps
before that compiler/renderer exists. Reimplementing a UI framework would delay
the platform integrations and imply unsupported semantic test generation.

## Decision

Initial interactive reference apps are application-authored TypeScript browser
apps. They use the public Batten client and scoped host context in CONTRACT-005,
with original UMF model/action identities and server-side authorization. They
never connect directly to a database, graph engine, secret store or provider.
ux-builder design assets and tooling remain an integration opportunity through
its qualified public surface, without a new Batten layout or component engine.

Native declarative behavior can drive generated server/CLI properties. TypeScript
UI journeys require real browser tests authored against app acceptance criteria;
arbitrary TypeScript cannot be declared automatically covered by FR-47. Future
declarative UI still must meet FR-39–41 and FR-47 before claiming that support.
This decision selects no new frontend framework or application dependency.

## Why We Chose This

### Over waiting for a declarative UI compiler

TypeScript apps can exercise the host, permissions and existing platform services
while renderer work proceeds independently.

### Over embedding platform clients in the browser

The public host boundary preserves identity, deployment portability and resource
containment; an app cannot supply authority through its own IDs or role labels.

## Consequences

**Good**: UI delivery can progress without another modeling or rendering engine.
**Trade-offs**: Initial UI behavior needs explicit browser scenarios and authored
accessibility checks. Pure CLI tests do not prove those journeys.
**Drift signals to watch**: Provider credentials in UI code, direct backend access,
unreviewed frontend dependencies or automatic coverage claims for arbitrary code.

## Concern Impact

Refines the delivery sequence for ux-builder integration, without replacing its
ownership or changing the longer-term declarative UI requirement.
