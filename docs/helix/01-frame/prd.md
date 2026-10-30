---
ddx:
  id: batten.prd
  type: prd
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.product-vision
      kind: derived_from
    - id: batten.boundary-audit
      kind: informed_by
kind: product
---

# Batten product requirements

## Summary

Batten is an open-source application SDK and packaged runtime in the Novirhyza family.
It targets hundreds of integrated applications on shared infrastructure, with
platform-owned dependency evolution, enforced observability and behavioral
verification. Deep declarative services reduce both initial integration and
ongoing fleet operating cost. This is intended behavior requiring qualification.

Authors compose native UMF declarations for data and behavior, with typed
procedural hooks and ux-builder interfaces. They select capabilities independently
of hosting environments and execution placement.
Host teams embed a public runtime contract that applies admission, identity,
permissions, audit, and lifecycle consistently across those surfaces.

The SDK separates portable contracts and execution policy from platform-specific
tables, isolation, Databricks, Lakebase, model gateway, and development hosting.
Platform libraries are supplied by the platform. Batten uses UMF's Python SDK
and compiler, Weft, Arras, and Tether through their public surfaces. It provides
no duplicated compiler, query engine, ontology engine, or agent loop.

The product scope below re-frames the owner's reference requirements into Batten
outcomes. Private application names, imports, deployment values, and implementation
structure are outside Batten's public contract. The owner has explicitly selected
native UMF authoring and typed access; consuming hosts own legacy compatibility.

## Problem and Goals

### Problem

An SDK that bundles unrelated platform implementations cannot give consumers a
small, stable dependency surface. A development host that reaches into application
internals cannot be installed and evolved independently. Plugin authors inherit
those integration responsibilities, and support claims blur offline doubles,
local database checks, and deployed behavior.

### Goals

1. Authors define data, behavior, and UI through one coherent application contract.
2. Hosts embed that contract without exposing their own internal modules.
3. Platform dependencies and permission responsibilities stay explicit and checkable.
4. Every specified capability receives implementation and qualification; an old
   reference implementation's absence or limitation does not silently reduce scope.
5. Application authors consume a complete qualified runtime without pip/npm
   installation; platform owners qualify dependency upgrades across applications.
6. Required telemetry, assertions and behavioral test coverage provide enforceable
   evidence for admission, operation and candidate runtime upgrades.
7. Hundreds of applications share services with explicit resource limits,
   ownership and attribution, and integrate through governed graph API contracts
   and future defined mechanisms.

8. Application semantics and use-case refinements drive complete CLI access and
   automatically generated property-based end-to-end conformance suites for every
   fully declarative UI-and-hook composition, including platform migration.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| App-specific integration effort | Baseline and target supplied by Erik LaBianca | Compare custom wiring for a fabricated application across hosts. |
| Developer iteration effort | Baseline and target supplied by Erik LaBianca | Observe build/admit/update steps and elapsed time. |
| Boundary independence | No private host dependency | Import census and installed-artifact qualification. |
| Declarative conformance | Every default construct and fully declarative UI/hook composition has automatic CLI and end-to-end qualification | Generate suites from effective semantics; replay against candidate platforms and reject mismatches or missing coverage. |
| Application package setup | No application-level pip/npm install | Exercise application build/admission/start against a complete runtime without package-registry access. |
| Upgrade qualification | All affected required behavior has current evidence before rollout | Compare exact candidate and accepted cohorts against application assertions, coverage and protocol compatibility. |
| Shared fleet scale | Hundreds of applications; exact load mix and service budgets to be qualified | Measure shared-service cost, contention, fairness, isolation and recovery using fabricated applications. |
| Governed integration | Declared, authorized interfaces only | Exercise graph API access, revocation and dependency change; future mechanisms require their own contracts. |

### Non-Goals

Host identity-provider deployment, shared infrastructure provisioning, a marketplace for
unknown third-party code, a hostile-code security boundary, and replacement
implementations of the platform libraries are outside product scope. Batten
handles its host integration and application-delivery responsibilities within
the platform supplied by the operator.

## Users and Scope

### Primary Persona: Application author

Python developers compose native data models and application behavior. They need
local development, portable artifacts, useful diagnostics, and clear limits on
what their application may reach.

### Secondary Persona: Host integrator and operator

Platform developers embed Batten, supply identity and platform services, set
permissions and limits, and admit application artifacts. They need stable public
APIs, revocation, audit, and independent compatibility checks.

### Consumers

Installed plugin projects, hosted-plugin declarations, and embedded host applications
are consumer forms. A declaration without Python source still receives compatibility
assessment. Source-specific consumer identities stay in the private audit packet.

## Requirements

### Must Have (P0)

The complete specified scope is required: declaration/admission, operations/UI,
native data access, worker/background execution, artifact delivery, platform
resources, author tooling, and host embedding. Selectable modules are optional per application; implementing their specified
contracts remains required product scope. Every FR below is P0; grouping
organizes ownership and does not create optional delivery tiers.

