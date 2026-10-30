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
FR-23/27/29. US-005 and the service discovery allocation below cover the expanded
FR-44; this plan does not assert complete product coverage.

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
6. Shared semantic identity, filtered discovery and exact revocable service bindings (US-005).

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

### Local development evidence

US-002 adds the required stub-auth/shared-pgserver/Tether profile. Its actor-gate
and no-fallback outcomes use public-boundary tests; shared-server identity,
separate ownership, borrower lifetime and reload preservation require native
PostgreSQL 18 observations through Truss and the public UMF table binding.
Tether adapter behavior uses a deterministic scripted model-API fixture; a
separately configured real endpoint supplies live integration evidence. Neither
replaces the other. Test configuration contains no real credential or firm data.

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

## Platform asset acceptance allocation

FR-46, FEAT-009 CMP-18–22 and CONTRACT-010 extend US-002 without changing the
source review gate. Reuse existing graph, source identity, authorization and
lifecycle matrices for the same observable behaviors. Rows allocate evidence,
not new test functions or a larger ceiling. Use fabricated data only.

| Acceptance ID | Required outcome | Primary evidence layer |
| --- | --- | --- |
| PLT-01 / US-002-AC13 | Managed, external and mixed manifests retain exact sources/contracts; duplicate owners, cycles, missing bytes, altered pins and relevant unknown semantics refuse without native effects. | Existing portable composition matrix |
| PLT-02 / US-002-AC13 | Installed core and generic wrapper import without SDK/CLI; core contains no native types; undeclared local/remote dependencies refuse without fetching. | Installed boundary/admission gate |
| PLT-03 / US-002-AC14 | Planning executes no native build hooks; altered source, bindings, dependency receipts, state or approval prevents apply. | Deployment provider conformance |
| PLT-04 / US-002-AC14 | Concurrent deployment/request-ID reuse preserve one owned operation; timeout, cancellation and lost acknowledgement retain partial/unknown effects and reconcile before mutation. | Durable deployment integration, restart and competing deployers |
| PLT-05 / US-002-AC15 | Managed/external bindings require exact trusted receipts, schema/contract compatibility, current permissions and readiness; definition-only deployment refuses until authorized initialization succeeds. | Native provider admission integration |
| PLT-06 / US-002-AC16 | Ordinary lifecycle preserves assets/borrowers; destruction and transfer require explicit approval and dependency checks. | Existing lifecycle plus deployment retention matrix |
| PLT-07 / US-002-AC15 | Producer changes identify affected consumers; consumers cannot deploy/adopt/grant external resources or discover hidden assets through failures. | Existing authorization/fleet matrices |
| PLT-08 / US-002-AC14 | Adapter maps native outputs/external assets to opaque bindings while retaining actor, effective deployer, operation and attribution gaps. | Native integration; existing audit allocation |

Databricks qualification MUST pin CLI/SDK/API, bundle format, feature profile,
workspace/target and principals. Observe resource creation, pipeline initialization
and output readiness, separately reviewed ordinary-table creation/migration,
permissions, drift, partial apply and reconciliation. Test App resource attachments
separately from creation. Doubles, lookups and deployed definitions cannot prove
native behavior. Live runs require separate namespace/operation authorization and
finite budgets. No implementation or native deployment suite is run by this evolution.

## Exit Criteria

Each required behavior has exercising, cited evidence, with canonical `@covers`
IDs in eventual tests. Installed/native/browser observations retain separate
cohort/scope. Shape/import/test ratchets run; unknown semantics remain explicit.
This strategy allocates verification and makes no implementation completion claim.

## Object storage acceptance allocation

CONTRACT-006 derives FR-26's first local/Volumes pair. Use one conformance matrix
per observable behavior across providers; extend existing lifecycle/authorization
scenarios where they already own the same invariant. The first reviewed suite
still establishes the measured function ceiling; these rows allocate no counts.

