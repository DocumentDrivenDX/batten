---
ddx:
  id: CONTRACT-001
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-004
      kind: informed_by
    - id: ADR-005
      kind: informed_by
---

# Public host API contract

**Contract ID**: CONTRACT-001
**Type**: library boundary
**Version**: proposed v1

## Purpose

Define the proposed public lifecycle/configuration/service boundary used by
development and deployed embedders. This contract replaces private host-helper
coupling; it is independent of any reference application's API or implementation.

## Scope and Boundaries

- In scope: factory, lifecycle, service registration, resource ownership,
  component readiness, invocation, safe outcomes, and compatibility.
- Out of scope: exact platform-specific data schemas, ontology semantics,
  wire transport, HTTP routes, and organization approval policy.
- Owner: Batten; Erik LaBianca owns review of this proposal.

## Normative Surface

All public I/O MUST be asynchronous. Factories and immutable declarations MAY
be synchronous. The module paths and signatures below are proposal contracts,
not claims of delivered APIs.

| Element | Type / Shape | Required | Rules |
|---------|---------------|----------|-------|
| `batten.runtime.create_host(config, services)` | `(HostConfig, HostServices) -> Host` | yes | Pure factory; no I/O, environment read, concrete adapter import, or mutable global registration. |
| `Host.start()` | `async -> None` | yes | Starts owned resources and prepares required components; succeeds only when required capabilities are ready. Calling while running is idempotent. |
| `Host.aclose()` | `async -> ShutdownReport` | yes | Seals admission, revokes active capabilities, drains/cancels work under configured deadlines, closes owned resources in reverse dependency order. Repeated close is safe. |
| `Host` context manager | `async with -> Host` | yes | Entry awaits start; exit awaits close. A failed start runs owned-resource cleanup and cannot report ready. |
| `Host.admit(artifact)` | `async (ArtifactRef) -> AdmissionOutcome` | yes | Obtains verified metadata through the artifact service; checks SDK/capabilities/policy before execution and prepares required modules. |
| `Host.invoke(call)` | `async (OperationCall) -> OperationOutcome` | yes | Dispatches only an admitted declared operation under verified actor/capability, current permissions and required confirmation. |
| `Host.readiness()` | `async -> ReadinessReport` | yes | Reports host state and per-component safe outcomes; readiness is observation, not a platform support assertion. |
| `HostConfig` | Frozen typed value | yes | Contains limits, ordered component selections, artifact/admission policy references, and resolved application settings. No raw credential values. |
| `HostServices` | Frozen named protocol bindings | yes | Identity, artifact admission, execution, durable work, audit, diagnostics, and component registry. No introspection of a consuming host's objects. |
| `ServiceBinding` | `{service, ownership}` | yes | Ownership is `borrowed` or `owned`. A borrowed service MUST NOT be closed or have its global configuration changed by Batten. |
| `ComponentRegistry` | Host-registered providers keyed by capability and interface version | yes | Registration is explicit at composition; plugin metadata cannot install a provider. Duplicate/ambiguous providers refuse construction. |
| `ComponentDeclaration` | `{kind, version, required, payload}` | yes | Module-owned, versioned payload preserved losslessly. Core neither interprets ontology/data meaning nor discards unknown extension content. |
| `CapabilityProvider` | Public generic prepare/invoke/retire interface | per selected component | Declares provided/required capability IDs; validates its own payload; reports readiness and generic dependency references. Concrete native clients stay private. |
| `OperationCall` | Declared operation identity, validated input reference/value, verified actor reference, capability, confirmation reference | yes | No raw connection, host object, credential, or driver exception crosses the application boundary. Input/output validation uses the owning declared schema validator. |
| `ShutdownReport` | `{state, retained_resources, outcomes}` | yes | State is `closed` only when owned cleanup has completed. Otherwise `draining` names safe resource IDs and the cleanup outcome. A timeout never claims completed shutdown. |

Host lifecycle states are `new`, `starting`, `running`, `draining`, and `closed`.
Invocation is admitted only in `running`. A closed host is not restarted; create
a new instance. Shutdown deadlines come from resolved typed configuration, not
hardcoded invented values.

The provider interface is:

- `prepare(declaration, context)` is asynchronous and returns a component handle,
  provided capability IDs/versions, dependency references, and readiness outcome.
- `invoke(handle, call)` is asynchronous and returns the module-defined outcome.
- `retire(handle, context)` is asynchronous and returns retired or a safe dependency/
  authority refusal; it does not imply deletion of durable data.
- Required capabilities and component dependencies form an acyclic graph. Core
  orders preparation and retirement; the provider supplies domain-dependent
  references and validates native compatibility. Capability IDs are opaque to core.

An ontology module MAY supply ontology-specific typed clients, schema declarations,
and operations from its own public package. Core MUST NOT define `OntologyType`,
`OntologyPort`, a query language, an ontology schema version, or a special
ontology load-order branch. Schema validation and relationship dependency checks
are the module's responsibility; generic readiness/dependency ordering is core's.

