---
ddx:
  id: batten.boundary-audit
  type: current-state-inventory
  activity: discover
  authoring:
    home: repo
  links: []
---

# Current-State Inventory: SDK boundaries

The reference SDK bundles portable declarations, compiler behavior, execution,
tests, and tooling. Its development host relies on application internals.
Structural separation is incomplete even where direct SDK-to-host imports are absent.

## Scope and Boundary

- Estate: the owner's read-only reference SDK, development host, and host plugin
  modules, inspected 2026-10-29. Source-specific names stay in the separate private
  audit packet; Batten owns no dependency on that application.
- Method: Python abstract syntax tree (AST) import census, physical line counts,
  module classification, literal dynamic-import/discovery review, and consumer census.
- Evidence: `boundary-audit/modules.csv`, `import-graph.csv`, `external-nodes.csv`
  and `summary.json`, generated from that census on 2026-10-29.
- Excluded: executing reference code, private operational data, credentials,
  source history, runtime import tracing, and live platform qualification.
- Owner: Erik LaBianca.

## Evidence Grades

| Grade | Means |
|-------|-------|
| Evidenced | A dated census demonstrates the structural observation only. |
| Partial | A material structural or behavior fact remains unrecorded. |
| Assumed | A claim has no inspected source. |
| Aspirational | Desired behavior rather than an observed component. |
| Spike-open | An unknown blocks a particular design decision. |

## Inventory

Each module has exactly one primary classification in `modules.csv`; mixed
responsibilities retain an explicit role. The table aggregates those assignments.
The contract category includes host contract implementations as well as declarations.

| Component classification | Modules | Grade | Evidence |
|--------------------------|---------|-------|----------|
| Contract/declaration and host orchestration | 75 | Evidenced | AST census, 2026-10-29 |
| Testing | 16 | Evidenced | AST census, 2026-10-29 |
| Packaging and CLI | 27 | Evidenced | AST census, 2026-10-29 |
| Tables/compiler | 18 | Evidenced | AST census, 2026-10-29 |
| Worker/isolation | 29 | Evidenced | AST census, 2026-10-29 |
| Databricks adapter | 16 | Evidenced | AST census, 2026-10-29 |
| PostgreSQL/Lakebase adapter | 21 | Evidenced | AST census, 2026-10-29 |
| Model-gateway adapter | 1 | Evidenced | AST census, 2026-10-29 |
| Development host | 20 | Evidenced | AST census, 2026-10-29 |

The census covers 117 SDK modules, 20 development-host modules, and 86 host
plugin modules. Physical line counts, including blanks and docstrings, are
20,487, 2,267, and 19,916 respectively; estimates from intake are not used as measurements.

There are 2,359 static import edges, including nested and type-only imports.
The graph also represents eight reviewed dynamic-import/discovery sites, using
explicit unresolved-target nodes where runtime observation is required. Three
static strongly connected components contain six, two, and three modules;
`static-cycles.csv` lists their members. Nested/type-only edges do not by themselves
prove a failing runtime circular import. One classic browser-script resource has
no static/dynamic import-pattern matches; it was not executed by this survey.
Ten development-host import sites reach application internals; one additional
site discovers the application dynamically. Checkout-path recognition also couples
installation to the source tree. The SDK has no static application import in this
census. Optional YAML and a lazy web-framework import still need dependency scoping.

The private packet lists all eleven sites and exact locations, all source module
names, and their crosswalk to the anonymous graph IDs. The public graph retains
external-inventory nodes explicitly. It does not hide an edge because its target
lies outside the selected module set.

The consumer census finds 90 SDK/development-host/package references in both
installed-plugin and hosted-plugin trees. One tree contains 86 Python files;
the hosted tree contains declarations without Python. These remain distinct
consumer forms for later compatibility assessment.

## Totals

| Grade | Classification entries | Modules |
|-------|------------------------|---------|
| Evidenced | 9 | 223 |
| Partial | 0 | 0 |
| Assumed | 0 | 0 |
| Aspirational | 0 | 0 |
| Spike-open | 0 | 0 |

Zero inventory entries lack structural evidence. None of these counts establishes
runtime behavior, platform support, or completeness of computed imports.

## Open Questions

| Question | Blocks | Owner |
|----------|--------|-------|
| Which computed import targets actually load on each execution path? | A complete runtime import claim | Batten implementation owner |
| Which exact platform release cohort preserves all required behaviors? | Compatibility support claim | Erik LaBianca and platform maintainers |
| Which legacy interfaces must the consuming host preserve? | Later consumer transition acceptance | Consuming-host owner |