| Acceptance ID | Required outcome | Primary evidence layer |
| --- | --- | --- |
| STO-01 | The same resource/key reads, writes, stats, lists and deletes fabricated bytes across both providers; no native paths escape. | Native local/Volumes conformance |
| STO-02 | Missing actor, scope escalation and revocation refuse without existence disclosure, including active streams and continuation. | Public host authorization integration |
| STO-03 | Traversal, encoding, symlink/ancestor races, special files and key aliases cannot escape or overwrite another logical object. | Native local filesystem conformance; Volumes path translation matrix |
| STO-04 | Conditional create/replace/delete preserve the winner or refuse; content/revision tokens and managed/native concurrency stay distinct. | Native competing-writer conformance, including a non-Batten writer |
| STO-05 | Large/empty objects, early close, chunk/source failure, timeout and cancellation obey bounds, close streams and retain possible effects. | Native transfer lifecycle integration |
| STO-06 | Shallow/recursive listing, projection and prefix pushdown avoid per-object HEAD and repeat scans; budgets, empty progress pages, authority and cursor scope/expiry hold. | Public provider conformance |
| STO-07 | Startup/reload preserves bytes; closing a borrower leaves shared clients usable; private staging never lists as content. | Native lifecycle integration |
| STO-08 | Metadata row failure after byte completion retains a partial workflow outcome; no cross-resource transaction or automatic retry is claimed. | Existing declared-action outcome integration |
| STO-09 | Storage-free installed core has no storage/vendor import; local storage imports without Databricks installed. | Installed artifact boundary gate |

Provider qualification pins SDK/API, workspace feature profile, native authority,
OS/filesystem and actual configured bounds. Documentation or doubles cannot prove
create-only, filesystem race containment, Unity Catalog enforcement or native
cancellation. Use fabricated records and a dedicated approved test namespace;
live grants, infrastructure changes and production data are outside this work.
Schema validation proves shapes only. No native conformance has been run here.

## Messaging acceptance allocation

CONTRACT-007 and ADR-011 derive FR-45 and extend FR-19/20/22. Extend the existing
host authorization/lifecycle matrices where they own the same invariant. These
acceptance IDs allocate observable outcomes, not new test-function counts or an
implementation sequence. PostgreSQL is the first native provider under test.

| Acceptance ID | Required outcome | Primary evidence layer |
| --- | --- | --- |
| MSG-01 | Effect-free assessment checks topology, limits, exact codec/profile closure and required features; missing support refuses before provider I/O. | Portable admission contract |
| MSG-02 | Queue consumers compete; each topic subscription receives its own logical delivery; acknowledgement affects only its subscription. | Native PostgreSQL public-provider conformance |
| MSG-03 | Publish/delivery/dedup commit together; concurrent same-ID retries enqueue once, changed content conflicts, response loss reconciles within retained windows. | Native PostgreSQL competing-transaction conformance |
| MSG-04 | Crash after claim, expired lease, stale receipt, response loss and retry/reject/ack conflicts retain correct outcomes; handlers execute outside claim transactions. | Native PostgreSQL fault/recovery conformance |
| MSG-05 | Missing/foreign/revoked authority refuses without payload, receipt or existence disclosure; background identity cannot impersonate a producer; permission checks cover lookup and settlement. | Existing public host authorization matrix |
| MSG-06 | Delay, visibility extension, bounded polling/batches, capacity, fairness, expiration and attempt exhaustion preserve configured budgets and retained terminal outcomes. | Native PostgreSQL scheduling/capacity conformance with controlled clock/faults |
| MSG-07 | Encode/publish/decode preserve exact writer profile and bytes; invalid/unsupported native payloads refuse; unknown metadata, numeric/presence/union semantics do not silently change. | Exact UMF/native-codec conformance; JSON first, Protobuf/Avro separately |
| MSG-08 | Same-store stage remains invisible before commit, rollback leaves no effects, wrong/closed/foreign context refuses, unknown commit preserves uncertainty. Without a qualified issuer, assessment refuses the feature. | Admission negative matrix; then exact executor/PostgreSQL integration |
| MSG-09 | Restart, missed notifications, reconnect and borrower shutdown preserve durable messages and shared services; interrupted receive does not acknowledge. | Native lifecycle/restart conformance |
| MSG-10 | An external effect followed by worker crash can redeliver; client idempotency prevents duplicate effect without claiming universal exactly-once behavior. | Public consumer/effect fault integration |
| MSG-11 | Core/messaging import without native drivers or codecs; Postgres messaging extra imports only the selected closure; all source observes CONTRACT-002 ceilings. | Installed artifact boundary gate |
| MSG-12 | Schema examples and boundary-negative values match authoritative definitions; semantic checks reject duplicate profile IDs, bad topology, bad base64, incompatible retention and changed profile meaning. | Schema validation plus portable settings contract |

