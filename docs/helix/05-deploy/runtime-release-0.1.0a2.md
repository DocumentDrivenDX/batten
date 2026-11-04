---
ddx:
  id: batten.runtime.release.0.1.0a2
  type: release-notes
  activity: deploy
  authoring:
    home: repo
  links:
    - id: ADR-005
      kind: informed_by
    - id: ADR-007
      kind: informed_by
    - id: ADR-016
      kind: informed_by
    - id: CONTRACT-012
      kind: informed_by
---

# Batten local runtime 0.1.0a2

## Release Scope

`runtime-v0.1.0a2` updates the local approval desk's dependency cohort and its
qualification tooling. Batten maintainers own this GitHub prerelease, dated
November 3, 2026. The independent storage release remains `storage-v0.1.0a1`.

## Audience and Channels

| Audience | Available material | Channel |
| --- | --- | --- |
| App authors | Approval desk, local registry and updated run instructions | Source and seven Batten wheels |
| Platform integrators | Original UMF companion wheels, exact cohort and constraints | GitHub release assets |
| Contributors | TypeScript 7, Oxlint and JavaScript Playwright qualification | Source, lockfiles and evidence |

## Highlights

- UMF Codegen and matching native Core move to 0.10.8; access remains dev8.
- The SQL compiler moves from `weft-sql` 0.4.54 to `umf-weft` 0.4.57.
  The Python import remains `weft`.
- Psycopg moves to 3.3.7. Development uses Python 3.13, Node 26.13.0 LTS,
  Bun 1.4.4 and uv 0.13.7.
- TypeScript 7.0.2 and Oxlint 1.91.0 replace the compiler-coupled ESLint parser.
  JavaScript Playwright retains the same two browser scenarios.

## Required Actions Summary

Prepare the recorded toolchain and install from the exact release cohort. The
new local qualification profile uses Python 3.13. Portable library metadata
retains its Python 3.11 floor; profile support follows actual recorded evidence.

Use a new dedicated fabricated workspace for initial qualification. Existing
installations require their matching verified model/head and cohort; startup
never performs an implicit migration.

## Changes and Fixes

### New or Improved

The original Codegen 0.10.8 wheel requires exactly Core 0.10.8. Compilation uses
the native Rust compiler supplied by Core. The assembler pins access and Codegen
artifacts independently to their original releases and hashes, then resolves
Core through normal dependency resolution. No replacement compiler is carried.

The obsolete Python Playwright, pyee, greenlet and V8 compiler dependencies leave
the cohort. Browser tests use `@playwright/test` 1.64.1. All prior authority,
stale-revision, receipt recovery, restart, installation-head, telemetry and
registry assertions remain in their registered scenarios.

Oxlint preserves the complexity 10, function-line 60, nesting 4 and one-class
limits. Positive and negative controls exercise each real rule. The common gate
counts Python and JavaScript test registrations together, including import aliases,
namespaces and assertion-bearing helpers; the ceiling remains 17 behaviors.

The latest Node declarations select an older Undici type package by default.
An explicit type-only override selects `undici-types` 8.12.3, checked by strict
TypeScript declaration validation and the same browser scenarios. This adds no
HTTP runtime implementation. The version audit records all locked packages.

### Fixes

Browser setup waits for enabled identity controls. The migrated tests retain
actual lost-response recovery and live native grant revocation; no scripted
substitute supplies database or browser results. App-only refresh selects the
exact declared wheel version even when the cache retains an older release.

## Breaking Changes and Required Actions

Contributor tooling changes to the recorded Python 3.13 and Node LTS profile.
Run `just approval-test` for the JavaScript browser suite. `just test` includes
both Python and browser scenarios; `just check` remains independent of database
processes. Application routes and operation envelopes retain their prior shape.

## Migration or Rollback Guidance

### Upgrade or Migration

From this release's source checkout, install the locked tools, run
`just approval-prepare`, explicitly initialize a dedicated fabricated workspace,
and start the host with `just approval`. Install the selected Chromium revision
with `node node_modules/playwright/cli.js install chromium` before browser tests.
The package installer never runs during application startup.

### Rollback or Hold Guidance

Retain the prior release assets and their matching workspace together. Stop the
host before changing its installed environment. Hold an upgrade if model/head,
current authority, receipt or required telemetry checks refuse. Reverting package
versions does not reverse database changes or completed business effects.

## Known Issues and Support

Qualification remains the recorded local approval-desk subset on PostgreSQL 18.
The microsite's twelve walkthroughs distinguish this runnable app from the other
specification journeys. This release does not establish complete fleet operation,
production authentication, hostile-code containment or an OTLP receiver profile.
No PyPI publication of Batten is included.

## References

- [Run the approval desk](../../../examples/approval-desk/README.md)
- [Local execution evidence](../reference-apps/approval-desk/specs/03-test/local-execution.json)
- [Dependency upgrade evidence](../04-build/dependency-upgrade/verification.json)
- [Quality and test policy](../02-design/adr/ADR-007-quality-and-test-ratchets.md)
