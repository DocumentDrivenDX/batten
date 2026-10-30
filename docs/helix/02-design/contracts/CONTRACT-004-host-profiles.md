---
ddx:
  id: CONTRACT-004
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: ADR-008
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
  schemas:
    - id: batten.composition.payloads
      version: "0.1.0"
      title: Batten composition payloads
      path: docs/helix/02-design/schemas/composition.schema.json
      schemaFormat: json-schema
---

# CONTRACT-004: Host profiles and execution placement

**Contract ID:** CONTRACT-004
**Type:** configuration and lifecycle boundary
**Version:** proposed 0.1.0

## Purpose

Bind one application to explicitly selected hosting, identity, resource ownership
and execution placement while retaining its application artifact unchanged.

## Scope and Boundaries

Batten owns profile interpretation and the existing CONTRACT-001 lifecycle.
Operators own provisioning, provider credentials, authentication and deployment.
Profile syntax describes choices; it does not establish live service behavior.

## Normative Surface

The `host` root in the local schema owns required fields and allowed mode/placement
values. `modules` pins installed module IDs/versions; `cohort` pins actual installed
wheel/upstream compatibility metadata. Selected versions MUST agree in both.

| Element | Type / Shape | Required | Rules |
| --- | --- | --- | --- |
| mode | `local`, `standalone`, `embedded` | yes | Composition/lifecycle owner; independent of provider and placement. |
| bindings | Schema `binding` entries | yes | Consumer ArtifactRef plus local requirement ID -> explicit provider/placement/ownership/resource/settings. Unique consumer/requirement binding; unknown keys preserved but rejected by semantic settings validation. |
| identity | Trusted identity binding ID | yes | Resolves from injected services, never from application claims. Fabricated identity allowed only for local, loopback-only composition. |
| resource | Opaque resource binding ID | per binding | Resolves through host-owned typed services. Carries no credential value, connection string or implicit authority. |
| ownership | `owned` or `borrowed` | per binding | Matches CONTRACT-001; borrowed services are never closed or globally reconfigured by Batten. |
| settings | Module-schema-validated object | per binding | Layered typed files per ADR-006; environment only existing explicit fallback. No new environment variables or secret literals. Resolve to immutable values once. |
| limits | Explicit positive finite configuration | yes | Lifecycle deadlines, resource caps and assessment budgets are supplied by host policy and typed owning schemas; missing required limits refuse. |
| placement | `in-process`, `child-process`, `remote-worker` | per binding | Must match module capability and host transport support. No silent relocation. |
| batten.hosting.start_plan(plan, services) | `async -> Host` | yes | Composition-root adapter constructs CONTRACT-001 Host after verifying the plan hash, original app/profile/cohort/evidence and trusted factory registry. Drift refuses before prepare/import effects. |

### Attribution across profiles and placements

Every profile MUST preserve CONTRACT-001 command/query, trusted attribution,
durable audit and OpenTelemetry obligations. Local fabricated identities exercise
the same propagation boundaries and MUST be marked as fixtures; they establish
no deployed identity evidence. Child/remote-worker bindings MUST preserve verified
origin and delegation across transport and recheck current authority at execution.
Host service or pooled database identities MUST remain distinguishable from users.
A profile MUST refuse execution when required attribution/audit capabilities are
missing; it MUST NOT substitute shared authority or silently disable capture.

### Service discovery and deployment bindings

CONTRACT-009 defines the selected ontology module's registry and resolution rules.
The host MUST bootstrap its trusted registry service from explicit configuration;
registry discovery cannot depend on resolving itself. Provider discovery produces
pinned evidence before effect-free assessment. A service binding uses the existing
exact consumer ArtifactRef/local requirement ID and opaque resource binding ID.
The host MUST validate the selected export, interface, profile, deployment and
resolution evidence before use. Catalog records and application metadata cannot
choose privileged factories or manufacture resource authority. Deployment changes
require new binding evidence and reassessment without changing semantic interface
identity. Credentials and private addresses stay in typed host configuration.
Graph-discovery hosts select `batten.arras`; other hosts MAY consume verified
explicit bindings without introducing an ontology dependency into portable core.

### Required local-development profile

Local hosting MUST support an explicitly configured stub identity provider,
one shared PostgreSQL 18 pgserver instance, direct UMF table access and Truss
on that same instance. A selected Tether capability MUST accept a host-supplied
model API binding through Tether's supported public adapter/provider boundary.

The composition root owns or borrows the pgserver instance exactly once. Each
consumer borrows its assigned connection source; closing one consumer MUST NOT
stop the shared server or invalidate another consumer's resources. Truss and
native tables retain their own schema/database, role and migration ownership.
Physical tables MUST have a single declared owner. Shared server placement grants
no cross-module access or cross-resource atomicity guarantee.

Stub identity MUST be an explicit local fixture mapping with fabricated actors,
roles and database principals. Requests still traverse ordinary Batten gates,
confirmation and native policy enforcement. A missing actor has no implicit
superuser/shared-identity fallback. The host MUST bind loopback only while stub
authentication is selected; standalone/embedded profiles MUST refuse it.

