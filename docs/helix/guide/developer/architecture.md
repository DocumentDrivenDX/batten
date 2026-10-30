<!-- helix:publish audience=developer page=architecture kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/df3553698c799c67 -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:9a0974a3fc6dec69 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-platform-modules-and-neutral-core.md sha256:f845d229ffe50254 -->
<!-- helix:source docs/helix/02-design/adr/ADR-003-platform-wheel-distribution.md sha256:afb392083440716f -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md sha256:f30000f983733880 -->
<!-- helix:source docs/helix/03-test/test-plan.md sha256:29d7680fa9244bd1 -->
<!-- helix:source docs/helix/02-design/adr/ADR-007-quality-and-test-ratchets.md sha256:471d35bf9671a37f -->

# A small core, explicit boundaries

Batten's architecture separates application contracts, generic execution policy, platform adapters and host composition. Concrete services are wired at the host boundary.

## Portable core

The contracts and runtime are designed to use Python's standard library. The core owns generic capability and lifecycle rules; it has no ontology-specific branches or native vendor types.

Native UMF validation belongs in its adapter. The core receives validated metadata projections and uses them to assess dependencies without importing provider code.

## Explicit platform modules

Separate wheels follow platform responsibilities. Tables, PostgreSQL, Lakebase, Databricks, gateway, ontology and agent integration have their own dependency boundaries.

The browser client is independent of Python host objects. Its optional ux-builder adapter owns its upstream UI dependencies.

## Public hosting boundary

The hosting layer resolves typed profiles and constructs explicitly selected public factories. Local development and embedding use the same asynchronous lifecycle contract.

Services declare owned or borrowed lifetime. Required components must prepare successfully before readiness. Cleanup retains unresolved resource outcomes.

## Verify the actual boundary

The design requires import, public-surface, size, complexity and test-count gates before dependent source features. Installed wheels must demonstrate their actual dependency closures.

Offline doubles, native database observations and browser journeys provide different evidence. A diagram or valid configuration cannot establish production support.

## Follow one operation

An admitted operation arrives through a route, tool or UI binding. The host resolves its actor, checks permission and confirmation, then dispatches to the selected provider.

The provider retains its native result or safe refusal. The host records the authorized outcome; an uncertain effect remains uncertain until its owner resolves it.

[Read the architecture record](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/architecture.md) or inspect the [quality contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md).
