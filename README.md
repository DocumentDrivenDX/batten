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

Start with the [review packet](docs/helix/README.md), including the product
requirements, boundary audit, and proposed module/distribution split. The owner has authorized the local storage implementation. Broader runtime
implementation follows its governed contracts.

Dual licensed under [MIT](LICENSE-MIT) OR [Apache-2.0](LICENSE-APACHE).
Copyright Synaptiq.


Development uses the locked uv workspace and Bun lint tooling:

```sh
uv sync --frozen --all-packages
bun install --frozen-lockfile
uv run python scripts/quality.py
```

The same command runs in CI; `just check` is an equivalent entry point. `just lint`
provides the configured local pre-commit check. Product storage has no third-party
runtime dependencies. Quality tools remain outside its wheel.