### Should Have (P1)

No additional capability is assigned this priority by the owner.

### Nice to Have (P2)

No additional capability is assigned this priority by the owner.

## Functional Requirements

### Subsystem: Declaration and admission

- **FR-1** — Authors declare each application's identity, SDK compatibility,
  components, providers, permissions, and audit vocabulary in one reviewed specification.
- **FR-2** — Hosts resolve typed, immutable settings from layered files, with
  environment only as a last resort; invalid or unknown keys fail by key name.
  Specifications carry no deployment values or secret values.
- **FR-3** — Hosts detect identity collisions, incompatible SDKs, inconsistent
  manifests, altered artifacts, and declaration/code disagreement before admission.
  Refusals expose safe reasons and readiness outcomes.
- **FR-4** — Application routes stay in their declared namespace and behind their
  own gate. Compatibility aliases, if needed, belong to the consuming host.
- **FR-5** — Every request resolves an authenticated actor and is permission-gated;
  configuration requires an administrator. Declared admin access matches enforced
  access in both directions. Missing identity never creates an ungated inbound path.
- **FR-6** — Users see only enabled, admitted, permitted applications and UI sections;
  catalog visibility follows the server's listing.
- **FR-7** — Refusals and port failures use stable safe outcomes without disclosing
  data, SQL, deployment addresses, credentials, or inaccessible object names.

### Subsystem: Operations and interfaces

- **FR-8** — Applications carry screens, routes, branding, views, and workflows as
  digest-covered resources. The host owns navigation, confirmations, downloads,
  and the permission-contained browser bridge; applications import no shell internals.
- **FR-9** — One typed operation supplies its route, tool, screen, view, and event
  adapters. Ambiguous tool ownership or undeclared calls are refused. Human-started
  operations use declared confirmations; model-started writes require approval.
  Command Query Responsibility Segregation (CQRS) is the default exposed mutation
  model: declared commands change business state; queries cannot conceal mutations.
  All adapters and local hooks preserve that distinction, authorization, attribution
  and audit. CQRS does not itself require event sourcing or separate databases.

- **FR-39** — UI applications integrate with ux-builder design artifacts and its
  public component/theme/audit tooling. Stable bindings connect UI controls to UMF
  metadata and Batten operations across local, standalone and embedded hosts.
  Headless applications omit UI dependencies. Host authentication, confirmation
  and resource containment apply equally to generated and custom screens.
- **FR-40** — Authors compose semantic wizards, grouped forms and editable
  collections from manifests, UMF and extensions, then implement detailed local
  controls in Python and/or TypeScript when needed. Ordinary customization adds
  no third-party dependency. Extra packages require an explicitly approved
  platform extension; declarations and local code cannot install them.
- **FR-41** — Application interactions separate meaning from presentation so
  qualified browser and terminal renderers can preserve validation, draft state,
  commit boundaries, confirmation and operation outcomes. Custom controls declare
  their supported surfaces; unsupported required interactions refuse explicitly.
  Terminal support is a design target requiring separate qualification.

### Subsystem: Native data and identity

- **FR-10** — Warehouse access is declared and bounded, executes as the caller,
  and supports paging. Users choose among operator-offered warehouses; choices
  persist and never grant access. Background application access is separately declared.
- **FR-11** — Applications declare native ontology types and operate through the
  platform's public reader/action interfaces, including paging, relationships,
  bounded multi-key reads, batches, idempotency, and consistency receipts.
  An application changes only its own declared module.
- **FR-12** — Native UMF declarations and upstream-generated, reviewed migrations
  govern application-owned PostgreSQL 18 tables. Lifecycle preserves containment,
  schema/role ownership, ordered and digest-checked steps, restart recovery,
  transactional/concurrent/validation/data-step behavior, checks, indexes, and comments.
- **FR-13** — Requests use the person's database identity; scheduled work states
  its application, owner, or delegated identity. There is no shared-identity fallback
  or stored user credential. Separate owner/request/batch authority and bounded
  person pools prevent schema or privilege changes by ordinary callers.
- **FR-14** — Upstream-generated row policy preserves deny-by-default commands,
  owner/group/association/parent scope, batch grants, explicit unscoped declarations,
  and reviewed scope changes. Unsupported meaning is refused or explicitly retained.
- **FR-15** — Effective permissions require both application request and operator
  grant, with deployment approval for exceptional capabilities. Checks apply during
  admission and use; generated structural changes need no arbitrary-SQL grant.
- **FR-16** — Native UMF typed access is the public data-authoring path. Bounded
  reads, exact pages, atomic batches, validation, backpressure, and declared indexes
  receive equivalent behavior in-process and through workers.
- **FR-17** — Exceptional direct SQL requires explicit request, grant, deployment
  approval, ownership separation, and complete row-scope declarations. It runs as
  the person through a DML guard and is unavailable to background jobs.

### Subsystem: Workers and background execution

