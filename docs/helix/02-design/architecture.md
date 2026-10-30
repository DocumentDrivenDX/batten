---
ddx:
  id: batten.architecture
  type: architecture
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: batten.boundary-audit
      kind: informed_by
    - id: batten.concerns
      kind: informed_by
---

# Batten architecture and proposed module split

## Scope

Batten has a platform-neutral application core and independently installed
platform modules. This is the proposal for the owner's first review. It covers
PRD FR-1–41. The composition/hosting packet elaborates the owner-selected
next design slice; migration and product code still require build authorization. The [boundary audit](../00-discover/current-state-inventory-boundaries.md)
precedes this target model.

**Pure core has zero ontology-specific capabilities.** Its capabilities are:
declaration handling, admission, authorization, operation dispatch, component
lifecycle/dependencies, background-work coordination, confirmation, and audit.
These use generic component and capability contracts. They import no ontology
type, query language, relationship model, schema registrar, or ontology provider.

An ontology provider is a Batten platform module, just as a table or model
provider is. Application data and ontology schema remain native upstream meaning;
the core preserves their opaque versioned declarations and invokes the owning
module's validator. A required component with no suitable provider is refused.

## Level 1: System Context

| Element | Type | Purpose | Protocol |
|---------|------|---------|----------|
| Application author | User | Declare native structures, behavior, and UI | Installed SDK/CLI |
| Host integrator/operator | User | Supply platform modules, identity, configuration, and approvals | Public host API |
| UMF and Weft | Platform library | Native schemas, compiler, typed access, query compilation | Public versioned library APIs |
| Arras | Platform library | Ontology provider and native reader/action semantics | Public library API |
| Tether | Platform library | Agent execution and durable session semantics | Public async API |
| UMF saga vocabulary/executors | Upstream semantics | Saga declaration and qualification; Batten supplies binding only | Exact qualified upstream profile |
| ux-builder | UI platform | Design-first artifacts, components, tokens and audits | Optional public adapter and pinned artifacts |
| Databricks, Lakebase, model gateway | Platform services | Governed data, storage, external jobs, models | Owning adapter APIs |
| Browser and MCP client | User surface | Reach declared operations and resources | Host bridge/MCP |

## Level 2: Container Diagram

| Container | Technology | Responsibilities | Communication |
|-----------|------------|------------------|---------------|
| Embedding host | Python 3.11+; optional FastAPI/ASGI | Composition, admission, dispatch, lifecycle | Public core API and injected ports |
| Worker | Python 3.11+; OS process containment | Owner-scoped application execution | Bounded capability-scoped messages |
| Optional ux-builder adapter | Preserve upstream design artifacts; bind controls/context through portable client | CONTRACT-005 | Public browser client and pinned public ux-builder packages | Core Python imports, copied design system/blueprint, shell internals |
| Browser client | Browser JavaScript; TypeScript build via Bun | Permission-contained screen/view bridge | Host-owned messages and operation calls |
| Local development supervisor | Python 3.11+; uv; PostgreSQL 18 helper | Installed-artifact author workflow and cleanup | Public host/platform APIs only |
| Application state | PostgreSQL 18 or Lakebase PostgreSQL 18 | Tables, durable schedules and lifecycle state | Owned native adapter |
| External compute/resources | Databricks APIs and configured gateway | Warehouse, files/search, jobs/pipelines, models | Owning platform module |

```mermaid
flowchart TB
  App[Application declarations and operations] --> Core[Portable contracts and runtime]
  Browser[Browser / MCP adapters] --> Core
  Core --> Ports[Core-owned capability and lifecycle ports]
  Ports -. injected implementations .-> Modules[Installed platform modules]
  Modules --> UMF[UMF / Weft]
  Modules --> Arras[Arras ontology provider]
  Modules --> Tether[Tether agent execution]
  Modules --> Services[PostgreSQL 18 / Databricks / gateway]
  Core --> Broker[Worker transport]
  Broker --> Worker[Owner-scoped worker]
  Dev[Development composition root] -. wires public APIs .-> Core
  Dev -. wires public APIs .-> Modules
```

Solid arrows show logical interaction, not a license for runtime imports from
core to adapters. Dashed arrows show composition-owned injection.

## Module Boundaries

**Source Applicability**: source; Batten owns independently written Python modules
and a browser client. Paths below are proposed import packages, not assertions
that source files already exist. The namespace root performs no eager re-exports.

`C` means `batten.contracts`; `R` means `batten.runtime`. Exact import roots,
public-surface checks, and failure rules are in CONTRACT-002.

