---
ddx:
  id: batten.concerns
  type: concerns
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.product-vision
      kind: derived_from
---

# Project concerns

## Active Concerns

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| modularity-and-encapsulation | library; selection source: baseline-policy | all | Handwritten SDK and UI source is expected from the owner's product intent. | Design names owners, public surfaces, integration boundaries, permitted dependencies, and checkers with negative controls before dependent source work. |

## Area Labels

- `area:ui` — application interfaces and components.
- `area:api` — application behavior and public service surfaces.
- `area:data` — structures, queries, actions, and storage interactions.
- `area:infra` — host integration and delivery mechanisms.
- `area:cli` — developer command-line tools, if selected.
- `area:docs` — product and developer documentation.

## Project Overrides

No baseline practices are overridden. Genesis does not select technology slots:
the owner will provide further requirements before Frame resolves runtime,
frontend, datastore, identity, deployment, and architecture choices. Sibling
stacks and shipped catalog defaults are context, not Batten decisions.

## Concern Conflicts

No practice conflict was identified in the single selected baseline. Revisit
composition when Frame selects additional concerns.

Observability and formal-methods applicability remain open until the first
workflow, runtime surfaces, and material failure costs are known.
