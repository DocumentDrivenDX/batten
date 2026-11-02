---
ddx:
  id: TD-101
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: US-101
      kind: informed_by
  schemas:
    - id: batten.approval-desk
      version: "0.10.0"
      title: Approval desk native table declarations
      path: docs/helix/reference-apps/approval-desk/specs/02-design/models/approval.umf.json
      schemaFormat: umf
---

# TD-101: Native local approval desk

**User Story**: [[US-101]] | **Feature**: [[FEAT-101]] | **Solution Design**: [[SD-101-approval-desk]]

Governing acceptance: US-101-AC1 through US-101-AC6; STP-101 owns exact proof.

## Technical Approach

Declare records, row policy, reads and conditional mutations in original UMF.
Use the original deployment compiler and native async table transport, with
current person identity supplied by the host outside wire inputs. Native RLS
permits owned requests and explicitly assigned reviewers. Conditional decisions
also require an inspected pending revision and a different current principal.

Use a pure generic host factory and injected services. An optional ASGI adapter
serves the TypeScript app through CONTRACT-012. The app cannot install providers,
execute SQL or choose the native identity. Explicit local setup creates an isolated
fabricated PostgreSQL 18 namespace; host startup only opens verified bindings.

## Component Changes

| Component | Ownership | Dependency rule |
| --- | --- | --- |
| contracts/runtime | Generic values, operation dispatch and lifecycle | stdlib and contracts only |
| tables | Portable table port | Contracts and stdlib only |
| umf_postgres | Public original UMF native adapter | UMF access/codegen, Weft and psycopg stay optional |
| hosting.local | Local identity, capture and provider assembly | Optional local adapter; no core-to-platform import |
| asgi | Local HTTP host/client boundary | Runtime/contracts and selected Starlette/Uvicorn |
| approval app | Business declaration, configuration and UI | Public Batten surfaces; no native driver in business/UI code |
| local maintenance | Dedicated test/dev database and native installation | Explicit command; never startup or ordinary invocation |

The common boundary gate must know these owners before dependent source and
reject provider imports in generic core. Public export inventory remains explicit.

## API/Interface Design

SDK CONTRACT-001/005/012 govern shared surfaces. The app binds its own original
model operations rather than exposing a raw SQL or unrestricted native API route.
The browser retains original invocation inputs and keys when an outcome is uncertain.

## Security

Loopback local stub identity is explicit and distinct from production auth.
Same-origin, host, JSON type, request bounds and cookie protections apply before
mutation dispatch. Current host and native authority are checked on each call.
Only source-declared current-principal values may create owner/decision identity.
Audit contains safe identifiers/outcomes, not request titles, SQL or credentials.

## Testing

Qualify native model compilation, actual PostgreSQL 18 row policy, independent
approval, stale edits, hidden/foreign/revoked access and original outcome observation.
Use a real browser for TypeScript interaction, keyboard/focus and denied/uncertain
states. Consolidate duplicated read setup to keep the existing function ceiling;
retain every prior storage assertion and add one complete app journey behavior.

## Schema Basis

Reuse original UMF core 0.10.0, tables 0.1.0 and table-operation 0.1 from the inspected
public SDK. No alternate model compiler or schema vocabulary. The app's native
table source owns its actual fields, policy and conditional command bodies.
Compiler and native codec limitations must refuse explicitly before app support.

## Diagnostic Wiring

Host invocation and table integration produce scoped OpenTelemetry spans and safe
durable audit. Capture/receiver qualification is reported separately; local output
is not a deployed receiver claim. Native attribution reports actual session roles.

## Implementation Sequence

Compile and verify the app source first; establish ownership/import gates; then
wire generic host, native tables, ASGI and the TypeScript client. Complete the
native/browser journey and installed dependency evidence before claiming the slice.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Candidate SDK assets differ from source | False cohort | Rebuild in an isolated pinned public source tree and retain hashes |
| Lost mutation response | Duplicate decision | Observe original native receipt and unchanged key/inputs |
| Local stub mistaken for real login | Unauthorized hosting | Restrict loopback/origin and reject production mode |

## Registry integration

The local registry owns `/`; this application moves to `/apps/approval-desk/`.
The Batten brand returns to the registry. Relative asset/API URLs and app-scoped
cookie paths preserve multiple app bindings without changing native records.
STP-101's existing journey enters through the registry and returns through the
brand link, proving the registry card's title, description, thumbnail and target.
