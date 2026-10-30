<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/118d11d5bee90a6c -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:34b99ee7b0cd2742 -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:44209bdd519038ed -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:ffb0e445269fc317 -->

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

## Follow each decision

The default command/query model separates business changes from reads. Every system interaction retains its initiating user, delegation and effective execution identity where available.

OpenTelemetry instrumentation follows database, messaging, model and other service calls. Durable audit survives trace sampling, and unsupported native attribution remains explicit.

## Choose the capabilities

A small portable core handles admission, authorization, dispatch and dependency lifecycle. Separately installed modules connect tables, ontology, agents, models and other platform services.

UMF owns model, action and saga semantics. Weft supplies query compilation. Arras supplies ontology capabilities, and Tether supplies agent execution. ux-builder supplies UI design artifacts and tooling.

## Keep the application portable

Application requirements, hosting environments and execution placement are independent choices. A local host and an embedded host can bind the same application artifact to different resources.

A provider must satisfy the required interface and exact compatibility checks. A missing capability produces a clear refusal before execution.

## Explore the design

The repository contains requirements, contracts and a proposed architecture. The SDK runtime and installable packages are not implemented. The interactive explorer illustrates those contracts; it does not run or deploy an application.

[Compose an application](composition.md), [choose a host](hosting.md), or read the [architecture](architecture.md).
