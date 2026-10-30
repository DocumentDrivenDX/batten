---
ddx:
  id: CONTRACT-009
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: FEAT-009
      kind: derived_from
    - id: ADR-013
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
    - id: CONTRACT-004
      kind: informed_by
  schemas:
    - id: batten.services
      version: "0.1.0"
      title: Batten platform service ontology
      path: docs/helix/02-design/schemas/services.umf.json
      schemaFormat: umf
---

# CONTRACT-009: Service discovery and binding

**Contract ID**: CONTRACT-009
**Type**: ontology and application integration boundary
**Version**: 0.1.0
**Related**: PRD FR-11/15/35/37/42/44; CMP-17, CMP-23–29; US-005; ADR-013

## Purpose

Let applications share native semantic contracts, discover permitted service
exports and consume exact host-approved bindings across qualified transports.

## Scope and Boundaries

Batten owns the platform ontology and binding policy. Unified Modeling Fabric
(UMF) owns native models, references and action semantics. Arras owns ontology
reads/actions. The owning transport module enforces its qualified access profile.
Core contracts/runtime handle opaque artifacts, capabilities and dependencies.

The native model defines five record types and their field shapes. It introduces
no new UMF extension, business ontology engine, service mesh or broker. Logical
references to artifacts follow CONTRACT-003; original bytes and their unknown
content MUST survive without lossy projection. Graph persistence and physical
hosting remain operator choices requiring qualification.

## Normative Surface

[services.umf.json](../schemas/services.umf.json) owns structure. Every record
`id` identifies an immutable revision; its scope includes the deployment/fleet
namespace. Reusing an ID for different content MUST refuse. Logical IDs identify
the same application, interface, export, requirement or binding across revisions.
All identifiers compare exactly; display names never resolve dependencies.
Required string values MUST be nonempty; all SHA-256 fields MUST be 64 lowercase
hexadecimal characters and match the supplied original artifact bytes.

| Record | Required meaning | Rules |
| --- | --- | --- |
| `Application` | Logical application ID and admitted original artifact ID/SHA-256 | The host verifies artifact provenance; a registry row cannot self-admit an application or establish its owner. |
| `ServiceInterface` | Logical interface ID/version and original contract artifact ID/SHA-256 plus native module/element | The selected native definition references shared UMF types, queries/actions and results. Business shapes stay in that artifact closure. |
| `ServiceExport` | Provider application revision, interface revision, transport/profile pins and descriptor artifact ID/SHA-256 | Descriptor carries exact operations and native targets. It contains no credentials; private deployment addresses remain host settings. |
| `ServiceRequirement` | Consumer application revision, interface revision, required flag and optional selected export revision | Selection restricts eligible candidates; it never grants access. The requirement's logical ID is local to its exact consumer artifact. |
| `ServiceBinding` | Requirement/export revisions, deployment revision, opaque host resource binding and resolution evidence artifact ID/SHA-256 | Only the host's authorized binding operation issues it. It records a resolution, never a durable grant or a live readiness claim. |

`Application.exports/requires` relationships MUST agree with child
`applicationRevision`. `ServiceExport.implements` and `ServiceRequirement.needs`
MUST agree with `interfaceRevision`. `ServiceBinding.resolves/selects` MUST agree
with `requirementRevision/exportRevision`. Each child has exactly one applicable
parent/target; no dangling reference or conflicting relationship is eligible.
UMF's structural relationship multiplicities do not enforce these record-level
joins; semantic validation MUST check them. Bindings MUST select the exact
interface revision required by the consumer. All original artifact bytes,
transitive references and validation evidence MUST be supplied and digest-checked.

### Shared semantic identity

Shared business types MUST be independently governed UMF artifacts with stable
namespaced identities and pinned revisions/digests. They MAY have a domain owner
separate from every consuming app. Equal field names or JSON shapes MUST NOT
establish semantic equivalence. An app references shared types rather than
claiming ownership or copying them into Batten's platform ontology.

An interface revision binds an exact contract closure, including input/output,
error and action definitions. Interface version, application revision, transport
profile version and deployed resource revision remain distinct. Changing a
physical endpoint alone MUST NOT change an interface's semantic identity.

### Discovery, publication and bootstrap

The host MUST derive export/requirement records from verified application
artifacts; arbitrary graph writes MUST NOT publish an admitted service. Shared
interface artifacts require trusted provenance under host policy. Publishing a
binding is an explicit authorized command. Queries MUST have no binding,
subscription-provisioning, schema-migration or execution side effects.

