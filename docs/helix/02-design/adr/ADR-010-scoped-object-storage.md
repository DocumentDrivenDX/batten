---
ddx:
  id: ADR-010
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-001
      kind: informed_by
    - id: ADR-003
      kind: informed_by
---

# ADR-010: Scoped object storage through an optional Batten module

## Problem

Applications need one byte-object interface over local files and Databricks
Unity Catalog Volumes. Exposing physical paths or vendor clients couples the
application to placement and can bypass application permission containment.
Filesystem and remote upload guarantees differ under cancellation and concurrency.

## Decision

Define CONTRACT-006 in an optional stdlib-only `batten.storage` module, with its
local implementation under `batten.storage.local`. The Databricks Volumes adapter
lives in `batten.databricks.volumes` and imports the public storage protocol.
The generic runtime handles opaque capability admission and lifetime; it does
not import storage types or vendor code. Host composition injects providers.

The first backend pair is local managed filesystem storage and Volumes through
the public Files API. Applications name resources and relative keys. The host
selects roots, native authority, bounded transfer policy and exact qualified
cohorts. S3/ADLS adapters will implement the same boundary when qualified.

Use streamed read/write, metadata observation, bounded listing and single-object
delete. Use explicit conditions for create, replacement and deletion, version-pinned
ranges, and optional multipart/resumable sessions. Conditions are evaluated at
publication. Qualify native versus adapter-managed concurrency and atomic visibility
separately. Prefer shallow prefix listing, key-only projection and native continuation
without per-object metadata calls. Require explicit bounded integrity verification;
entity tags remain opaque validators. Preserve possible effects after failure and cancellation. Keep attachment
metadata in native UMF records, outside backend-specific object attributes.

Do not select Obstore, Obspec or another new storage dependency for this slice.
Batten's boundary is implementable using stdlib local I/O and the already scoped
public Databricks SDK. Library reuse can later be selected inside owning adapters
without exposing vendor types or changing application declarations.

## Why We Chose This

### Over a separate general-purpose storage project

The new behavior is application authority, scope, lifetime and qualified provider
binding. It belongs to Batten's capability boundary. A separate project would add
release coordination without an identified independent consumer requirement.

### Over exposing a vendor filesystem abstraction

A raw filesystem API exposes paths, directory operations and backend-dependent
credentials. A small object interface limits authority and makes unsupported
concurrency guarantees explicit. Optional adapters can still reuse mature engines.

## Consequences

**Good**: The same application resource works locally and on Volumes without
platform types in pure core. Headless core installations need no storage module.

**Trade-offs**: Local namespaces are adapter-managed. Applications store display
metadata separately and handle uncertain writes. Native qualification is required
for each cohort's conditional behavior; a configuration claim cannot provide it.

**Drift signals to watch**: storage imports in generic core, raw native clients in
app hooks, path traversal, unbounded transfer, automatic uncertain-write retries,
cloud access behind a volume that bypasses Unity Catalog, fake conditional writes,
recursive listing by default, per-object HEAD enrichment, or a cache bypassing authority.

## Assumptions

Erik LaBianca reviews the initial interface and supplies local bounds. Deploying
host owners supply workspace authority, resource roots and deployment bounds.
Public SDK upload/download and listing can be bridged asynchronously with bounded
buffers; a native qualification must demonstrate that assumption before support.
No specific SDK release, preview feature or create-only guarantee is inferred.

## Validation

**Result**: not tested against native backends.
**Evidence**: CONTRACT-006 records public API documentation and schema inspection;
the project test plan allocates semantic and native qualification separately.

## Concern Impact

Follows modularity, async public I/O, platform-adapter ownership, typed file
configuration and authorization concerns. No new framework, runtime or third-party
dependency is selected. ADR-003's optional-wheel policy applies to storage.

## Additional capability boundaries

Native copy can avoid downloading and re-uploading bytes, but needs source
version and destination conditions plus identity checks on both resources.
Bulk operations need bounded per-item outcomes and explicit partial failure.
Cache revalidation needs a distinct not-modified result, separate from a failed
read precondition. Multi-range reads need a bounded selection/result ordering
contract and must preserve one validator across all selected regions.
Historical versions, snapshots and change feeds need separate identities,
authority and consistency contracts; an entity tag supplies none of those.
Signed transfers change credential exposure and revocation semantics. Retention,
encryption and lifecycle controls belong to host policy with native enforcement.
These distinctions guide later capability proposals; they do not silently enlarge
the first local/Volumes operation surface.

[Databricks Files API](https://docs.databricks.com/aws/en/volumes/files-api/) grounds
conditional ranges and multipart behavior. [S3 listing](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html)
and [Azure listing](https://learn.microsoft.com/en-us/rest/api/storageservices/list-blobs)
show prefix, grouping and continuation features; their sorting and metadata guarantees
differ. [S3 integrity](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html)
separates checksums from version validators. These are API design evidence, not
qualification of Batten backends or adoption of those platforms for this slice.