| Module | Responsibility / Owned Types | Public API | Allowed Dependencies | Forbidden Dependencies |
|--------|------------------------------|------------|----------------------|------------------------|
| `batten.contracts` | Actor, component/capability references, operation declarations, generic outcomes, provider protocols | Declaration/value types and provider SPI, CONTRACT-001 | Python stdlib only | All other Batten modules, frameworks, native drivers, ontology/data types, host applications |
| `batten.runtime` | Generic admission, permission decisions, dispatch, dependency lifecycle, queue coordination, confirmation, audit policy | `create_host`, `Host`, `HostServices`, CONTRACT-001 | C and stdlib | Every adapter, testing/tooling, ontology-aware code, concrete HTTP/DB/model types |
| `batten.packaging` | Wheel metadata, artifact verification, digest, dependency checks, CLI, explain/docs | `inspect_artifact`, `verify_artifact`, author command surface | C, stdlib, `packaging`; uv/pytest as explicit build/test tools | Runtime construction, platform adapters, legacy source imports, runtime package installation |
| `batten.testing` | Portable doubles, outcome recorders, reusable public-port conformance | `TestHost`, doubles and conformance runners | C, R, stdlib; pytest only at test-runner boundary | Production adapters, host internals, compiler or SQL simulation claiming native equivalence |
| `batten.umf` | Native application/module/UI UMF validation, metadata projection, typed procedural and saga-reference binding | CONTRACT-003 validation adapter; upstream native targets | C and public UMF APIs | Copied envelope/action/saga compiler, concrete saga engine, host internals |
| `batten.hosting` | Typed profile resolution, trusted factory composition, ownership/placement binding | CONTRACT-004 `start_plan` | C, R; selected public factories injected; settings dependencies at composition | Eager unselected providers, private host discovery, automatic installs |
| `batten.tables` | Native UMF component binding, upstream compiler/typed-access integration | `TableComponent`, `TableProvider`, native artifact validation | C and public UMF/Weft APIs | Copied compiler/planner/parser/RLS emitter, native driver, legacy-format adapter |
| `batten.workers` | Transport, signed authority/owner envelope, process supervision, limits and shutdown | `WorkerExecutor`, `WorkerPolicy`, lifecycle interface | C, R, stdlib/OS interfaces | Host app internals, database credentials, platform SDKs, automatic service construction |
| `batten.postgres` | PostgreSQL 18 execution, owned/borrowed sessions, identity/pools, durable state, messaging provider and native migration execution | `PostgresServices`, `ConnectionSource`, CONTRACT-007 provider, explicit maintenance API | C, public `batten.messaging` in messaging provider, stdlib, `psycopg` | Databricks/gateway SDKs, upstream compiler duplication, UI, host app internals |
| `batten.messaging` | Scoped channels/subscriptions, payload profile references, settlement protocols and validation | CONTRACT-007 `Channel`, `Subscription`, `Payloads`, `for_resource`, `payloads` | C and stdlib; codecs/providers injected | Runtime internals, native drivers, broker SDKs, copied UMF codecs/action engines, host app internals |
| `batten.lakebase` | Lakebase endpoint/role/credential integration and qualification | `LakebaseAuthority`, public authority/session factory | C, stdlib, Databricks SDK | Generic SQL executor duplication, host environment reads, other adapter internals |
| `batten.databricks` | Warehouse choice, UC files/search/grant reporting, jobs/pipelines, lineage and artifact store | `DatabricksServices`, module-specific resource clients | C, stdlib, Databricks SDK | PostgreSQL execution, model/session loop, host app internals |
| `batten.gateway` | Gateway completion/embedding translation, aliases, budgets, attribution | `GatewayModels`, configured client factory | C, stdlib, `httpx` or injected supported client | Agent loop, concrete model choice in declarations, unrelated platform adapters |
| `batten.arras` | Ontology declaration validation/registration, reads/actions, links, receipts, retirement dependencies | `OntologyProvider`, module-owned ontology client/types | C and public Arras/UMF APIs | Core ontology special cases, private store access, duplicate ontology engine |
| `batten.tether` | Agent/session integration and operation-to-tool binding | `AgentProvider`, session/tool integration | C and public Tether APIs | A second agent loop, private Tether modules, concrete storage owned by another adapter |
| `batten.asgi` | HTTP and FastAPI route/gate mapping | `create_app`, route adapter and actor binding | C, FastAPI/Starlette/ASGI types | Concrete data/model providers, host app construction/private dependencies |
| `batten.mcp` | Operation-derived tools and resources; local stdio transport | `serve_stdio`, tool/resource adapters | C and public MCP SDK | Admin-tool exposure, private host discovery, remote-token forwarding, agent-loop ownership |
| `batten.dev` | Local composition, typed file config, fake identity, PostgreSQL lifecycle, supervisor/logging | `run_project`, `stop_project`, `project_status` | Public APIs of the preceding modules; uvicorn, Pydantic Settings, PostgreSQL 18 helper | Any private API, importing a consuming application, source-checkout discovery, new environment names |
| Browser client | Frame calls, navigation/focus, views and downloads; optional host-side bridge implementation | `AppHost` and host bridge API | Browser APIs; TypeScript/Bun/Playwright for build/verification only | Python objects, shell internals, runtime Bun/Node APIs, arbitrary network credentials |

