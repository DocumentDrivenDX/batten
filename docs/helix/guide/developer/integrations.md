<!-- helix:publish audience=developer page=integrations kind=explanation voice=onboarding budget=800 reviewed=2026-10-29/fleet_alignment_reader/c876dddcc435eb4e -->
<!-- helix:source docs/helix/02-design/architecture.md sha256:ebb43c32ec3db5ba -->
<!-- helix:source docs/helix/02-design/contracts/CONTRACT-005-ux-builder-binding.md sha256:0008fd4ad87e294d -->
<!-- helix:source docs/helix/02-design/adr/ADR-009-ux-builder-ownership.md sha256:d15b944955d35bc9 -->
<!-- helix:source docs/helix/01-frame/features/FEAT-009-composition-and-hosting.md sha256:107baf00adf9690e -->
<!-- helix:source docs/helix/02-design/adr/ADR-002-native-umf-platform-dependency.md sha256:19b600b856750646 -->

# Build on the platform

Batten connects platform capabilities through public boundaries. It depends on upstream libraries and preserves their meaning instead of carrying another implementation of their engines.

## Model and act with UMF

UMF supplies native models, typed access and action declarations. It also owns the saga semantics Batten intends to consume.

Batten binds saga references to explicitly qualified executors. It preserves original outcomes and uncertainty; it does not provide a fallback saga language or claim unsupported execution.

Weft owns query compilation. Arras owns ontology capabilities. Their native types and semantics stay with their modules, outside the platform-neutral core.

## Execute agents with Tether

The Tether module connects agent sessions and operation-to-tool binding. It uses the platform's public execution surface rather than introducing another agent loop.

Model access is a separate gateway capability. Host-managed aliases, budgets and identity remain explicit resource bindings.

## Design with ux-builder

ux-builder owns its design workflow, blueprint, components, themes and audits. Batten adds stable references between controls, UMF metadata and admitted operations.

A portable client and supplied host context connect the same screen across local, standalone and embedded hosts. Navigation, focus, confirmation and downloads follow that public boundary.

The UI must explain loading, denial, validation failure, success and uncertain outcomes. An uncertain write is observed through its original invocation identity; it must not become a fresh automatic write.

## Keep optional integrations optional

Headless applications omit UI dependencies. Platform modules are independently installed, and the host selects providers from a reviewed cohort.

Exact public API and package combinations require integration evidence. Upstream UI audit, browser authorization checks and native execution qualify different properties.

[Explore ux-builder](https://documentdrivendx.github.io/ux-builder/) or read the [binding contract](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/02-design/contracts/CONTRACT-005-ux-builder-binding.md).
