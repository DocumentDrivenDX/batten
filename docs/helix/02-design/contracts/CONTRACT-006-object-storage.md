---
ddx:
  id: CONTRACT-006
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-010
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
  schemas:
    - id: batten.storage.values
      version: "0.1.0"
      title: Batten object storage boundary values
      path: docs/helix/02-design/schemas/storage.schema.json
      schemaFormat: json-schema
---

# CONTRACT-006: Scoped object storage

**Contract ID**: CONTRACT-006
**Type**: asynchronous library boundary
**Version**: 0.1.0; capability interface `batten.storage.objects/1`
**Related**: PRD FR-26; ADR-010; CONTRACT-001/003/004

## Purpose

Give application hooks the same scoped byte-object operations over Databricks
Unity Catalog Volumes and a local managed filesystem namespace.

## Scope and Boundaries

Batten owns the interface, admission and permission checks. Platform adapters own
translation and native authority. Erik LaBianca owns interface review and local
limits; the deploying host owner supplies workspace, volume and authority bindings.

The first backend pair is local filesystem and Databricks Volumes. S3 and Azure
Data Lake Storage remain required extensions of this boundary under FR-26.
Directory management, arbitrary host paths, database transactions and application
file metadata are outside this interface. UMF records own original filenames,
media types, attachment relationships and application attributes.

## Normative Surface

`storage.schema.json` owns serialized value shapes. The Python protocols below
own call signatures, lifetimes and non-serialized stream/context types. All
references to types name the matching schema definition unless defined here.
No callable/provider is loaded during effect-free composition assessment.

### Resource admission and authority

An application places the storage schema's `requirement` value at
`CapabilityRequirement.settings.storage`, using CONTRACT-003. The parent interface
pin is `{id: batten.storage.objects, version: '1'}`; `batten.storage.objects/1`
is its shorthand inside the storage payload. The parent requirement ID and payload
resource MUST match. The selected module registers this settings validator. It MUST request operations and features
explicitly. This payload grants no authority and selects no backend. The host
binds that requirement to exactly one `localBinding` or `volumesBinding` through
CONTRACT-004. The host binding places its backend value at `binding.settings.storage`;
its `resource` MUST match the requirement. These initial providers declare
`in-process` placement; remote API access does not qualify remote-worker placement.
Settings remain opaque to generic core.

Admission MUST intersect application requests, authenticated actor policy and
native authority. The host MUST issue a request-scoped `ObjectStore` through
`batten.storage.for_resource(context, resource)`; this synchronous resolver does
no I/O. `context` is the trusted invocation context, not an app-supplied actor.
The returned handle exposes only the intersection. Applications cannot change
identity, workspace, root, credentials or allowed operations through a handle.

Every operation and continued stream/page MUST check current authority. Revocation
prevents subsequent chunks/pages/effects; already delivered bytes cannot be
recalled. Revocation during a native mutation preserves its actual uncertainty.
Closing the invocation revokes handles and closes active streams. Closing a
borrower MUST NOT close host-owned shared platform clients.

### Public Python interface

`batten.storage` owns protocol/value types, validation and the resolver.
`batten.storage.local` owns its local factory. `batten.databricks.volumes` owns the
Volumes factory. Factories receive resolved typed settings, explicit owned/borrowed
services and trusted authorization; they perform no construction-time I/O.
Provider `prepare` checks readiness under CONTRACT-001.