**Integration Owners**: UMF application/saga metadata → `batten.umf`;
ux-builder → optional browser adapter; typed host profiles → `batten.hosting`;
UMF/Weft → `batten.tables`; PostgreSQL →
`batten.postgres`; Lakebase authority → `batten.lakebase`; Databricks resources →
`batten.databricks`; models → `batten.gateway`; ontology → `batten.arras`;
agent sessions → `batten.tether`. Each translates provider representations at
its public boundary. Core component payloads preserve unknown extension content;
they do not become a competing schema language.

**Construction Policy**: the embedding host's composition root, or `batten.dev`,
constructs concrete modules. For example, it injects Lakebase authority into the
PostgreSQL service and native compiled artifacts into its execution port; neither
adapter imports the other's implementation. Core constructs no concrete adapter.
Module exports and required capabilities are registered explicitly by the host.
Application declarations cannot install or replace a privileged platform provider.
`TestHost` wraps the real portable runtime with doubles; it does not reimplement
admission, permissions, or dispatch as a second test-only host.

**Boundary Check**: the specified entry point is
`uv run python scripts/check_boundaries.py --base HEAD`, with CONTRACT-002's
per-module allowlists, public-export checks, and negative controls. It will be
implemented only after this review. Documentation validation is not evidence
that an import gate already executes; dependent source work requires that gate.

## Deployment

| Component | Infrastructure | Instances | Scaling | Backup / Recovery |
|-----------|----------------|-----------|---------|-------------------|
| Local host/supervisor | Loopback process and PostgreSQL 18 helper | One project session; identity fixtures explicit | Operator-set worker and resource bounds | Persistent project database; awaited shutdown and stale-process reconciliation |
| Embedded host | Operator's Python/ASGI service, including Databricks Apps | Host-owned topology; no invented fleet size | Host/operator policy | Host-owned durable state/backup; qualified restart/recovery checks |
| Worker | Owned child process | Per application/owner scope within explicit caps | Demand, idle retirement, circuit/backoff | Revoked capabilities; stop/drain; generation-aware restart |
| Browser client | Host-served approved resources | Per user view | Host HTTP service | Re-read/reverify immutable artifact; no durable browser authority |
| Platform services | PostgreSQL 18, Lakebase, Databricks, gateway | Platform-owned | Platform-owned limits | Native backup/recovery and lineage, verified for each claimed cohort |

The SDK does not provision operator infrastructure. No deployment, remote creation,
dependency installation, or operational credential access is part of this review.

## Composition and host profiles

CONTRACT-003 separates immutable application requirements, installed module
metadata and effect-free assessment. CONTRACT-004 binds the result to local,
standalone or embedded hosting with independent in-process, child-process or
qualified remote-worker placement. Providers/resources are selected explicitly;
application intent does not change between profiles. Remote placement remains
unsupported until its transport and recovery obligations are qualified.

The public browser client is portable. CONTRACT-005’s optional ux-builder
adapter preserves original blueprint/assets and maps controls to native targets.
A headless closure imports no UI packages. `batten.umf` converts exact native
validation results to core metadata; generic core does not parse ontology or saga
semantics. `batten.hosting` builds services through a trusted catalog of selected
public factories, after plan verification. No native saga engine is selected.

### Semantic interaction composition and local implementation

The authoring progression is manifests/UMF/extensions, then local Python and/or
TypeScript, then exceptional platform dependencies. CONTRACT-003 owns dependency
admission and CONTRACT-005 owns control/renderer metadata. ux-builder owns semantic
control definitions and composition slots; Batten binds their data/actions and
preserves source artifacts. No second layout or workflow engine enters core.

The operation/outcome boundary is independent of presentation. Browser and terminal
clients implement separate scoped host contexts; the existing browser client keeps
its runtime/import restrictions. Renderer selection adds an independent presentation
choice to capability, hosting and placement. Terminal client packaging and runtime
remain open until a qualified dependency-free implementation or approved platform
extension is selected. No new framework is chosen here.

