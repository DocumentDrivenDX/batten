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

Batten is an open-source application SDK in the Novirhyza family. Authors compose native UMF declarations for data and behavior, with typed
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

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| App-specific integration effort | Baseline and target supplied by Erik LaBianca | Compare custom wiring for a fabricated application across hosts. |
| Developer iteration effort | Baseline and target supplied by Erik LaBianca | Observe build/admit/update steps and elapsed time. |
| Boundary independence | No private host dependency | Import census and installed-artifact qualification. |

### Non-Goals

Host identity-provider deployment, infrastructure provisioning, a marketplace for
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

- **FR-39** — UI applications integrate with ux-builder design artifacts and its
  public component/theme/audit tooling. Stable bindings connect UI controls to UMF
  metadata and Batten operations across local, standalone and embedded hosts.
  Headless applications omit UI dependencies. Host authentication, confirmation
  and resource containment apply equally to generated and custom screens.

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
- **FR-21** — Declared Databricks jobs and pipelines support reviewed deployment
  and governed reconciliation, staged verified artifacts, least-privilege job
  identity, platform scheduling, enable/pause/cancel, observation, accounting,
  and lineage drift reporting. Limits that cannot bind externally started work
  are disclosed in the confirmation.
- **FR-22** — Applications trigger their declared jobs and non-admin event operations,
  inspect authorized run handles, and read durable run records. Event work uses
  explicit application authority and cannot impersonate an interactive caller.

### Subsystem: Artifact delivery and lifecycle

- **FR-23** — Authors build self-describing wheels containing declarations,
  resources, digests, and tests. Hosts validate SDK series and the baked-in
  dependency cohort before plugin code executes; runtime dependency resolution
  and vendored platform libraries are refused.
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
  errors. Files remain within the application's storage scope.
- **FR-27** — Namespaced audit and declared telemetry cover admission and execution
  across all surfaces. They carry safe identifiers/counts/outcomes, report capture
  limits, and distinguish offline, native, browser, and deployed evidence.
- **FR-28** — Authors declare required platform grants; operators inspect their
  resolved status and apply them through the platform owner. Applications do not
  acquire grant authority by declaring a requirement.

### Subsystem: Author tooling and qualification

- **FR-29** — Shared conformance checks validate declarations, gates, resources,
  artifacts, platform boundaries, compatibility, and documentation against observable behavior.
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
  placement; unavailable combinations refuse before effects. Separated workers
  require independently qualified transport and recovery.
- **FR-37** — Authors assess composition without starting services or executing
  application/provider code. Results explain missing or ambiguous capabilities,
  cycles, incompatibilities, unknown semantics and placement limits with safe
  identifiers. An eligible plan is bound to exact inputs and is not runtime readiness.
- **FR-38** — Saga-enabled applications use UMF-owned saga declarations and exact
  executor capabilities. Batten exposes scoped invocation, observation and recovery
  bindings while preserving UMF outcomes and uncertainty. Missing upstream support
  blocks the affected component rather than invoking a Batten-specific fallback.

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

## Success Criteria

Every FR has an exercising acceptance path, qualified on the platform cohort it
claims. Every source module is classified and every target module has an enforced
import/public-surface contract. Installed SDK and development-host artifacts work
without a private source checkout. Consumer outcomes stay unchanged across both
repositories. The actual checks, rather than documentation alone, prove boundary,
shape, and test-count ratchets before dependent feature implementation.
