---
ddx:
  id: CONTRACT-010
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: ADR-012
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
  schemas:
    - id: batten.platform.assets
      version: "0.1.0"
      title: Batten platform asset declarations
      path: docs/helix/02-design/schemas/platform-assets.schema.json
      schemaFormat: json-schema
---

# CONTRACT-010: Platform assets and deployment dependencies

**Contract ID**: CONTRACT-010
**Type**: asynchronous library and deployment boundary
**Version**: proposed 0.1.0; capability `batten.platform.assets/1`
**Related**: PRD FR-21/46; FEAT-009 CMP-18–22; ADR-012

## Purpose

Let applications carry deployment packages and consume externally managed assets
through a generic platform wrapper. Keep native bundle syntax, resource APIs and
deployment state inside the owning provider and operator deployment service.

## Scope and Boundaries

Optional `batten.platform` owns portable asset protocols and values. Core sees
ordinary capability requirements and assessment results, and imports no platform
asset or vendor types. Operators inject an admitted provider and deployment
authority; applications cannot construct that authority from declarations.

One manifest may combine app-managed packages with external requirements.
App-managed means release/deployment ownership, independent of CONTRACT-004's
owned/borrowed client lifetime. Closing a client or stopping an application MUST
NOT destroy persistent assets. Shared infrastructure remains operator-owned.

## Normative Surface

`platform-assets.schema.json` owns manifest shape. CONTRACT-003 owns ArtifactRef,
capability pins, original-byte inventory and plan canonical encoding. All IDs
compare exactly. Values are immutable; all I/O below is async.

### Declarations

An application MUST include exactly one platform manifest in its digest-covered
artifact inventory when requiring `batten.platform.assets/1`. Its capability
requirement ID MUST equal the manifest's `requirement` value. A trusted native
validator projects this relationship into composition evidence outside core.
The wrapper cannot install packages or fetch undeclared source.

| Element | Required | Meaning |
| --- | --- | --- |
| `manifest.requirement` | yes | Local capability requirement ID in the consuming application. |
| `manifest.packages` | yes, possibly empty | Managed packages with exact format pin, source inventory, entry artifact, declared output contracts and dependencies on local requirement IDs. |
| `manifest.requirements` | yes, possibly empty | Required or optional resources with exact interface pins, contract ArtifactRefs, consumer access and readiness profiles. |
| `package.sources` | yes | Complete original source closure, including native configuration, code, SQL and migrations; every item must also occur in the application inventory. |
| `package.outputs` | yes | Local output IDs paired with exact contract ArtifactRefs and interface pins. No implicit export of other native resources. |
| `requirement.access` | yes | Nonempty list of operations defined by the pinned interface; declarations request access but grant none. |
| `requirement.readiness` | yes | Exact profile pin and predicate ArtifactRef; owning validator interprets schema, freshness, initialization or other required conditions. |
| `requirement.source` | yes | Either local package/output IDs or an external release ArtifactRef plus output ID. External release records carry owner and provenance, never credentials. |

A provider format pin identifies a native package format, not an arbitrary command
or factory. Host policy chooses its interpreter from the installed cohort.
External release records describe published resource contracts and deployment
provenance; referencing one MUST NOT deploy, adopt or modify its assets.
An external release record MUST contain immutable `id`, `version`, `owner` and
`outputs` (the same output shape as packages). Trusted environment records MUST
map its ArtifactRef/output IDs to provider, environment and producer receipt IDs.
The deployment service verifies producer provenance and effective ownership;
an application-supplied owner label is not authoritative. Exact release pins
are compatibility identities, not an obligation to retain the producer's old
physical implementation; inspection must establish current compatible behavior.
Environment-specific workspace IDs, names and credentials stay in trusted typed
provider bindings. One immutable application can use different approved bindings.

Reject duplicate IDs, dangling references, conflicting owners and dependency
cycles before effects. A required dependency on an optional inactive resource
refuses. Every output MUST have a single lifecycle owner across managed state;
the deployment service checks ownership against trusted state before mutation.
Each source output MUST match the requirement's exact interface and contract
ArtifactRef. Readiness predicates and requested operations MUST be supported by
that interface's admitted validator and selected provider, or binding refuses.
Native code dependency closure needs separate platform admission under CONTRACT-003;
carrying a bundle does not authorize pip/npm installs on remote compute.

### Provider and operator interfaces

These signatures use immutable process-local values, not a new wire protocol.
The deployment service supplies `context` with verified initiating actor,
effective principal, application/environment scope, current authority, deadline,
finite byte/item/depth budgets and audit attribution. It supplies opaque native
bindings through injected services. No interface accepts credential literals.

| Call | Result | Rules |
| --- | --- | --- |
| `validate(manifest, artifacts, cohort, limits)` | validation evidence | Pure; no imports of application/native build code, network, environment reads or provider effects. Unknown relevant meaning refuses while retaining bytes. |
| `await plan(manifest, bindings, context)` | `DeploymentPlan` | Read-only live inspection; never part of pure composition assessment. Any native tooling that can run build hooks requires a separate admitted build stage. |
| `await apply(plan, approval, request_id, context)` | `DeploymentReceipt` | Explicit operator operation. Verify plan freshness, exact authorization and durable request identity before effects; refuse absent/stale approval. |
| `await inspect(receipt, context)` | `ResourceAssessment` | Recheck required contracts, readiness, current grants, ownership and drift without mutation. |
| `await recover(receipt, context)` | `DeploymentReceipt` | Read-only reconciliation of retained operation/native IDs. Further mutations require a fresh reviewed plan and approval. |