- **FR-18** — Owner-scoped workers and job children receive only admitted requests
  and revocable capabilities, with bounded resources, deadlines, restart/circuit
  behavior, and deterministic shutdown. Denied calls start no worker; children
  receive no host credential or raw database connection.
- **FR-19** — Declared recurring functions use one durable queue with idempotent
  schedule firing, fairness, concurrency/queue limits, retries, cancellation,
  ownership, suspension, accounting, and no downtime catch-up storm.
- **FR-20** — Owners confirm writes and external job starts against the displayed
  identity, scope, executor, and schedule. Material change invalidates confirmation;
  access is rechecked at execution and loss suspends work with an owner-visible reason.
- **FR-21** — Declared platform jobs and pipelines, initially targeting Databricks,
  support reviewed deployment
  and governed reconciliation, staged verified artifacts, least-privilege job
  identity, platform scheduling, enable/pause/cancel, observation, accounting,
  and lineage drift reporting. Limits that cannot bind externally started work
  are disclosed in the confirmation.
- **FR-22** — Applications trigger their declared jobs and non-admin event operations,
  inspect authorized run handles, and read durable run records. Event work uses
  explicit application authority and cannot impersonate an interactive caller.
- **FR-45** — Applications publish schema-qualified messages and consume declared
  durable subscriptions through one scoped asynchronous interface. PostgreSQL 18
  is the first backend. Queue consumers compete; topic subscriptions progress
  independently. Delivery is at least once with explicit settlement, bounded
  retries and recovery. Payloads reuse original UMF schemas with exact qualified
  codecs; provider capabilities refuse unsupported guarantees. Future Kafka,
  SQS and NATS bindings must preserve the selected profile without client-native
  broker APIs. Same-store publication requires a qualified transaction executor;
  backend availability alone establishes no atomicity.

### Subsystem: Artifact delivery and lifecycle

- **FR-23** — Authors build self-describing wheels containing declarations,
  resources, digests, and tests. Hosts validate SDK series and the baked-in
  dependency cohort before plugin code executes. New third-party dependencies
  are exceptional platform changes requiring owner approval and host admission;
  runtime dependency resolution
  and vendored platform libraries are refused. The platform delivers the complete
  qualified runtime, including selected Python/browser dependencies and services;
  application build, admission and start must not require pip/npm installation.
- **FR-24** — Hosts admit installed and stored artifacts under explicit approval
  policies, support shared and owner-scoped admission, and revoke or roll back by
  artifact identity. Packaged extensions expose reviewed public surfaces and
  version handshakes. Removal checks dependents and requires a fresh confirmed plan;
  disabling alone preserves data.

### Subsystem: Platform resources and diagnostics

- **FR-25** — Applications declare secret references by purpose. Host resolution
  is scoped, uncached, permission-checked, and audited without exposing values in
  representation or diagnostics. Secret values travel only for the authorized call.
- **FR-26** — File, search, completion, and embedding ports enforce declared resources,
  caller or explicit application identity, bounded results, budgets, and safe
  errors. Files remain within the application's storage scope. Object-storage
  access must support S3, Azure Data Lake Storage, Databricks Volumes and a local
  filesystem through one scoped capability, preserving each backend's qualified
  guarantees rather than assuming filesystem or transactional equivalence.
  The initial backend pair is Databricks Volumes and a local managed filesystem;
  S3 and Azure Data Lake Storage extend the same application boundary.
  Qualified capabilities include conditional mutations, version-pinned byte ranges,
  multipart/resumable upload and explicit integrity verification. Listing is shallow
  and bounded by default, with native continuation and optional metadata projection.
  Unsupported concurrency or publication guarantees refuse before effects.
- **FR-27** — Namespaced audit and declared telemetry cover admission and execution
  across all surfaces. They carry safe identifiers/counts/outcomes, report capture
  limits, and distinguish offline, native, browser, and deployed evidence.
  Required telemetry is a host-enforced admission/execution obligation, not an
  optional application opt-in. Capture loss is observable and cannot silently
  become passing evidence. OpenTelemetry (OTel) instrumentation covers every
  database, messaging, AI gateway, storage, search, worker, graph and other system
  interaction, including reads, refusals, retries and background work. Attribution
  retains the initiating user when present, delegation and effective execution
  identity with application/resource and causal correlation. Each provider uses
  the strongest supported native attribution and reports remaining gaps explicitly.
  Durable audit preserves decisions and actual or uncertain outcomes independently
  of trace sampling. Telemetry context never grants authority; capture and exports
  enforce access, redaction and bounded identity disclosure.
- **FR-28** — Authors declare required platform grants; operators inspect their
  resolved status and apply them through the platform owner. Applications do not
  acquire grant authority by declaring a requirement.

### Subsystem: Author tooling and qualification