```python
class ObjectStore(Protocol):
    def open_read(
        self,
        key: str,
        *,
        offset: int = 0,
        length: int | None = None,
        condition: ReadCondition = Any(),
        expected_digest: Digest | None = None,
    ) -> AsyncContextManager[ObjectRead]: ...
    async def stat(
        self, key: str, *, condition: ReadCondition = Any()
    ) -> ObjectInfo: ...
    async def write(
        self,
        key: str,
        source: bytes | AsyncIterable[bytes],
        *,
        condition: WriteCondition = Absent(),
        expected_digest: Digest | None = None,
    ) -> WriteReceipt: ...
    async def delete(
        self, key: str, *, condition: ReadCondition = Any()
    ) -> DeleteReceipt: ...
    async def list(
        self,
        *,
        prefix: str = "",
        recursive: bool = False,
        detail: Literal["keys", "basic"] = "keys",
        cursor: str | None = None,
        limit: int,
    ) -> ListPage: ...
    async def begin_upload(
        self,
        key: str,
        *,
        condition: WriteCondition = Absent(),
        expected_digest: Digest | None = None,
    ) -> UploadInfo: ...
    async def upload_status(self, upload: UploadRef) -> UploadInfo: ...
    async def write_part(
        self,
        upload: UploadRef,
        part_number: int,
        source: bytes | AsyncIterable[bytes],
        *,
        expected_digest: Digest | None = None,
    ) -> PartReceipt: ...
    async def list_parts(
        self, upload: UploadRef, *, cursor: str | None = None, limit: int
    ) -> PartPage: ...
    async def complete_upload(
        self, upload: UploadRef, parts: Sequence[PartReceipt]
    ) -> WriteReceipt: ...
    async def abort_upload(self, upload: UploadRef) -> AbortReceipt: ...


class ObjectRead(Protocol):
    info: ObjectInfo
    selection: ReadSelection
    verification: TransferVerification | None

    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def aclose(self) -> None: ...
```

Values are immutable. `open_read` performs I/O on async context entry; entry
opens the object and supplies its observed metadata. `ReadCondition` accepts `Any()` or `Matches(version)`; `WriteCondition` also
accepts `Absent()`. Constructors map to schema `condition.kind` values.
The stream is single-use,
emits nonempty chunks, closes on exit/early exit/error and never materializes
an unbounded object. Empty objects yield no chunks. `aclose` is idempotent.
All I/O, including filesystem and synchronous SDK work, MUST avoid blocking the
application event loop. Async cancellation MUST NOT imply a worker thread stopped.

| Operation | Permission | Outcome and required behavior |
| --- | --- | --- |
| `open_read` | `read` | Stream bytes; `Matches` pins the returned bytes to the validator or refuses; unconditioned concurrent reads have no snapshot guarantee. |
| `stat` | `stat` | ObjectInfo; `version` is opaque and nullable. Never infer it from size/mtime or treat an entity tag as a universal checksum. |
| `write` | `write` | Complete receipt only after the entire source is accepted and native completion succeeds. Streaming backpressure and configured bounds apply. |
| `delete` | `delete` | Delete exactly one object. Already missing returns `absent` after authorization; no recursive delete or implicit directory removal. |
| `list` | `list` | Bounded page of objects under a segment prefix. Shallow by default with child prefixes; recursion is explicit. No globally sorted or snapshot listing guarantee. |

Methods raise `StorageError` carrying the schema `error` shape; they never expose
native exceptions. Native cancellation propagates the runtime's cancellation
signal; invocation tracking MUST retain any possibly effective mutation's
`effect=unknown` and incident ID before unwinding.

### Keys and namespace

A key MUST be nonempty UTF-8 text relative to the bound namespace. `/` separates
segments. Leading/trailing slash, empty segments, `.`/`..`, backslash, colon,
NUL and control characters are invalid. Adapters MUST NOT URL-decode, trim,
case-fold or Unicode-normalize keys. Percent signs are literal and encoded once
when constructing native API paths. Key comparisons are exact and case-sensitive.
A local adapter MUST use an injective representation or refuse unsupported names
before effects; case-insensitive filesystems cannot alias distinct logical keys.

Keys name regular byte objects only. Native directory/ancestor collisions return
`path_conflict`; they MUST NOT delete or reinterpret another object. The local
namespace is managed by its adapter; arbitrary preexisting files are not imported.
Backend paths, volume names and physical encoding never appear in public results.

A list prefix is empty for the whole namespace, or a valid key followed by `/`.
`reviews/` includes descendant objects; `reviews` is invalid as a prefix. A key
may be listed only when that actor can discover it. A denied namespace fails
before enumerating; inaccessible entries MUST NOT leak through counts or errors.

### Writes, features and concurrent access

The baseline provides read/stat/write/delete/list. Write `Any()` explicitly permits
unconditional replacement. `Absent()` is the safe default and requires
`create_only`. `Matches(version)` requires the operation's `conditional_read`,
`conditional_replace` or `conditional_delete` feature. The provider MUST evaluate
the condition against the destination at the native operation's commit point.
An existence/stat check followed by unconditional mutation is forbidden.

A qualified failed condition raises `precondition_failed` with `effect=none`,
including a missing target for `Matches`. It MUST NOT silently become create or
replace. Unsupported conditions fail before source consumption or provider effects.
`Any()` delete of a missing object returns `absent`; conditional delete does not.
Authorization precedes missing/version details. Date/mtime/size are not validators.

