<!-- helix:publish audience=developer page=integrations kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/microsite_reader_review/80c026964778503c -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-009-service-discovery-and-binding.md sha256:53b8b2e0e2ef2dc3 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-010-platform-assets.md sha256:37a6ebc7946ae5b4 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-007-messaging.md sha256:f265082768032e42 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-006-object-storage.md sha256:7ba084a3e83a0976 -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:ffb0e445269fc317 -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-005-ux-builder-binding.md sha256:e258d27340318003 -->
<!-- helix:source docs/helix/02-design/adr/ADR-009-ux-builder-ownership.md sha256:d15b944955d35bc9 -->
<!-- helix:source docs/helix/01-frame/features/FEAT-009-composition-and-hosting.md sha256:ad49c3fcde9f276e -->
<!-- helix:source docs/helix/02-design/adr/ADR-002-native-umf-platform-dependency.md sha256:19b600b856750646 -->

<!-- helix:source docs/helix/02-design/adr/ADR-012-generic-platform-assets.md sha256:1c38e89475ee2c90 -->

# Build on the platform

Batten connects platform capabilities through public boundaries. It depends on upstream libraries and preserves their meaning instead of carrying another implementation of their engines.

## Model and act with UMF

UMF supplies native models, typed access and action declarations. It also owns the saga semantics Batten intends to consume.

Batten binds saga references to explicitly qualified executors. It preserves original outcomes and uncertainty; it does not provide a fallback saga language or claim unsupported execution.

Weft owns query compilation. Arras owns ontology capabilities. Their native types and semantics stay with their modules, outside the platform-neutral core.

## Deploy platform assets

The optional platform wrapper accepts application-owned packages and external resource contracts. Providers translate native formats and return scoped bindings after deployment and readiness verification.

Databricks is the first target. Its adapter owns bundle syntax, workspace bindings and Unity Catalog identities. Tables and pipelines keep their native lifecycle; the generic interface promises no automatic schema translation.

Operator planning and approved apply are separate from runtime startup. The host checks required contracts and current grants before use; persistent assets survive application shutdown.

## Store byte objects

A storage resource gives application hooks relative object keys and streamed byte operations. The host binds it to a local managed directory or Databricks Volumes.

The optional storage module owns the interface; each backend preserves its native authority. Application filenames and attachment metadata remain UMF records.

Write conditions can require an absent object or a matching version. Range reads can pin that version across requests. Multipart uploads check their captured condition when completing.

Listing is shallow by default, with child prefixes and key-only results. Richer summaries use native listing metadata without a separate request for every object.

Conditional updates, atomic visibility, integrity verification and resumability each require qualified support. An interrupted upload can leave an uncertain outcome; file bytes and metadata rows do not share a transaction.

## Publish and consume messages

The messaging design starts with PostgreSQL 18. Applications use scoped channels and durable subscriptions through one public boundary, without receiving broker or database connections.

Payload profiles pin existing UMF definitions and qualified codecs. Delivery retries retain their causal origin and distinct attempts; publication does not grant a consumer the producer's authority.

Future brokers need separate qualification. Database staging does not imply atomic publication across unrelated databases or services.

## Discover shared application services

Batten's platform ontology describes application interfaces, exports, requirements and host-approved bindings. Arras provides scoped discovery; shared business types retain their own UMF ownership.

Exact revisions and current grants govern use. Seeing an export grants no execution permission, and a changed binding cannot silently choose a new provider or replay a command.

## Execute agents with Tether

The Tether module connects agent sessions and operation-to-tool binding. It uses the platform's public execution surface rather than introducing another agent loop.

Model access is a separate gateway capability. Host-managed aliases, budgets and identity remain explicit resource bindings.

For local development, the host binds Tether to an explicit model API and model profile through typed configuration. Agent tools still require declared bindings and approval. An unavailable API produces an explicit failure; it never silently switches to another endpoint or a scripted response. Scripted model fixtures provide separate deterministic test evidence.

## Design with ux-builder

ux-builder owns its design workflow, blueprint, components, themes and audits. Batten adds stable references between controls, UMF metadata and admitted operations.

A portable client and supplied host context connect the same screen across local, standalone and embedded hosts. Navigation, focus, confirmation and downloads follow that public boundary.

The UI must explain loading, denial, validation failure, success and uncertain outcomes. An uncertain write is observed through its original invocation identity; it must not become a fresh automatic write.

## Keep optional integrations optional

Headless applications omit UI dependencies. Platform modules are independently installed, and the host selects providers from a reviewed cohort.

Exact public API and package combinations require integration evidence. Upstream UI audit, browser authorization checks and native execution qualify different properties.

[Explore ux-builder](https://documentdrivendx.github.io/ux-builder/) or read the [binding contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-005-ux-builder-binding.md).
