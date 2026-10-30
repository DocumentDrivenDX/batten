<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/fleet_alignment_reader/60326208c908ecc4 -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:a5beca963fd573ca -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:ffee14faf077b38c -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:ebb43c32ec3db5ba -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-002-boundaries-and-quality.md sha256:5cb8aef4c04f1c57 -->

# Batten

Batten is an application SDK and packaged runtime in the Novirhyza family. Its goal is to reduce the cost and risk of operating hundreds of integrated AI applications on shared infrastructure.

## Declare the application

Describe data and behavior through UMF, the platform's portable modeling foundation. Use typed code hooks for application-specific work. Bind an interface to the same governed operations.

The host supplies identity, permissions, resource bindings and lifecycle. Authors choose capabilities without rebuilding that integration for every application.

## Consume a complete runtime

The platform supplies a qualified set of runtime dependencies and deep declarative services. Application authors use the supplied APIs without running pip or npm installation.

Platform owners qualify dependency upgrades against affected application assertions, behavioral test coverage and required telemetry. Changed application or runtime inputs require fresh evidence.

## Share services with explicit boundaries

The design targets hundreds of applications sharing infrastructure, with per-application identity, limits, attribution and lifecycle control. Actual capacity requires measured workloads and service budgets.

Applications integrate through declared graph API capabilities and future defined interfaces. Each interaction checks current authority and target access; a graph relationship grants no permission.

## Test the declared behavior

Authors declare desired behavior and refine it for the application. Batten must expose every fully declarative construct through the CLI and automatically generate property-based end-to-end tests.

That includes complete UI journeys and declarative hook outcomes. Generated sequences check declared invariants through the actual client, host and providers. Missing semantics or required coverage blocks qualification.

The same properties must qualify a candidate platform before migration. Results retain exact inputs, replayable failures and exploration bounds. Arbitrary procedural hooks need explicit semantic test contracts.

## Choose the capabilities

A small portable core handles admission, authorization, dispatch and dependency lifecycle. Separately installed modules connect tables, ontology, agents, models and other platform services.

UMF owns model, action and saga semantics. Weft supplies query compilation. Arras supplies ontology capabilities, and Tether supplies agent execution. ux-builder supplies UI design artifacts and tooling.

## Keep the application portable

Application requirements, hosting environments and execution placement are independent choices. A local host and an embedded host can bind the same application artifact to different resources.

A provider must satisfy the required interface and exact compatibility checks. A missing capability produces a clear refusal before execution.

## Explore the design

The repository contains requirements, contracts and a proposed architecture. The SDK runtime and installable packages are not implemented. The interactive explorer illustrates those contracts; it does not run or deploy an application.

[Compose an application](composition.md), [choose a host](hosting.md), or read the [architecture](architecture.md).
