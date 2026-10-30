---
ddx:
  id: CONTRACT-002
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.architecture
      kind: derived_from
    - id: ADR-001
      kind: informed_by
    - id: ADR-007
      kind: informed_by
---

# Module boundary and quality contract

**Contract ID**: CONTRACT-002
**Type**: boundary and verification interface
**Version**: proposed v1

## Purpose

Specify mechanical import, public-surface, size/complexity, and test-count gates
for the proposed module split. These are the obligations of the first executable
scaffold after the owner's review, before dependent feature implementation.

## Scope and Boundaries

- In scope: every handwritten Python/browser module, tools, tests, adapter import
  closures, packaged-artifact checks, local/edit/hook/CI entry points, and ratchets.
- Excluded: dependency environments, lockfiles, generated compiler output, and
  build artifacts through explicit generated-path rules. No handwritten source
  or test file receives an exception.
- Owner: Batten; Erik LaBianca owns review of the first measured test budget.

## Normative Surface

Each row defines an import contract, not merely a suggested folder. Python
standard-library imports are allowed unless another rule forbids an effect.
`C` means `batten.contracts`, `R` means `batten.runtime`.

| Contract name | Module | Other Batten roots allowed | Third-party roots allowed |
|---------------|--------|----------------------------|---------------------------|
| BND-C | `batten.contracts` | None | None |
| BND-R | `batten.runtime` | C | None |
| BND-P | `batten.packaging` | C | `packaging`; build/test executables through explicit tool boundary |
| BND-T | `batten.testing` | C, R | None in portable doubles; `pytest` only in runner adapter |
| BND-N | `batten.umf` | C | Exact public UMF APIs in the selected cohort; no native engine reimplementation |
| BND-HOST | `batten.hosting` | C, R | `pydantic`, `pydantic_settings`; selected public factories supplied through a closed trusted catalog |
| BND-UX | Optional ux-builder browser adapter | Public browser-client API | Pinned public ux-builder packages; no Python/Bun/Node runtime or private host imports |
| BND-U | `batten.tables` | C | Public `umf_core`, `umf_codegen`, `umf_access`, `weft` surfaces in selected cohort |
| BND-W | `batten.workers` | C, R | None; OS capabilities qualified separately |
| BND-G | `batten.postgres` | C | Public `psycopg` surfaces |
| BND-L | `batten.lakebase` | C | Public `databricks.sdk` authority/endpoint/role surfaces |
| BND-D | `batten.databricks` | C | Public `databricks.sdk` resource surfaces |
| BND-M | `batten.gateway` | C | `httpx` or a cohort-declared injected public gateway client |
| BND-A | `batten.arras` | C | Public `arras`, `umf_core`, `umf_access` surfaces |
| BND-H | `batten.tether` | C | Public `tether` surfaces |
| BND-I | `batten.asgi` | C | `fastapi`, `starlette`; ASGI protocol types |
| BND-Q | `batten.mcp` | C | Public `mcp` surfaces |
| BND-V | `batten.dev` | Public APIs of all selected Batten modules | `pydantic_settings`, `pydantic`, `uvicorn`, public PostgreSQL 18 helper, explicit build tools |
| BND-B | Browser client | Own browser-client public modules | Browser APIs; no runtime Node/Bun modules; declared build/test tools only in build/test sources |

Exact upstream exports and supported versions MUST come from the selected public
cohort manifest. A permitted package root does not permit private submodule imports.
Unlisted third-party and consuming-application roots are forbidden by default.
Sibling platform adapters MUST NOT import one another; composition injects their
public protocol products. Both halves of a bidirectional integration remain owned.

The checker MUST:

1. Parse every source module, including nested imports, aliases, relative imports,
   optional imports, and type-checking imports. Resolve every Batten module to
   exactly one boundary row; unclassified handwritten source fails.
2. Check direct and transitive Batten dependencies, cycles, self-cycles through
   re-export barrels, and access to another module's private names. Export inventories
   are explicit; a namespace root must not eagerly import optional modules.
3. Inventory dynamic imports, entry points, loader calls, path mutation, and
   process module launches. Computed targets require a declared, owned loader
   boundary and installed-artifact observation; they are never ignored as safe.
4. Reject undeclared ambient environment reads and configuration/credential reader
   effects outside the composition/owning adapter boundaries.
5. Inspect wheel metadata and a clean installed environment for each published
   dependency closure. Optional-import fallbacks cannot hide an undeclared dependency.
6. Verify an allowed edge passes and a forbidden edge fails in a temporary
   fixture through the actual checker. Cover a cycle and private export breach.
   Negative controls are removed from the product tree after the check.

Core schema/dispatch semantic review MUST additionally prove no ontology-specific
types or branches. An import scanner alone cannot prove this property, runtime
reflection targets, or permission containment.

### Gate entry points

The proposed local command is
`uv run python scripts/check_boundaries.py --base HEAD`.
The complete recipe is `just lint`: boundary check, Ruff check/format,
strict type checking, file-size and ceiling ratchets, and test-count ratchet.
Post-edit checks, pre-commit, and CI call that same recipe or its documented
affected-file front end; the full recipe runs before code-work closeout.

