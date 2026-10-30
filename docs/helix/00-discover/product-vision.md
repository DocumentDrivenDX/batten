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

Batten is a core-and-extensions SDK and packaged runtime for declarative AI
applications. Its goal is to let teams build and operate hundreds of integrated
applications on shared infrastructure while the platform manages dependency
evolution, observability and compatibility. Builders compose deep declarative
services with typed procedural hooks and ux-builder interfaces.

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

**North Star**: Reduce the ongoing cost and risk of building, operating and
upgrading a fleet of integrated applications through one governed runtime.
Reducing application-specific integration work is an enabling outcome.

The platform supplies a complete, qualified runtime cohort. Application authors
use its supplied APIs and services without application-level pip/npm installation.
Operators compose optional modules into reviewed runtime artifacts at platform
build time; application admission cannot expand that dependency closure.

The bounded dependency and capability surface lets the platform require telemetry,
assertions and behavioral test coverage, then qualify dependency upgrades against
application evidence before rollout. Applications share governed semantic types
and discover services through Batten's platform ontology. Declared exports, requirements and host-approved bindings
connect applications through qualified graph, table, API or messaging profiles,
preserving resource ownership and current authorization. Shared infrastructure
retains per-application attribution,
limits and lifecycle control. Hundreds of applications is the owner's scale
objective; exact capacity and upgrade-safety claims require measured evidence.

Every system interaction is attributable to its initiating user or explicit
non-user authority through delegated and background execution. Builders use a
command/query model by default, and operators can reconstruct decisions and
outcomes across data, messaging and AI services without exposing private payloads.

## User Experience

Applications may carry native deployment packages and require externally managed
resource contracts through a generic platform wrapper. Operators deploy and
verify those assets separately from runtime startup. Provider syntax and native
resource identity stay behind adapters; persistent data retains one lifecycle owner.

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
| Qualified packaged runtime | Application delivery needs no package installation; platform owners qualify a common dependency cohort. |
| Enforced observability and verification | Required telemetry, assertions and behavior coverage make application outcomes inspectable and upgrades assessable. |
| Shared fleet operation | Declarative services amortize runtime and infrastructure costs across hundreds of applications, subject to capacity qualification. |
| Governed application integration | Graph API and future defined mechanisms connect applications through explicit contracts and permission boundaries. |
| Explicit module and permission boundaries | Authors and host owners can see what an application depends on and may reach. |
| Shared development and deployed host contract | Local work exercises the same admission and execution behavior that deployment consumes. |
| Independent application delivery | A reviewed application update can be admitted without rebuilding unrelated applications. |

## Success Definition

| Indicator | Measurement |
|-----------|-------------|
| Authoring effort | Observe time and manual steps from a native model to a working fabricated workflow. |
| Integration effort | Count host-specific glue and private import dependencies required by a second host. |
| Contract clarity | Record compatibility refusals and workarounds encountered by real application authors. |
| Upgrade safety and effort | Compare candidate cohorts against affected application assertions, coverage and telemetry; measure regressions, qualification effort and recovery outcomes. |
| Fleet efficiency and isolation | Measure resource cost, concurrency, fairness and cross-application interference across a fabricated fleet targeting hundreds of applications. |
| Integration control | Exercise authorized graph interactions and denied cross-application access, including dependency changes and revocation. |

The owner supplies numeric acceptance thresholds after baseline workflows are measured;
the hundreds-of-applications scale objective is already owner-selected.
These learning indicators establish no customer-adoption gate.

## Why Now

The [boundary survey](current-state-inventory-boundaries.md) identifies concrete
coupling between an existing development host and its application, alongside
compiler, worker, testing, and packaging responsibilities in one SDK. The owner
has chosen a cleanroom implementation with native platform dependencies. That
creates a defined opportunity to establish public boundaries before more
applications depend on private wiring.