A version token is opaque and bound to resource, key and provider/profile identity.
`validator_kind` is `content`, `revision`, or null together with a null version.
Content validators can repeat when bytes return to an earlier value; they do not
prove that no intervening write occurred. Revision validators require a qualified
non-repeating revision identity. Neither implies access to historical versions.

A provider exposes `providerProfile` in its module-owned qualification evidence.
`concurrency_domain=native` includes writers using the backend outside Batten.
`adapter_managed` requires an exclusively managed namespace and serialization of
all its admitted writers. Host policy MUST prohibit outside writers in that
profile; a process-local lock alone is insufficient. An application requiring
native concurrency MUST refuse an adapter-managed profile. The selected domain
is part of the admitted plan; local and remote guarantees cannot be silently equated.
A native profile may satisfy an adapter-managed requirement; the reverse is forbidden.
Conditional providers MUST return non-null qualified validators on successful stat,
read and write. Weak entity tags cannot support `Matches`. Required `atomic_publish`
MUST resolve to `publication=atomic_replace`; resume requires multipart support.

### Range reads and transfer integrity

`offset` is a zero-based byte position; `length` is a nonnegative byte count or
null to read to EOF. Selection is half-open `[offset, offset + length)` clipped
to the observed object size. Offset at EOF yields an empty stream; offset beyond
EOF raises `range_not_satisfiable`. Negative/overflowing inputs refuse before I/O.
`selection` reports actual offset/length and full observed object size.
Nondefault ranges require `read_range`. The adapter MUST validate native status,
range headers, length and encoding; a server ignoring Range cannot yield a whole
object as a successful range. No transparent decompression may change byte offsets.

Multi-request or resumed reads MUST use the same `Matches` validator for every
request, including native part fetches. A mismatch fails; mixed-revision bytes
MUST NOT be presented as a valid assembled transfer. Single-key unconditioned
reads remain available, with their weaker concurrency semantics explicit.

An optional `expected_digest` is a SHA-256 hexadecimal digest of the exact input
or selected output bytes. It requires `verified_transfer`. The adapter MUST count
bytes, verify the digest and report its verification scope: `source` means consumed
upload bytes, `delivered` means yielded read bytes, `stored` means verified stored
bytes under a pinned object identity. Native multipart/composite checksums MUST
NOT be relabeled as whole-object SHA-256. An entity tag is never inferred to be a digest.

Read verification becomes valid only after EOF; `verification` remains null on
early close/failure. Already yielded bytes are not retroactively withdrawn.
Upload verification mismatch MUST NOT yield a successful receipt. If publication
may already have happened, report `integrity_mismatch` with `effect=unknown`;
source verification alone MUST NOT claim destination validation or rollback.

### Multipart and resumable uploads

All upload methods require `write` permission and `multipart_upload`;
reattachment across invocations requires
`resumable_upload`. UploadRef is opaque, non-authorizing and bound to original actor,
application, resource, key, condition, expected digest, profile revision and expiry.
Host restart invalidates sessions unless that exact cohort qualifies durable resume.
Reattachment always rechecks current authority; an upload reference grants none.

`begin_upload` captures the immutable condition/digest and effective part bounds.
`expires_at` is a UTC RFC 3339 time set from host upload TTL at initiation;
part writes do not extend it. Inconsistent effective min/max part bounds refuse
initiation. `upload_status` may report `expired`; other session methods then raise
`upload_expired`. Status never reports another actor's session.
The condition MUST be evaluated again at completion against the current destination,
not consumed at initiation. Part numbers start at 1. Parts contain nonempty bytes;
an empty object uses `write`. Parts may arrive out of order within bounded parallelism.
The final manifest MUST contain exactly contiguous part numbers in ascending order,
each once, with current provider-issued tokens and sizes. Every nonfinal part meets
`min_part_bytes`; total bytes/parts stay within resolved host and native bounds.
Unknown, missing, stale, duplicated or cross-session receipts fail before completion.