Future provider qualification reuses applicable rows and records every refusal,
auxiliary durable store and semantic limitation. Kafka must prove safe settlement
across partition commit frontiers/rebalances; SQS must tolerate duplicate active
deliveries and qualify fan-out routing; NATS must qualify durable JetStream
consumers and settlement confirmation. No broker equivalence follows from matching
method names. Lakebase additionally needs direct-session, scale-to-zero/reconnect
and restart evidence on its exact cohort.

Use fabricated payloads and isolated approved databases. No production migration,
role grant or service deployment is authorized by this allocation. Schema checks
are separate from the unrun native provider and instance-codec qualification.

| Acceptance ID | Required outcome | Primary evidence layer |
| --- | --- | --- |
| STO-10 | Ranges validate offset/count, EOF, native range responses and the same validator across resumed reads; changed content refuses rather than mixes bytes. | Native range conformance |
| STO-11 | Multipart condition is checked at completion; stale/foreign manifests, duplicate part races, part replacement, complete/abort races and lost acknowledgments preserve original state. | Native upload-session integration |
| STO-12 | Qualified reattachment rechecks authority and exact profile; expiry/revocation/restart and staging cleanup never expose partial uploads or delete a completed destination. | Native durable-resume lifecycle integration |
| STO-13 | Source/delivered/stored checksum evidence stays distinct; mismatch, early close and composite native checksums never yield false whole-object verification. | Transfer integrity conformance |
| STO-14 | Prefetch/cache/retry/parallelism obey shared budgets; cached state cannot satisfy a failed current precondition or survive authority loss. | Public provider performance/correctness matrix |
| STO-15 | A provider advertising atomic publication shows old-or-new whole bytes to competing readers; other profiles do not inherit that guarantee. | Native competing-reader/writer integration |

Listing benchmarks observe native request counts, scan continuation and bounded
memory for shallow, recursive and filtered pages. They allocate no invented
throughput or timing target. Reuse STO-02/05/06/07 for the same invariants rather
than adding duplicate tests; scenario IDs do not allocate test functions.

## CQRS, attribution and audit acceptance allocation

FR-9/13/26/27 and CONTRACT-001/004/006 govern these outcomes. Command Query
Responsibility Segregation (CQRS) separates business commands from queries;
OpenTelemetry (OTel) supplies system instrumentation. Extend existing public
boundary scenarios where they own an invariant; these IDs allocate no test counts.

| Acceptance ID / source | Required observable outcome | Primary evidence layer |
| --- | --- | --- |
| ATT-01 / FR-9 | Route/tool/UI/event/hook projections preserve command/query intent and gates; concealed query mutations and raw-client bypass refuse before effects. Read audit/cache bookkeeping remains permitted. | Public operation/provider integration |
| ATT-02 / FR-13/27 | Human, delegated, approved-model and autonomous calls retain origin, approver, effective authority and application separately; forged identity/baggage, expired delegation and revoked grants confer no authority. | Existing host authorization integration |
| ATT-03 / FR-27 | Context survives publish/delivery/redelivery, schedules, workers, agent tools and graph calls; logical command/run remains stable, attempts differ and changed retry intent refuses. Unknown effect remains uncertain. | Durable messaging/worker/provider integration |
| ATT-04 / FR-13/27 | Concurrent users, pooled sessions and reused workers retain distinct principals and causal context after failure/cancellation; no identity leaks into the next call. | Native database and worker integration |
| ATT-05 / FR-26/27 | Every selected system boundary emits correlated OTel evidence; native request/principal and available model usage stay distinct from Batten user attribution. Missing native support is explicit; required unavailable capability refuses. | Native provider conformance matrix |
| ATT-06 / FR-27 | Sampling or absent trace context preserves required durable audit. Capture outage/overflow before effects blocks required capture; failure after possible effects retains uncertainty, loss and reconciliation without false success. | Audit persistence/fault integration |
| ATT-07 / FR-27 | Current scope gates audit query/export; applications cannot alter/delete records. Redaction precedes export, metrics remain bounded and baggage cannot leak user credentials, private payloads or cross-user identity. | Existing non-disclosure/access integration |
| ATT-08 / FR-9/27 | Command outcome, delayed projection and actual audit persistence remain distinct; retries and partial multi-service effects cannot claim exactly-once or cross-resource atomicity without evidence. | Existing action/receipt integration |

