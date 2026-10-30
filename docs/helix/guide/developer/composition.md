<!-- helix:publish audience=developer page=composition kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/fleet_alignment_reader/0ea4c7bd1018b8de -->
<!-- helix:source docs/helix/01-frame/features/FEAT-009-composition-and-hosting.md sha256:107baf00adf9690e -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-003-composition.md sha256:24a8f4d0f0ca8d00 -->
<!-- helix:source docs/helix/01-frame/user-stories/US-001-assess-composition.md sha256:2b7f7c973b5a5fd4 -->
<!-- helix:source docs/helix/02-design/adr/ADR-005-sdk-series-and-cohort-compatibility.md sha256:ab9d3cdd3a48ecfd -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md sha256:5cb8aef4c04f1c57 -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:ffee14faf077b38c -->

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

## Test the declared behavior

Authors declare desired behavior and refine it for the application. Batten must expose every fully declarative construct through the CLI and automatically generate property-based end-to-end tests.

That includes complete UI journeys and declarative hook outcomes. Generated sequences check declared invariants through the actual client, host and providers. Missing semantics or required coverage blocks qualification.

The same properties must qualify a candidate platform before migration. Results retain exact inputs, replayable failures and exploration bounds. Arbitrary procedural hooks need explicit semantic test contracts.

## Assess before effects

The proposed assessor checks immutable metadata without importing application or provider code. It reports missing capabilities, incompatible versions, cycles, unsupported placement and relevant unknown semantics.

An eligible plan binds the application, host profile, provider cohort and validation evidence. It does not establish readiness or grant authority.

Changed inputs require assessment again. Startup verifies the plan before constructing selected services; invocation still checks current permission.

## Follow a review queue

The fabricated reference application has review records, an agent recommendation and an approval action. Its optional UI binds a review screen to the same operation.

The same application should run through local and embedded bindings. Missing saga support should refuse the saga component without inventing an alternate engine.

[Compare hosting patterns](hosting.md) or inspect the [composition contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-003-composition.md).
