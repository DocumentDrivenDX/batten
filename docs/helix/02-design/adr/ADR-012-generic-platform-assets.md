---
ddx:
  id: ADR-012
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: FEAT-009
      kind: derived_from
    - id: ADR-001
      kind: informed_by
    - id: ADR-008
      kind: informed_by
---

# ADR-012: Generic platform assets with provider-owned deployment

## Problem

Applications need tables, pipelines and other platform assets, including assets
owned by independent teams. Embedding Databricks bundle syntax in core would
couple application admission to one vendor and confuse deployment ownership with
the lifetime of borrowed runtime clients.

## Decision

Use optional stdlib-only `batten.platform` for CONTRACT-010's asset declarations,
provider protocols, deployment plans and receipts. Core retains generic capability
assessment and lifecycle, with no asset/provider-specific imports or branches.
Providers interpret native source packages and return scoped runtime bindings.
Host composition injects the wrapper and admitted provider; operators own apply.

Support app-managed packages, exact external release/output dependencies and
mixed manifests. Each physical resource has one lifecycle owner. Generic wrappers
describe contracts, access and readiness; qualified native tooling owns data models,
DDL and pipeline definitions. Preserve original source closure and unknown bytes.

The first provider target is `batten.databricks.platform`, using Databricks
Declarative Automation Bundles for supported resources. Its native format,
toolchain, workspace bindings and Unity Catalog identities stay adapter-owned.
CONTRACT-010 applies to other providers without promising semantic equivalence.

## Why We Chose This

### Over native bundles in the core interface

A provider protocol hides native syntax and state while retaining exact source
identity. Core can assess capability metadata without importing a vendor SDK or
executing native build/deployment hooks.

### Over startup provisioning

Separate deployment plans expose migrations, initialization and partial effects
for operator review. Application startup verifies readiness without taking broad
creation privileges or treating a deployed definition as usable data.

### Over implicit bundle dependencies

Explicit resource contracts and trusted deployment receipts retain owner,
compatibility, environment and readiness evidence. Name lookups alone do not
establish those properties or authorize modification of a shared asset.

## Consequences

**Good**: Applications carry their own packages, consume shared assets and vary
environment bindings through one generic boundary. Persistent data outlives
runtime shutdown. Existing operator infrastructure ownership is preserved.

**Trade-offs**: Each provider must qualify supported formats, resource kinds,
identity, drift, initialization and recovery. A small wrapper cannot make native
deployments atomic or translate all platform schemas into one portable language.

**Drift signals to watch**: Bundle/Unity Catalog fields in core; native IDs in
application logic; apply during start; multiple state managers owning one asset;
remote installers bypassing cohort policy; external resource adoption by lookup.

## Validation

**Result**: not tested.
**Evidence**: CONTRACT-010 and TP-001 PLT allocation define required behavior.
Databricks documentation supports bundle resources, variables and app bindings;
it does not qualify Batten's adapter or a selected CLI/API cohort.

## Concern Impact

Preserves hexagonal architecture, platform adapter ownership and typed file
configuration. No framework, runtime dependency or deployment authorization is added.
