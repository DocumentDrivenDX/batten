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