- **FR-29** — Shared conformance checks validate declarations, gates, resources,
  artifacts, platform boundaries, compatibility, and documentation against observable behavior.
  Hosts require application assertions and test evidence covering declared behavior,
  bound to artifact identity and the qualified cohort. Missing, failing or stale
  required evidence refuses admission or upgrade qualification. Behavioral coverage
  and the decreasing test-function budget are independent requirements; no numeric
  code-coverage threshold is implied.
- **FR-30** — Offline doubles and public-boundary test hosts let applications test
  without the embedding application. Distinct integration tests qualify real
  PostgreSQL 18, workers, browsers, and deployed adapters; doubles do not confer native support.
- **FR-31** — Authors scaffold, configure, validate, build, inspect, test, explain,
  run, stop, and inspect applications through documented tooling. A standalone
  loopback development host and operation-derived MCP access exercise the public
  host contract; the executable guide uses fabricated data.

### Subsystem: Host embedding and compatibility

- **FR-32** — Embedders construct, start, stop, inspect, and configure a host through
  a public asynchronous lifecycle API with explicit ownership of services and resources.
- **FR-33** — Each platform module installs and imports within its declared
  dependency closure. Host development uses public APIs only. Consumer transition
  must preserve visible behavior in both the SDK and consuming-host repositories.

### Subsystem: Composition and hosting

- **FR-34** — Authors and host operators select independently installed modules
  with explicit capabilities, dependencies and compatibility. Unselected optional
  modules introduce no eager imports or mandatory platform dependency.
- **FR-35** — Authors compose application meaning through native UMF documents
  and Batten-owned application extensions. Models, action types, saga semantics
  and unknown content retain upstream authority; procedural hooks bind by reviewed
  identity without declarations installing code or granting authority.
- **FR-36** — Operators bind the same application to local, standalone and embedded
  hosting independently of platform choices and execution placement. Profiles
  describe identity, ownership, resources, selected providers and supported
  placement; unavailable combinations refuse before effects. The required local
  profile uses explicit stub authentication and a shared PostgreSQL 18 pgserver
  instance for Truss and direct UMF table access. It also supports local Tether
  execution through a host-configured model API. Separated workers
  require independently qualified transport and recovery.
- **FR-37** — Authors assess composition without starting services or executing
  application/provider code. Results explain missing or ambiguous capabilities,
  cycles, incompatibilities, unknown semantics and placement limits with safe
  identifiers. An eligible plan is bound to exact inputs and is not runtime readiness.
- **FR-38** — Saga-enabled applications use UMF-owned saga declarations and exact
  executor capabilities. Batten exposes scoped invocation, observation and recovery
  bindings while preserving UMF outcomes and uncertainty. Missing upstream support
  blocks the affected component rather than invoking a Batten-specific fallback.

### Subsystem: Fleet operation and evolution

- **FR-46** — Applications carry digest-pinned native deployment packages, require
  exact externally managed resource contracts, or combine both through a generic
  platform wrapper. Providers own native formats, resource kinds and environment
  bindings; core interfaces contain no vendor deployment semantics. Operators
  separately plan, authorize, apply and reconcile changes under scoped identity.
  Each asset has one lifecycle owner. Admission requires current contract,
  access and readiness evidence; deployment alone does not prove usable outputs.
  Startup/reload never applies, migrates or grants. Persistent assets survive
  runtime shutdown/removal by default; destructive changes require separate
  authorization and dependency checks. Recovery retains partial/uncertain effects.

- **FR-42** — Platform owners qualify candidate dependency/runtime cohorts against
  affected application assertions, behavioral coverage, required telemetry and
  interface compatibility before rollout. Evidence binds exact application and
  runtime artifacts; changed inputs invalidate prior qualification. Operators can
  identify impacted applications, withhold an incompatible upgrade and retain a
  qualified cohort. Recovery must respect durable-state compatibility; a code
  rollback does not imply data/schema rollback.
- **FR-43** — The runtime supports a target fleet of hundreds of applications on
  shared infrastructure through declarative services, with per-application and
  owner attribution, authorization, bounded concurrency/resource use, fairness
  and lifecycle control. One application's excess use, revocation or failure
  must not bypass another's scope or silently consume its allocation. Exact
  workload, capacity, failure-domain limits and service budgets require qualification.
- **FR-44** — Applications share independently governed native semantic types and
  discover permitted services/shapes through a Batten-owned platform ontology.
  Declared interfaces, owner exports, consumer requirements and host-approved
  bindings identify exact contracts, providers and upgrade dependencies. Discovery
  visibility, binding and execution authority remain distinct. Every interaction
  checks authenticated caller or explicit application authority, target access
  and current grants; graph relationships confer no authority. Qualified graph,
  owner-published table/view, API and messaging profiles retain their own access,
  consistency and recovery contracts. Bindings refuse incompatible, ambiguous,
  stale or unsupported dependencies without silent provider/version fallback.
  Direct private imports, raw shared connections and undeclared side channels
  cannot substitute for integration. UMF/Arras retain native semantic ownership;
  portable core remains ontology-neutral.

