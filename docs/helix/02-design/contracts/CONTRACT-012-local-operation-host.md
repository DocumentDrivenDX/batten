---
ddx:
  id: CONTRACT-012
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-005
      kind: informed_by
    - id: ADR-016
      kind: informed_by
---

# CONTRACT-012: Local operation host and TypeScript client slice

**Contract ID**: CONTRACT-012
**Type**: library and local HTTP boundary
**Version**: 0.1.0

## Purpose

Implement a bounded local app slice of CONTRACT-001/005 without importing native
engines into generic runtime or treating local identity as production authentication.

## Scope and Boundaries

Generic contracts and runtime own host lifecycle, admitted operation metadata,
current authority, invocation limits and safe outcomes. The optional UMF tables
module owns native table binding. The optional ASGI module owns HTTP transport.
The approval app owns its original UMF business model, native configuration and
TypeScript interface. No direct database/client object crosses into the browser.

## Normative Surface

The local host uses frozen contract values and explicit service injection. Host
construction MUST be effect-free; start prepares the selected services, and close
revokes handles and closes only owned resources. Calls require running state,
an admitted operation and current host-bound identity. Native table binding and
validators preserve original model identity and outcomes rather than recompile SQL.

| Surface | Shape | Rules |
| --- | --- | --- |
| Local identity | Opaque server session cookie | HTTP-only, same-site strict, runtime-generated; no identity/role header authority |
| `GET /api/session` | Safe current actor or anonymous outcome | No native connection or credential |
| `POST /api/local-session` | `{actor: string}` | Loopback-only development mode, same-origin JSON, explicit fixed host allowlist |
| `POST /api/logout` | Empty JSON | Revokes the current session |
| `POST /api/operations/{operation}` | `{inputs: object, key?: string, phase?: string}` | Exact declared operation; phase invoke/observe; unknown fields refuse |
| Outcome | Safe status, result and original invocation identity | Distinguishes denied, invalid, precondition, success, pending/uncertain and capture loss |
| Query | Declared read-only operation | No business mutation or command replay |
| Mutation | Stable original caller key | Input-preserving native receipt/observation; no automatic new-key retry |

The ASGI adapter MUST enforce configured host/origin, bounded request bytes,
concurrency and deadlines. Mutation endpoints require same-origin JSON, independent
of cookie policy. CORS cannot grant another origin access. Static assets contain
no credentials and use a restrictive content security policy. Startup MUST NOT
create roles, tables, migrate or grant access. Explicit maintenance is separate.

Local stub identities are available only on loopback under explicit development
configuration. They are not authentication for a remote, preview or production
host. Application inputs cannot choose the native principal or provider binding.

Safe durable audit and OpenTelemetry instrumentation are required host services.
Capture failure cannot silently report success. After a possible mutation it
retains uncertainty and the original key. Local captured spans do not establish
an OTLP receiver, production telemetry or native attribution beyond observed facts.

## Precedence and Compatibility

CONTRACT-001 owns generic host semantics; CONTRACT-005 owns the UI boundary.
Native UMF source and SDK own persistence, row policy, receipts and codecs.
This local HTTP subset grants no whole-SDK or production compatibility claim.
Additional transports or authentication modes require their own qualification.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery |
| --- | --- | --- | --- |
| Unknown/revoked/foreign actor | Safe denial or nondisclosing absence | After legitimate policy change | No hidden record detail |
| Invalid input or undeclared operation | Invalid/refused | Correct the call | No provider effect |
| Stale revision or prohibited self-decision | Precondition/denial | Inspect current state | Preserve the newer record |
| Lost mutation acknowledgement | Uncertain original invocation | Observe original key | Never blindly issue a fresh decision |
| Capture/provider loss | Explicit unavailable/uncertain | Reconcile original outcome | No silent fallback |

## Examples

An app submits a request with a retained invocation key, then an independent
approver decides using the revision they inspected. If the requester edits first,
the stale decision cannot overwrite that edit. A lost decision response is
observed with unchanged original inputs and key.

## Schema Basis

Original app models use UMF core 0.10.0, `umf.tables` 0.1.0 and native table
operation 0.1. The inspected public source is the pinned UMF candidate in the
app build evidence. Local session/operation transport envelopes are host-owned
protocol metadata; they do not redefine business records or action semantics.

## Local application registry

The owner requires the local host's root `/` to be an application registry.
Each explicitly registered app has a unique stable slug, title, description and
packaged visual thumbnail. Entries link to `/apps/{slug}/`; the app's Batten brand
link returns to `/`. Registry content is host-owned metadata, never inferred by
scanning private application records or importing arbitrary discovered modules.
Only registered apps receive routes. Duplicate/invalid slugs refuse at composition.

App assets and APIs live under the same app prefix. Session cookies are scoped
to that app's API path; each app retains its own identity, authority, host services
and data binding. Listing an app grants no business access. Local origin/host
checks and security headers protect the registry as well as application routes.
Thumbnails are packaged fabricated previews, not live private-data screenshots.
The registry lists configured local apps; it makes no production discovery claim.
