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

The owner authorized defaults for the proposal except the explicitly open policy
decisions. Selection sources distinguish rulings from proposed defaults.

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| modularity-and-encapsulation | library; baseline-policy | all | Handwritten SDK, adapters, and UI require enforceable ownership. | Public surfaces, import allowlists, cycle/private-access checks, and negative controls. |
| python-uv | library; assumption/default, ADR-001 | all | Python plugin and host consumers need independent installed artifacts. | Python 3.11 consumer floor; uv locks/builds, Ruff, strict Pyright, pytest; no runtime installer. |
| hexagonal-architecture | library; assumption/default, ADR-001 | all | UI, tools, jobs, and tests drive one core over multiple platform providers. | Core owns ports; adapters translate; concrete services wired only at host composition. |
| code-shape-ceilings | library; baseline-policy | all | This is greenfield source. | Strict ceilings and downward ratchets, no source exceptions; CONTRACT-002 owns values. |
| testing | library; operator-override, ADR-007 | all | Consumer behavior and permission boundaries need evidence with minimal duplication. | One test per observable behavior; tables of cases; public boundaries; no growth by renaming or indirection. |
| authorization-model | library; operator-override | api | Trusted applications still need explicit permission containment. | Central deny-by-default decision; actor before access; negative cases; host and database permissions compose. |
| model-gateway | library; operator-override | api, infra | Completion/embedding access uses host-managed routes and attribution. | Product aliases; one adapter owns gateway calls; qualify actual features and identity; no duplicate retry layer. |
| native-platform-libraries | project-local; operator-override, ADR-002 | all | UMF, Weft, Arras, and Tether are platform capabilities. | Depend on public upstream packages; no compiler/engine vendoring; preserve exact meaning and evidence scope. |
| platform-adapter-ownership | project-local; operator-override, ADR-001 | api, data, infra | Databricks, PostgreSQL 18, Lakebase, and gateway have different dependencies. | Isolated dependency closure, native clients at owning boundaries, platform facts qualified on a pinned cohort. |
| browser-client | project-local; assumption/default, ADR-001 | ui | Screens and views need a browser bridge, not Python host objects. | Browser-compatible JavaScript; TypeScript/Bun build tools outside runtime; no shell imports; Chromium/Playwright qualification. |
| typed-file-configuration | project-local; operator-override, ADR-006 | all | Files are authoritative; no new environment variables. | Immutable typed settings, explicit layers, injected identity/services, redacted diagnostics. |
| cleanroom-public-artifacts | project-local; operator-override | all | Batten is independently implemented and openly distributable. | MIT OR Apache-2.0, copyright Synaptiq; no private source/history, client identities, credentials, or operational data. |

The project-local concerns declare their scopes and practices here. They do not
select a private design system, identity provider, or platform deployment topology.
This is a library/host SDK: those exclusive slots remain host-owned. Frontend
framework is also author/host-owned; the bridge itself uses browser APIs.

## Project Overrides

| Concern | Practice | Override | Authority |
|---------|----------|----------|-----------|
| python-uv | Environment precedence | Layered typed files win; only already-supported host environment fallback may fill absent values. No new environment names or dotenv loading. | Owner ruling; ADR-006 |
| python-uv | Settings dependency in all packages | Portable contracts/runtime stay stdlib-only; host configuration uses Pydantic Settings at composition. | ADR-001, ADR-006 |
| code-shape-ceilings | Strict default branches/test size | Use the stricter observed reference limits: branches 9, test files 488 lines; source files 500 and public methods 15 use stricter greenfield defaults. | ADR-007; CONTRACT-002 |
| testing | Multi-layer strategy | Give each behavior one primary test; another layer requires a distinct outcome. No numeric coverage floor or test budget is invented. | Owner ruling; ADR-007 |

## Area Labels

- `area:ui` — browser client, host-drawn controls, and screen/view integration.
- `area:api` — contracts, host runtime, operations, workers, and permissions.
- `area:data` — native modeling, typed reads/actions, PostgreSQL, ontology, and migrations.
- `area:infra` — platform adapters, release artifacts, and host configuration.
- `area:cli` — author tools and development supervision.
- `area:docs` — requirements, reference documentation, and executable guides.

## Concern Conflicts

Python and browser tooling apply to different source scopes. The browser client
does not select a second backend runtime. Configuration precedence explicitly
overrides the Python concern's environment-first default. Native third-party
dependencies remain outside the portable contracts/runtime closure.

The first code slice must wire real boundary, shape, and test-count checks before
dependent features. The current review authorizes their contracts, not their code.
Observability is required as a product surface; exporter/protocol/version details
will be selected in a focused contract before any integration support claim.
