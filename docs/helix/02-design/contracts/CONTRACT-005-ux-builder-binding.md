---
ddx:
  id: CONTRACT-005
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-002
      kind: derived_from
    - id: ADR-009
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

# CONTRACT-005: ux-builder and public UI binding

**Contract ID:** CONTRACT-005
**Type:** declaration, browser client and host boundary
**Version:** proposed 0.1.0

## Purpose

Connect ux-builder-owned design/artifact semantics to UMF metadata and the same
Batten operation boundary across local, standalone and embedded hosts.

## Scope and Boundaries

ux-builder owns its blueprint, journeys, layout, components, tokens, themes and
lint/audit tools. UMF owns schemas and action/saga semantics. Batten owns stable
operation bindings, the portable client and the host bridge. This contract selects
no unpublished ux-builder API or latest-version runtime dependency.

## Normative Surface

The schema `ui` root owns payload shape. Its application is an exact ID/version pin; the containing admitted application
must reference this UI artifact by digest. Blueprint and built assets are exact
ArtifactRefs. This one-way artifact closure avoids circular content hashes. Its client pin is checked independently of Batten's
SDK series and ux-builder versions. `controls` bind unique control IDs to exact
native operation targets and explicit model references for inputs; layout and
presentation metadata remain in original upstream artifacts.

| Element | Type / Shape | Required | Rules |
| --- | --- | --- | --- |
| UiBinding | Schema `ui` | for UI apps | Pinned app/blueprint/assets/client and stable controls. Headless apps omit it. |
| OperationTarget | Schema `target` | per control | Resolves an admitted native action/operation. Member interpretation belongs to exact vocabulary; names never authorize execution. |
| HostContext | Injected immutable browser service object | yes for rendering | Provides public client, permitted navigation, focus, confirmation, resource/download access and safe capabilities. No host shell object, credential, Python object or ambient discovery. |
| Client.invoke(target, input, invocation) | Async -> OperationOutcome | per operation | Input/output validation follows native types; invocation retains the original call identity and required confirmation. Server binds actor and current authorization. |
| Client.observe(invocation) | Async -> OperationOutcome | for uncertain calls | Authorized observation/reconciliation of original work only. Never reissue an uncertain write as a fresh call. |
| OperationOutcome | Existing CONTRACT-001 domain result | yes | Must distinguish pending/invalid/denied/succeeded/uncertain behavior without collapsing native failures or saga state. Transport mapping requires a pinned companion before cross-origin/runtime support claims. |
| HostContext.navigate/focus/confirm/download | Async scoped host services | where used | Host enforces permitted destinations and digest-covered authorized resources. UI cannot supply authority by choosing an app/resource ID. |

UI validation MUST resolve every control against the exact application and artifact
inventory before admission. Unknown relevant binding or renderer semantics refuse;
unknown source blueprint/native metadata survive unchanged. Validation must not
insert default actions or infer write permissions from the presence of a button.

Local, standalone and embedded hosts MUST use the same application-facing client
contract. Hosts supply authenticated transport/session integration; no token is
placed in model documents, blueprints, generated bundles or diagnostic payloads.
Explicit configured origin and message-sender checks are mandatory for any
cross-origin/frame transport. Such a transport needs its own qualified protocol;
this packet does not treat a generic postMessage call as a secure bridge.

The UI MUST render loading, denied, field-validation, successful and uncertain
outcomes. It MUST retain form inputs on recoverable failure, present an accessible
error/validation explanation and preserve confirmation/focus behavior. Permission
revocation MUST deny server-side calls, listings and protected downloads even if
an old screen remains visible. Confirmation binds the declared target, inputs,
actor and scope; stale or changed input requires a current confirmation.

The supported starter entry is the owner-selected
`npm create @ux-builder/app@latest my-idea` for author exploration. Reproducible
Batten builds MUST record the exact resolved starter/package/blueprint/client
cohort; they MUST NOT resolve floating latest versions at runtime. No starter is
executed during this design work. Integrate through its supported design-first
flow and public outputs; do not assume immediate React generation or copy its
blueprint schema into Batten.

## Precedence and Compatibility

Upstream artifacts remain the authority for their own shape and meaning. Batten's
binding schema adds exact references only. Client/host, renderer/blueprint and
native vocabulary compatibility are checked separately. An altered asset digest,
unknown required renderer or unresolved control target prevents UI admission.
The portable browser bridge imports no ux-builder packages; the optional adapter
owns those public packages and preserves headless installation closure.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Asset/binding/native target mismatch | `ui_binding_invalid` | Rebuild/reassess | No invocation. |
| Missing renderer or client pairing | `ui_capability_unavailable` | Install reviewed cohort | No guessed component fallback. |
| Denied operation/resource | CONTRACT-001 `denied` | After actual access change | No data disclosure; accessible denial. |
| Native input invalid | CONTRACT-001 `invalid` | Correct input | Retain inputs; native field explanation without private payload. |
| Possible effect without known result | Original `uncertain` outcome | Observe original only | No fresh automatic write. |
| Invalid frame/origin context | `host_context_invalid` | Correct trusted embedding | Refuse messages/resources before dispatch. |

## Examples

```text
Review approval control -> exact UMF approve action and native input Fields.
ux-builder blueprint -> journey, layout, components, theme and interaction design.
Local/embedded HostContext -> same client; different trusted transport bindings.
Lost approval acknowledgement -> observe original invocation; no second approval.
```

## Non-Normative Notes

The published [ux-builder documentation](https://documentdrivendx.github.io/ux-builder/)
was inspected for starter/design-first, blueprint, UI/token and audit boundaries.
Exact integration APIs remain a cohort proof, owned by Erik LaBianca and the
ux-builder maintainer before runtime implementation. SDK audit is separate from
Batten browser/server authorization and native effect evidence.

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