Reusing a part number explicitly replaces that staged part, not the destination;
parallel writes to the same part number MUST refuse with `upload_conflict`.
A receipt confirms staged bytes, not object publication. Its optional digest verifies
consumed part bytes only; it is not a whole-object digest or native storage proof. `list_parts` provides
bounded authoritative accepted-part observations; callers MUST reconcile a timed-out
part before replacing it. Transparent part retries are allowed only with a qualified
stable session/part identity and replayable identical bytes; no live source replay
or new upload session may be manufactured. A stale receipt cannot complete.

State is `open`, `completing`, `complete`, `aborting`, `aborted`, `expired` or
`unknown`. Complete and abort are serialized. During completion no part may change.
Repeated completion of the same manifest returns the original receipt only if
proven; a different manifest conflicts. A lost completion response produces
`unknown` until `upload_status` can resolve that original attempt. Destination
existence or matching bytes alone cannot prove which attempt completed.

`abort_upload` reports aborted, already_aborted, already_complete or unknown.
It MUST NOT delete a completed destination. Expiry/revocation stops parts and
completion; host-owned cleanup can retire staging without impersonating the actor.
Partial cleanup stays visible to the host until reconciled. Closing an invocation
closes handles; it does not claim an unfinished upload was rolled back. Qualified
resumable sessions retain bounded staging until expiry; other sessions request abort.

### Publication, retries and visibility

No operation promises multi-object transactions or rollback. `publication` is
`completion_only` or `atomic_replace`; the latter requires `atomic_publish` and
proves readers observe an old or a complete new object, never partial destination
bytes, within the stated concurrency domain. Conditional mutation and atomic
publication are separate guarantees and MUST be qualified separately. Multipart
staging is never ordinary listable/readable content.

No in-place byte patch or append operation is exposed. Failed/cancelled mutations
may have left partial bytes or completed unless a qualified guarantee proves
otherwise. The adapter MUST preserve uncertainty and MUST NOT delete a possible
concurrent writer's object as cleanup. Mutations with possible effects are not
automatically retried outside the explicitly qualified part rule. Backend SDK
retry configuration MUST obey the same rule. Reads/listing may use bounded retries
under one deadline; a partly delivered read resumes only under its original validator.

### Bounds, continuation and metadata

The host MUST resolve every schema `limits` field to a positive finite value;
no implicit unlimited defaults. Bytes are bytes; depth counts key segments;
transfer buffers include staging and SDK parallel buffers. Timeouts use monotonic
elapsed time. Cursor TTL begins at page issuance. Providers MUST refuse an
unhonorable bound before effects; observed overflow during upload retains effect
uncertainty. Admission takes the stricter host/application bound where declared.
Erik LaBianca supplies initial local values; the deploying host owner supplies
other profiles. No measured limits are inferred from vendor maxima.

`limit` MUST be positive and no greater than `max_page_items`. A page may be empty
with a non-null cursor when scan work reaches `max_scan_entries`. Only a null
cursor ends enumeration. A prefix with no matching objects yields an empty final
page; native missing-directory responses are translated accordingly.

Cursors are opaque, bounded and scoped to actor, application, resource, profile
revision, prefix, recursive, detail and limit. Subsequent requests MUST repeat
those options.
Tampering, mismatched scope and host restart invalidate them; expiration returns
`cursor_expired`. Cursors confer no authority. Concurrent mutation may cause
omissions or duplicates; no continuation snapshot is promised. Revocation is
checked on every continuation. Hidden objects and physical paths MUST NOT occur
in cursor plaintext exposed to applications.

`size_bytes` is observed content length, including zero. `modified_at` is a UTC
RFC 3339 timestamp or null; `version` is a provider token or null. Only a qualified version token provides
the declared conditional semantics. An object growing beyond the read bound
fails the stream. No receipt implies an application metadata row was committed.

### Listing performance and cache correctness

Shallow listing is the default: `recursive=False` returns immediate objects and
`common_prefixes` for immediate children. Prefixes are virtual navigation groups,
not independently readable objects. A prefix is disclosed only with authorized
navigation or descendant visibility. `recursive=True` explicitly traverses all
descendants and returns no common prefixes. Empty physical directories need not
appear. No item/prefix duplication occurs within a page; concurrent changes may
repeat entries across pages.

`detail="keys"` returns key-only entries. `detail="basic"` returns summary entries
with size, modified time, version and validator kind; fields unavailable from the
native listing are null. Adapters MUST NOT issue per-object HEAD/stat requests to
fill summaries. Authors call `stat` explicitly when they need authoritative details.
`items + common_prefixes` MUST fit `limit` and the page byte bound. All scans,
including directories and filtered entries, count against host work limits.

