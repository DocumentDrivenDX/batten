---
ddx:
  id: batten.product-vision
  type: product-vision
  activity: discover
  authoring:
    home: repo
  links:
    - id: batten.research.foundations
      kind: derived_from
    - id: batten.research.convex
      kind: derived_from
    - id: batten.research.mcp-apps
      kind: derived_from
---

# Batten product vision

## Mission Statement

Batten is a core-and-extensions SDK for declarative AI application development.
Builders compose UMF declarations with typed procedural hooks, choose platform
modules, and deliver interfaces through reusable hosts and ux-builder integration.

## Positioning

For Python plugin authors and the teams embedding their applications, Batten is
an application software development kit (SDK) with explicit platform modules and
one public host boundary. The alternative is assembling platform libraries and
private host wiring for each application.

UMF supplies modeling and typed access, Weft supplies query compilation, Arras
supplies ontology interfaces, and Tether supplies agent execution. UMF owns saga
semantics; Batten binds qualified executors without defining a second saga language.
ux-builder owns UI design, components and themes. Batten connects declarations,
typed clients and hosting without duplicating those platform responsibilities.

## Vision

A builder models application data, declares its operations, connects an interface,
and runs the same application through development and deployed hosts. Each module
has one platform responsibility, a documented public surface, and enforced
dependency rules. A host embeds Batten without exposing its private internals.

**North Star**: Reduce application-specific integration work from a declared
workflow to a working interface, measured against independent assembly.

## User Experience

A developer defines a fabricated task board using native UMF documents, typed
reads, and declared actions. They attach a screen, a chat tool, and a scheduled
summary to those operations, then run it locally with fabricated identities and
PostgreSQL 18. The host enforces permissions and row scope and displays its audit
outcomes. The developer builds an application artifact that the deployed host
can admit through its published contract.

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | Python developers building trusted first-party data applications; host teams providing their execution environment. |
| Pain | Development tooling and applications can depend on private host construction, identity, configuration, and database helpers. |
| Current Solution | Compose modeling, query, action, agent, and UI capabilities with application-specific host integration. |
| Why They Switch | A stable public host contract and platform modules let them change applications without repeatedly rebuilding that wiring. |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| Native platform capabilities | Authors use the platform's supported semantics without maintaining duplicate compilers or engines. |
| Explicit module and permission boundaries | Authors and host owners can see what an application depends on and may reach. |
| Shared development and deployed host contract | Local work exercises the same admission and execution behavior that deployment consumes. |
| Independent application delivery | A reviewed application update can be admitted without rebuilding unrelated applications. |

## Success Definition

| Indicator | Measurement |
|-----------|-------------|
| Authoring effort | Observe time and manual steps from a native model to a working fabricated workflow. |
| Integration effort | Count host-specific glue and private import dependencies required by a second host. |
| Contract clarity | Record compatibility refusals and workarounds encountered by real application authors. |

The owner supplies numeric targets after baseline workflows are measured.
These learning indicators establish no customer-adoption gate.

## Why Now

The [boundary survey](current-state-inventory-boundaries.md) identifies concrete
coupling between an existing development host and its application, alongside
compiler, worker, testing, and packaging responsibilities in one SDK. The owner
has chosen a cleanroom implementation with native platform dependencies. That
creates a defined opportunity to establish public boundaries before more
applications depend on private wiring.
