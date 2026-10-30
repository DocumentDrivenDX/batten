---
ddx:
  id: ADR-007
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: batten.concerns
      kind: informed_by
---

# ADR-007: Enforce boundaries, shape, and a decreasing test budget

## Problem

Module names do not enforce boundaries. Large units and duplicated tests can
recreate a monolith even with a platform package layout. A greenfield test count
of zero cannot be the permanent ceiling while implementing required behavior.

## Decision

Implement CONTRACT-002's actual import/public-surface, cycle, code-shape, and
test-count checks before dependent feature code. One local quality entry point
is used by edit checks, pre-commit, and CI; it fails rather than skipping because
the comparison base or module inventory is missing.

Use the fewest tests that pin observable behavior, one primary test per behavior,
with parameterized inputs and whole-outcome assertions. Reuse an existing scenario
before adding another. Separate integration/registry/browser outcomes only where
they prove a distinct boundary; preserve authorization, non-disclosure, isolation,
and concurrency invariants exactly once each.

The owner authorized the first reviewed behavioral suite to establish the measured
test-count ceiling. After that, the ceiling and count only decrease. No automatic
growth exception, renamed helper-test, hidden body, duplicate layer, skipped test,
or count change can evade the rule. New genuinely distinct behavior that cannot
fit requires an owner decision changing this policy, not a silent gate bypass.

The exact code-shape limits come from the stricter of the observed reference
ceilings and the installed greenfield defaults, as recorded in CONTRACT-002.
No numeric test budget, coverage floor, latency target, or claimed platform
capacity is invented. Numeric policy values and measured outcomes are distinct.

## Application evidence and upgrade gates

PRD FR-27/29/42 require host-enforced telemetry, application assertions and test
coverage of declared behavior for admission and candidate runtime qualification.
Required evidence must be current for exact application/cohort inputs and cannot
be replaced by a coverage percentage or a declared list of tests. Missing, failing
or stale evidence refuses the affected admission or upgrade qualification.

This strengthens behavioral assurance while preserving the decreasing function
budget: consolidate redundant tests without dropping distinct invariants. No
numeric code-coverage floor or automatic test-count exception is introduced.
CONTRACT-002 governs evidence obligations; telemetry schema, runtime failure policy
and evidence exchange remain downstream contract work before implementation.

## Semantic generation decision

FR-47 requires automatic property-based end-to-end suites and complete CLI access
for all default fully declarative constructs and UI/hook compositions. Author
intent and effective refinements define the model; qualified adapters exercise
each platform and renderer against its oracle. Reuse those properties for migration.
Shared behavior runners and generated cases must preserve the decreasing function
budget. There is no automatic growth exception. The property-testing framework,
CLI/test-model protocols and evidence format need separate selection/contracts;
this direction authorizes no package installation or runtime implementation.

## Why We Chose This

### Over a test-growth trailer as an automatic exception

The owner requires a ceiling that only moves down. An automatic positive-growth
exception would defeat that stronger requirement.

### Over one test per function or repeated coverage at every layer

Tests should detect a distinct failure at a public boundary. A private refactor
should not force rewriting several tests of the same outcome.

## Consequences

**Good**: Boundary and quality claims are executable, and suite maintenance has
an explicit budget tied to measured behavior coverage.

**Trade-offs**: The first suite needs deliberate review. Subsequent changes must
consolidate redundancy without hiding missing behaviors or changing tests to match defects.

**Drift signals to watch**: undocumented exclusions, raised limits, missing-base
passes, renamed tests, growing parameter tables that mix unrelated behavior, or
claims of mechanical enforcement based only on a document.

## Concern Impact

Records stricter branch/test-file limits for code-shape-ceilings and the
owner's stronger testing policy. The checks' implementation follows the review gate.