Adapters MUST push approved prefixes, shallow/delimiter selection and native page
sizes down where supported, then enforce Batten authority on returned candidates.
Local listing uses bounded directory enumeration; Volumes uses native directory
pages. Continuations preserve native tokens/traversal state and unconsumed bounded
page entries; they MUST NOT restart scanning or globally sort prior pages.
Recursive walkers bound depth, requests, state and bytes. On work-budget exhaustion,
return progress plus a cursor, including an empty page when needed. Single-entry
or cursor state exceeding its byte bound raises `limit_exceeded`; never loop
without progress. Providers that cannot retain progress within bounds refuse.

Speculative prefetch and parallel transfers count toward the same request, buffer,
concurrency and deadline budgets. No unbounded background listing or query-time
index rebuild is permitted. Namespace listing is not application search, stable
pagination or a total count; use indexed UMF records for those application needs.
That index has separate reconciliation/freshness and is not storage authority.

Caches MUST be scoped by actor/policy, resource, provider/profile and validator,
and recheck authority on every access. A conditional current read MUST validate
its condition against current native state; a cached old object cannot establish
that it still matches. Current listings/stat MUST NOT reuse stale cached results
as fresh observations. A listing cache requires a qualified namespace invalidation
mechanism; a TTL alone does not prove currentness. Cached bytes may accelerate a
validated read but cannot weaken the requested condition or integrity scope.

Host diagnostics record safe per-operation request counts, scanned/returned counts,
bytes, cache outcomes, retry attempts and latency. Names/keys/native paths and
hidden-entry counts remain unavailable to applications. Erik LaBianca supplies
benchmark workload and local budgets; deploying hosts supply their native workload.
Qualification compares observed requests and bounded memory, not invented throughput.

### Initial backend bindings

| Binding | Host-only settings | Mandatory adapter rules |
| --- | --- | --- |
| `localBinding` | Absolute managed `root`; resolved limits | Keep all operations beneath an opened trusted root; refuse symlinks, junctions/reparse points and special files. Prevent ancestor replacement races; resolve-then-open checks alone are insufficient. Private staging is bounded and outside listable keys. |
| `volumesBinding` | `workspace_ref`, `/Volumes/catalog/schema/volume[/prefix]` root, `authority_ref`, limits | Use the public Databricks Files API through an injected scoped client. Encode each key segment once. Preserve Unity Catalog checks; never access the volume's backing cloud store directly. |

Volume/workspace creation, grants and root initialization are explicit host
maintenance operations. Parent directories within the approved root MAY be
created for writes. Ordinary start/reload MUST NOT erase or adopt data.
The Databricks adapter MUST explicitly set upload overwrite behavior, bound native
pagination/parallel buffers and close SDK streams. Iterator convenience APIs
MUST NOT silently fetch an unbounded listing. Public Files API/SDK versions and
workspace features require an exact cohort and native qualification.

A host may use a service principal only when its authority and Batten actor policy
are both scoped. It MUST NOT claim native per-user enforcement for that binding.
The local process identity likewise does not replace application authorization.

Every storage request, stream, page, range and multipart/resume attempt MUST
preserve CONTRACT-001's trusted attribution and OpenTelemetry correlation.
Writes, deletes and upload completion MUST retain logical command and distinct
attempt identity, including reconciliation after a lost acknowledgment. Native
request references and available byte/usage counts MUST be correlated without
exporting object bytes, unsafe keys or upload credentials. Host-owned staging
and cleanup use explicit service authority while retaining originating workflow
correlation; they MUST NOT impersonate the initiating user. Read/list/cache paths
remain attributable and audited, including refusal and native-attribution gaps.

## Precedence and Compatibility

PRD FR-26 owns scope; this contract owns storage behavior; CONTRACT-001 owns
lifecycle and CONTRACT-003/004 own composition. SDK series/cohort rules follow
ADR-005. Schema version 0.1.0 and exact interface `batten.storage.objects/1` are
assessed independently. Unknown required operations/features refuse before I/O.
No implicit fallback backend, key rewriting or weakened write condition is permitted.

## Error Semantics

Authorization precedes existence disclosure. `incident_id` is an opaque safe
correlation ID; diagnostic payloads omit key text, native path, credentials and
native exception bodies. Reads/stat/list errors have `effect=none`.