### Subsystem: Semantic application verification

- **FR-47** — Every default fully declarative Batten construct must expose its
  complete functionality through the CLI, including observable UI state,
  navigation, validation, confirmation, cancellation, hooks, effects and recovery.
  Batten must automatically generate property-based end-to-end suites from the
  author's desired semantics and effective use-case refinements. Every fully
  declarative UI-and-hook composition must be conclusively and automatically
  tested against that contract without per-application handwritten tests.
  The same properties must qualify new runtime/platform bindings and block
  migration on semantic mismatch, missing required coverage or unsupported meaning.
  Results must identify exact declarations, refinements, platform cohort, model,
  generation/replay inputs, coverage and exploration bounds. A bounded property
  run is evidence within that scope, not a proof for unbounded executions.
  Arbitrary procedural hooks require explicit contracts/oracles; their behavior
  must not be guessed or silently labeled fully declarative.

## Acceptance Test Sketches

Each row covers the named P0 requirements; these are verification sketches, not
test functions or permission to write code before the review gate.

| Requirement | Scenario | Input | Expected Output |
|-------------|----------|-------|-----------------|
| FR-1 | Declare independent component combinations | Fabricated table-only and UI/tool applications | Both validate without a host-private type. |
| FR-2 | Resolve configuration | Layered files, fallback environment, unknown key | Defined precedence, immutable settings, safe key-only refusal. |
| FR-3 | Admit an artifact | Compatible wheel, altered file, newer SDK, conflicting declaration | Valid wheel admitted; invalid cases execute no plugin code. |
| FR-4 | Admit routes | Own namespace and escaped namespace | Own route admitted; escaped route refused. |
| FR-5 | Exercise access boundaries | Permitted user, stranger, missing actor, admin mismatch | Only authorized outcome occurs; refusals are recorded. |
| FR-6 | List applications | Enabled/disabled, approved/unapproved, admin/user | Listing and UI agree with effective access. |
| FR-7 | Fail a port | Hidden object, invalid parameters, timeout | Stable safe outcome with no private payload. |
| FR-8 | Open screen/view and download | Approved resource, altered bytes, unlisted operation | Host navigation and permitted calls work; altered/unlisted resources fail closed. |
| FR-9 | Call one operation across surfaces | Same declared input through route/tool/view/event | Same authorized behavior; model-write approval is respected. |
| FR-10 | Choose and page warehouse | Offered and unoffered choices for fabricated callers | Choice persists; grants still decide rows; no choice elevates access. |
| FR-11 | Read and change ontology | Own/foreign module, batch, cursor, receipt | Own permitted changes and consistent reads; foreign mutation refused. |
| FR-12 | Evolve native tables | Reviewed migration phases, interruption, changed applied digest | Correct catalog and resumable phases; altered history refused. |
| FR-13 | Execute under principals | Person, delegated run, batch, ordinary schema change | Effective identity audited; unauthorized DDL and fallback refused. |
| FR-14 | Exercise row scopes | Fabricated owners, groups, associations, parent, batch | Exactly declared visibility and write rights, including default denial. |
| FR-15 | Use a capability | Request/grant/deployment combinations | Only effective approved capability executes. |
| FR-16 | Page and batch typed access | Bounded native declarations and invalid/oversized requests | Correct page/batch outcome or explicit backpressure, with worker parity. |
| FR-17 | Invoke exceptional SQL | Approved person call, forbidden statement, job call | Guarded person DML succeeds; forbidden and job paths refuse. |
| FR-18 | Cross worker boundary | Wrong owner, revoked capability, denied gate, timeout | No unauthorized execution; bounded cleanup and safe failure. |
| FR-19 | Fire recurring work | Concurrent ticks, backlog, missed time, cancellation | No duplicate fire; fairness/limits hold and cancellation settles correctly. |
| FR-20 | Confirm and revoke access | Changed confirmation fields or removed entitlement | Stale confirmation cannot run; loss suspends and informs owner. |
| FR-21 | Govern external job | Declared job, changed definition, external run, unavailable lineage | Verified deployment and traceable accounting; drift uncertainty is explicit. |
| FR-22 | Trigger and inspect runs | Declared/foreign jobs and events | Authorized run observable; foreign and impersonating calls refused. |
| FR-23 | Check dependency closure | Baked-in cohort and undeclared/vendored library | Supported artifact accepted without fetching; outside cohort refused. |
| FR-24 | Revoke and remove | Active artifact, dependent module, stale plan | Revocation closes access; data removal requires current unblocked confirmation. |
| FR-25 | Resolve secret reference | Declared and undeclared names | Authorized resolution only; no value in representation or audit. |
| FR-26 | Exercise resources | Scoped files/search and bounded model calls | Authorized bounded outcomes, safe refusal and accurate attribution. |
| FR-27 | Inspect diagnostic output | Calls, refusals, limits, deliberately lost capture | Declared safe events and explicit capture gaps. |
| FR-28 | Inspect grants | In-place, missing, unresolved, unreadable requirements | Accurate read-only report; no implicit grant. |
| FR-29 | Check negative controls | Forbidden import, wrong admin declaration, stale docs | Actual checks fail with actionable locations. |
| FR-30 | Compare evidence layers | Same behavior through double and installed/native adapter | Parity tested; each support claim names its actual evidence. |
| FR-31 | Run the author guide | Empty fabricated project through local host and MCP | Documented workflow works from installed artifacts alone. |
| FR-32 | Embed and shut down | Borrowed and owned services, cancellation | Public lifecycle manages only its owned resources and reports cleanup. |
| FR-33 | Qualify consumers | Installed project and hosted declaration | No private dependency; preserved outcomes across both repositories. |
| FR-34 | Select a headless module closure | Only core and a reviewed provider installed | No UI/platform package imported outside selection; closure conflicts refuse. |
| FR-35 | Exchange application intent | Native model/action references plus unfamiliar extension content | Original meaning retained; relevant unknown semantics block eligibility. |
| FR-36 | Change host profile | One review application under local and embedded profiles | Same application digest; different explicit bindings; unsupported placement refuses. |
| FR-37 | Assess before execution | Missing/ambiguous provider, cycle, wrong version | Safe deterministic findings; no provider/application import or service effect. |
| FR-38 | Admit a saga component | Exact UMF declaration with absent or qualified executor | Explicit refusal or upstream-preserving binding; no fallback engine. |
| FR-39 | Review through ux-builder UI | Loading, denied, invalid, successful and uncertain approval | Authorized server outcome and accessible recovery across both host profiles. |
| FR-40 | Compose then customize a review journey | Wizard/form/collection with a local detailed editor; undeclared library import | Local code works within supplied APIs; extra dependency refuses without a platform exception. |
| FR-41 | Present the same review journey on web and terminal | Shared interactions; one browser-only custom control | Supported surfaces preserve meaning; terminal admission refuses the unsupported required control before effects. |
| FR-42 | Qualify a runtime upgrade | Compatible/breaking cohort, changed app evidence, incompatible durable state | Required exact evidence qualifies; impacted apps are named and unsafe recovery is refused. |
| FR-43 | Share services across a fabricated fleet | Hundreds of applications, bounded load, an abusive/failing app and revoked owner | Qualified budgets/fairness and scope hold; measured limits and failure domains are reported. |
| FR-44 | Integrate via graph API | Authorized interaction, foreign target, revoked grant and changed interface | Only declared authorized interactions execute; affected dependents are identified without private access. |
| FR-47 | Generate and migrate a declarative UI/hook application | Refined wizard/form/collection, declarative hooks, changed platform semantics and unsupported behavior | Automatic CLI and real-client suites exercise all declared behavior; mismatches and coverage gaps block qualification with replayable failures. |
| FR-47 | Generate and migrate a declarative UI/hook application | Refined wizard/form/collection, declarative hooks, changed platform semantics and unsupported behavior | Automatic CLI and real-client suites exercise all declared behavior; mismatches and coverage gaps block qualification with replayable failures. |

