<!-- helix:publish audience=developer page=composition kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/1984ed399bfbb119 -->
<!-- helix:source docs/helix/01-frame/features/FEAT-009-composition-and-hosting.md sha256:fefdffd0c6d1e34c -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-003-composition.md sha256:d1a88cf57bd00157 -->
<!-- helix:source docs/helix/01-frame/user-stories/US-001-assess-composition.md sha256:2b7f7c973b5a5fd4 -->
<!-- helix:source docs/helix/02-design/adr/ADR-005-sdk-series-and-cohort-compatibility.md sha256:4ca6d0d532ec0eba -->

# Compose an application

An application declares the capabilities it needs. A host selects installed providers that satisfy them. This separates business intent from deployment products.

## Start with native meaning

UMF documents describe data, actions and their native identities. Batten's proposed application extension connects those declarations to capability requirements and reviewed procedural hooks.

A handler reference names an installed, admitted implementation. The reference grants no permission and installs no code.

## Select a module closure

A module describes its provided interfaces, dependencies, settings and supported execution placements. The host checks those descriptors against its exact installed cohort.

Required dependencies resolve transitively. Ambiguous providers need an explicit choice. Headless applications can omit UI modules and their dependencies.

An optional missing component stays explicitly inactive. An operation that requires it cannot remain eligible.

## Assess before effects

The proposed assessor checks immutable metadata without importing application or provider code. It reports missing capabilities, incompatible versions, cycles, unsupported placement and relevant unknown semantics.

An eligible plan binds the application, host profile, provider cohort and validation evidence. It does not establish readiness or grant authority.

Changed inputs require assessment again. Startup verifies the plan before constructing selected services; invocation still checks current permission.

## Follow a review queue

The fabricated reference application has review records, an agent recommendation and an approval action. Its optional UI binds a review screen to the same operation.

The same application should run through local and embedded bindings. Missing saga support should refuse the saga component without inventing an alternate engine.

[Compare hosting patterns](hosting.md) or inspect the [composition contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-003-composition.md).
