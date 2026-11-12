# Batten

Batten is a small Python application SDK from Novirhyza. You declare tables and
operations once; Batten hosts them behind a public operation API with identity,
audit capture, bounded concurrency and an ASGI transport, on top of UMF and Weft
tables stored in PostgreSQL 18.

**Status: alpha (0.1.0a3).** What CI tests today, on Linux with Python 3.11, 3.12
and 3.13: the host runtime, the ASGI registry and operation endpoints, the local
object store, the UMF table provider (compiling the approval model with released
`umf-codegen`), and the example approval desk end to end on a real pgserver
PostgreSQL 18 cluster with Playwright browser scenarios (Python 3.13).

Batten ships **standalone** for now. It depends on UMF, Weft and pgserver only;
there is no Arras, Lintel or Truss integration yet (see the [roadmap](ROADMAP.md)).
Local identities are loopback development stubs, not production authentication.

## Install and run the example

Needs Python 3.11 to 3.13 on Linux or macOS arm64. `pgserver-pg18` is not on PyPI
yet, so the install points pip at its GitHub release.

<!-- quickstart -->
```sh
python -m venv .venv
. .venv/bin/activate
pip install --pre --find-links https://github.com/DocumentDrivenDX/pgserver/releases/expanded_assets/pg18.6-pgv0.8.6-r2 novirhyza-batten-approval-desk
batten-approval init
batten-approval call --actor alex --operation list
batten-approval serve
```
<!-- /quickstart -->

`init` creates a fabricated local PostgreSQL 18 cluster in `.local/approval`;
`call` runs one operation as Alex; `serve` starts the app. Open
<http://127.0.0.1:8820/> and choose **Approval desk**. CI runs these exact commands
against the built wheels before every release.

## Packages

All distributions share one version and one `v*` release tag.

| PyPI name | Import | What it is |
|---|---|---|
| `novirhyza-batten` | `batten.contracts`, `batten.runtime`, `batten.tables`, `batten.asgi` | Operation contracts, host runtime, table port, ASGI transport and app registry |
| `novirhyza-batten-storage` | `batten.storage` | Portable object storage and a managed local filesystem store; no dependencies |
| `novirhyza-batten-local` | `batten.hosting.local`, `batten.umf_postgres` | Local host and UMF/Weft table provider on pgserver PostgreSQL 18 |
| `novirhyza-batten-approval-desk` | `approval_desk` | The example app (`batten-approval` command) |

## Development

```sh
uv sync --frozen --all-packages
bun install --frozen-lockfile
uv run python scripts/check.py        # boundaries, ruff, pyright, oxlint, tsc, pytest
uv run python scripts/prepare_approval.py && uv run pytest -m integration && bun run test:native
```

The last line needs native PostgreSQL (pgserver) and a Playwright browser; it runs
in CI on every pull request. See [AGENTS.md](AGENTS.md) for the layout and rules.

## More

[Microsite](https://documentdrivendx.github.io/batten/) ·
[Changelog](CHANGELOG.md) · [Roadmap](ROADMAP.md) ·
[Design records](docs/helix/README.md) · [Object storage](packages/batten-storage/README.md)

Dual licensed under [MIT](LICENSE-MIT) OR [Apache-2.0](LICENSE-APACHE).
Copyright Synaptiq.