## Technical Context

Proposed defaults and platform ownership are in the architecture, concerns,
ADRs, and contracts. The Python consumer floor is 3.11; PostgreSQL support is
18 only. Exact platform dependency releases require a qualification cohort before
implementation support claims. Browser client code targets browser JavaScript;
its TypeScript/Bun build tools remain outside the browser runtime.

## Constraints, Assumptions, Dependencies

## Acceptance Test Sketches

Each row covers the named P0 requirements; these are verification sketches, not
test functions or permission to write code before the review gate.

| Requirement | Scenario | Input | Expected Output |
|-------------|----------|-------|-----------------|
| FR-1 | Declare independent component combinations | Fabricated table-only and UI/tool applications | Both validate without a host-private type. |
| FR-2 | Resolve configuration | Layered files, fallback environment, unknown key | Defined precedence, immutable settings, safe key-only refusal. |
| FR-3 | Admit an artifact | Compatible wheel, altered file, newer SDK, conflicting declaration | Valid wheel admitted; invalid cases execute no plugin code. |
| FR-4 | Admit routes | Own namespace and escaped namespace | Own route admitted; escaped route refused. |
| FR-5 | Exercise access boundaries | Permitted user, stranger, missing actor, admin mismatch | Only authorized outcome occurs; refusals are recorded. |
| FR-6 | List applications | Enabled/disabled, approved/unapproved, admin/user | Listing and UI agree with effective access. |
| FR-7 | Fail a port | Hidden object, invalid parameters, timeout | Stable safe outcome with no private payload. |
| FR-8 | Open screen/view and download | Approved resource, altered bytes, unlisted operation | Host navigation and permitted calls work; altered/unlisted resources fail closed. |
| FR-9 | Call commands and queries across surfaces | Same operation through route/tool/view/event, including a hidden query write | Same attributed command behavior; query mutation refuses; model-write approval holds. |
| FR-10 | Choose and page warehouse | Offered and unoffered choices for fabricated callers | Choice persists; grants still decide rows; no choice elevates access. |
| FR-11 | Read and change ontology | Own/foreign module, batch, cursor, receipt | Own permitted changes and consistent reads; foreign mutation refused. |
| FR-12 | Evolve native tables | Reviewed migration phases, interruption, changed applied digest | Correct catalog and resumable phases; altered history refused. |
| FR-13 | Execute under principals | Person, delegated run, batch, ordinary schema change | Effective identity audited; unauthorized DDL and fallback refused. |
| FR-14 | Exercise row scopes | Fabricated owners, groups, associations, parent, batch | Exactly declared visibility and write rights, including default denial. |
| FR-15 | Use a capability | Request/grant/deployment combinations | Only effective approved capability executes. |
| FR-16 | Page and batch typed access | Bounded native declarations and invalid/oversized requests | Correct page/batch outcome or explicit backpressure, with worker parity. |
| FR-17 | Invoke exceptional SQL | Approved person call, forbidden statement, job call | Guarded person DML succeeds; forbidden and job paths refuse. |
| FR-18 | Cross worker boundary | Wrong owner, revoked capability, denied gate, timeout | No unauthorized execution; bounded cleanup and safe failure. |
| FR-19 | Fire recurring work | Concurrent ticks, backlog, missed time, cancellation | No duplicate fire; fairness/limits hold and cancellation settles correctly. |
| FR-20 | Confirm and revoke access | Changed confirmation fields or removed entitlement | Stale confirmation cannot run; loss suspends and informs owner. |
| FR-21 | Govern external job | Declared job, changed definition, external run, unavailable lineage | Verified deployment and traceable accounting; drift uncertainty is explicit. |
| FR-22 | Trigger and inspect runs | Declared/foreign jobs and events | Authorized run observable; foreign and impersonating calls refused. |
| FR-23 | Check dependency closure | Baked-in cohort and undeclared/vendored library | Supported artifact accepted without fetching; outside cohort refused. |
| FR-24 | Revoke and remove | Active artifact, dependent module, stale plan | Revocation closes access; data removal requires current unblocked confirmation. |
| FR-25 | Resolve secret reference | Declared and undeclared names | Authorized resolution only; no value in representation or audit. |
| FR-26 | Exercise resources | Scoped files/search and bounded model calls | Authorized bounded outcomes, safe refusal and accurate attribution. |
| FR-27 | Follow a user across services | Database/message/model/storage calls, delegated retry, sampled trace and lost capture | Causal user/effective-principal attribution, durable audit, explicit provider/capture gaps and safe disclosure. |
| FR-28 | Inspect grants | In-place, missing, unresolved, unreadable requirements | Accurate read-only report; no implicit grant. |
| FR-29 | Check negative controls | Forbidden import, wrong admin declaration, stale docs | Actual checks fail with actionable locations. |
| FR-30 | Compare evidence layers | Same behavior through double and installed/native adapter | Parity tested; each support claim names its actual evidence. |
| FR-31 | Run the author guide | Empty fabricated project through local host and MCP | Documented workflow works from installed artifacts alone. |
| FR-32 | Embed and shut down | Borrowed and owned services, cancellation | Public lifecycle manages only its owned resources and reports cleanup. |
| FR-33 | Qualify consumers | Installed project and hosted declaration | No private dependency; preserved outcomes across both repositories. |
| FR-34 | Select a headless module closure | Only core and a reviewed provider installed | No UI/platform package imported outside selection; closure conflicts refuse. |
| FR-35 | Exchange application intent | Native model/action references plus unfamiliar extension content | Original meaning retained; relevant unknown semantics block eligibility. |
| FR-36 | Change host profile | One review application under local and embedded profiles | Same application digest; different explicit bindings; unsupported placement refuses. |
| FR-37 | Assess before execution | Missing/ambiguous provider, cycle, wrong version | Safe deterministic findings; no provider/application import or service effect. |
| FR-38 | Admit a saga component | Exact UMF declaration with absent or qualified executor | Explicit refusal or upstream-preserving binding; no fallback engine. |
| FR-39 | Review through ux-builder UI | Loading, denied, invalid, successful and uncertain approval | Authorized server outcome and accessible recovery across both host profiles. |
| FR-40 | Compose then customize a review journey | Wizard/form/collection with a local detailed editor; undeclared library import | Local code works within supplied APIs; extra dependency refuses without a platform exception. |
| FR-41 | Present the same review journey on web and terminal | Shared interactions; one browser-only custom control | Supported surfaces preserve meaning; terminal admission refuses the unsupported required control before effects. |
| FR-42 | Qualify a runtime upgrade | Compatible/breaking cohort, changed app evidence, incompatible durable state | Required exact evidence qualifies; impacted apps are named and unsafe recovery is refused. |
| FR-43 | Share services across a fabricated fleet | Hundreds of applications, bounded load, an abusive/failing app and revoked owner | Qualified budgets/fairness and scope hold; measured limits and failure domains are reported. |
| FR-44 | Discover and bind services | Shared types, visible/hidden exports, ambiguous providers, changed interfaces and revoked grants | Exact authorized resolutions work; unsafe bindings refuse; affected dependents are visible only to permitted callers. |
| FR-46 | Deploy and bind platform assets | Managed package, external contract, mixed dependencies, drift and partial apply | Generic admission preserves source identity; authorized deployment yields verified bindings or explicit uncertainty; startup and shutdown preserve assets. |
| FR-45 | Publish and consume messages | Competing consumers, fan-out, duplicates, crash/response loss, revocation and unknown codec | CONTRACT-007 MSG acceptance proves scoped delivery/recovery; unsupported features refuse before effects. |

