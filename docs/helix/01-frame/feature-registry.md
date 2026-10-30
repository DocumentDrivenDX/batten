---
ddx:
  id: batten.feature-registry
  type: feature-registry
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
---

# Feature registry

**Last Updated**: 2026-10-29

## Active Features

These stable identities organize the scoped product requirements. The PRD is the
governing source for this first review; detailed feature specifications and stories
follow the owner's scope review rather than empty placeholder files.

| ID | Name | Description | Priority | Owner | Source | Updated |
|----|------|-------------|----------|-------|--------|---------|
| FEAT-001 | Declaration and admission | Specification, settings, gate, namespace, listing, safe refusal. | P0 | Erik LaBianca | PRD FR-1–7 | 2026-10-29 |
| FEAT-002 | Operations and interfaces | One operation across surfaces, including semantic controls, local implementations and renderer bindings. | P0 | Erik LaBianca | PRD FR-8–9, FR-39–41 | 2026-10-29 |
| FEAT-003 | Native data and identity | Native UMF, typed access, lifecycle, row policy, principal separation. | P0 | Erik LaBianca | PRD FR-10–17 | 2026-10-29 |
| FEAT-004 | Workers and background execution | Owner-scoped execution, scheduling, confirmation, jobs, events and durable messaging. | P0 | Erik LaBianca | PRD FR-18–22, FR-45 | 2026-10-29 |
| FEAT-005 | Artifact delivery and lifecycle | Complete runtime delivery, admission, fleet upgrade qualification, revocation and recovery. | P0 | Erik LaBianca | PRD FR-23–24, FR-42 | 2026-10-29 |
| FEAT-006 | Platform resources and diagnostics | Secrets, files, search, models, enforced audit/telemetry and grants. | P0 | Erik LaBianca | PRD FR-25–28 | 2026-10-29 |
| FEAT-007 | Author tooling and qualification | Semantic CLI coverage, automatic property-based end-to-end suites, migration qualification and author tooling. | P0 | Erik LaBianca | PRD FR-29–31, FR-47 | 2026-10-29 |
| FEAT-008 | Host embedding and compatibility | Public host API and independent consumer/dependency closures. | P0 | Erik LaBianca | PRD FR-32–33 | 2026-10-29 |
| FEAT-009 | Composition and hosting | Selectable modules, profiles, platform assets, fleet hosting and platform-ontology service discovery/binding. | P0 | Erik LaBianca | PRD FR-34–38, FR-43–44, FR-46 | 2026-10-29 |

## Dependencies

| Feature | Depends On | Type | Notes |
|---------|------------|------|-------|
| FEAT-009 | FEAT-001, FEAT-003, FEAT-008 | Required | Composes admitted apps and resolves governed services using native semantic types through public boundaries. |
| FEAT-002 | FEAT-001, FEAT-009 | Required | All surfaces use the same declared operation and gate. |
| FEAT-003 | FEAT-001 | Required | Data requires effective actor and permission context. |
| FEAT-004 | FEAT-001, FEAT-003 | Required | Workers/jobs preserve declared scope and identity. |
| FEAT-005 | FEAT-001, FEAT-004 | Required | Admission and worker verification precede artifact execution. |
| FEAT-006 | FEAT-001 | Required | Resource calls need scoped authority and safe outcomes. |
| FEAT-007 | Author tooling and qualification | Semantic CLI coverage, automatic property-based end-to-end suites, migration qualification and author tooling. | P0 | Erik LaBianca | PRD FR-29–31, FR-47 | 2026-10-29 |
| FEAT-008 | FEAT-001 | Required | Embedding supplies services to the portable contract. |

## Relevant References

[PRD](prd.md), [concerns](concerns.md), [boundary audit](../00-discover/current-state-inventory-boundaries.md),
[architecture](../02-design/architecture.md), and
[open decisions](decision-points.md). Feature dependencies describe capability
relationships, not an implementation or migration sequence.

## Feature Categories

- Application contract: declaration, operations, and host embedding.
- Platform execution: data, workers/background work, resources, and diagnostics.
- Developer lifecycle: artifact delivery and author qualification.

## ID Rules

Assign sequential three-digit feature IDs. Never reuse an ID. Keep detailed
behavior in the governing PRD until the reviewed scope supports feature specs.
