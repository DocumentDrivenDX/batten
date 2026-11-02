---
ddx:
  id: approval-desk.build
  type: implementation-plan
  activity: build
  authoring:
    home: repo
  links:
    - id: US-101
      kind: informed_by
    - id: TP-101
      kind: informed_by
---

# Approval desk build

## Scope

The owner authorized building the first reference app after pushing the corpus.
Implement the requester/independent approver journey with native UMF/PostgreSQL
tables, local host and authored TypeScript UI. US-101, FEAT-101 and TP-101 govern
business behavior; SDK CONTRACT-001/003/005/011 and ADR-015/016 govern integration.

## Shared Constraints

No new ORM, compiler, agent or UI framework. Generic runtime imports no platform
libraries. Browser code uses public operations; authentication is explicitly
local-only and server-bound. Startup never migrates; explicit maintenance creates
only the dedicated fabricated local namespace. No production service or secret
access. Preserve the decreasing measured test-function ceiling and native meanings.

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate |
| --- | --- | --- | --- | --- |
| AD-01 | Contract and native source basis | US-101, ADR-016 | None | Inspect public SDK and compile original app declarations |
| AD-02 | Module boundaries and generic host ports | SDK CONTRACT-001/002 | AD-01 | Import/export/shape gates and negative controls before dependent source |
| AD-03 | Native tables and explicit local setup | Original UMF app model | AD-02 | PostgreSQL 18, RLS, conditional commands and original receipt observation |
| AD-04 | Public ASGI/client and TypeScript app | SDK CONTRACT-005, app transport contract | AD-03 | Same-origin/local identity, native authorization and accessible browser journey |
| AD-05 | Native/browser proof and documentation | TP-101 and story test plan | AD-04 | Positive, stale, self/foreign/revoked, retry/recovery and restart outcomes |

## Execution Contract

The current user instruction supplies build authorization, including necessary
local test setup. No production apply, real credentials or migration of existing
data is authorized. Token, money and time ceilings were not supplied; available
tools have no reliable billing meter. Verification and review remain in scope.
The preceding corpus commit/push is separate from this implementation's source.

## Continuation Evidence

Resume from the diff, native compilation and actual test outputs. The corpus was
pushed before source work. Keep native SDK limitations explicit; do not replace
an unavailable feature with handwritten persistence or a scripted app result.

## Validation Plan

Reuse installed original SDK code and compile app-owned UMF declarations. Test
real PostgreSQL 18 and actual TypeScript browser interactions, current authority,
stale revisions, original-attempt observation and server restart. Consolidate only
duplicated read setup to preserve the global function budget. Inventory validation
does not establish app execution, and local capture does not establish deployed
or OTLP receiver qualification. Record each actual evidence layer separately.

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
| --- | --- | --- | --- |
| Candidate SDK subset refuses app semantics | Native integration blocked | Diagnose exact public capability and retain upstream ownership | Refuse affected operation |
| Local stub escapes intended surface | Identity confusion | Loopback-only origin/host guards and explicit local mode | Disable local authentication route |
| Mutation acknowledgement is lost | Duplicate decision | Observe original native receipt with unchanged inputs | Never blindly replay with a fresh key |

## Exit Criteria

The app can be built and run locally through documented commands, and its chosen
native/browser journey passes against original UMF/PostgreSQL behavior. Required
boundaries and evidence remain explicit; no unsupported production, broader SDK
or full-corpus qualification is claimed.

## Completion evidence

The local approval journey and registry are implemented. Native/browser proof
passed two tests; the fast gate passed 18 cases within the unchanged 17-function
ceiling. See `../03-test/local-execution.json` and STP-101 for exact cohort and
assertion scope. Broader platform and production qualification remain governed by
their own integration work items.