Missing base, missing module rules, missing public-export inventory, and a
missing ratchet baseline MUST fail. No network remote or upstream branch is
required: a local reviewed base or explicit approved baseline is sufficient.
The recipe and checker files are proposal interfaces to implement after review;
their names in documentation are not an execution result.

### Shape ceilings

| Rule | Ceiling | Authority |
|------|---------|-----------|
| Handwritten source physical lines/file | 500 | Installed greenfield default, stricter than observed reference 501 |
| Test physical lines/file | 488 | Observed reference policy, stricter than installed default 800 |
| Python cyclomatic complexity/function | 10 | Observed reference and installed greenfield default |
| Python statements/function | 40 | Observed reference and installed greenfield default |
| Python returns/function | 6 | Observed reference and installed greenfield default |
| Python branches/function | 9 | Observed reference, stricter than installed default 12 |
| Python public methods/class | 15 | Installed greenfield default, stricter than observed reference 18 |
| Browser JavaScript/TypeScript complexity/function | 10 | Installed greenfield ESLint default |
| Browser function nonblank/noncomment lines | 60 | Installed greenfield ESLint default |
| Browser nesting depth | 4 | Installed greenfield ESLint default |
| Browser classes/file | 1 | Installed greenfield ESLint default |

Ruff rules MUST select the actual complexity/statement/branch/return/public-method
checks; browser lint MUST enforce the listed shape rules. Parameter counts receive
cohesion review, not wrappers introduced solely to satisfy an argument count.
Numbers above are policy choices with sources, not measurements of Batten code.
Every ceiling only decreases. Rule suppression, per-file exceptions, renamed
exclusions, and changing the counter to hide growth fail the ratchet.

### Test-count policy

The first reviewed behavioral suite establishes the measured ceiling. Thereafter
each accepted change MUST satisfy both actual function count no greater than
the prior accepted count and configured ceiling no greater than its prior value.
The ceiling is lowered to reflect accepted reductions.

Count all test functions/registrations across root tests, module tests, shipped
application tests, and browser tests. Parameterized cases count once per behavior
test. Renamed former tests, hidden helper bodies, delegated test wrappers, and
dynamic registrations do not remove a behavior's code from the census. Review
tables to ensure they vary inputs rather than bundle unrelated outcomes.

One public-boundary test asserts a behavior's whole outcome. Another layer earns
a test only for a distinct observable property. Prefer extending an existing
table before adding a function. Keep each distinct authorization, disclosure,
isolation, ordering, and concurrency invariant exactly once. Do not assert the
type checker, language defaults, private helper structure, or incidental wording.

Database-process tests MUST be integration tests. Registry-inventory checks are
marked as such. Browser races fail and are fixed at their synchronization, without
blind retries. Tests await observable state, events, or controlled clocks rather
than sleeping. The behavior-to-acceptance mapping follows any consolidation.
No positive-growth trailer automatically authorizes exceeding the ceiling.

## Precedence and Compatibility

The owner's review gate postpones executable scaffold changes until review;
it does not waive the gate before dependent feature work. ADR-007 governs policy.
The first reviewed measured baseline is the sole initial-budget exception.
Thereafter a change to the policy itself requires an explicit owner ruling.

Static analysis and installed-artifact observations are separate evidence layers.
Neither proves arbitrary runtime code isolation. Support claims identify the
versions, operating system, subset, and native/browser/deployed observations used.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| Forbidden import/transitive edge | Nonzero; source, line, target and violated contract | After fix | Move behavior to its owner or inject a public service. |
| Private export, cycle, unclassified source | Nonzero; exact module/path and rule | After fix | Repair boundary; no blanket baseline exception. |
| Dynamic target lacks evidence | Nonzero readiness result for affected loader path | After qualification | Record owned target policy and installed-artifact observations. |
| Shape limit or suppression | Nonzero; measured unit and allowed ceiling | After split | Split by responsibility; never raise ceiling. |
| Test count grows or baseline increases | Nonzero; before/after counts and scoped sources | After consolidation | Preserve behavior coverage; owner resolves genuine policy conflicts. |
| Missing baseline/rules/base | Nonzero; missing input named | After setup | Supply local approved baseline; do not skip or fabricate. |

## Examples

```text
Allowed: batten.arras -> batten.contracts
Allowed: batten.arras -> public Arras API in the selected cohort
Forbidden: batten.runtime -> batten.arras
Forbidden: batten.dev -> private consuming-host factory
Forbidden: batten.lakebase -> batten.postgres private connection helper
Allowed: composition injects Lakebase authority into public PostgresServices
```

## Non-Normative Notes

An AST-based project checker is the proposed import-linter equivalent. Its
scaffold must prove real positive and negative controls before it can be called
enforced. The reference audit script is an analysis aid outside the product,
not Batten's future checker or a reusable implementation imported from the reference.
