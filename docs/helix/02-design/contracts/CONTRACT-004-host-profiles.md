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