The model API address, model/profile, limits and optional credential reference
are host configuration resolved under ADR-006. Values MUST NOT appear in app
models, generated UI or diagnostics. Credentials are supplied only by the host's
scoped provider, not read from newly introduced environment names. A configured
unavailable/incompatible model API MUST return an explicit capability/provider
failure; it MUST NOT silently switch to scripted output or another endpoint.
A deterministic scripted provider remains an explicitly selected test profile.

Tether owns agent execution, tool approval, sessions and its selected persistence
contract. The host exposes only declared, approved Batten operations as agent
tools; it MUST NOT inherit unrestricted local shell/filesystem tools by launching
a generic reference client. Tether persistence need not use pgserver unless its
selected public store explicitly supports that binding.

Database installation, schema migration and fixture reset are explicit reviewed
operations. Ordinary start/reload MUST NOT reset data or bypass native admission.
Local readiness requires the selected providers and original database ownership
bindings; a model API or integration described in config is not live evidence.

Local hosting may own PostgreSQL 18 helper/process resources. Standalone hosting
owns its Batten service lifecycle within operator-managed infrastructure.
Embedded hosting accepts explicit borrowed service bindings and host-managed
identity; it uses no private host factory, globals or import-path discovery.
Neither standalone nor embedded permits fabricated identity.

Process placement is independent of hosting mode. An in-process application has
permission containment, not a hostile-code boundary. Child processes require
CONTRACT-001 and worker authority/transport qualification. Remote-worker placement
requires a separately qualified transport, effect custody, cancellation and
recovery profile; naming it in configuration never qualifies it. Databricks and
Lakebase are provider/environment choices, not extra hosting-mode enums.

Readiness requires every required component prepared under its effective identity
and permissions. Start orders dependencies from the assessed plan. Startup failure
stops new admissions, cleans owned prepared resources in reverse order and returns
safe outcomes through CONTRACT-001. Unsettled cleanup remains draining with
retained resource IDs. Live invocation rechecks current authority; an assessed
plan is not an authorization grant. No UI state changes lifecycle authority.

## Platform asset bindings

CONTRACT-010 binds required resource contracts to trusted deployment receipts and
opaque resource IDs through the selected provider. Deployment ownership is distinct
from this contract's owned/borrowed client lifetime. Preparation MUST verify exact
application/environment/provider/contract identity and current access/readiness;
missing or uncertain required evidence refuses readiness. A receipt grants no
authority and a current invocation still rechecks permissions. Ordinary start,
reload, cleanup and removal MUST NOT deploy, migrate, initialize, grant or destroy
persistent assets. Operators separately authorize deployment and destructive work.

## Precedence and Compatibility

Application meaning is fixed by its ArtifactRef; profile changes produce a new
profile/plan digest without rewriting the application. CONTRACT-001 owns Host
states, resource ownership and invocation errors. CONTRACT-003 owns assessment;
ADR-006 owns config resolution; schema owns structure. No provider can silently
substitute another meaning-compatible-looking native service.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Bound bytes/cohort differ from plan | `plan_stale` | Reassess | No factory starts. |
| Fabricated identity outside local | `identity_invalid` | Correct profile | No deployed readiness. |
| Missing binding, incompatible ownership/settings | `binding_invalid` | Correct typed profile | No guessed default resource. |
| Unsupported process/remote profile | `placement_unsupported` | Supply qualified support | No local fallback. |
| Partial startup or shutdown | CONTRACT-001 safe outcomes | Reconcile retained resources | Never claim closed while cleanup is unresolved. |

## Examples

```text
Application: review-queue, unchanged artifact digest.
Local: explicit fabricated identity; owned PostgreSQL18 and child worker.
Embedded: host-authenticated identity; borrowed PostgreSQL18 service.
Standalone: operator identity binding; owned service lifecycle.
Remote worker: refuses until selected transport/recovery profile is qualified.
```

No example constitutes infrastructure setup or native qualification.

## Schema Basis

The authoritative local payload shape is
[composition.schema.json](../schemas/composition.schema.json), proposed 0.1.0.
It describes extension payloads and core metadata projections, not a replacement
UMF envelope. Inspection used UMF core 0.10.0's `spec/metamodel/umf.yaml`,
`spec/core/extension-package.schema.json`, `umf.actions` 0.1.0's schema/package,
and the medical domain-pack metadata in the local public UMF project. The source
receipt is [upstream-schema-basis.json](../schemas/upstream-schema-basis.json).

Reuse: exact document/module/element identity, extension registration, unknown
preservation, native action/handler references and independent semantic validity.
Domain packs describe business data; they do not supply application module,
host composition or UI-to-operation bindings. Those are the specific local gaps.
The inspected extension registry does not establish a released saga vocabulary.
No saga fields are introduced here.

The initial proposed document-scoped vocabularies are `batten.application`,
`batten.module`, `batten.host` and `batten.ui`, each at 0.1.0 against an explicitly
pinned supported UMF core. Their payload roots select the matching schema
`$defs` entry. Registration packages and native semantic validation must be
qualified before implementation claims. Unknown payload members remain preserved;
unknown relevant meaning blocks eligibility even when shape validation passes.
No publication or rendering support is claimed by these declarations.
