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

Batten helps application builders design data structures, act on them, and deliver
a user interface within a constrained technology space, with deployment and
integration handled around their application.

## Positioning

For developers building applications with UMF, Tether, Weft, and Arras, Batten is
an application software development kit (SDK) that brings modeling, behavior,
and interface delivery into a coherent authoring experience.

The initial alternative is assembling these libraries and a UI host independently.
[Adjacent prior art](research/convex.md) shows how a coordinated data/function/client
model can reduce setup work. Batten's proposed distinction is a constrained
application experience grounded in the named Novirhyza foundations. Demand for
that distinction remains an assumption to test with the first workflow.

## Vision

An application builder expresses the structures and behavior their app needs,
connects an interface, and delivers a usable application through a defined host
boundary. The surrounding tools carry the integration and delivery work that
would otherwise be repeated for each app.

**North Star**: Reduce the app-specific integration work required to take a
modeled workflow through an action to a usable interface, measured on real apps.

## User Experience

Illustrative scenario, awaiting the owner's first workflow: a developer models
tasks and their relationships, defines an action to complete a task, and connects
a task list and completion control. They validate the workflow and deliver the
interface through Batten's supported host. They can identify what Batten handles
and what their application must supply.

## Target Market

| Attribute | Description |
|-----------|-------------|
| Who | Initial audience assumption: developers composing the four named foundations into data-oriented apps. First users and workflow remain open. |
| Pain | Each application can require repeated technology selection, wiring, and delivery work. Owner-stated problem; prevalence is unmeasured. |
| Current Solution | Assemble UMF, Tether, Weft, Arras, and an application host independently. |
| Why They Switch | Hypothesis: a constrained authoring path reduces integration effort enough to justify its limits. |

## Key Value Propositions

| Value Proposition | Customer Benefit |
|-------------------|------------------|
| A deliberately constrained technology space | Builders spend less effort selecting and assembling infrastructure. |
| Connected data design, actions, and UI authoring | Builders carry an application concept through to an interactive workflow. |
| Delivery and integration handled around the application | Builders can focus on application behavior within an explicit responsibility boundary. |

## Success Definition

Strategic learning indicators guide refinement; numeric targets await requirements
and a baseline workflow. They establish no release or customer-adoption gates.

| Metric | Measurement |
|--------|-------------|
| Time to first usable workflow | Observe elapsed authoring and setup time for the first real app. |
| App-specific integration effort | Compare custom integration code and manual setup with independent assembly. |
| Constraint usefulness | Record which supported choices help builders and which force workarounds. |

## Why Now

The owner has selected the four foundations as the basis for a new application
SDK. The [foundation survey](research/foundations.md) identifies relevant modeling,
query, action, interface, and agent-session surfaces, alongside unresolved host
responsibilities. This supports investigating their composition; it establishes
neither complete integration readiness nor a market timing claim.
