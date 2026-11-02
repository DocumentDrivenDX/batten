---
ddx:
  id: batten.runtime.release.0.1.0a1
  type: release-notes
  activity: deploy
  authoring:
    home: repo
  links:
    - id: ADR-016
      kind: informed_by
    - id: CONTRACT-012
      kind: informed_by
    - id: US-101
      kind: informed_by
---

# Batten local runtime 0.1.0a1

## Release Scope

`runtime-v0.1.0a1` is the first runnable local application prerelease: an approval
desk, a visual application registry and independently packaged runtime modules.
Release date: November 2, 2026. Batten maintainers own this GitHub release.
The existing design/site and storage releases retain their own tags.

## Audience and Channels

| Audience | Available capability | Channel |
| --- | --- | --- |
| App authors | Working native-table approval app and authored TypeScript UI | Source checkout and installed app wheel |
| Host integrators | Portable contracts/runtime/table port, optional native adapter, HTTP transport and local composition | Separate wheels on GitHub Releases |
| Contributors | Exact original platform cohort, qualification receipt and repeatable tests | Repository and release assets |

## Highlights

- Open the local registry to choose an app with a description and visual preview.
  The Batten brand returns to the registry.
- Submit and edit requests, inspect their revisions, and independently approve
  or reject them through original UMF/Weft on PostgreSQL 18.
- Recover a lost mutation response using its original native receipt. Restarting
  retains requests and receipts; local sessions require a new login.

## Required Actions Summary

Use Python 3.11 and the recorded dependency cohort for this preview. Source
assembly also uses Bun 1.4.3 and uv. Explicitly initialize a new dedicated
fabricated database before serving. Run with loopback-only stub identities;
this is a local development profile.

## Changes and Fixes

### New or Improved

The release adds `novirhyza-batten-contracts`, `novirhyza-batten-runtime`,
`novirhyza-batten-tables`, `novirhyza-batten-umf-postgres`,
`novirhyza-batten-asgi`, `novirhyza-batten-local` and
`novirhyza-batten-approval-desk`, all at `0.1.0a1`.
Core contracts, runtime and the portable table port remain independent of native
providers. Original UMF SDK wheels accompany the cohort as upstream dependencies;
Batten does not carry a replacement ORM or compiler.

The registry uses explicit host-owned app metadata and packaged fabricated
thumbnails. Apps use distinct URL prefixes and API cookie paths. Host/origin
checks protect both the registry and app routes. Safe local audit and linked
OpenTelemetry spans preserve operation identity without logging request text,
SQL or connection details.

### Fixes

Identity selection waits for app initialization, preventing fast registry
navigation from selecting an identity before its handlers are ready.
A separate app-only rebuild command speeds UI and hook iteration against the
already prepared platform cohort.

## Breaking Changes and Required Actions

This is the first public local-runtime package release. For anyone using the
unreleased root-page demo, `/` is now the registry and the app is at
`/apps/approval-desk/`. Refresh the browser and establish a local session again.
The app's API routes and cookie path follow its URL prefix.

No database migration accompanies this release. Startup verifies the installed
model and schema head and refuses drift; it never creates roles or migrates tables.

## Migration or Rollback Guidance

### Upgrade or Migration

From the release source checkout:

```sh
uv sync --frozen --all-packages
bun install --frozen-lockfile
just approval-prepare
just approval-init
just approval
```

Open `http://127.0.0.1:8820/`. Initialization refuses an existing data directory;
retain an existing matching demo workspace and run `just approval` to reopen it.
Use `just approval-refresh` after app-only edits, then restart the host.
Model changes require an explicitly initialized matching workspace.

The release includes separate wheels, the qualified cohort and constraints,
checksums, original upstream SDK dependencies and installation instructions.
Package assembly happens before runtime startup; serving does not install packages.

### Rollback or Hold Guidance

Retain the release assets and matching application data/model together. Stop the
host before changing its installed environment. Restore the previous matching
cohort and app artifacts, then reopen the retained workspace. Hold an upgrade
when model/head verification or an affected native/browser assertion fails.

## Known Issues and Support

Native execution is qualified for the recorded macOS arm64, Python 3.11 and
PostgreSQL 18 local cohort. Linux CI supplies its own exact result. Platform-neutral
wheel tags alone do not establish other native profiles. Local stub identity and
local span capture do not establish production login or OTLP receiver qualification.

The strict full-corpus conformance gate retains its separate requirements. Use
project-scoped ddx work items for integration work and the recorded app evidence
to assess this release's bounded claims. No PyPI publication is included.

## References

- [Run and iterate on the approval desk](../../../examples/approval-desk/README.md)
- [Local execution evidence](../reference-apps/approval-desk/specs/03-test/local-execution.json)
- [Local HTTP and registry contract](../02-design/contracts/CONTRACT-012-local-operation-host.md)
- [Platform assembly decision](../02-design/adr/ADR-016-local-approval-stack.md)