ATT-05 extends FLT-03 and storage conformance rather than duplicating their
outcomes. Qualify the actual logger/ingestion/export path through a real OTel
receiver, with no duplicate ingestion, and separately prove audit persistence and
access. Pin SDK/semantic-convention/provider versions and application/cohort policy.
Provider matrix covers database, messaging, AI gateway, storage/search, secrets,
workers, graph and host lifecycle interactions, including traced and untraced cases.
Operators must contract audit retention/integrity, query/export, loss policy,
identity-disclosure bounds and required native attribution before dependent source
work. This is verification allocation; no native/runtime tests were run.

## Service discovery and binding allocation

PRD FR-44, CMP-17/CMP-23–29 and US-005 govern CONTRACT-009's five-type native
platform model. These rows allocate evidence; they add no test functions or
passing claims. Extend the existing resolution, FLT-06 authorization, headless,
upgrade and recovery scenarios for their owned invariants.

| Acceptance ID / criteria | Primary layer | Required observable outcome |
| --- | --- | --- |
| SVC-01 / US-005-AC1/4/5 | Native declaration structure plus composition semantic validation | All five record shapes and references resolve; exact shared identity and digests hold. Same-name types, changed artifacts, conflicting joins, ambiguous providers and unknown required meaning refuse without losing bytes. |
| SVC-02 / US-005-AC2/6 | Extend FLT-06 public Arras/provider integration | Actor-filtered metadata, paging/counts, target lookup and dependency paths disclose no hidden objects. Separate discovery grants from invocation grants; forged app/delegation/header identities and revoked grants yield no effects. |
| SVC-03 / US-005-AC3/4 | Extend US-001 effect-free resolution | Separate host evidence pins the unchanged consumer; its digest enters the plan without a self-reference cycle. Resolution performs no network/import/start; absent/ambiguous/incompatible/cyclic required dependencies refuse; optional absence remains inactive. |
| SVC-04 / US-005-AC5/9 | Registry publication/bootstrap integration and installed closure | Only verified app exports and authorized host commands create eligible bindings. Explicit root registry binding avoids self-resolution. Core-only hosts import no ontology engine and consume equivalent explicit evidence. |
| SVC-05 / US-005-AC7/10 | Extend binding drift, FLT-04/07 upgrade/recovery | Cached bindings and continuation cannot outlive current authority/revisions. Relocation retains semantic interface identity; dependency impact is exact and permission-filtered. No fallback/replay; retirement/revocation preserves uncertainty and active-dependent policy. |
| SVC-06 / US-005-AC8 | Native transport conformance per selected profile | Graph, owner-published table/view, API and messaging independently prove native authority, semantic mapping and their declared consistency/recovery. No raw connection, arbitrary cross-app write, implicit subscription creation or assumed cross-resource transaction. |

Fixtures use fabricated customer-owner/review-queue applications, a shared native
Customer artifact, a same-name incompatible type, two competing exports, hidden
providers and expired/revoked bindings. Exercise user and explicit background or
delegated authority. Reuse CONTRACT-007 MSG delivery/codec cases and existing
attribution/audit scenarios rather than duplicating their invariants here.

Native observations MUST pin original ontology/interface/application artifacts,
Arras/UMF and transport cohort, registry revision/visibility profile, trusted
resolution evidence, policy and finite limits. Structural validation proves only
UMF declaration shape. Native record joins, coherent snapshot/continuation,
principal-scoped reads, async adaptation, provider identity and concurrent
revocation require public integration evidence. A local graph double cannot
qualify Unity Catalog, Lakebase, API or messaging behavior. No live registry,
transport, capacity or operational change is authorized by this allocation.

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