Hosts offering graph discovery MUST explicitly install `batten.arras` and supply
the platform model, registry resource and authenticated access before application
resolution. This root binding is operator configuration; discovering the catalog
through itself is forbidden. Plain headless/core-only compositions MAY consume
explicit bindings without loading ontology packages.

Discovery runs through authenticated public Arras reads outside portable
assessment. Results MUST filter by current metadata visibility before pagination,
counts or dependency expansion. Visibility is separate from invocation permission;
metadata access MUST NOT imply permission to call a service. A hidden target and
an absent target MUST have the same public lookup outcome. Operators may inspect
broader impact graphs only with separately authorized metadata access.

Discovery MUST use finite host-configured item, byte, depth and duration limits.
Continuation MUST bind the principal/authority scope, query and catalog revision;
current visibility MUST be rechecked on every page. Changed revisions/authority
invalidate continuation rather than mixing snapshots. No hidden names, counts,
addresses, descriptors or dependency paths may enter public diagnostics.

### Resolution and admission

The host obtains a bounded authorized catalog snapshot and original artifacts,
then invokes the owning module's semantic resolver. That resolver produces
inert resolution evidence for CONTRACT-003 assessment; assessment itself MUST
NOT query Arras, fetch artifacts, import applications or start providers.

The evidence MUST cover the exact catalog snapshot artifact, consumer and
provider artifacts, requirement/export/interface revisions, transport descriptor,
profile/cohort, deployment revision and trusted policy/evidence revisions.
It MUST include the dependency edges used by generic lifecycle/upgrade checks.
The host verifies evidence provenance; self-authored validation is insufficient.
Evidence uses CONTRACT-003 ArtifactRefs and canonical plan rules; opaque resource
binding IDs use CONTRACT-004's trusted bindings, not client strings as authority.

A required unresolved/incompatible dependency refuses eligibility. An optional
missing dependency remains inactive and cannot be called. Multiple compatible
exports without explicit selection refuse; choosing the first/newest is forbidden.
Even an explicitly selected export MUST satisfy interface, visibility, grants,
transport and cohort constraints. Cyclic required startup dependencies refuse;
this does not prohibit mutually referring domain types or later message flows
whose providers can start independently.

The module supplies binding evidence as a separate host-owned immutable artifact;
it MUST NOT be added to the consumer artifact whose digest it references.
CONTRACT-003 ValidationEvidence.artifact pins those supplied evidence bytes, and
the plan's evidence array binds them into its canonical hash. Application service
requirements remain in the original application artifact and generic capability
requirements; evidence cannot rewrite that application or install a provider. CONTRACT-004 identifies the exact consumer plus
requirement ID and opaque host resource. No new ontology field enters core types.
Resolution evidence MUST also identify any platform resource release/output and
verified deployment receipt used by the selected export under the
[platform asset contract](CONTRACT-008-platform-assets.md). Asset
readiness/ownership remain that contract's responsibility; discovery MUST NOT
deploy, adopt or reconcile those assets.
The exact discovery capability ID and native Arras async bridge require upstream
qualification; these record names are not executable methods or released APIs.

### Invocation, changes and retirement

At use, the host MUST authenticate the user or explicit background/delegated
application authority, enforce consumer/export/operation/target scope and current
grants, and verify binding/provider/deployment revisions. Original initiating
user and effective executor attribution remain distinct across asynchronous work.
Payload headers, graph edges, artifact authors and registry fields grant nothing.

A stale binding or unavailable provider MUST refuse safely; no automatic provider,
transport or newest-interface fallback is permitted. Cached metadata may inform
search, but cannot establish current authorization or readiness. Revocation must
be effective at the next authorization boundary even with a cached binding;
streaming/long-running work follows its separately qualified cancellation policy.

Changing a contract, descriptor, application, deployment resource or relevant
policy/evidence invalidates affected resolutions. A new immutable binding revision
requires reassessment and authorized activation. Old revisions may coexist only
when their providers remain admitted and current grants permit their use.
Deprecation remains host catalog lifecycle policy; it MUST NOT silently rewrite
bindings. Retirement checks active dependents and requires explicit drain or
approved replacement. Revoked authority is never retained merely to finish a drain.
Uncertain in-flight effects remain uncertain; rebinding does not replay a command.

### Transport profiles

`transport` is one of `graph`, `table`, `api`, or `messaging`. Every use requires
a pinned, qualified `profileId/profileVersion` and its descriptor closure. Naming
a transport in this model selects no provider and qualifies no access guarantee.