Development composition MUST use this same host interface and public platform
factories. Its own `run_project`, `stop_project`, and `project_status` interfaces
supervise the project process and owned PostgreSQL 18 instance. Fabricated identity
is explicit, loopback-only, and not accepted as deployed identity evidence.

### Shared application execution

PRD FR-43/44 require shared services without merged authority. `Host.admit` MUST
check required application evidence under CONTRACT-002. `Host.invoke` MUST bind
application/actor identity, declared capability and authorized target, rechecking
current access for cross-application graph calls. A graph relationship MUST NOT
confer a grant. CONTRACT-009 governs module-owned discovery and service bindings.
The host MUST verify binding evidence, exact consumer/export/deployment revisions
and current authority on use. Discovery does not admit code or provision resources.
Interactions MUST use reviewed public provider interfaces, including qualified
owner-published table access; no private object or raw shared database connection
crosses the application boundary.

Resolved limits MUST bound each application's and owner's concurrency and resource
use; configured scheduling MUST preserve fairness. Revocation and application
shutdown MUST preserve other applications' borrowed services and allocations.
Host-owned diagnostics MUST attribute admission, invocation, refusal and capture
loss to safe application/artifact/cohort identities. Required telemetry MUST NOT
be disabled by application settings. Exact telemetry failure policy, resource
accounting and graph-operation surfaces require contracts before source work.
The command/query and attribution obligations below apply to every selected provider.
These requirements do not promise hostile-code isolation or measured fleet capacity.

OpenTelemetry (OTel) is the required instrumentation model. Its baggage carries
propagated correlation metadata; it is not an authentication channel.

### Default command/query execution

- The exposed operation model MUST default to Command Query Responsibility
  Segregation (CQRS). Declarations MUST distinguish commands from queries;
  adapters MUST preserve that intent across routes, tools, UI, events and hooks.
- Queries MUST NOT mutate business state or publish business effects. Necessary
  telemetry, access audit and bounded cache bookkeeping do not turn a read into
  a business command. A provider unable to enforce a required query boundary
  MUST refuse it before effects rather than silently allow a write.
- Commands MUST pass the same declared input, capability, current authorization
  and confirmation gates on every surface. Database writes, message publication,
  storage mutations and agent-triggered effects cannot bypass this path through
  a local hook or raw native client. Existing exceptional SQL and maintenance
  paths MUST remain explicitly authorized, attributed and audited.
- Command identity MUST remain stable across retries of the same logical command;
  attempts MUST remain distinguishable. Reuse with changed intent, payload or
  authority MUST refuse. Provider-qualified deduplication and reconciliation
  govern recovery; CQRS promises neither exactly-once delivery nor a transaction
  across resources. Unknown outcomes MUST NOT be retried as fresh commands.
- Queries MAY return a projection with declared freshness/consistency limits;
  command success MUST NOT imply immediate visibility in a separate projection.
  Batten MUST preserve upstream UMF action, receipt and transaction semantics.

### Trusted attribution and causal continuity

- The host MUST establish attribution from authenticated identity or explicit
  authorized non-user authority. Caller input, message headers and OTel baggage
  MUST NOT establish a principal, grant, role or delegation.
- Invocation context MUST retain the initiating user when present, effective
  execution principal, authorized delegation, application/artifact/cohort,
  operation and resource identity, logical run/command and distinct attempt
  identity. Approval authority MUST remain distinguishable from the requester
  and executor. Autonomous work MUST name its service/application authority;
  it MUST NOT invent a user or impersonate the approving human.
- Background jobs, schedules, messaging delivery/redelivery, worker placement,
  agent/tool calls and cross-application calls MUST preserve causal origin.
  Execution MUST recheck current grants and bounded delegation, including after
  revocation; retaining the original user identity confers no continuing right.
- Propagation across process or durable-message boundaries MUST be integrity
  protected by the selected trusted transport/store and scoped to its audience.
  Imported remote context MUST be treated as untrusted correlation until verified.
  Concurrent requests, reused workers and pooled database sessions MUST NOT leak
  actor, delegation or trace context between calls; cleanup MUST survive failure
  and cancellation. No user credentials are persisted with causal context.

### System instrumentation and durable audit

- Every database, messaging, AI gateway, storage, search, secret-resolution,
  worker, graph and other system interaction MUST have host/provider-owned
  OTel instrumentation, including reads, refusals and failures.
  Applications MUST NOT disable required capture or bypass instrumented ports.
  This includes supporting lifecycle/control interactions under explicit host
  authority, even where no business command or human initiator exists.
- Instrumentation MUST correlate traces and logs with trusted application,
  operation, run/attempt and permitted user/effective-principal references.
  Metrics MUST use bounded dimensions; per-user identity MUST NOT become an
  unbounded metric label. Existing native instrumentation SHOULD be reused
  without duplicate capture; missing coverage MUST be supplied at the adapter.
