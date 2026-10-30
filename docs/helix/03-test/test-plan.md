---
ddx:
  id: TP-001
  type: test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: FEAT-002
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
---

# Batten test strategy: composition and first-host slice

## Strategy

Prove the first P0 composition/hosting/UI boundary through public behavior before
claiming installed, native, browser or deployed support. FEAT-009 and the initial
FEAT-002 ux-builder story define this packet's scope. The rest of PRD FR-1–33
remains required product scope and needs its own story/test allocation before
its implementation; this plan does not assert complete product coverage.

## Framework Selection & Cost

| Layer | Framework | Justification | CI Time Impact | Maintenance Burden |
| --- | --- | --- | --- | --- |
| Schema/contract | Existing JSON Schema validator in author tooling, then pinned UMF validators | One authoritative payload source and upstream semantics | Unmeasured; measure first gate | Retain semantic checks distinct from shape. |
| Portable behavior | pytest, ADR-001 | Installed Python public API with whole-outcome tables | Unmeasured; no invented timing | Fewest behavior tests; review consolidation. |
| Native/installed | uv wheel installs and PostgreSQL18 integration, ADR-001 | Prove real closure/lifecycle/effects beyond doubles | Unmeasured | Isolated resources, explicit ownership. |
| Browser E2E | Playwright/Chromium, ADR-001 | Same real client/server journey under both hosts | Unmeasured | Stable observable waits; no blind retries. |
| UX quality | Pinned ux-builder lint/audit | Upstream presentation/interaction checks | Unmeasured | Keep cohort and reports independent of authorization proof. |

No dependencies are installed by this packet. Runtime/timing/count baselines
must be measured from the first reviewed behavioral suite; its ceiling thereafter
only decreases under ADR-007. Scenario names do not allocate new test functions.

## Critical Paths (P0)

1. Effect-free resolution and headless installed closure (US-001).
2. Same application across profiles, drift refusal and owned/borrowed cleanup (US-002).
3. A ux-builder review screen, server authorization and uncertain-write recovery (US-003).
4. Upstream saga support refusal or exact qualified binding without a fallback (US-004).
5. Actual import/shape/test gates before all dependent source features (CONTRACT-002).

## Acceptance Criteria Layer Allocation

| Criterion class / source | Planned primary layer | Why |
| --- | --- | --- |
| US-001 resolution/unknowns/inert handlers | Portable contract | No effects are allowed during assessment. |
| US-001 headless closure | Installed artifact | Source imports cannot prove wheel independence. |
| US-002 profile comparison/drift/identity/unsupported placement | Portable contract | Deterministic refusal precedes effects. |
| US-002 lifecycle cleanup/uncertainty | Lifecycle integration | Observe actual public start/close behavior with controlled services. |
| US-003 review states, confirmation, revocation and original-outcome recovery | Whole-stack browser | Observe UI and server/effect outcome together across local/embedded profiles. |
| US-003 binding integrity | Contract | Tampered/undeclared targets refuse before rendering. |
| US-003 upstream starter/cohort | Upstream integration | Public tool outputs and exact package closure require direct observation. |
| US-004 absent support and passthrough | Contract, then upstream native conformance for support claims | Doubles prove only Batten translation; upstream qualifies saga execution. |

Story Test Scenarios name the planned observable assertions. Per-story test plans
and technical designs must bind those scenarios to actual files/commands before
source implementation. No planned test is represented as passing evidence.

## Test Data Strategy

Use a fabricated review queue with Review records, approve action, deterministic
recommendation double and a separate optional saga reference. Keep the same
application bytes across local/embedded profiles. Native PostgreSQL18 fixtures,
identities and UI records are fabricated; no production snapshots or credentials.

## Known Gaps

No source tests, first measured ceiling or native cohort exist in this packet.
UMF saga executor, ux-builder public integration surface, frame transport and
remote-worker custody require separate evidence. These gaps block their support
claims, not effect-free composition design or independent headless applications.

## Build Commands

Planned commands, not executable/passing claims:

```text
uv run python scripts/check_boundaries.py --base HEAD
uv run pytest tests/composition tests/hosting
uv run pytest -m integration tests/installed
bunx playwright test tests/browser/review.spec.ts
```

The first scaffold must implement the actual gate and positive/negative import,
cycle, private-access, shape and test-count controls, then wire the same command
locally, in hooks and CI. Missing checkers/tests fail readiness rather than skip.
UI lint/audit commands must come from the verified pinned ux-builder outputs.

## Exit Criteria

Each required behavior has exercising, cited evidence, with canonical `@covers`
IDs in eventual tests. Installed/native/browser observations retain separate
cohort/scope. Shape/import/test ratchets run; unknown semantics remain explicit.
This strategy allocates verification and makes no implementation completion claim.
