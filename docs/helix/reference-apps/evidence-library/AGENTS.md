# Working on Evidence and attachment library

Read this directory's `.helix.yml` and engage the installed HELIX skill. This is
application MA-004; governed artifacts belong only in `specs/`. Start with
`specs/01-frame/prd.md`, then the story and test plan. Follow
[the Batten app workflow](../../04-build/batten-app-workflow.md), using templates,
prompts and metadata from the installed HELIX catalog. Do not vendor the catalog.

Reference app rules are fabricated conformance defaults, not real business policy.
UMF owns models/actions and typed persistence; PostgreSQL 18 and Truss own native
storage/execution. UI is application-authored TypeScript through the public host
client, with room for ux-builder. No direct database/provider access in the UI.
Read applicable SDK contracts through explicit file paths; local artifact IDs
resolve inside this app scope. App specs do not authorize SDK or upstream edits.

Build only after a scoped app implementation instruction and qualified integration
closure. No credentials, production data, migrations, applies, commits or pushes
without their applicable authorization. Never replace a required failing positive
case with a skip, mock result or changed expected outcome.
