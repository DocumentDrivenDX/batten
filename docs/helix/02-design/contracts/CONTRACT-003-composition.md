---
ddx:
  id: CONTRACT-003
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

# CONTRACT-003: Module and application composition

**Contract ID:** CONTRACT-003
**Type:** library and declaration boundary
**Version:** proposed 0.1.0

## Purpose

Define inert module/application metadata and deterministic assessment before
provider loading, configuration effects or application execution.

## Scope and Boundaries

Batten owns module selection and capability resolution. UMF owns its envelope,
model, values, actions and sagas; this contract adds application composition.
Host policy owns allowed factories, dependencies and authority. This is a
proposed interface, not an assertion of published packages or upstream support.

## Normative Surface

The local schema owns field shape and requiredness. The following rules own
semantics and MUST be enforced in addition to schema validation.

| Element | Type / Shape | Required | Rules |
| --- | --- | --- | --- |
| ModuleDescriptor | Schema `module` | per selected module | Installed wheel metadata; exact module/version/distribution, SDK series, capability interfaces, dependencies, supported vocabularies/settings/placements and inert factory ID. No eager import to discover metadata. |
| ApplicationComposition | Schema `application` | yes | Application identity, SDK, required/optional capabilities, exact artifact inventory and inert hook bindings; optional UI artifact. Application data cannot install modules or choose privileged provider factories. |
| ArtifactRef | Schema `artifact` | per reference | ID and SHA-256 of supplied original bytes, including unknown content. No implicit network fetching. Missing bytes or digest mismatch refuse. |
| TargetRef | Schema `target` | per native target | Exact artifact/module/element plus optional member interpreted by its vocabulary. Display names and guessed latest revisions never resolve references. |
| CapabilityRequirement | Schema `requirement` | per dependency | Stable requirement ID, exact interface ID/version and required flag; optional explicit provider ID. Provider module version is separate from interface version. |
| Hook | Schema `hook` | per procedural binding | Exact handler ID/version in an admitted code catalog and native target; required capabilities. Metadata alone authorizes no code loading. |
| assess(application, modules, profile, evidence, limits) | Pure function -> Assessment | yes | Inputs are immutable copied metadata and supplied artifacts. No provider/application import, environment read, network, factory invocation or service start. |
| ValidationEvidence | Schema `evidence`; trusted build/host input | yes for referenced semantics | Source artifact digests, validator ID/version, interpreted vocabulary pins, complete/valid distinctions and known diagnostic paths. Author assertions are not trusted evidence. Native validators run outside portable core and supply exact pinned results. |
| Assessment | Schema `assessment` | yes | State is `eligible` or `refused`. Findings are ordered `{code, subject, path}` with safe IDs only. Refused has no plan. Uninterpreted optional components remain explicitly inactive in an eligible plan. |
| CompositionPlan | Schema `plan` | when eligible | ArtifactRefs for application/profile/cohort; selected provider IDs/versions and placements, dependency order and inactive requirement IDs; bound validation evidence and finite assessment limits. Hash covers a canonical UTF-8 encoding of the complete plan content except its own hash. No effect or readiness claim. |
| limits | Schema `limits`; host-supplied finite limits | yes | Positive integer `bytes`, `items` and `depth` limits for every input and traversal, including nested JSON and dependency depth. Exceeding any bound refuses with no partial plan. Deployment owners supply values. |

All declaration IDs compare exactly without normalization. Host bindings and
resolved requirements identify the exact consumer ArtifactRef plus its local
requirement ID. Local IDs alone do not resolve requirements across consumers;
array positions and display names never replace stable identity. Identity uniqueness
is scoped by application, module, requirement or control as appropriate. Exact
interface matching is the initial rule; ranges or coercions are not inferred.
SDK series follows ADR-005. A provider selection MUST satisfy the required
interface and be installed in the cohort; name equality alone is insufficient.

Resolve all required dependencies transitively. More than one matching provider
without explicit selection refuses; an explicit provider must be among the
matches. Reject cycles before effects. Stable topological order selects the
lexicographically smallest ready module ID at each step. Declarations are finite;
resolution must retain every source artifact and diagnostic basis.

Assessment limits are part of the plan and trusted policy. Any unrecognized
member of the plan, metadata projection or profile remains retained but blocks
semantic eligibility; no caller can smuggle additional execution meaning through
the permissive preservation schema.

An optional missing capability is retained inactive. An admitted operation or
required component depending on it MUST refuse. A required unknown vocabulary
blocks eligibility; unknown annotations are inert only where their owning
vocabulary explicitly says so. Never infer irrelevance from a field's spelling.

Plan canonical encoding uses JSON values only, Unicode scalar strings, no
nonfinite or numeric business values, object keys sorted by Unicode code point,
array order retained, no insignificant whitespace and UTF-8 without a byte-order
mark. Strings escape quote/backslash with their short JSON escapes, all U+0000
through U+001F controls as lowercase four-digit Unicode escapes, and emit every
other Unicode scalar literally. Integers use unsigned base-10 without leading
zeros; other JSON numeric forms are forbidden in plan metadata. Implementations
must use shared byte fixtures; language-default JSON escaping is not a
cross-language canonicalization claim. Artifact digests always
cover original bytes, not this plan encoding.

Saga targets require the exact UMF-owned declaration/profile and a separately
qualified executor capability. Batten preserves upstream results and recovery
identity without synthesizing rollback, retries or completion. Until that
pairing exists, the saga requirement refuses; unrelated applications can assess.

## Precedence and Compatibility

PRD FR-34–38 governs scope; the schema governs structure and this contract owns
semantic rules. Unrecognized semantic versions do not fall back. ADR-005 governs
SDK compatibility independently of payload, module and upstream versions.
The portable runtime imports stdlib/contracts only; the owning UMF module supplies
validated metadata. Plans must be reassessed when any bound artifact or evidence changes.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Missing target bytes or digest mismatch | `artifact_invalid` | After repair | Preserve originals; do not execute. |
| Duplicate identity or malformed payload | `declaration_invalid` | After correction | Safe ID/path only. |
| Missing, ambiguous or incompatible provider | `capability_unavailable`, `provider_ambiguous`, `capability_incompatible` | After selection/cohort repair | No implicit install or fallback. |
| Cycle or placement mismatch | `component_cycle`, `placement_unsupported` | After profile repair | No eligible partial graph. |
| Relevant unknown or incomplete validation | `semantics_unchecked` | After exact support supplied | Retain source content. |
| Unsupported handler or dependency | `handler_unavailable`, `dependency_unapproved` | After reviewed admission | No code import to test it. |
| Exceeded finite bound | `limit_exceeded` | After bounded input/profile change | No truncated eligible plan. |

Findings sort by subject, path, then code using Unicode code-point order; duplicates
collapse by that tuple. Diagnostics contain no input values, deployment addresses,
SQL, raw exceptions, secret references or provider configuration bodies.

## Examples

```text
review-queue requires records/1 and approval/1; UI is absent.
The installed cohort offers one reviewed provider for each interface.
Assessment returns the dependency order and the exact app/profile/cohort pins.
Adding a second approval/1 provider without selecting one -> provider_ambiguous.
Adding a required UMF saga without its executor -> capability_unavailable.
```

These illustrative IDs are fabricated. A profile claiming an interface is not
native execution evidence. Structural examples are not released extension packages.

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