- Providers MUST apply the strongest supported native user/delegated attribution
  consistent with current grants. Batten correlation and native enforcement MUST
  be reported separately. A service-principal call MUST retain its actual native
  principal and initiating-user correlation; a tag MUST NOT claim user execution.
  A required unavailable native identity capability MUST refuse before effects.
  Otherwise the exact native-attribution gap MUST remain observable.
- Messaging MUST correlate publish, delivery, retry and consumer outcomes.
  AI interactions MUST correlate agent/tool/model invocations, native request
  references and available usage/cost accounting without logging prompts,
  completions or private payloads by default. Unsupported accounting stays unknown.
- Durable audit MUST retain authorization/approval decisions and attempted,
  completed, refused, failed, cancelled or uncertain effects, plus attributable
  reads/access. It MUST be protected against application alteration/deletion and
  queried/exported only under current scope and access policy. Audit retention,
  integrity protection and operator access MUST be explicitly contracted.
- Trace sampling MUST NOT sample away required audit. Trace context MAY be absent;
  logical operation/run/attempt identity MUST still support reconstruction.
  Capture loss, overflow, exporter outage and audit-write failure MUST be visible.
  A required audit precondition failing before an effect MUST block admission to
  that effect. Failure after a possible effect MUST preserve uncertainty and
  reconciliation, never claim rollback or successful audit persistence.
- The host MUST define bounded buffering/backpressure and loss policy before
  execution, separating diagnostic-export failure from required audit capture.
  Neither application settings nor an outage may silently downgrade required
  evidence. Cross-service atomic audit/effect persistence requires exact provider
  evidence; it MUST NOT be inferred from a local database transaction.
- Capture MUST minimize identity disclosure and redact before export. Credentials,
  raw SQL parameters, message bodies, prompts and inaccessible resource names
  MUST NOT enter telemetry by default. External propagation MUST allowlist safe
  correlation; user identity MUST NOT be placed in unrestricted baggage.

OTel conceptual grounding: [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
and [sensitive-data handling](https://opentelemetry.io/docs/security/handling-sensitive-data/).
These are unversioned upstream guidance. Exact OTel API/SDK, semantic-convention
and integration versions, local event mappings, capture/query schemas, bounds,
ordering/continuation and recovery remain required focused contracts before
source implementation; no new wire schema or exporter is selected here.

### Replacements for development-host coupling

| Responsibility | Public owner |
|----------------|--------------|
| Host application construction and registry wiring | `create_host`; `batten.asgi.create_app(host, identity)` |
| Worker defaults and child configuration | `batten.workers.WorkerPolicy` supplied through `HostConfig` |
| Permission/settings interpretation | Core declaration/policy types and composition's typed configuration resolver |
| Embedded database opening and shutdown | Owned `batten.postgres` service plus host-dev's PostgreSQL 18 helper session |
| Signal, logging and diagnostic setup | `batten.dev` supervisor and injected diagnostic sink; host async lifecycle |
| Source lookup/import-path mutation | Installed public packages; no checkout-discovery replacement |

## Precedence and Compatibility

Owner rulings and PRD govern scope; this contract governs the proposed public
surface. ADR-005 governs `sdk` compatibility. Core and all installed module
capability interfaces are checked independently of embedding-host product versions.
An unknown required component is `capability_unavailable`; an unknown optional
payload is retained and has no side effects.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| Call before running or during shutdown | `host_not_running` | After ready/new host | No operation executes. |
| Missing/incompatible required provider | `capability_unavailable` / `capability_incompatible` | After config/cohort repair | Application is not ready; unrelated admitted applications follow host failure policy. |
| Core/provider dependency cycle | `component_cycle` | No | Fix declared composition; do not guess an order. |
| SDK mismatch | `sdk_mismatch` | No | Rebuild or use a compatible cohort before import. |
| Permission or actor refusal | `denied` | After access changes | Record safe identifiers and reason; no provider effect. |
| Invalid component or operation input | `invalid` | Correct input | Module-owned validation identifies safe field names. |
| Lifecycle deadline exceeded | `timeout` with retained-resource report | Explicit reconciliation | Preserve actual outcome; never imply resources have stopped. |

Provider failures return safe domain outcomes; private exception bodies never
become public errors. Cancellation after a possible effect MUST retain uncertainty
until the owning provider resolves it; the host cannot manufacture a successful rollback.

## Examples

Illustrative API usage; no implementation is authorized by this example:

```text
services = HostServices(explicit reviewed protocol bindings)
host = create_host(resolved_config, services)
async with host:
    admission = await host.admit(verified_artifact_reference)
    outcome = await host.invoke(actor_bound_declared_operation)
report = await host.aclose()  # repeated close remains safe
```

## Non-Normative Notes

No ontology-specific core capability is needed. A generic component dependency
graph is enough to know that a provider must be ready before its consumer and
cannot retire while a dependent still needs it. The ontology module explains
why a native relationship creates that dependency.
