---
ddx:
  id: CONTRACT-100
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: CONTRACT-006
      kind: derived_from
    - id: CONTRACT-001
      kind: informed_by
---

# CONTRACT-100: Storage provider host integration

**Contract ID**: CONTRACT-100
**Type**: library boundary
**Version**: 0.1.0

## Purpose

Define explicit host injection for the local storage implementation without
constructing a generic Batten runtime or importing a platform adapter into core.

## Scope and Boundaries

Storage owns its typed protocols and local provider. The host owns trusted
identity, current authorization, attribution and telemetry sinks. Implementing
this provider does not qualify the complete runtime or Databricks cohort.

## Normative Surface

| Element | Shape | Rules |
| --- | --- | --- |
| `local.initialize(root)` | async explicit maintenance | Creates a new empty managed namespace; refuses adoption of existing unmanaged data. No environment lookup. |
| `local.create_store(root, limits)` | pure factory returning LocalProvider | Requires absolute root and complete Limits; no I/O. |
| `LocalProvider.prepare()` | async | Opens the existing managed namespace, validates ownership/layout and readiness. Never resets bytes. |
| `LocalProvider.bind(authority)` | synchronous ObjectStore | Borrows provider lifetime; the authority is host-supplied and request-scoped. |
| `LocalProvider.aclose()` | async | Revokes bound handles, closes reads/cursors and resources; preserves published objects and qualified resumable staging. |
| `for_resource(context, resource)` | synchronous ObjectStore | Delegates to trusted `context.storage(resource)`; does not resolve credentials or construct adapters. |
| `Authority.identity` | stable opaque string | Host binds actor, application, resource and profile revision into this identity; caller text is not authority. |
| `Authority.check(operation, key)` | async | Raises denial on absent/revoked scope; key is relative, operation is CONTRACT-006 permission. Checks happen before existence and continued reads/pages/parts. |
| `Authority.observe(code, effect, incident_id)` | async | Required host-owned safe outcome capture, including cancellation/uncertainty. Host closure supplies trusted attribution and correlation. No key, path or content is included. |
| `ObjectStore.aclose()` | async | Revokes that request's handles and closes streams/cursors; never closes a borrowed provider. |

`Limits` mirrors CONTRACT-006's schema with no implicit operational values.
Python dataclasses are immutable boundary values; serialization uses the owning
schema names. The local profile provides adapter-managed concurrency, revision
validators and atomic replacement. External writers are prohibited by host policy.
Local roots are dedicated, owner-only directories with descriptor-relative,
no-follow regular-file/directory operations. Supported platforms are qualified
POSIX systems with directory descriptors, advisory file locking and atomic rename.
Unqualified operating systems refuse prepare.

A local namespace uses encoded logical path segments, immutable content blobs,
atomic pointer records and a cross-process namespace lock. Pointer records own
storage metadata only; they are not application records or a second model engine.
Staging and cursor/session registries have finite host bounds. Provider restart
invalidates cursors; restart-safe upload recovery requires persisted session state.

Observation failure MUST be visible and deny successful completion reporting.
If bytes may already be published, observation failure retains `effect=unknown`.
No provider sink claims an OpenTelemetry receiver or runtime identity propagation
was qualified; those are separate host integration obligations under CONTRACT-001.

## Precedence and Compatibility

CONTRACT-006 owns object semantics. This contract supplies construction/context
interfaces; it grants no authority to application-created objects. The trusted
host composition boundary injects these objects. Borrowed services remain borrowed.

## Error Semantics

| Condition | Outcome | Retry | Recovery |
| --- | --- | --- | --- |
| Unmanaged root or unsafe layout | `invalid_request` | After explicit maintenance | Preserve existing data. |
| Missing platform primitives | `unsupported` | Qualified platform | Never weaken containment. |
| Missing/revoked authority | `denied` | Explicit authority change | No existence disclosure. |
| Observation sink failure | `unavailable` | Reconcile original operation | Preserve possible effects; never report silent telemetry success. |

## Examples

```python
await initialize(approved_empty_root)  # explicit maintenance, once
provider = create_store(approved_empty_root, resolved_limits)
await provider.prepare()
objects = provider.bind(host_authority)
await objects.write("reviews/demo.txt", b"Fabricated review")
await objects.aclose()  # provider and data remain usable
await provider.aclose()
```

## Schema Basis

CONTRACT-006's storage.schema.json and storage-schema-basis.json own existing
values and UMF reuse evidence. Injected Python authority/context protocols have
no serialized schema; they contain executable host behavior, not application
model declarations. No new model vocabulary or environment setting is introduced.
