<!-- helix:publish audience=developer page=hosting kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/fda22f74ac68bf22 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-004-host-profiles.md sha256:4f792bde222396d6 -->
<!-- helix:source docs/helix/02-design/adr/ADR-008-independent-composition-axes.md sha256:55626555379d1780 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-001-public-host-api.md sha256:496f18dd0d526258 -->
<!-- helix:source docs/helix/02-design/adr/ADR-004-public-async-host-api.md sha256:7e563f0b689d1140 -->
<!-- helix:source docs/helix/02-design/adr/ADR-006-typed-file-configuration.md sha256:d693d339350ec93e -->

<!-- helix:source docs/helix/01-frame/prd.md sha256:44209bdd519038ed -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-010-platform-assets.md sha256:37a6ebc7946ae5b4 -->

# Choose a host

A host profile binds the application to identity, resources, providers and lifecycle ownership. Changing that profile preserves the application's declared business meaning.

## Develop locally

The required local pattern uses stubbed authentication with explicit fabricated actors and loopback-only access. Those actors pass through normal authorization checks; a missing actor is refused.

Truss and UMF table access share one PostgreSQL 18 pgserver instance. The composition root owns or borrows that instance once; each module borrows its binding. Shared hosting preserves table ownership and permission boundaries. Closing one borrower leaves the others usable.

Starting or reloading an application preserves records. Migration and reset are explicit operations. Local Tether execution uses a host-configured model API; see [platform integrations](integrations.md).

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

## Carry attribution across placements

The host preserves the initiating user, authorized delegation and actual executor through background jobs and remote workers. Local fixtures exercise these boundaries without proving deployed identity.

OpenTelemetry covers system calls, while durable audit records decisions and uncertain effects independently of trace sampling. Missing required attribution or audit capabilities block execution.

## Choose execution placement separately

The design distinguishes in-process execution, child processes and remote workers. Each selected provider must support its placement; a mismatch refuses instead of silently relocating work.

Remote workers require a separately qualified transport, authority and recovery profile. Configuration syntax alone does not supply those guarantees.

## Deploy assets before startup

Operators review and apply asset deployment plans separately from application startup. Trusted receipts identify outputs; preparation checks their contracts, current access and readiness.

A deployed pipeline definition may still need an explicitly authorized initialization run before its tables are usable. Start and reload never provision, migrate or grant access.

Deployment ownership differs from client lifetime. Stopping or removing an application preserves persistent assets by default. External assets retain their producer's lifecycle owner.

## Keep authority explicit

Profiles contain typed settings and opaque resource references. Trusted host services resolve identity and credentials. Application declarations cannot select another tenant or grant themselves provider access.

[Read the host profile contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-004-host-profiles.md).
