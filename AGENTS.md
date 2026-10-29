# Working in Batten

Batten is an open-source application SDK in the Novirhyza family. Start with
`docs/helix/README.md`, the product vision, PRD, concerns, and relevant contracts.

## Scope and handling

- Use the installed HELIX skill. Read `.helix.yml`; keep project artifacts under
  `docs/helix/` and resolve graph/templates/prompts/meta from the installed plugin.
  Read governing artifacts before downstream work; preserve IDs, frontmatter,
  deliberate trace links, and unknown extension content.
- MIT OR Apache-2.0; copyright Synaptiq. Use fabricated data only. No credentials,
  tokens, token-shaped literals, private client material, or operational data.
- Cleanroom implementation: reference evidence informs behaviors and boundaries.
  Do not copy private source, tests, documents, or git history. Do not depend on,
  locate, or import a consuming application's internals. Source-specific audit
  material stays outside this repository.
- Native UMF authoring and typed access are settled. Use public UMF, Weft, Arras,
  and Tether dependencies; do not vendor or reimplement their engines. The
  consuming host owns legacy compatibility. Qualify support by cohort, subset,
  and observed evidence; make unsupported meaning and loss explicit.
- Plugins are trusted first-party code; containment limits permissions. Do not
  claim hostile-code security. No new environment variables. Resolve typed file
  configuration once at composition, with environment only as explicit fallback.
- Public I/O is async-first. Pure declarations/factories/planners may be sync.
  PostgreSQL 18 is the only supported database major.
- Do not introduce a framework/runtime/dependency without a selected concern or
  ADR. Follow the module ownership and import contracts. Pure core contains no
  ontology-specific types or branches.

## Review boundary and work items

The current authorized delivery is genesis/framing artifacts, the boundary audit,
and the proposed split/ADRs/contracts. Wait for owner review before migration
planning or product code, including executable quality scaffolding. After review,
establish real checks before dependent source work. Build all specified behavior;
do not replace requirements with a list of omitted capabilities.

Work items are project-scoped ddx beads, never GitHub issues. Run the CLI from
this repository with `DDX_BEAD_DIR="$PWD/.ddx" DDX_BEAD_PREFIX=batten` to select
this workspace. The installed CLI resolves its canonical project store outside
Git; the variable selects the workspace rather than forcing an in-tree store.
`docs/helix/01-frame/work-items.jsonl` is the review export, not a second live store.
Refresh it with `ddx --no-update-check bead export` after tracker changes.
Do not push, create a remote, or commit unless asked. A future requested commit
follows the owner's attribution instructions; no identity is invented.

## Tests and quality

- Use the fewest tests that pin behavior: one test per observable behavior,
  asserting the whole outcome. Vary inputs with a table, not more test functions.
- Search existing tests first. Extend a covering scenario or parameter table.
  Test public boundaries; add another layer only for a distinct observable outcome.
- Do not test language/type-checker guarantees, constructor defaults, incidental
  wording, private helper structure, or a mock interaction with no observable effect.
- Preserve each distinct authorization, non-disclosure, isolation, ordering,
  and concurrency invariant exactly once. Name behaviors and trace acceptance IDs.
- Consolidation removes duplicate code. Renamed former tests, helper wrappers,
  hidden bodies, dynamic registration, and skipped tests do not evade the budget.
- The first reviewed behavioral suite establishes a measured function-count
  ceiling. Afterward the count and ceiling only decrease; no automatic positive
  growth exception. Preserve coverage while consolidating; do not weaken assertions.
- Database-process tests are integration tests; registry inventories are marked.
  Keep the fast gate independent of database processes. Await observable state,
  events, or controlled clocks; no test sleeps or blind browser retries.
- Enforce CONTRACT-002's global size/complexity/import/public-surface ceilings;
  no per-file exception or suppression. Split by responsibility rather than raise
  a limit. Local, edit, hook, and CI checks use the same gate.
- Installed-artifact/native/browser/deployed evidence are separate. Never call a
  documented checker enforced, an offline double native, or an unrun check passing.
