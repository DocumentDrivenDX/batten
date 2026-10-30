# Batten review packet

## Composition and hosting packet

The owner-selected next design slice treats Batten as a core-and-extensions SDK
for declarative AI applications. UMF owns saga semantics; ux-builder owns UX
artifacts and design tooling. This packet prepares source work without authorizing
implementation, migration or deployment.

1. [FEAT-009: composition and hosting](01-frame/features/FEAT-009-composition-and-hosting.md).
2. [FEAT-002: operations and ux-builder](01-frame/features/FEAT-002-operations-and-interfaces.md).
3. [CONTRACT-003: module/application composition](02-design/contracts/CONTRACT-003-composition.md).
4. [CONTRACT-004: host profiles](02-design/contracts/CONTRACT-004-host-profiles.md).
5. [CONTRACT-005: semantic controls, local implementations and renderer binding](02-design/contracts/CONTRACT-005-ux-builder-binding.md).
6. [ADR-008: independent axes](02-design/adr/ADR-008-independent-composition-axes.md) and
   [ADR-009: UX ownership](02-design/adr/ADR-009-ux-builder-ownership.md).
7. [Verification allocation](03-test/test-plan.md) and [work items](01-frame/work-items.jsonl).

US-001 through US-004 in `01-frame/user-stories/` define the fabricated review
queue across local and embedded hosts. The structural payload schema is an
authoring artifact; registered UMF packages, runtime validators and real service
behavior require implementation and qualification.


Batten is an independently implemented application SDK with native platform
dependencies and a public host API. This packet is ready for scope and boundary
review; the owner review gate precedes migration planning and product code.

## Read in this order

1. [Product vision](00-discover/product-vision.md) and
   [intent](00-discover/intent-and-intake.md).
2. [PRD](01-frame/prd.md): complete specified scope, grouped into stable requirements.
3. [Boundary audit](00-discover/current-state-inventory-boundaries.md): classifications,
   import graph, observed coupling, and evidence limits.
4. [Proposed architecture and module split](02-design/architecture.md): purpose,
   public API, platform dependencies, and permitted/forbidden imports for each module.
5. [Feature registry](01-frame/feature-registry.md) and [concerns](01-frame/concerns.md).
6. [Decision points](01-frame/decision-points.md): questions needing the owner's judgment.

## Public contracts

- [CONTRACT-001: host API](02-design/contracts/CONTRACT-001-public-host-api.md).
- [CONTRACT-002: boundary and quality gates](02-design/contracts/CONTRACT-002-boundaries-and-quality.md).

## Decisions

- [ADR-001: platform modules and neutral core](02-design/adr/ADR-001-platform-modules-and-neutral-core.md).
- [ADR-002: native UMF](02-design/adr/ADR-002-native-umf-platform-dependency.md).
- [ADR-003: distributions](02-design/adr/ADR-003-platform-wheel-distribution.md).
- [ADR-004: public asynchronous host](02-design/adr/ADR-004-public-async-host-api.md).
- [ADR-005: SDK series/cohorts](02-design/adr/ADR-005-sdk-series-and-cohort-compatibility.md).
- [ADR-006: typed files](02-design/adr/ADR-006-typed-file-configuration.md).
- [ADR-007: quality/test ratchets](02-design/adr/ADR-007-quality-and-test-ratchets.md).

## Audit and provenance

The public census contains anonymous module IDs. The source-specific graph,
line locations, read-only source receipt, consumer census, and requirement
crosswalk are delivered separately as a private local audit packet. They are
excluded from this repository; public Batten documents carry their own identities
and no dependency on the reference application.

Prior-art research remains in `00-discover/research/`. It informs direction;
the current owner rulings and PRD govern scope. The installed HELIX plugin owns
the methodology catalog; `.helix.yml` scopes artifacts to `docs/helix/`.

## Work and review

Work items are project-scoped ddx beads; the installed CLI keeps its canonical
store outside Git. The [review export](01-frame/work-items.jsonl) contains the
owner review gate, original scope epics and the composition/hosting work items,
all with execution authorization off. Feature scope is recorded without an implementation sequence; dependent
implementation work requires the owner review.
The current owner instruction authorizes the composition/hosting specification
packet and tracking. Migration remains separate. Before source work, review the
contracts and dependency proofs, establish the real quality scaffold, then build
the assessor, host binding and UX slice. No existing open policy is silently settled.
