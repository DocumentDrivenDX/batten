# Note/Task release gate

GitHub Releases stores the sealed packet. The CI entry point downloads it
into a new directory, verifies the archive SHA-256 before extraction, and
checks every file against the reviewed manifest. It removes the downloaded
and extracted inputs after the run, leaving the receipt.
[Durable packet release](https://github.com/DocumentDrivenDX/batten/releases/tag/note-task-packet-20261111)

```sh
bash scripts/note_task_gate/ci.sh verify "$(mktemp -d)/note-task"
```

Replace `verify` with `macos`, `linux`, `apps`, or `workers` for an individual
target. `gate.py all` accepts an already verified packet and runs the four
targets serially. A missing pin, failed replay, or failed cleanup fails the
gate. Each receipt identifies the shared source and records completed targets.

## GitHub Actions

The Note/Task release workflow runs packet preflight on pull requests and main
pushes that change the gate. A manual dispatch from `main` runs the four target
jobs after preflight and uploads their receipts. It uses dedicated runners
labeled `batten-note-task-macos`, `batten-note-task-linux`,
`batten-note-task-apps`, and `batten-note-task-workers`. Install the pinned
prerequisites on those runners and limit runner access to trusted workflows.
Configure the matching `note-task-<target>` environments before dispatching.

Set `BATTEN_GATE_PYTHON` when the pinned Python is outside the runner's PATH.
For macOS, set `BATTEN_GATE_UV` and set `BATTEN_GATE_PG_BIN` if PostgreSQL is
outside `/opt/homebrew/bin`. For Apps, configure the `aidev-cus` login on the
runner and set `BATTEN_DATABRICKS_APP`, `BATTEN_DATABRICKS_HOST`, and
`BATTEN_DATABRICKS_WORKSPACE_ID` as environment variables in GitHub Actions.
For Workers, set the environment variable `CLOUDFLARE_ACCOUNT_ID` and the
environment secret `CLOUDFLARE_API_TOKEN` for the qualification account.

| Target | Runner prerequisites and cleanup |
| --- | --- |
| macOS | macOS arm64, the pinned CPython 3.11.17 and uv executables, and Homebrew PostgreSQL 18.6. Use `--python`, `--uv`, and `--pg-bin` to select the matching installation. The gate stops the temporary socket-only cluster. |
| Linux | Docker with the two local arm64 images identified by SHA-256 in the gate. The gate uses an internal network and removes the runner, database container, and network. |
| Databricks Apps | The pinned Databricks CLI and an authenticated profile, defaulting to `aidev-cus`. Pass `--app` for a dedicated stopped qualification app, `--workspace-host`, and `--workspace-id`. The gate uses the caller's workspace identity, stops the app, and deletes the run's uploaded source directory. |
| Workers/D1 | The pinned Node and npm versions and an authorized Cloudflare account ID passed via `--cloudflare-account`. npm verifies Wrangler dependencies against the packaged lock. The gate creates a private Worker and Workflow with a disposable D1 database and deletes all three. |

The packet manifest pins all 962 input files, including the writable UMF
source, prepared SQL and Lintel artifacts, generated SDK, synthetic fixtures,
runtime dependencies, wheel locks, and deployed harness. PostgreSQL readers
and migration administrators install binary-only, hash-pinned wheels offline.
Workers loads its pinned packaged Python runtime. The gate runs the shipped
artifacts without UMF, Weft, or Lintel compilation.

The suite verifies an owner-scoped write, effect receipt recovery and replay,
owner isolation, the Task-to-Note join, and Lintel Relay pagination and
readback. Each target applies its own prepared forward migration and proves
that the data survived and the new head is live. PostgreSQL adds an index.
D1 renames a table and column, then checks that the receipts and foreign keys
survived as well.

`scripts/note_task_gate/assemble.py` builds a packet from the prepared host
staging directories and wheel inventories. Review the resulting manifest as
part of a new candidate. The run command consumes the reviewed manifest and
checks it before creating any resource.

The four targets passed as independent gate invocations. A fresh archive
extraction passed preflight, and changing the D1 source byte stream caused
preflight to fail before any service calls.
[Gate receipt](receipt.json) · [Archive SHA-256](archive.sha256)

The CI entry point passed preflight and all four targets from a fresh Batten
clone with only the candidate gate and workflow files applied. Every target
fetched the published archive and retained its receipt after removing the
staged inputs. GitHub Actions dispatch still requires the workflow on main
and registered qualification runners.
[Clean-checkout receipt](ci-clean-checkout.json)
