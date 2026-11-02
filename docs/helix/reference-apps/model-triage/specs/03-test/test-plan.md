---
ddx:
  id: TP-108
  type: test-plan
  activity: test
  authoring:
    home: repo
  links:
    - id: US-108
      kind: informed_by
---

# AI-assisted inbox triage: conformance allocation

## Strategy

**Goal**: Qualify MA-008's full authorized journey and distinct business invariant.
**Out of scope**: No exactly-once external side-effect guarantee or autonomous high-impact decision.
Use shared runner obligations from SDK CONTRACT-011 and preserve the independent
story expectations. No app result may be inferred from inventory validation.

## Framework Selection & Cost

| Layer | Framework | Justification | CI Time Impact | Maintenance Burden |
| --- | --- | --- | --- | --- |
| Inventory | Existing stdlib corpus checker | Exact scope/fixture integrity without app loading | Measured by shared command; no estimate supplied | Shared |
| Native actions | Qualified UMF/existing provider conformance | Reuse native ORM/graph semantics rather than duplicate them | Unknown; Erik owns budget | One shared runner, app data |
| UI journey | Real TypeScript client/browser harness | Authored UI requires independent observable journeys | Unknown; harness selection precedes app build | App acceptance scenarios |
| Model behavior where requested | Deterministic scripted API plus separate live API cut | Reproducible rules and actual integration prove different properties | Unknown | Fixture/model cohort scoped |

## Critical Paths (P0)

1. Story FR-1/2: one attributable disposition and a settled delivery outcome; invariant: Delivery retries cannot repeat an accepted business disposition; a model suggestion cannot grant write authority.
2. Story FR-3: unauthorized, stale, duplicate and uncertain work never loses its
   actual authority or outcome boundary.
3. Story FR-4: exact supported client/cohort preserves business meaning and safe
   diagnostics, including current identity on continuation.

## Acceptance Criteria Layer Allocation

| AC class / source | Story Test Plan | Primary Layer | Why this layer |
| --- | --- | --- | --- |
| US-108 main business and invariant classes | App story test plan at build handoff | Public client/host/native provider journey | Only full path proves business result |
| US-108 permission/recovery classes | Same app story test plan | Native integration | Current authority and durable effects cross boundaries |
| US-108 surface/candidate classes | Same app story test plan | Real browser plus separate CLI parity observation | TypeScript and server behavior require distinct observations |

The build handoff must author the per-criterion story test plan and native model/
technical design from installed HELIX templates before executable app code.
No preselected test function or framework is fabricated before that contract exists.

## Secondary Paths (P1-P2)

Optional UI polish cannot weaken required denial, uncertainty or accessibility
behavior. There is no optional escape from an active P0 criterion.

## Test Data Strategy

Use `../../fixtures.json` and the story's independent Given/When/Then examples.
Create isolated native namespaces with explicit PostgreSQL 18/Truss bindings and
scoped local identity. No production snapshot, credentials or inferred grants.
Every generated/native input retains its app/model/refinement identity.

## Known Gaps

Complete app execution requires qualified host/client, native model artifacts,
selected integrations and a trusted evidence runner. These are qualification
blockers, not accepted runtime risk or passing skips. SDK component storage
checks qualify only their own boundary. TypeScript UI is authored, not generated
from a declarative UI model. UI harness selection belongs to the app build design.

## Build Commands

From the SDK repository root:

```sh
python scripts/check_micro_apps.py
python scripts/check_micro_apps.py --require-execution
```

The first command verifies inventory only; the second must refuse absent complete
app execution evidence. SDK platform dependencies are explicit file references:
`../../../../02-design/contracts/CONTRACT-003-composition.md`,
`../../../../02-design/contracts/CONTRACT-004-host-profiles.md`,
`../../../../02-design/contracts/CONTRACT-005-ux-builder-binding.md`, and
`../../../../02-design/contracts/CONTRACT-011-micro-app-conformance.md`.

**Blocking gate**: Every active story criterion and shared obligation must have
trusted passing evidence for exact inputs before this app is called qualified.
No test-function ceiling increase; parameterize cases in shared machinery.

## Diagnostic Test Strategy

Exercise actual safe host audit and required telemetry across client, host and
providers, including a real receiver, refusal, retries, capture loss and shutdown.
A mocked exporter or parsed JSON is not receiver qualification. Erik supplies
workload and diagnostic overhead budgets before production qualification.
