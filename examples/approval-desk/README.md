# Approval desk

A working local Batten application: submit and edit a request, inspect the current
revision, and let a different person approve or reject it. Alex and Casey are
requesters; Blake is an independent reviewer who can also submit requests.
All identities and data are fabricated.

From the repository root, with Python 3.13, uv 0.13.7, Node 26.13.0, Bun 1.4.4 and Just installed:

```sh
uv sync --frozen --all-packages
bun install --frozen-lockfile
just approval-prepare
just approval-init
just approval
```

Open the registry at <http://127.0.0.1:8820/>, choose **Approval desk**, then
choose a local identity. The app lives at `/apps/approval-desk/`; the Batten brand
returns to the registry. Registered apps supply a title, description and packaged
thumbnail, with separate API and cookie paths. Use separate browser
profiles to inspect a request as Blake and then edit it as Alex. Blake's stale
decision is refused; refresh and inspect before deciding again. A lost mutation
response retains its original key; **Check original outcome** queries the native
receipt rather than silently creating another command.

`approval-init` explicitly creates a new dedicated PostgreSQL 18 pgserver cluster
under `.local/approval`. It refuses an existing data directory. Ordinary startup
verifies the installed model and native schema head; it never creates roles or
migrates tables. Restarting preserves requests and native receipts; local login
sessions must be established again. `local.toml` supplies typed limits and port.
No application environment variables or cloud credentials are needed.

The assembler downloads the original access dev8 wheel from `umf-v0.5.8` and
Codegen 0.10.8 from `umf-v0.10.8`, verifying each original SHA-256 digest.
Codegen selects exactly Core 0.10.8 through normal dependency resolution.
The SQL compiler is `umf-weft==0.4.57`. Batten
packages are built from this checkout. Dependencies are installed once at
composition time into `.cache/approval-runtime`; serving and calling the app do
not install Python or npm dependencies. Cohort and wheel hashes are recorded in
`.cache/approval-cohort.json`.

The installed CLI uses the same host, identity, business operations and native
tables as the browser:

```sh
.cache/approval-runtime/bin/python -I -m approval_desk.cli call --actor blake --operation list
```

The authoritative declaration is
[approval.umf.json](../../docs/helix/reference-apps/approval-desk/specs/02-design/models/approval.umf.json).
Original UMF owns records, row permissions, queries, conditional commands and
receipts; Weft owns SQL planning. App procedural hooks validate public inputs and
map outcomes through Batten's table port. The UI is an authored TypeScript DOM
application; it does not claim a declarative UI engine or ux-builder integration.

Verify the installed native path separately from the fast gate:

```sh
node node_modules/playwright/cli.js install chromium
just approval-test
just check
```

The two browser scenarios are JavaScript Playwright tests; Python Playwright,
pyee and the V8 compiler dependency are absent from this cohort. Oxlint enforces
the same four shape limits alongside TypeScript 7 compilation.

This preview selects one record table, bounded queries (up to the model's declared
page size), one local host and this exact original platform cohort. Loopback stub
login is a development facility. Local redacted OpenTelemetry capture is not an
OTLP receiver qualification or fleet-deployment claim. The complete micro-app
conformance gate still refuses until its full execution obligations are met.

For UI or procedural-hook edits after the initial platform preparation, stop the
local host, run `just approval-refresh`, then `just approval`. This rebuilds only
the app wheel against the prepared platform cohort. Model changes still require
an explicitly initialized matching database; startup does not migrate existing
data. The registry is composed from explicit `AppListing`/ASGI app entries using
`batten.asgi.create_registry`; configured entries supply their own app bindings.
