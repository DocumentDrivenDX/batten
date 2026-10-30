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
