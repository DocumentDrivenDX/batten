# Changelog

All distributions share one version and one `v*` tag. Versions before 0.1.0a3 were
separate GitHub prereleases (`runtime-v*`, `storage-v*`).

## 0.1.0a3 - 2026-11-11

First release from PyPI.

- One version for every distribution; one `v*` tag; tag-driven release workflow with
  trusted publishing to PyPI, a fresh-venv install smoke test and a GitHub Release.
- Seven wheels became three plus the example: `novirhyza-batten` (contracts, runtime,
  tables, ASGI; the `batten.*` import paths are unchanged), `novirhyza-batten-storage`,
  `novirhyza-batten-local` (local host and UMF/Weft provider) and
  `novirhyza-batten-approval-desk`. The old `novirhyza-batten-{contracts,runtime,tables,asgi,umf-postgres}`
  names were never published to PyPI.
- Python 3.11 to 3.13 supported (tested in CI); the workspace was 3.13 only.
- Dependency ranges instead of exact pins: `umf-codegen>=0.10.8,<0.11`,
  `umf-weft>=0.4.57,<0.5`, `umf-access>=0.1.0.dev8,<0.2`, `psycopg>=3.3.7,<4`,
  `pgserver-pg18>=18.6.1,<19` (still installed from its GitHub release until it is
  on PyPI).
- Removed the unimplemented reference-app specifications, evidence and verification
  files, and the ratchet gates; added unit tests for contracts, runtime, ASGI, the
  UMF provider and the local host; CI runs on Linux for every pull request.
- Optional `lintel` extra on `novirhyza-batten-local` hosts the Lintel task board (GraphQL) on generated PostgreSQL; it pins `lintel-api==0.1.0a6`.
- The approval UMF model now lives in `examples/approval-desk/model/`.

## 0.1.0a2 (runtime-v0.1.0a2, 2026-11-03)

- UMF codegen and core 0.10.8; Weft SQL compiler moved from `weft-sql` 0.4.54 to
  `umf-weft` 0.4.57; psycopg 3.3.7.
- TypeScript 7 and Oxlint for the browser tooling; the same two Playwright scenarios.

## 0.1.0a1 (runtime-v0.1.0a1, 2026-11-02)

- First runnable local application: approval desk and a visual app registry, with
  contracts, runtime, table port, UMF/PostgreSQL adapter, ASGI transport and local
  host as separate wheels.
- Submit, edit, approve and reject requests through UMF tables and Weft on PostgreSQL 18;
  a lost mutation response is recovered from its original native receipt.

## storage 0.1.0a1 (storage-v0.1.0a1)

- `novirhyza-batten-storage`: portable async object storage protocols and a managed
  local POSIX provider (scoped writes, pinned reads and ranges, conditional
  replacement, bounded listing, multipart uploads).