| Condition | Error / Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Bad key, prefix, condition or limit | `invalid_key` / `invalid_request` | Correct request | No provider effect. |
| Authority absent/revoked | `denied` | After authority change | No existence detail; interrupted mutations may be unknown. |
| Missing object on read/stat | `not_found` | Explicit new observation | Authorization checked first. |
| Existing create target | `precondition_failed` | New key or explicit replace | No overwrite. |
| Native directory/object collision | `path_conflict` | Correct key | Preserve existing data. |
| Required operation/feature unqualified | `unsupported` | Qualified binding | Refuse before consuming input. |
| Bound exceeded | `limit_exceeded` | Correct bounds/request | Report unknown if mutation may have begun. |
| Invalid/expired continuation | `cursor_invalid` / `cursor_expired` | Restart enumeration | No implied snapshot continuity. |
| Native conditional conflict | `precondition_failed` | Explicit reconciliation | No effect when the native precondition refused. |
| Unsatisfiable byte range | `range_not_satisfiable` | Correct selection | No content returned. |
| Digest mismatch | `integrity_mismatch` | Explicit reconciliation | Reads fail verification; a possibly published write remains unknown. |
| Upload missing/expired | `upload_invalid` / `upload_expired` | New explicit session | Never transfer authority or reuse another upload. |
| Part/state/manifest conflict | `upload_conflict` | Reconcile original session | No implicit part replacement or new completion attempt. |
| Platform unavailable/deadline/I/O | `unavailable` / `timeout` / `io_failure` | Reads may retry explicitly | Mutations with uncertain effect require reconciliation. |
| Cancellation | `cancelled` in invocation tracking | Explicit reconciliation | Propagate cancellation; never claim rollback from cancellation alone. |

For completion, effect concerns the destination; failed preconditions may leave
staging to clean up. Part-method effects concern staged bytes.
Only a proven pre-effect mutation failure has `effect=none`; all possibly
effective failures have `effect=unknown`. A completed receipt records observed
completion, not a promise that a concurrent actor has not changed the object.

## Examples

Illustrative typed-hook use; `context` is supplied by the admitted invocation:

```python
objects = for_resource(context, "attachments")
receipt = await objects.write(
    "reviews/demo/summary.txt", b"Fabricated review", condition=Absent()
)
async with objects.open_read(receipt.info.key) as content:
    async for chunk in content:
        await approved_consumer.send(chunk)
page = await objects.list(
    prefix="reviews/", recursive=False, detail="keys", limit=context.storage_page_limit
)
info = await objects.stat(receipt.info.key)
assert info.version is not None  # conditional capability required at admission
await objects.write(
    info.key, b"Revised fabricated review", condition=Matches(info.version)
)
```

The same app resource binds locally or to a Volumes root. Neither root is in the
app model. A required `create_only` feature refuses an unqualified Volumes cohort;
Batten MUST NOT substitute `Any()` to make the example run.

## Schema Basis

UMF core 0.10.0, actions 0.1.0, JSON Schema extension 0.1.0 and the medical pack
were inspected. Exact inspected source hashes and reuse/gaps are in
`schemas/storage-schema-basis.json`. Native UMF records/actions remain authoritative
for application metadata and action meaning. Existing composition supplies
capability references and inert handler binding. No competing action language is
introduced.

The inspected definitions do not specify async object transfer, scoped handles,
continuation or effect uncertainty. The local JSON Schema 2020-12 defines only
boundary values. Python stream/context protocols have no serialized equivalent.
Lexical paths, native authority, races, bounded transfer and conditional behavior
require semantic tests beyond schema validation. No storage dependency is selected.

## Non-Normative Notes

[Databricks Files SDK documentation](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/files.html)
provides streaming upload/download, metadata and directory listing. Its overwrite
default must be overridden explicitly. [Files API 3.0](https://docs.databricks.com/aws/en/volumes/files-api/)
documents conditional/range/multipart features under a workspace-enabled beta.
For multipart requests, precondition headers are set at initiation and checked at
completion; adapters must use the qualified API, not infer SDK method coverage.
[Native directory pagination](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/files.html)
and [S3 prefix/delimiter listing](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html)
inform the portable listing shape. Documentation inspection does not qualify
concurrency, publication, checksums, resume or any workspace/API cohort.
