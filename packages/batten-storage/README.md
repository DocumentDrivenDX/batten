# Batten object storage

`novirhyza-batten-storage` supplies portable async storage protocols and the first
local filesystem provider. It has no third-party runtime dependencies. Importing
`batten.storage` does not import `batten.storage.local` or any cloud adapter.

The provider needs a dedicated owner-only managed directory on a qualified POSIX
filesystem, advisory locks, no-follow directory descriptors and atomic rename.
Logical key segments are limited to 120 UTF-8 bytes by this encoded local layout.
Other writers must use this provider. It does not adopt arbitrary existing files.
Atomic visibility does not promise power-loss durability or network-filesystem
qualification. The complete Batten application runtime is separate work.

A trusted host supplies a complete `Limits` value through its typed configuration,
a stable opaque identity bound to actor/application/resource/profile revision, and
an `Authority` implementation. `check(operation, key, features)` enforces current
permissions, including requested optional features; `observe(...)` records safe
outcomes and metrics through the host's attribution and telemetry services.
Never accept an application-provided identity as authorization.

```python
from batten.storage.local import create_store, initialize

# Explicit maintenance, once, against an approved empty absolute root.
await initialize(approved_root)
provider = create_store(approved_root, resolved_limits)  # pure; no I/O
await provider.prepare()
objects = provider.bind(host_authority)
try:
    receipt = await objects.write("reviews/demo.txt", b"Fabricated review")
    async with objects.open_read(receipt.info.key) as content:
        async for chunk in content:
            await consume(chunk)
finally:
    await objects.aclose()  # shared provider and published bytes remain
    await provider.aclose()
```

Writes default to create-only. Explicit `Any()` permits replacement; `Matches`
requires an opaque current revision. Read ranges, SHA-256 verification, bounded
listing and multipart sessions use the same scoped handle. Listing is shallow by
default; `recursive=True` is explicit. `detail="basic"` leaves unavailable summary
fields null and never performs per-object metadata enrichment. Cursors are opaque,
request-bound, expiring and invalid after restart. Listing is live, not a snapshot.

Resuming uploads across handles/restart requires the original identity, unchanged
limits/profile and `resumable_upload` permission. Sessions without that permission
request abort when their originating handle closes. Upload expiry is enforced on
access; private expired staging is reclaimed on later upload admission. An uncertain
completion remains uncertain; matching bytes never synthesize a receipt. Abort
cannot undo a published object. No random range mutation or append API is exposed.

Build and prove the installed artifact from the repository root using the common
quality command in the root README. `tests/storage/test_distribution.py` builds a
wheel, installs without dependencies into a clean environment, and checks imports.
This source wheel has not been uploaded to a package registry.
