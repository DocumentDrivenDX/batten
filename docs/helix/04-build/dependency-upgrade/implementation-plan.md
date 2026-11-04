---
ddx:
  id: batten.dependency-upgrade-20261103
  type: implementation-plan
  activity: build
  authoring:
    home: repo
  links:
    - id: ADR-005
      kind: informed_by
    - id: ADR-007
      kind: informed_by
    - id: ADR-016
      kind: informed_by
    - id: CONTRACT-002
      kind: informed_by
    - id: CONTRACT-012
      kind: informed_by
---

# Published dependency upgrade

## Scope

The owner requests upgrading every dependency after the runtime-v0.1.0a1 audit.
Preserve the public local approval workflow and qualify the exact replacement
cohort under ADR-005/007/016 and CONTRACT-002/012. The release target is
runtime-v0.1.0a2; the independent storage package remains unchanged.

## Shared Constraints

Use original published UMF Core/Codegen 0.10.8, access dev8, umf-weft 0.4.57,
Psycopg 3.3.7 and PostgreSQL 18. Fetch each upstream artifact from its actual
release with original hashes. No native engine is copied or replaced. Python
3.13 is the new local test cohort; library consumer floors remain explicit.
Replace compiler-coupled linting with Oxlint and move browser tests to JavaScript
Playwright as selected by the owner. Do not apply unqualified major or peer overrides. The single type-only
undici-types 8.12.3 minor override requires strict TypeScript declaration checking
and the real browser scenarios; it replaces Node types’ older nested pin. Do not weaken shape rules, hide assertions or increase the 17-function budget.
Use dedicated fabricated data, never implicitly migrate an existing workspace.

## Implementation Slices

| Slice | Area | Depends on | Validation gate |
| --- | --- | --- | --- |
| D-001 | Published native dependency pins and per-artifact compiler assembly | None | Normal resolver, pip check, compiler entry points and installed-wheel closure |
| D-002 | TypeScript 7 and Oxlint | D-001 | Exact four shape gates with positive/negative controls; no older lint dependency tree |
| D-003 | JavaScript Playwright scenarios and cross-language census | D-002 | Same two scenarios and invariants; 17 total registered behaviors; strict typing |
| D-004 | Qualification, documentation and release | D-003 | Fast/native/browser/CI gates, wheel hashes, reviewed site, immutable prerelease assets |

## Execution Contract

The owner's instruction authorizes implementation and follows the existing
release/publishing request. Reuse the clean release checkout on
codex/dependencies-20261103 and preserve the other chat's app expansion.
Token usage estimate and spending ceiling are unknown; no monetary budget was
supplied and the runtime exposes no reliable task cost meter. Verification and
independent review are included. Do not claim an unsupported package combination
as qualified or change unrelated app behavior to make an upgrade pass.

## Continuation Evidence

D-001 resolves and installs the published compiler/Core pair, current access,
Weft and Psycopg through normal dependency metadata; both installed environments
pass pip check. D-002 passes the four real shape controls with Oxlint 1.91.0 and
TypeScript 7.0.2. D-003 ports both canonical scenarios and preserves the combined
17-function census, including alias, namespace, hidden-helper and skip controls.
The final upgraded browser run passes both scenarios with zero retries, adds
fresh registry viewport captures and records nine exact controller/cohort hashes.
A readiness overlap found during capture was fixed before the passing run.
All 18 Python cases pass. The final registry audit checks 110 locked entries and
finds zero older published versions. D-004 review, CI and publication remain open.

## Validation Plan

Run the common quality recipe, preserve its actual negative controls and validate
registered browser counts. Run the existing approval and registry scenarios from
installed wheels against real PostgreSQL 18 and Chromium. Verify dependency
metadata with the normal resolver and pip check. Record exact artifacts,
interpreter, original source and observed results; independently review the
changed code and reader pages before merging and publishing.

## Risks and Rollbacks

| Risk | Response | Rollback |
| --- | --- | --- |
| Native compiler protocol or output drift | Qualify original bundles, migration, RLS and receipts | Retain the old release with its matching workspace |
| Browser migration loses an assertion | Compare the complete old/new scenario mapping and census | Keep the old qualified test/release snapshot |
| Lint replacement weakens a gate | Exercise each exact threshold with real controls | Restore the previous tool cohort |

## Exit Criteria

All selected direct and transitive dependencies are current published versions,
the new cohort passes its required gates, all prior distinct invariants remain
covered, and the 17-function ceiling holds. Updated qualification receipts,
source-stamped site content and immutable runtime-v0.1.0a2 assets are published.
