---
ddx:
  id: ADR-014
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: informed_by
---

# ADR-014: Independently scoped reference applications

## Problem

Reference apps must describe business outcomes independently of SDK internals.
One shared spec tree can confuse an app requirement with a platform requirement
and let a passing platform unit test masquerade as a complete app journey.

## Decision

Each app has a nested HELIX marker binding only its own `specs/` tree. The SDK
retains its existing root. A shared Batten app workflow specializes the installed
HELIX lifecycle through repository instructions; it does not fork the catalog,
add a second public skill or invent an unsupported methodology resolver.

Corpus references qualify artifact identity with the application ID and path.
Each scope resolves its own local artifact links. Platform contracts are explicit
file dependencies, not unregistered cross-flow graph edges. Repeated generic
requirements use shared obligations; app-specific business rules remain local.

## Why We Chose This

### Over a single shared application PRD

Independent roots preserve each app's user outcome, owner decisions and evidence.
They can be targeted by opening that app directory and invoking HELIX there.

### Over a vendored HELIX catalog or new helix-batten skill

Installed templates and prompts remain authoritative. Batten owns only the
product-specific selection, inputs and exit gates. A future native catalog
extension requires upstream agreement rather than a guessed plugin API.

## Consequences

**Good**: Each example is an independent specification and qualification target.
**Trade-offs**: Aggregate tooling must understand nested roots and qualified IDs.
**Drift signals to watch**: Shared root assumptions, copied methodology templates,
or changing an app's expected result merely to match a provider defect.

## Concern Impact

Preserves cleanroom boundaries, fewest-tests policy and platform modularity.
The corpus is author/test data, never a portable-core runtime dependency.
