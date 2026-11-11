# Batten

Batten is an application software development kit (SDK) in the Novirhyza family.
Authors define native data structures, operations, workflows, jobs, and interfaces.
A public host contract handles admission, execution, integration, and delivery
through explicitly bounded platform modules.

The proposed portable core has no ontology-specific capability. An ontology
provider is one Batten module, backed by Arras. UMF, Weft, Tether, and other
platform libraries are dependencies supplied by the platform.

Visit the [Batten microsite](https://documentdrivendx.github.io/batten/).

Explore the [microsite source and local preview instructions](docs/helix/site/README.md)
or read the [application overview](docs/helix/guide/developer/index.md).
The microsite explains the design. The first source implementation is the optional
[local object-storage package](packages/batten-storage/README.md); the complete
application runtime remains in design.

Dual licensed under [MIT](LICENSE-MIT) OR [Apache-2.0](LICENSE-APACHE).
Copyright Synaptiq.


Development uses Python 3.13, Node 26.13.0, Bun 1.4.4 and the locked uv 0.13.7
workspace. Oxlint and TypeScript 7 supply the browser quality checks:

```sh
uv sync --frozen --all-packages
bun install --frozen-lockfile
uv run python scripts/check.py
```

`just test` runs both the Python suite and the two JavaScript Playwright scenarios.
The same quality command runs in CI; `just check` is an equivalent entry point. `just lint`
provides the configured local pre-commit check. Product storage has no third-party
runtime dependencies. Quality tools remain outside its wheel.


What is not built is listed in the [roadmap](ROADMAP.md).

## Run the first reference application

The [approval desk](examples/approval-desk/README.md) uses original UMF tables and
Weft on a dedicated PostgreSQL 18 pgserver, a modular local Batten host and an
authored TypeScript UI. Start with `just approval-prepare`, explicitly initialize
with `just approval-init`, then run `just approval`. The installed app opens at
<http://127.0.0.1:8820/>. Browser tests run with `just approval-test`;
`just check` stays independent of database processes.