## Technical Context

Proposed defaults and platform ownership are in the architecture, concerns,
ADRs, and contracts. The Python consumer floor is 3.11; PostgreSQL support is
18 only. Exact platform dependency releases require a qualification cohort before
implementation support claims. Browser client code targets browser JavaScript;
its TypeScript/Bun build tools remain outside the browser runtime.

## Constraints, Assumptions, Dependencies

### Constraints

- MIT OR Apache-2.0; copyright Synaptiq; clean history and independent implementation.
- Trusted first-party plugins; sandboxing provides permission containment.
- No credentials, tokens, customer content, or token-shaped literals in repository artifacts.
- Async-first public I/O; synchronous pure declaration/planning work is allowed.
- Native UMF and upstream compilers; legacy translation is the consuming host's responsibility.
- No new environment variables, no vendored platform libraries, no runtime installer.
- Every specified behavior stays in delivery scope. No migration plan or product
  code until the owner reviews the first artifact packet. No commit without instruction.

### Assumptions

Python 3.11 is the lowest initial consumer runtime. Framework-neutral operation
contracts and a separately owned FastAPI adapter are proposed to preserve Python
host fit without coupling core declarations to a web framework.

### Dependencies

Public UMF, Weft, Arras, and Tether APIs; PostgreSQL 18; optional Databricks and
gateway services; a host-supplied identity and configuration boundary. Platform
maintainers qualify any upstream behavior needed beyond their current cohort.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Upstream capability differs from reference semantics | Unmeasured | Meaning or behavior changes | Compare a complete capability matrix; resolve upstream gaps without embedding a second compiler. |
| Public host API becomes an internal-object export | Unmeasured | Coupling persists | Installed-artifact-only consumer checks and explicit public protocol ownership. |
| Packaging split creates mixed cohorts | Unmeasured | Admission differs by installation | Common contract release and tested compatibility matrix. |
| An old open policy is mistaken for a decision | Unmeasured | Privilege or lifecycle change | Owner decision register; no new exception by default. |