| Transport | Required descriptor meaning and binding evidence |
| --- | --- |
| `graph` | Exact public Arras operations/native targets, actor/delegation, reads/actions, paging, receipts and consistency. No private object access. |
| `table` | Owner-published native table/view target, semantic field/key mappings, permitted operations, row/column policy, freshness/consistency and schema evolution. Host injects the scoped public accessor; clients receive no raw connection or arbitrary SQL capability. |
| `api` | Exact operation/request/result/error contract, authority/delegation, limits, idempotency, consistency and qualified public client. Address and credential resolution remain host-private. |
| `messaging` | Exact channel/subscription and writer/reader payload profile pins, publish/consume permissions, delivery/retention/recovery guarantees and codec evidence. CONTRACT-007 owns delivery semantics; discovery creates no subscription and grants no actor authority. |

Table profiles MAY expose owner-governed reads. A cross-application write MUST
use an explicitly declared owner command/action; a later writable table profile
needs its own exact validation, mutation authority and transaction contract.
FR-17's exceptional SQL restrictions remain. Unity Catalog and Lakebase bindings
need distinct native identity/policy and consistency evidence; sharing storage
or registering metadata establishes neither equivalence nor atomicity.

## Precedence and Compatibility

PRD FR-44 and FEAT-009 govern scope; ADR-013 governs ownership. Native UMF owns
shape and original semantic definitions; this contract owns eligibility and use.
Exact interface revision/digest matching is version 1's compatibility rule.
Version ranges, structural compatibility, field coercion and writer/reader schema
migration MUST NOT be inferred. A future compatibility profile needs separate
qualification and explicit consumer adoption.

Unknown source content MUST remain recoverable. Unknown relevant semantics block
binding; annotations are inert only when their owning vocabulary says so.
Structural validity and graph visibility establish neither native qualification,
execution authority nor readiness. Transport contracts retain their stronger
limits and uncertainty semantics; this contract cannot relax them.

## Error Semantics

| Condition | Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Hidden/absent target | `service_unavailable` | After authorized catalog change | Same safe public outcome; no hidden identifiers. |
| Multiple candidates | `service_ambiguous` | After explicit selection | Show only visible candidates; no automatic choice. |
| Interface/profile mismatch | `service_incompatible` | After exact contract/cohort repair | No coercion or transport fallback. |
| Altered bytes or conflicting revision | `artifact_invalid` | After verified repair | Preserve original bytes; no execution. |
| Dangling/contradictory relationships | `declaration_invalid` | After declaration repair | No partially eligible graph. |
| Unknown relevant meaning | `semantics_unchecked` | After qualified validation | Preserve source; block affected dependency. |
| Missing authority or revoked grant | `denied` | After authorized access change | No target effect or existence disclosure. |
| Changed binding/catalog continuation | `binding_stale` | After fresh resolution | Reassess; never automatically replay possible effects. |
| Required startup cycle | `component_cycle` | After dependency repair | No guessed startup order. |
| Exceeded finite budget | `limit_exceeded` | After bounded request/config change | No truncated eligible resolution. |

Providers translate internal errors before disclosure. Required uncertainty,
attribution and audit follow the host/transport contracts, including unsampled
audit obligations; this contract defines no replacement telemetry wire format.

## Examples

```text
customer-owner revision A exports customer-lookup revision E.
review-queue revision B requires customer-lookup interface revision I.
I references exact shared Customer and lookup action definitions in UMF.
The visible export E implements I using an admitted graph profile.
Host resolution binds B's requirement to E and an opaque scoped resource.
Revoking access leaves the graph records intact; the next invocation is denied.
A second export implementing I requires explicit selection before binding.
Moving E to a new deployment retains I and requires a new binding revision.
```

All names are fabricated. A table or message export uses the same requirement
model but must satisfy its own transport profile and semantic evidence.

## Schema Basis

[Source receipt](../schemas/services-schema-basis.json) pins inspected UMF core
0.10.0, `umf.actions` 0.1.0 and the medical domain pack 1.2.0. Native core records,
fields, keys and relationships represent the five Batten types. The business pack
and actions do not define application exports or deployment bindings; those are
the local domain additions. No new general UMF vocabulary is necessary here.

Arras's public principal-scoped reads inform the provider boundary. Its inspected
synchronous Python surface does not prove Batten's async-first bridge, registry
snapshot semantics, native persistence or transport authority. US-005 and TP-001
allocate those observations. Core schema validation checks declaration structure;
record joins, artifact closure, visibility, grant enforcement and binding recovery
need semantic/native evidence before source work or support claims.
