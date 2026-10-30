<!-- helix:publish audience=developer page=architecture kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/4a346c747c170527 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-001-public-host-api.md sha256:496f18dd0d526258 -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:0d20e13aee47c983 -->
<!-- helix:source docs/helix/02-design/adr/ADR-001-platform-modules-and-neutral-core.md sha256:f845d229ffe50254 -->
<!-- helix:source docs/helix/02-design/adr/ADR-003-platform-wheel-distribution.md sha256:de51435c7c5bc7cd -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md sha256:4b3b0e0324fa4e84 -->
<!-- helix:source docs/helix/03-test/test-plan.md sha256:3b4e83eec6fa7988 -->
<!-- helix:source docs/helix/02-design/adr/ADR-007-quality-and-test-ratchets.md sha256:abdbdc7e0dc65782 -->

<!-- helix:source docs/helix/02-design/contracts/CONTRACT-010-platform-assets.md sha256:37a6ebc7946ae5b4 -->
<!-- helix:source docs/helix/02-design/adr/ADR-012-generic-platform-assets.md sha256:1c38e89475ee2c90 -->

# A small core, explicit boundaries

Batten's architecture separates application contracts, generic execution policy, platform adapters and host composition. Concrete services are wired at the host boundary.

## Portable core

The contracts and runtime are designed to use Python's standard library. The core owns generic capability and lifecycle rules; it has no ontology-specific branches or native vendor types.

Native UMF validation belongs in its adapter. The core receives validated metadata projections and uses them to assess dependencies without importing provider code.

## Explicit platform modules

Separate wheels follow platform responsibilities. Tables, PostgreSQL, Lakebase, Databricks, gateway, ontology and agent integration have their own dependency boundaries.

The browser client is independent of Python host objects. Its optional ux-builder adapter owns its upstream UI dependencies.

## Package and qualify the runtime

The optional platform wrapper defines resource contracts and deployment protocols. Databricks bundle tooling stays in its adapter. Operators deploy assets separately; core consumes generic admission results and scoped runtime capabilities.

Platform owners assemble selected modules and their dependencies into a complete runtime. Application delivery consumes that runtime without pip or npm installation.

Dependency upgrades must qualify against affected application assertions, behavioral coverage and required telemetry. Evidence is tied to exact application and runtime artifacts. Missing or stale evidence blocks qualification.

## Operate a shared fleet

The design targets hundreds of applications sharing declarative services. Hosts enforce application and owner limits, fairness, lifecycle and diagnostic attribution. Capacity and failure domains require measured evidence.

Graph API integration uses public provider boundaries and current grants. Core remains generic; the owning provider retains graph semantics.

## Public hosting boundary

The hosting layer resolves typed profiles and constructs explicitly selected public factories. Local development and embedding use the same asynchronous lifecycle contract.

Services declare owned or borrowed lifetime. Required components must prepare successfully before readiness. Cleanup retains unresolved resource outcomes.

## Preserve commands and attribution

Command Query Responsibility Segregation (CQRS) separates state-changing commands from queries. The host preserves those rules across routes, tools, screens and background work.

Trusted invocation context follows the initiating user and effective principal through workers and service calls. Telemetry cannot grant authority, and reused connections must not leak identities.

OpenTelemetry instrumentation belongs to host and provider adapters, keeping the portable core free of concrete SDK dependencies. Durable audit remains independent of sampled traces.

## Verify the actual boundary

The design requires import, public-surface, size, complexity and test-count gates before dependent source features. Installed wheels must demonstrate their actual dependency closures.

Offline doubles, native database observations and browser journeys provide different evidence. A diagram or valid configuration cannot establish production support.

## Follow one operation

An admitted operation arrives through a route, tool or UI binding. The host resolves its actor, checks permission and confirmation, then dispatches to the selected provider.

The provider retains its native result or safe refusal. The host records the authorized outcome; an uncertain effect remains uncertain until its owner resolves it.

[Read the architecture record](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/architecture.md) or inspect the [quality contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md).

## Test the declared behavior

Authors declare desired behavior and refine it for the application. Batten must expose every fully declarative construct through the CLI and automatically generate property-based end-to-end tests.

That includes complete UI journeys and declarative hook outcomes. Generated sequences check declared invariants through the actual client, host and providers. Missing semantics or required coverage blocks qualification.

The same properties must qualify a candidate platform before migration. Results retain exact inputs, replayable failures and exploration bounds. Arbitrary procedural hooks need explicit semantic test contracts.