## Open Questions

Erik LaBianca owns the policy decisions in `decision-points.md`: ontology-provider
exceptions, approval/review authority, persona exposure, job-trigger confirmation,
unbound scoped data steps, and the first measured test budget. Platform operators
own Lakebase and deployed identity qualification; those require observation rather
than a policy guess. The private source plan's undefined decision references carry
no inferred outcome.

## Composition authority and open dependencies

The owner authorized a composition-and-hosting design packet and ddx work items.
This advances specification work; the original implementation/migration review
gate remains until explicit build authorization. UMF owns saga semantics and
ux-builder owns design artifacts. Exact dependency releases and upstream public
APIs require pinned integration proofs; Erik LaBianca and upstream maintainers
supply the first supported cohort. Deployment availability and service-level
targets are unmeasured and remain operator-owned.

## Fleet qualification dependencies

The owner selected the packaged-runtime, enforced-evidence and shared-fleet goals.
Platform owners must supply supported cohort artifacts and upgrade evidence policy;
host operators must define workloads, telemetry failure policy, resource budgets
and service objectives for capacity qualification. Upstream maintainers and host
owners must qualify exact Arras discovery operations, the async bridge, registry
revision/visibility behavior and transport authority/delegation profiles before
integration implementation. CONTRACT-009 defines the platform model and resolution
rules; transport support still requires exact provider evidence. No registry store,
API protocol or additional messaging provider is selected by discovery design.
None of these design obligations is a live service claim.

## Success Criteria

Every FR has an exercising acceptance path, qualified on the platform cohort it
claims. Every source module is classified and every target module has an enforced
import/public-surface contract. Installed SDK and development-host artifacts work
without a private source checkout. Consumer outcomes stay unchanged across both
repositories. Application delivery requires no dependency installation.
Candidate cohorts pass
required application evidence before rollout; shared-fleet capacity and graph
integration claims name their measured workload, provider and authority scope.
The actual checks, rather than documentation alone, prove boundary,
shape, and test-count ratchets before dependent feature implementation.
