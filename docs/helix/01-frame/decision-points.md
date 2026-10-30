# Owner decision points

The current review covers requirements, the boundary audit, module boundaries,
and the owner-authorized composition/hosting and ux-builder design packet. Migration planning and product code require the owner's review.
These questions preserve source-marked open decisions without inventing outcomes.

## Resolved direction

- Batten remains the product and repository in the Novirhyza family.
- Reference material is read-only behavioral/coupling evidence; Batten is an
  independent cleanroom implementation with its own public API and history.
- Native UMF documents and typed access form Batten's authoring contract. The
  consuming host owns legacy format and API compatibility.
- Platform libraries are platform dependencies. PostgreSQL 18, async-first,
  layered typed files, no new environment variables, fabricated data, dual
  licensing, and trusted first-party permission containment are fixed rulings.
- The first reviewed behavioral suite establishes the measured test-count ceiling;
  afterward it only decreases.

- UMF owns saga semantics; Batten binds exact supported declarations/executors.
- ux-builder integration is explicit and optional; its design artifacts remain upstream-owned.
- Application capability selection, host environment and execution placement
  are independent axes. The owner authorized their specification and ddx work items.

- The complete packaged runtime removes application-level dependency installation;
  platform owners qualify dependency upgrades across application evidence.
- Telemetry, assertions and behavioral test coverage are required platform gates.
- Shared infrastructure targets hundreds of applications; graph API and future
  defined mechanisms govern integration without implicit grants.

## Fleet design and evidence questions

The product direction is settled. Platform/host owners must define qualification
policy, required telemetry and its bounded failure behavior, evidence exchange,
workload mix, budgets and service objectives. Upstream graph API operations,
delegation and interface/dependency profiles need exact contracts and qualification.
Runtime artifact format and rollout/recovery controls also need downstream design.
These are open implementation inputs; the fleet goals do not await another
product-scope decision and do not authorize rollout, migrations or product code.

## Semantic verification design inputs

FR-47 settles automatic testing and CLI completeness for fully declarative UI and
hooks as required scope. Upstream semantic owners must expose exact refinement,
state-transition, invariant and effect meaning. Batten must contract the CLI,
generator/oracle interface, replay/shrinking evidence and platform adapter coverage.
Qualification policy must distinguish complete declared-behavior coverage from
bounded state-space exploration. Missing contracts block affected implementation,
not the requirement. Arbitrary procedural code requires an explicit semantic oracle.

## Questions requiring the owner

| ID | Decision | Recommendation for review | Affected scope | Owner |
|----|----------|---------------------------|----------------|-------|
| D-001 | Which ontology responsibilities belong in the Batten module? | The owner's module question is answered by a normal ontology-provider module through Arras. Zero ontology-specific core capabilities; generic capability/dependency lifecycle only. Review this proposal before adding exceptions. | Ontology provider boundary and lifecycle | Erik LaBianca |
| D-002 | Who approves each admission tier and packaged extension? | Retain explicit host policy and digest binding; do not make Batten choose the organization's reviewers. | Admission policy integration | Erik LaBianca with the consuming host's policy owner |
| D-003 | What persona information may an application listing expose? | List only effective permitted surfaces; additional persona disclosure needs a ruling. | Catalog/listing metadata | Erik LaBianca |
| D-004 | Should a manually triggered writing job have independent confirmation or reuse a schedule's confirmation? | Preserve the effective confirmation requirement; decide the independent confirmation object before its contract. | Triggered job confirmation | Erik LaBianca; delegated subject policy owner where needed |
| D-005 | Which authority may run a data step on an already row-scoped table? | No implicit row-security bypass; require an explicit reviewed maintenance identity decision. | Scoped migration data steps | Erik LaBianca and database platform owner |
| D-006 | Is a separate bundle-call audit identity required? | Use Batten-owned names; settle session/sessionless semantics before defining the event schema. | UI/tool audit contract | Erik LaBianca |

Do not decide a row by choosing a convenient implementation. These are policy
questions, not reasons to omit the capability from the requirements.

## Consumer-owned and evidence questions

Legacy route prefixes, schemas/roles, setting names, and source compatibility
belong to the consuming host under the native-authoring ruling. The later
transition plan must include both installed and hosted consumer forms and keep
both repositories green without a visible behavior change.

Lakebase ownership, role switching, row policies, and native identity require
real platform evidence. Upstream maintainers must identify a cohort covering
the complete table lifecycle and policy matrix. This review does not substitute
historical local checks for those observations.

The source plan refers to decision labels whose definitions are absent in the
provided file. Its domain-specific pipeline/evaluation policy is not silently
re-framed as an SDK decision; the owner must supply any relevant missing intent.

## Bounded integration proof dependencies

These require evidence rather than a new policy ruling. Erik LaBianca and the
UMF/ux-builder maintainers supply the exact public release/API cohort; the host
owner supplies resource limits, identity and transport qualification. Until then,
required unsupported capabilities refuse. A descriptor, declared version or
valid schema is not proof of native saga execution, UI quality or deployed hosting.
