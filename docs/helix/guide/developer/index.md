<!-- helix:publish audience=developer page=index kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/bd5e052e8e86013c -->
<!-- helix:source docs/helix/00-discover/product-vision.md sha256:bb32dd92919bd60f -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:3570b5c283508bf7 -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:9a0974a3fc6dec69 -->

# Batten

Batten is a core-and-extensions SDK for declarative AI applications in the Novirhyza family. Its design combines native application models, typed procedural hooks and reusable hosting.

## Declare the application

Describe data and behavior through UMF, the platform's portable modeling foundation. Use typed code hooks for application-specific work. Bind an interface to the same governed operations.

The host supplies identity, permissions, resource bindings and lifecycle. Authors choose capabilities without rebuilding that integration for every application.

## Choose the capabilities

A small portable core handles admission, authorization, dispatch and dependency lifecycle. Separately installed modules connect tables, ontology, agents, models and other platform services.

UMF owns model, action and saga semantics. Weft supplies query compilation. Arras supplies ontology capabilities, and Tether supplies agent execution. ux-builder supplies UI design artifacts and tooling.

## Keep the application portable

Application requirements, hosting environments and execution placement are independent choices. A local host and an embedded host can bind the same application artifact to different resources.

A provider must satisfy the required interface and exact compatibility checks. A missing capability produces a clear refusal before execution.

## Explore the design

The repository contains requirements, contracts and a proposed architecture. The SDK runtime and installable packages are not implemented. The interactive explorer illustrates those contracts; it does not run or deploy an application.

[Compose an application](composition.md), [choose a host](hosting.md), or read the [architecture](architecture.md).
