---
ddx:
  id: ADR-003
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-001
      kind: informed_by
---

# ADR-003: Distribute platform modules separately

## Problem

Optional dependencies in one wheel can keep installation light, but the wheel
still carries every integration and permits accidental cross-platform imports.
Consumers need installation and verification at the actual platform boundary.

## Decision

Use separate Python wheels with one shared namespace and no eager root exports.
Names below are proposals, not registry-availability or publication claims.

| Distribution | Import modules | Direct dependency boundary |
|--------------|----------------|----------------------------|
| `novirhyza-batten-core` | `batten.contracts`, `batten.runtime` | Standard library |
| `novirhyza-batten-tools` | `batten.packaging`, `batten.testing` | Core and artifact tooling; pytest at test-runner boundary |
| `novirhyza-batten-workers` | `batten.workers` | Core and OS process APIs |
| `novirhyza-batten-umf` | `batten.umf` | Core and public UMF validation/metadata APIs |
| `novirhyza-batten-hosting` | `batten.hosting` | Core and typed-settings tools; provider factories injected |
| `novirhyza-batten-tables` | `batten.tables` | Core and public UMF/Weft packages |
| `novirhyza-batten-postgres` | `batten.postgres` | Core and psycopg; messaging provider extra adds public Batten messaging |
| `novirhyza-batten-messaging` | `batten.messaging` | Core and stdlib; provider and qualified codec implementations injected |
| `novirhyza-batten-lakebase` | `batten.lakebase` | Core and Databricks SDK for authority/endpoint integration |
| `novirhyza-batten-storage` | `batten.storage`, including local provider | Core and stdlib |
| `novirhyza-batten-databricks` | `batten.databricks` | Core, public Batten storage protocol and Databricks SDK for resource APIs |
| `novirhyza-batten-gateway` | `batten.gateway` | Core and supported gateway client/HTTPX |
| `novirhyza-batten-arras` | `batten.arras` | Core and public Arras/UMF packages |
| `novirhyza-batten-tether` | `batten.tether` | Core and public Tether package |
| `novirhyza-batten-asgi` | `batten.asgi` | Core and FastAPI/Starlette |
| `novirhyza-batten-mcp` | `batten.mcp` | Core and public MCP SDK |
| `novirhyza-batten-dev` | `batten.dev` | Reviewed public module cohort, settings/server tools, PostgreSQL 18 helper |

The browser bridge has its own versioned artifact, proposed as
`@novirhyza/batten-ui`; host and frame protocol compatibility is explicit.
The optional ux-builder adapter is a separate browser artifact, proposed as
`@novirhyza/batten-ux-builder`, depending on the portable client and the selected
public ux-builder cohort. It adds no mandatory dependency to headless wheels.
Extras may provide convenient installation groups referencing these wheels;
they do not weaken the underlying module boundaries.

A release publishes an exact tested cohort and a lock/install manifest. Platform
modules built into a host are resolved at host build time. Plugin admission checks
both allowed dependency names and version constraints against that installed cohort;
it never fetches dependencies or treats a name-only match as compatibility.

Platform owners assemble these artifacts and their resolved dependencies into a
complete qualified runtime. Application build, admission and start consume it
without pip/npm installation or registry resolution. This includes supplied
browser assets; optional modules remain selectable during platform assembly.
The platform owns dependency upgrades and their cross-application qualification.
Exact runtime transport/container/archive format remains a later packaging design;
this decision does not select a new deployment technology.

Provisional risk: namespace packaging and cohort release automation add work.
An installed-artifact proof must demonstrate independent imports and wheel-only
development hosting before a distribution support claim.

## Why We Chose This

### Over one wheel with extras

Extras select dependencies, not physical module ownership. Separate wheels make
the platform dependency closure installable and independently testable.

### Over one wheel per source file

Distribution follows a platform or stable portable-tool boundary. Internal source
decomposition remains a module concern and does not create more releases.

## Consequences

**Good**: Hosts install the platform integrations they supply; the portable core
can be checked without those integrations present.

**Trade-offs**: Coordinated release and compatibility testing across multiple
artifacts; namespace/package metadata must not overwrite another wheel's files.

**Drift signals to watch**: monolithic mandatory adapter dependencies, mixed
untested cohorts, runtime installation, or platform libraries copied into a wheel.

## Concern Impact

The proposal follows platform-adapter ownership and Python/uv packaging. It
does not select a package registry or create any remote repository.

Wheel construction uses Hatchling through the uv build toolchain. Hatchling is a
build-only dependency; Ruff, strict Pyright, pytest, pytest-asyncio and the wheel
build frontend remain development tools. pytest-asyncio executes the async public
boundary behaviors without introducing an application event loop or framework.
No application loads the build toolchain or installs dependencies at invocation.