Local detailed controls are application code, not privileged provider modules.
They use supplied primitives, ordinary language facilities and explicitly exposed
platform APIs. A new dependency changes the platform closure and needs explicit
owner approval and host admission. Existing platform modules keep their reviewed
dependencies. Headless applications import neither graphical nor terminal UI code.


## Data Flow

Illustrative contract flow, not an observed Batten runtime:

```mermaid
sequenceDiagram
  actor Author
  participant Host as Public host API
  participant Core as Portable runtime
  participant Provider as Ontology provider module
  participant Arras as Arras platform
  Author->>Host: Admit application with required component
  Host->>Core: Verified declaration and injected module registry
  Core->>Provider: Validate/prepare declared component
  Provider->>Arras: Native module validation/registration
  Arras-->>Provider: Native result or bounded refusal
  Provider-->>Core: Capability readiness and dependency references
  Core-->>Host: Admission outcome
  Author->>Host: Invoke declared operation as actor
  Host->>Core: Typed call and verified actor
  Core->>Core: Authorize and confirm when required
  Core->>Provider: Invoke capability with scoped authority
  Provider->>Arras: Native reader/action call
  Arras-->>Provider: Receipt / data / safe error
  Provider-->>Core: Module-defined result
  Core-->>Host: Authorized outcome and safe audit
```

Core can order and retire providers through generic dependency references. It
does not inspect type relationships; the ontology module supplies the applicable
dependency/refusal result. Failed required preparation prevents readiness.

## Quality Attributes

| Attribute | Target | Strategy | Verification |
|-----------|--------|----------|--------------|
| Ontology independence | Zero ontology-specific core imports or vocabulary-driven branches | Module-owned schemas and generic capability/dependency contracts | Import checks plus semantic review of core public types and dispatch |
| Host independence | Zero private consuming-host imports | Public lifecycle and injected services | Installed-artifact-only host and negative import controls |
| Shape | CONTRACT-002 ceilings only decrease | Global edit/local/hook/CI gate | Actual over-limit and forbidden-edge controls |
| Test discipline | First reviewed measured suite establishes ceiling; then only decreases | One primary test per behavior, no disguised growth | Function/case census and coverage review |
| Behavior preservation | Every FR has an observable acceptance path | Native/double/worker/browser/deployed evidence kept distinct | Scoped qualification matrix and consumer outcomes |
| Latency/recovery | Targets supplied by Erik LaBianca and platform operators | Measure work and native plans before selecting budgets | No invented service-level objective or unsupported recovery promise |

## Decisions and Tradeoffs

| Decision | Direction | Rationale | Follow-up |
|----------|-----------|-----------|-----------|
| ADR-001 | Platform modules around an ontology-neutral core | Keeps platform semantics out of admission/dispatch | Review module/public API map |
| ADR-002 | Native upstream UMF and typed access | Settled owner ruling; no duplicate compiler | Qualify complete upstream lifecycle/policy matrix |
| ADR-003 | Core plus separate platform/tool/development wheels | Install and test actual dependency closures | Review distribution/cohort policy |
| ADR-004 | One public asynchronous host API | Replaces private construction/config/database/logging reach | Review CONTRACT-001 |
| ADR-005 | SDK series independent of host release | Declare compatibility without coupling every release | Review capability and release matrix |
| ADR-006 | Typed files authoritative, environment fallback only | Settled owner ruling | Review existing-host fallback mapping later |
| ADR-007 | Shape and test-count ratchets | Prevent growth from erasing modularity | First executable gate slice after review |

Owner decisions remain in `../01-frame/decision-points.md`. An ontology-provider
module is the proposed shape; special application-plugin privileges, host identity
exceptions, and storage exemptions are not inferred from that shape.

## Messaging boundary

[CONTRACT-007](contracts/CONTRACT-007-messaging.md) owns named channels, durable
subscriptions, exact UMF payload profiles and explicit delivery settlement.
[ADR-011](adr/ADR-011-postgres-first-messaging.md) selects the first PostgreSQL 18
provider. Its `batten.postgres.messaging` adapter owns logged messages, subscription
deliveries, deduplication and retained settlement records. Short claim transactions
end before application handlers execute. The composition root injects trusted
connection/authority and separately qualified codecs through public protocols.

Generic runtime coordinates the existing durable-work service using admitted
provider handles; messaging adds no second scheduler or saga executor. Declared
operations still enter through `Host.invoke` with current authorization and required
confirmation. Message headers convey correlation, never operation authority.
Future broker adapters must satisfy an explicit capability profile; no native
offset/queue URL enters application APIs. UMF schemas define business payloads;
no new messaging vocabulary or universal instance codec is assumed.
