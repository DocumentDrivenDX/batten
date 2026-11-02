---
ddx:
  id: batten.storage.release.0.1.0a1
  type: release-notes
  activity: deploy
  authoring:
    home: repo
  links:
    - id: CONTRACT-006
      kind: informed_by
    - id: ADR-010
      kind: informed_by
    - id: implementation-plan
      kind: informed_by
---

# Batten storage 0.1.0a1

## Release Scope

`storage-v0.1.0a1` delivers the `novirhyza-batten-storage==0.1.0a1` wheel and
source distribution as a GitHub prerelease. It packages the already-merged
portable async storage protocols and managed local POSIX provider. The existing
`v0.1.0-alpha.1` design/site preview remains unchanged.

## Audience and Channels

Python host authors can download the package archives, checksum manifest and
source/qualification receipt from GitHub Releases. No PyPI publication or
complete Batten application runtime is claimed.

## Highlights

The storage module provides scoped object writes, pinned reads and ranges,
conditional replacement, bounded listing and multipart upload lifetimes.
Importing the portable protocol does not import the local adapter or any cloud
or platform dependency. Trusted host code supplies resolved limits, identity,
authorization and outcome observation.

## Changes and Fixes

This is the first package delivery of the storage slice already on main. The
common quality recipe passes 20 cases in 17 behavior functions on macOS arm64
with Python 3.11.17, including competing OS processes, native filesystem behavior,
cleanup and wheel-only import closure. Strict typing, format/lint and boundary
positive/negative controls pass. The Linux source CI retains its own exact
workflow evidence; local qualification does not broaden that record.

## Breaking Changes and Required Actions

There is no earlier public storage package to upgrade. Verify `SHA256SUMS` and
install the downloaded wheel in a clean environment. Read the package README
before binding a dedicated owner-only managed directory. All writers must use
the provider and host authorization must be supplied explicitly.

## Migration or Rollback Guidance

The release performs no database, cloud or existing-directory migration. Keep
published object data and its ownership/configuration separate from the package
environment. Retain the archive and receipt for repeatable environment rollback.

## Known Issues and Support

Qualification covers the recorded managed local POSIX profile and cooperating
writers. Network filesystems, Databricks Volumes, hostile plugin containment,
power-loss durability and performance targets remain unqualified. Atomic
visibility is not a power-loss guarantee. This prerelease does not deliver the
rest of the specified Batten host, worker or platform modules.

## References

- [Storage package and host requirements](../../../packages/batten-storage/README.md)
- [Implementation and native evidence](../04-build/local-storage-verification.json)
- [Storage contract](../02-design/contracts/CONTRACT-006-object-storage.md)
