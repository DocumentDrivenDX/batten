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
its implementation. Fleet allocation below adds FR-42–44 and the strengthened
FR-23/27/29; this plan does not assert complete product coverage.

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

## Semantic controls and extension allocation

US-003-AC8–14 expand the same fabricated review journey under FR-40/41.
Allocation is planned evidence, not additional test functions or passing results.

| Behavior | Primary layer | Observable evidence |
| --- | --- | --- |
| Composed wizard/form/collection state and commit policy (AC8/9) | Real renderer/client/server journey | Back/forward, invalid fields, stable row IDs, explicit cell/row/batch commit; conflicts and partial outcomes preserve native meaning. |
| Detailed local code without added packages (AC9) | Installed/built artifact | Python and TypeScript cases exercise supplied APIs; closure evidence includes generated bundles. |
| Web/terminal semantic equivalence (AC10) | Surface conformance against same server | Same declared edits, validation, cancellation/confirmation, denial and original uncertain invocation; independently exercise keyboard/focus/navigation. |
| Missing renderer/control (AC11) | Contract assessment | Required browser-only editor refuses terminal before imports/effects; explicit qualified alternative is a separate case. |
| Unapproved package closure (AC12) | Artifact build/admission | Table covers direct/transitive imports, bundled/vendor/remote/dynamic loads and installer attempts; no package fetch/import/install occurs during assessment. |
| Approved exceptional extension (AC13) | Installed extension integration | Exact reviewed closure admitted; changed closure refuses; platform code still denied undeclared access. |
| Instance cleanup and scope (AC14) | Renderer lifecycle integration | Teardown disposes observers and prevents actor/resource/revision state leakage. |

Extend the existing review-state/recovery scenarios for custom controls rather
than duplicate their authorization assertions. Terminal tooling and exact commands
require a separately qualified runtime; browser evidence cannot substitute for it.
The metadata schema validates reference shape only. Upstream semantic definitions,
slot bindings, renderer coverage, cycles and closure provenance need semantic tests.


## Test Data Strategy

Use a fabricated review queue with Review records, approve action, deterministic
recommendation double and a separate optional saga reference. Keep the same
application bytes across local/embedded profiles. Native PostgreSQL18 fixtures,
identities and UI records are fabricated; no production snapshots or credentials.

## Fleet and runtime evolution allocation

PRD FR-23/27/29/42–44 add fleet assurance to the first-host plan. These rows are
planned qualification, not passing evidence or new test-function allocations.
Extend existing public-boundary scenarios for invariants they already own.

| Acceptance ID / source | Primary evidence layer | Required observable outcome |
| --- | --- | --- |
| FLT-01 / FR-23 | Installed runtime/application delivery | Build/admit/start fabricated applications using only the supplied runtime with registry access unavailable; attempted pip/npm fetch/install refuses. |
| FLT-02 / FR-29/42 | Admission and cohort qualification integration | Missing, failing, stale or mismatched app assertions/behavior coverage refuses; current exact evidence qualifies. Changing the app/cohort/policy invalidates it. |
| FLT-03 / FR-27/42 | Host diagnostics integration | Application opt-out cannot disable required capture; calls/refusals carry safe app/artifact/cohort attribution. Sink loss is visible and cannot produce passing evidence. |
| FLT-04 / FR-42 | Candidate/accepted cohort comparison | Breaking dependency/interface changes identify affected apps and integration dependents; required behavior executes before eligibility and incompatible candidates are withheld. |
| FLT-05 / FR-43, CMP-16 | Native shared-host load qualification | A fabricated fleet targeting hundreds of apps runs the declared mix; excess use, failures, cancellation and revocation preserve scope, configured fairness and allocations. Measure capacity and failure domains. |
| FLT-06 / FR-44, CMP-17 | Public graph-provider authorization integration | Authorized declared interaction works; foreign target, missing authority, revoked grant and undeclared private access refuse. Graph links confer no grants. |
| FLT-07 / FR-42 | Runtime recovery and durable-state integration | Retained qualified cohort remains usable when state-compatible; incompatible schema/state refuses rollback and uncertain external effects stay visible. |

Platform-only tests or schema validation cannot qualify an application fleet.
Owners must specify workload, concurrency, per-app/owner budgets, telemetry loss
policy, evidence policy and pass thresholds before tests can claim capacity or
upgrade safety. Pin runtime/application digests, provider versions, platform and
policy in each result. Use fabricated data; no live fleet operations are authorized.
The function-count ratchet remains in force; consolidation must preserve every
required outcome. No capacity, percentage-coverage or latency measurement exists
in this packet. Exact evidence/telemetry/graph and rollout contracts are required
before dependent source work.

## Semantic application conformance allocation

FR-47 is P0. Automatic conformance for every fully declarative UI-and-hook
composition is required; default-construct support gaps cannot be treated as
optional test exclusions. Use generated cases through shared public behavior
runners; these rows allocate outcomes, not additional test functions.

| Acceptance ID | Primary layer | Observable outcome |
| --- | --- | --- |
| SEM-01 | Semantic generator conformance | Every default construct and allowed refinement produces a complete behavior/CLI/property inventory; a missing definition, hook oracle or CLI mapping prevents qualification. |
| SEM-02 | CLI/host end-to-end | Generated commands exercise every declared behavior, including UI navigation/state, hook effects, validation, denial, confirmation, cancellation and original-call recovery; no private-host bypass. |
| SEM-03 | Real renderer/host/provider end-to-end | Automatically generated legal/illegal state sequences check semantic invariants and actual UI/hook outcomes, including focus/accessibility where relevant; no handwritten per-app cases are required. |
| SEM-04 | Generator/oracle negative controls | Deliberately wrong transitions, ignored refinements and altered declarative hook effects produce reproducible minimized failures; implementation self-comparison cannot pass. |
| SEM-05 | Cross-platform migration conformance | Exact app/refinements and properties run on accepted/candidate bindings; semantic drift, absent UI/hook behavior or missing required coverage blocks migration qualification. |
| SEM-06 | Reproducibility/evidence integration | Replay pinned seeds/traces and shrunk counterexamples against exact artifacts/cohorts; changed semantics invalidate prior evidence and exploration limits remain explicit. |

Generate from desired semantics after use-case refinement, preserving original
UMF/ux-builder meaning and testing implementation through public execution paths.
The default declarative hook set must supply deterministic contracts/oracles for
observed effects; external nondeterminism requires controlled fixtures or qualified
properties, never guessed exact outputs. Arbitrary procedural hooks need explicit
test contracts and cannot silently inherit declarative completeness.

Conclusive qualification means all required declared behaviors have adequate
oracles, CLI mappings and real end-to-end coverage, with a decisive pass/fail
verdict for the stated domain and exploration policy. Property-based sampling is
not an exhaustive proof of unbounded behavior; finite modeled state spaces may
also be explored exhaustively. Report coverage and bounds, never turn a missing
case into success. Generation must preserve configured authority/resource limits,
use fabricated inputs and controlled clocks, and retain uncertain effects without
blind replay. No live platform migration or external effect is authorized here.

Exact semantic model/refinement, generator/oracle, CLI and execution-report
contracts, qualified renderer/platform adapters and the testing framework remain
implementation prerequisites. No generated runtime suite has executed in this
specification packet. Existing first-host and native evidence requirements remain.

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
