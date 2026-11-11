# Approval desk

A working local Batten application: submit and edit a request, inspect the current
revision, and let a different person approve or reject it. Alex and Casey are
requesters; Blake is an independent reviewer who can also submit requests.
All identities and data are fabricated.

From the repository root, with Python 3.13, uv, Bun and Just installed:

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

`just approval-prepare` bundles the TypeScript app, builds the Batten wheels from
this checkout and installs them with their dependencies into
`.cache/approval-runtime`. Serving and calling the app do not install anything.

The installed CLI uses the same host, identity, business operations and native
tables as the browser:

```sh
.cache/approval-runtime/bin/python -I -m approval_desk.cli call --actor blake --operation list
```

The authoritative declaration is
[approval.umf.json](model/approval.umf.json).
Original UMF owns records, row permissions, queries, conditional commands and
receipts; Weft owns SQL planning. App procedural hooks validate public inputs and
map outcomes through Batten's table port. The UI is an authored TypeScript DOM
application; it does not claim a declarative UI engine or ux-builder integration.

Browser scenarios (Playwright, real PostgreSQL 18 through pgserver):

```sh
node node_modules/playwright/cli.js install chromium
just approval-test
```

This preview has one record table, bounded queries, one local host and loopback
stub login, which is a development facility. It is not a production deployment.

For UI or procedural-hook edits after the initial platform preparation, stop the
local host, run `just approval-refresh`, then `just approval`. This rebuilds only
the app wheel against the prepared platform cohort. Model changes still require
an explicitly initialized matching database; startup does not migrate existing
data. The registry is composed from explicit `AppListing`/ASGI app entries using
`batten.asgi.create_registry`; configured entries supply their own app bindings.
