# Batten intent and intake

## Accepted direction

Source: owner instructions and answers in this conversation, 2026-10-29.

Batten is the Novirhyza application SDK. It constrains the technology design space
so authors can design data structures, act on them, and deliver UI without
repeating deployment/integration work. It is independently implemented from
behavioral requirements and read-only boundary evidence. It imports no private
host application and carries no private source or history.

Public platforms are supplied as dependencies: UMF, Weft, Arras, and Tether.
Native UMF documents and typed access are the authoring contract; consuming hosts
own legacy format/API translation. PostgreSQL 18 only; async-first; layered typed
files with environment as last resort and no new environment names. MIT OR
Apache-2.0, copyright Synaptiq. Fabricated data only. Plugins are trusted
first-party code; the sandbox provides permission containment.

The first reviewed behavioral suite establishes the measured test-count ceiling;
it only decreases afterward. The owner is considering the ontology-provider
module boundary. The proposal places it in a normal Batten platform module and
requires zero ontology-specific core capabilities.

## Packaged runtime and fleet direction

Source: owner clarification and authorization to integrate and realign, 2026-10-29.
The complete packaged runtime and deep declarative services are central product
value. Application authors must not need pip/npm installation. The platform owns
qualification of dependency upgrades across applications, enforces telemetry,
assertions and behavioral test coverage, and bounds out-of-scope behavior.

The scale objective is hundreds of applications sharing infrastructure and
integrating through the graph API and future defined mechanisms. It is an owner
goal, not an observed capacity result. Exact load mix, service budgets, upgrade
policy thresholds and graph integration profiles need design and qualification.
Separate platform-module distributions remain compatible with this direction:
platform assembly resolves a cohort once; applications consume the complete
runtime. This authorizes document alignment, retaining the source/build review gate.

## Semantic testing and platform migration direction

Source: owner direction in this conversation, 2026-10-29. Batten must expose
application intent and use-case refinements as testable semantics. Every default
fully declarative construct, including composed UI and declarative hooks, must
expose its complete functionality through the CLI and automatically produce
property-based end-to-end tests. Every fully declarative UI-and-hook implementation
must receive an automatic conformance verdict, reusable to qualify migration to
new platforms. Missing semantics, oracles or execution coverage cannot silently
pass. This direction authorizes specification and integration, not runtime code.

## Authorized scope

Deliver the product vision, PRD, concerns, feature registry, boundary audit,
proposed module/distribution/public-host API split, decision records, and ddx
work items. This includes specification of the eventual mechanical checks.

Wait for owner review before writing a migration plan, executable quality gates,
or product code. Do not edit the read-only reference checkout, copy its history,
push, create a remote repository, or commit without instruction.

## Decision ownership

[Decision points](../01-frame/decision-points.md) retain open policy questions
with owners and affected scope. Upstream library maintainers own native semantics
and qualification. Host operators own deployment topology, identity providers,
resource provisioning, policy authority, and legacy behavior compatibility.

## Next action

Review the product scope and module boundaries, especially the ontology-neutral
core and generic provider lifecycle. After review, resolve affected policy
questions and prepare the separate two-repository consumer transition plan with
installed and hosted consumer forms and green checks at each slice.

## Composition and hosting direction

The owner authorized the next requirements/contracts/ddx packet following the
core-and-extensions discussion. Native UMF is the declarative foundation, UMF
owns saga semantics, and ux-builder supplies the UI design/tooling integration.
Selectable modules, host profiles and execution placement are independent. This
authorization advances design and tracking; it does not authorize source code,
migration, deployment, commits or pushes. The original consumer-transition
requirements remain in scope for their later separately reviewed plan.

## Interaction composition and extension direction

Source: owner direction, 2026-10-29. Start with declarative application manifests,
UMF and UMF extensions. Supply high-level semantic controls through ux-builder,
including wizards, grouped/scrollable forms and editable collections. Preserve
composition and detailed application-local control implementations in Python
and/or TypeScript. Local code is an ordinary escape hatch, not a platform exception.

Adding third-party packages through pip/npm or equivalent dependency mechanisms
is an exceptional platform extension. Using the already selected platform's public
APIs does not add a dependency. Applications cannot expand the installed cohort.
A terminal user interface (TUI) is a design target for the same application
meaning; support must be qualified per control and renderer. This authorizes
requirements/contracts/test allocation, retaining the existing source review gate.
