<!-- helix:publish audience=developer page=composition kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/c1f1be2f7f852967 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-009-service-discovery-and-binding.md sha256:53b8b2e0e2ef2dc3 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-010-platform-assets.md sha256:37a6ebc7946ae5b4 -->
<!-- helix:source docs/helix/01-frame/features/FEAT-009-composition-and-hosting.md sha256:ad49c3fcde9f276e -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-003-composition.md sha256:82fd01c7c975cb5a -->
<!-- helix:source docs/helix/01-frame/user-stories/US-001-assess-composition.md sha256:2b7f7c973b5a5fd4 -->
<!-- helix:source docs/helix/02-design/adr/ADR-005-sdk-series-and-cohort-compatibility.md sha256:ab9d3cdd3a48ecfd -->

<!-- helix:source docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md sha256:4b3b0e0324fa4e84 -->

# Compose an application

An application declares the capabilities it needs. A host selects installed providers that satisfy them. This separates business intent from deployment products.

## Start with native meaning

UMF documents describe data, actions and their native identities. Batten's proposed application extension connects those declarations to capability requirements and reviewed procedural hooks.

A handler reference names an installed, admitted implementation. The reference grants no permission and installs no code.

## Select a module closure

A module describes its provided interfaces, dependencies, settings and supported execution placements. The host checks those descriptors against its exact installed cohort.

Required dependencies resolve transitively. Ambiguous providers need an explicit choice. Headless applications can omit UI modules and their dependencies.

An optional missing component stays explicitly inactive. An operation that requires it cannot remain eligible.

## Use the supplied runtime

Platform owners package a complete qualified runtime from the selected modules and their dependencies. Application authors use supplied APIs without installing packages through pip or npm.

The platform requires assertions and behavioral coverage for declared application behavior. Candidate runtime upgrades must qualify against current evidence from affected applications and their declared integrations.

## Declare platform assets

An application can include native deployment packages, require resource contracts managed elsewhere, or combine both. Its immutable inventory includes the package sources and exact contracts.

The optional platform wrapper handles these declarations. Provider adapters interpret native formats; core continues to assess ordinary capabilities. External dependencies grant no authority to deploy or modify their assets.

## Assess before effects

The proposed assessor checks immutable metadata without importing application or provider code. It reports missing capabilities, incompatible versions, cycles, unsupported placement and relevant unknown semantics.

An eligible plan binds the application, host profile, provider cohort and validation evidence. It does not establish readiness or grant authority.

Changed inputs require assessment again. Startup verifies the plan before constructing selected services; invocation still checks current permission.

## Bind resources and shared services

An authorized operator plans and applies deployment separately. Host startup checks required receipts, readiness and current access; startup never applies a deployment or migration.

Shared-service requirements reference exact semantic interfaces and provider exports. Discovery filters visible metadata, while host-approved bindings still require current invocation permission.

## Follow a review queue

The fabricated reference application has review records, an agent recommendation and an approval action. Its optional UI binds a review screen to the same operation.

The same application should run through local and embedded bindings. Missing saga support should refuse the saga component without inventing an alternate engine.

[Compare hosting patterns](hosting.md) or inspect the [composition contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-003-composition.md).
