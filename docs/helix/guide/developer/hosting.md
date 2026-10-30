<!-- helix:publish audience=developer page=hosting kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/fleet_alignment_reader/19805e44c1ab7694 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-004-host-profiles.md sha256:364f6a74adf2a817 -->
<!-- helix:source docs/helix/02-design/adr/ADR-008-independent-composition-axes.md sha256:55626555379d1780 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-001-public-host-api.md sha256:543a6c53e2e03a58 -->
<!-- helix:source docs/helix/02-design/adr/ADR-004-public-async-host-api.md sha256:7e563f0b689d1140 -->
<!-- helix:source docs/helix/02-design/adr/ADR-006-typed-file-configuration.md sha256:d693d339350ec93e -->
<!-- helix:source docs/helix/01-frame/prd.md sha256:ffee14faf077b38c -->

# Choose a host

A host profile binds the application to identity, resources, providers and lifecycle ownership. Changing that profile preserves the application's declared business meaning.

## Develop locally

The local pattern uses explicit fabricated identity and loopback-only access. It can own a PostgreSQL 18 development instance and supervised process resources.

Fabricated identity is restricted to local hosting. A local configuration is not evidence of deployed identity or service behavior.

## Run a standalone service

In the standalone pattern, Batten owns its service lifecycle inside operator-managed infrastructure. The operator supplies authenticated identity, approved providers and resources.

Batten does not provision that infrastructure. A platform choice such as Lakebase is separate from the hosting pattern.

## Embed in an existing host

An embedding application supplies services through Batten's public API. It can lend a database service and retain ownership of its lifetime.

Batten closes owned resources in reverse dependency order. It leaves borrowed services open. Incomplete cleanup remains visible instead of reporting a completed shutdown.

## Share infrastructure across applications

Shared hosting targets hundreds of applications using common declarative services. Each application retains its own authorization, resource allocation, diagnostic attribution and lifecycle.

Hosts enforce configured concurrency, limits and fairness. Application shutdown preserves other borrowers' services. Actual fleet capacity requires workload and failure-domain measurements.

Required telemetry remains host-controlled. An application cannot disable required capture, and capture loss stays visible. Graph interactions check declared capabilities and current target access.

## Choose execution placement separately

The design distinguishes in-process execution, child processes and remote workers. Each selected provider must support its placement; a mismatch refuses instead of silently relocating work.

Remote workers require a separately qualified transport, authority and recovery profile. Configuration syntax alone does not supply those guarantees.

## Keep authority explicit

Profiles contain typed settings and opaque resource references. Trusted host services resolve identity and credentials. Application declarations cannot select another tenant or grant themselves provider access.

[Read the host profile contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-004-host-profiles.md).