`DeploymentPlan` MUST bind application/manifest/source digests, exact provider,
format, validator and toolchain cohort, environment binding digest, observed state
revision, dependency receipts, finite limits, ordered changes, retained/deleted
assets and declared initialization/migration phases. Its hash uses CONTRACT-003
canonical encoding. Approval binds that hash and permitted changes under current
operator policy. Plans MUST NOT contain secrets or arbitrary shell commands.

`apply` MUST serialize conflicting changes within the ownership scope or reject
stale state. Persist request-to-plan identity before the first native effect.
Reusing a request ID with a different plan refuses; retrying the same request
returns or reconciles its original operation. A lost acknowledgement, timeout,
cancellation or partial apply MUST retain known effects and native operation IDs.
No exactly-once, atomic multi-resource apply or automatic rollback is implied.

`DeploymentReceipt` MUST include the plan hash, durable operation ID, observed
state revision, provider/cohort/environment identities, exact output-to-resource
bindings, dependency receipt identities, phase outcomes and unresolved effects.
Its state is `ready`, `failed`, `partial` or `unknown`. `ResourceAssessment` is
`ready`, `refused` or `unknown`, with observed contract/readiness evidence and
safe findings. Trusted records retain native IDs privately; app-visible results
contain scoped opaque bindings, safe IDs and reason codes only.
Receipts MUST be immutable, integrity-checked records from the trusted deployment
service, identified by ArtifactRef. Reconciliation emits a new receipt retaining
the original operation ID and previous receipt identity. Dependency plans refer
to exact receipts; old observations never substitute for current inspection.

Deploying a definition MUST NOT mark its outputs ready. Required initialization
or migration phases MUST be explicitly planned and authorized; successful
execution and predicate evidence are required before `ready`. No generic wrapper
translates a portable data model into guessed vendor DDL or pipeline semantics.
Native model generation belongs to qualified upstream/provider tooling.

### Runtime admission and retention

CONTRACT-003 static eligibility proves no live existence, grants or readiness.
CONTRACT-004 preparation MUST verify trusted receipts against the exact admitted
application, environment, provider and contracts, then perform current inspection.
Absent, stale, refused or unknown required evidence blocks readiness; optional
absence stays inactive. Receipt fields or application claims never grant access.
Invocation rechecks current authority through the existing runtime ports.
Runtime table, storage and job operations continue through their owning capability
interfaces. The deployment wrapper supplies scoped bindings and MUST NOT expose
native admin clients, arbitrary native commands or a universal resource executor.

Start/reload MUST NOT call `apply`, initialize, migrate or grant access.
App removal MUST retain persistent assets by default. Destruction, ownership
transfer, schema migration and production apply require their separately scoped
authorization. External dependents block destructive plans until resolved.
Reverting application code does not reverse data mutations or native effects.
Audit MUST preserve initiating user, delegation, effective deployer and operation
identity under FR-27; unsupported native attribution remains explicit.

## Precedence and Compatibility

Native resource and data semantics remain provider/upstream-owned. Exact interface
and contract pins are the initial compatibility rule; no inferred coercion or
latest-version lookup is allowed. Changed source, contracts, bindings, dependencies
or cohort invalidate affected plans and qualification evidence. Unknown provider
semantics are retained but cannot become eligible through shape validation alone.
This manifest is a companion artifact; it adds no vendor fields to UMF core or
CONTRACT-003's generic application shape. Extension registration is separate work.

## Error Semantics

| Condition | Code | Recovery |
| --- | --- | --- |
| Missing source, mismatched digest or unknown meaning | `asset_invalid` | Supply exact supported artifacts; no effects. |
| Missing provider/format/profile support | `asset_unsupported` | Select a qualified provider; no fallback. |
| Missing/ambiguous external binding or changed contract | `dependency_unavailable` | External owner repairs or publishes an explicitly adopted release. |
| Cycle or conflicting lifecycle owner | `ownership_conflict` | Resolve dependency/ownership; never silently adopt. |
| Changed observed state, bindings, pins or approval | `deployment_stale` | Inspect and replan; no stale mutation. |
| Missing/revoked actor or privilege | `asset_denied` | Reauthorize; no resource existence disclosure. |
| Timeout, cancellation or uncertain native outcome | `deployment_unsettled` | Retain receipt and reconcile; never blindly replay. |
| Deployed definition lacks usable outputs | `asset_not_ready` | Explicitly authorize required phase or repair predicate failure. |

## Examples

```text
Application review-queue requires capability batten.platform.assets/1.
Managed package prepare-reviews exports review-table and refresh-job contracts.
External release customer-data-v3 exports customer-table with requested read access.
prepare-reviews depends on customer-table; environment bindings resolve native IDs.
Operator plans, approves, applies and verifies initialization.
Host starts only after the required output contracts and current access pass.
Stopping review-queue closes its owned clients and retains both tables.
```

## Schema Basis

The companion schema reuses exact artifact and interface references from
CONTRACT-003. Inspected UMF core 0.10.0, extension registration, `umf.actions`
0.1.0 and the medical domain pack supply native identity and model/action meaning;
they do not establish deployment-package ownership, plans or resource receipts.
The source hashes and limits are in `platform-assets-schema-basis.json`.
Local additions cover deployment declarations only; native schemas and unknown
bytes remain upstream-owned. Shape validation does not qualify deployments.
