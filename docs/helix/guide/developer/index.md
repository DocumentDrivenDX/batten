<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 reviewed=2026-11-02/microsite_release_reader/3d34ba8a375671a4 -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:7a27692a25188d22 -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:e50a20aa72953aa2 -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:0d20e13aee47c983 -->

<!-- helix:source docs/helix/04-build/implementation-plan.md sha256:5a5a5bbe91a6f77c -->

<!-- helix:source docs/helix/04-build/batten-app-workflow.md sha256:4d56d64a8364c75c -->

<!-- helix:source docs/helix/05-deploy/runtime-release-0.1.0a1.md sha256:05463eb9e1a57115 -->

<!-- helix:source docs/helix/02-design/contracts/CONTRACT-012-local-operation-host.md sha256:7107fb4919ade466 -->

# Batten

Batten is an application SDK and packaged runtime in the Novirhyza family. Its goal is to reduce the cost and risk of operating hundreds of integrated AI applications on shared infrastructure.

## Declare the application

Describe data and behavior through UMF, the platform's portable modeling foundation. Use typed code hooks for application-specific work. Bind an interface to the same governed operations.

The host supplies identity, permissions, resource bindings and lifecycle. Authors choose capabilities without rebuilding that integration for every application.

## Consume a complete runtime

The design calls for a qualified set of runtime dependencies and deep declarative services. Application authors use the supplied APIs without running pip or npm installation.

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

Application requirements, hosting environments and execution placement are independent choices. The design allows local and embedded hosts to bind the same application artifact to different resources.

A provider must satisfy the required interface and exact compatibility checks. A missing capability produces a clear refusal before execution.


## Explore the design

Enterprise reference apps have independent HELIX specification scopes and shared conformance obligations. The initial UI path is a TypeScript app. Inventory validation checks the specs; complete app support requires actual client, host and provider evidence.

The local runtime preview delivers an approval desk and a visual application registry, with native UMF/Weft persistence on PostgreSQL 18. Separate wheels package the contracts, runtime, table port, native adapter, ASGI transport, local host and app. Qualification is bounded to the recorded cohort and local development identities; the complete fleet remains a design goal. Optional local object storage has its own release. The interactive explorer illustrates the broader contracts and makes no service calls.

[Get the runtime preview](https://github.com/DocumentDrivenDX/batten/releases/tag/runtime-v0.1.0a1) or [read the run instructions](https://github.com/DocumentDrivenDX/batten/blob/main/examples/approval-desk/README.md).

[Compose an application](composition.md), [choose a host](hosting.md), or read the [architecture](architecture.md).

## Test the declared behavior

Authors declare desired behavior and refine it for the application. Batten must expose every fully declarative construct through the CLI and automatically generate property-based end-to-end tests.

That includes complete UI journeys and declarative hook outcomes. Generated sequences check declared invariants through the actual client, host and providers. Missing semantics or required coverage blocks qualification.

The same properties must qualify a candidate platform before migration. Results retain exact inputs, replayable failures and exploration bounds. Arbitrary procedural hooks need explicit semantic test contracts.

## Follow an example

[Walk through the example apps](examples.md), from the local approval desk to the specification journeys for intake, evidence, agents, graphs and service handoff.
