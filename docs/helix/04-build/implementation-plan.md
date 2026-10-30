---
ddx:
  id: implementation-plan
  type: implementation-plan
  activity: build
  authoring:
    home: repo
  links:
    - id: TD-006
      kind: derived_from
    - id: CONTRACT-002
      kind: informed_by
---

# Local storage implementation plan

## Scope

Governing artifacts: PRD FR-26, ADR-007/010, CONTRACT-002/006/008, TD-006 and
TP-001 STO-01–15. The owner authorizes merging the evolved specifications into
main, then implementing the local filesystem backend with platform modularity.

## Shared Constraints

Async-first; stdlib product boundary; explicit typed configuration; no new
application environment variables; no credentials/private source. Preserve
platform-neutral core, optional distributions and downward quality ratchets.

## Implementation Slices

| Slice | Area | Depends on | Validation gate |
| --- | --- | --- | --- |
| B-001 | Validate and integrate evolved specifications on main | None | Artifact/schema/guide/static checks; source-control confirmation |
| B-002 | Executable quality scaffold | B-001 | Real import/cycle/private/shape/export/census positive and negative controls; common just lint recipe |
| B-003 | Portable storage and local POSIX provider | B-002 | Native STO conformance and explicit host authority/outcome injection |
| B-004 | Streams, bounded listing, conditions/ranges and upload lifecycle | B-003 | Concurrency, denial, lifetime, recovery and integrity observations |
| B-005 | Installed artifact, documentation and final review | B-004 | Build/install in clean environment; zero cloud dependencies; full common gate |

## Execution Contract

The owner's current instruction authorizes these slices. Specification integration
is committed and pushed to main before source implementation. Source work remains
reviewable on a codex branch. No remote repository creation, infrastructure change
or upstream implementation is required. Token usage estimate and monetary cost
are unknown; no spending ceiling was supplied. Available tools expose no reliable
per-task billing meter. Verification and review are included in the authorized work.

## Continuation Evidence

Resume from git diff, this plan and actual gate/test output. Record safe evidence
in local-storage-verification.json; tracker status stays in project ddx beads when
updated. B-001 completed with specification integration pushed to main at
61f4ae1efedb393e339cac99f182bc9b57085907. B-002 through B-005 are implemented
on codex/local-object-storage. The common recipe passed on the local macOS POSIX
profile: 17 behavior functions, 20 collected cases, strict typing, shape/import
checks and a clean wheel-only import observation. This reviewed initial suite
establishes the measured ceiling of 17 functions; parameter cases do not increase
that ceiling. Negative controls cover module/vendor/private/loader access, cycles,
export drift, missing accepted baseline and increased test ceilings.

Published data survived handle/provider restart. Separate OS processes competed
on the same validator with one successful publication, while an existing reader
retained its original generation. Feature revocation, partial reads, expiry,
cancellation, active-part abort and post-publication observation loss were exercised.
The implementation and evidence remain reviewable source; no product package
registry publication or Databricks/native runtime integration is claimed.

## Validation Plan

Validate governed documents and schemas; independently evaluate changed guide
pages. Test concrete native filesystem behavior and installed package closure.
Review typed APIs, import ownership, authorization, concurrency and possible effects.
Apply the same quality recipe locally, in hooks and CI; missing checks fail.

## Risks and Rollbacks

| Risk | Response | Rollback |
| --- | --- | --- |
| Unsupported filesystem semantics | Refuse profile before effects | Retain data and select qualified host |
| Defective source slice | Keep source branch reviewable | Revert reviewed source; immutable data remains untouched |
| Concurrent documentation edits | Preserve and revalidate current sources | Never overwrite unrelated owner work |

## Exit Criteria

Specifications are integrated into main. Local storage implements its qualified
profile with explicit unsupported refusals for other profiles. Required native,
installed and quality checks pass; evidence and remaining platform qualification
limits are accurate. No full-runtime or Databricks implementation claim is made.
