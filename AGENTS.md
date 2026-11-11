# Working in Batten

Batten is an application SDK: a UMF/Weft/PostgreSQL-backed local host, an ASGI
registry and an object store. Packages: `packages/batten` (contracts, runtime,
tables, asgi), `packages/batten-storage`, `packages/batten-local` (local host and
`umf_postgres`); example app in `examples/approval-desk`. One version for all,
checked by `scripts/check_versions.py`; releases are `v*` tags (`release.yml`).

- Setup and checks: `uv sync --frozen --all-packages`, `bun install --frozen-lockfile`,
  `uv run python scripts/check.py` (boundaries, ruff, pyright, oxlint, tsc, pytest).
- Integration and browser tests need native PostgreSQL via pgserver:
  `uv run python scripts/prepare_approval.py`, `uv run pytest -m integration`,
  `bun run test:native`. They run nightly in CI; run them locally only on macOS or
  Linux with PostgreSQL on a Unix socket, never TCP 5432.
- Import boundaries (`scripts/boundary_model.py`, `scripts/public-api.json`): portable
  packages must not import native or platform modules. Keep new public names in
  `public-api.json`.
- Use fabricated data only; no credentials. MIT OR Apache-2.0.
- `README.md` has the quickstart that `scripts/smoke_install.py` executes in CI; keep
  its commands and that script in step.
- CI is the gate. Do not commit evidence, receipts, verification JSON or
  qualification packets. `ROADMAP.md` lists what is not built; do not describe it as
  supported.
