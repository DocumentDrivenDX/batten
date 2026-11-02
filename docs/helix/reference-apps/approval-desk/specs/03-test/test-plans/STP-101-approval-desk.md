---
ddx:
  id: STP-101
  authoring:
    home: repo
  links:
    - id: US-101
      kind: informed_by
    - id: TD-101
      kind: informed_by
---

# Story Test Plan: STP-101-approval-desk

## Story Reference

**User Story**: [[US-101-journey]]
**Technical Design**: [[TD-101-approval-desk]]
**Related Solution Design**: [[SD-101-approval-desk]], SDK architecture and CONTRACT-012.
**Project Test Plan**: [[test-plan]] (TP-101).

## Scope and Objective

Prove the first local application through installed wheels, real PostgreSQL 18,
original UMF/Weft and the actual TypeScript browser client. The blocking command
is `just approval-test`. This bounded proof does not qualify other hosts/cohorts,
the complete micro-app corpus, generated semantic suites or an OTLP receiver.

## Acceptance Criteria Test Mapping

The business rows use `test_approval_desk_native_browser_journey` in
`tests/apps/test_approval.py`, citing each ID in its docstring.

| AC ID | Acceptance Criterion | New or Existing Test(s) to Create or Run | Asserted Behavior (what the test verifies) | AC-ID Citation | Test Level | File or Command | Setup / Data | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-101-AC1 | Submit, inspect, independently decide | Native browser journey | Blake approves Alex's pending record, current owner/title and attributable decision survive restart | `@covers US-101-AC1` | E2E | `just approval-test` | Dedicated new local cluster; fabricated people | Includes empty view and reject path |
| US-101-AC2 | Inspected revision becomes stale | Same journey | Alex's edit persists; Blake's stale approval returns conflict; refresh permits the current revision; self decision has no effect | `@covers US-101-AC2` | E2E | Same command | Two independent browser sessions | Server/native conditions govern |
| US-101-AC3 | Foreign, anonymous or revoked access | Same journey | Anonymous and logged-out calls denied; Casey cannot see foreign record; browser-supplied identity and alternate origin/host refused | `@covers US-101-AC3` | E2E | Same command | Actual cookie sessions | No client role authority |
| US-101-AC4 | Mutation response is lost | Same journey | Browser intercept forwards the real mutation then aborts its response; original key observation confirms the actual receipt with no duplicate record | `@covers US-101-AC4` | E2E | Same command | Real native receipt | Capture loss remains explicit |
| US-101-AC5 | Another supported surface | Same journey | Installed CLI sees the same decided record under current identity after server restart; unsupported operations refuse | `@covers US-101-AC5` | Integration | Same command | Same dedicated cluster | One exact local cohort only |
| US-101-AC6 | Discover app and return to registry | `test_registry_lists_visual_apps_and_brand_returns_home` | Card includes description and loaded visual thumbnail; opens its app URL; brand returns to registry; cookies use the app path; unregistered/legacy API routes return 404 | `@covers US-101-AC6` | E2E | `just approval-test` | Same installed local cluster, without new business mutations | Listing grants no authority |

## Executable Proof

### Primary Commands

```sh
just approval-prepare
just approval-test
just check
```

### Planned Test Files

`tests/apps/test_approval.py` owns the business journey; its fixture owns only
process setup/cleanup. Shared storage range/integrity coverage consolidates real
read setup without removing assertions, keeping the function ceiling unchanged. Registry coverage also consolidates the
shared listing setup for projection, progress and cursor scope without dropping
any storage assertions.

### Coverage Focus

Authorization, native revision conditions, safe original-outcome recovery,
installed closure and no implicit deployment during startup.

## Data and Setup

Use fixture names Alex, Blake and Casey; all titles are fabricated. Compile the
original app UMF source with the pinned public SDK. Explicitly initialize a fresh
temporary PostgreSQL 18 cluster. Await the socket-bound JSON readiness signal;
use Playwright's observable-state assertions, with no test sleeps or blind retries.

## Edge Cases and Failure Modes

Empty state, invalid/foreign operations, stale decisions, self decisions, revoked
sessions, response loss and capture failure must preserve actual effect knowledge.
Transport denial occurs before business invocation. Startup verifies the original
installed schema head rather than creating roles, tables or migrating data.

## Build Handoff

Initialize the native model, assemble installed dependencies, then execute the
browser journey and installed CLI against the same data. Keep core independent
of providers and business/UI code independent of native clients. Completion
requires passing observed results, not only this allocation or inventory checks.

## Diagnostic Proof

Inspect actual instrumented database child spans and durable safe audit records;
no titles, SQL, connection strings or cookie material may reach these files.
A required-capture failure must return a safe unavailable/uncertain result.
This local capture profile is separate from the real receiver qualification
required for fleet deployment; JSONL inspection cannot establish that claim.
Erik owns the production workload and telemetry overhead budgets.

## UX Coverage

| Pattern | Disposition | AC IDs or Reason | Evidence |
| --- | --- | --- | --- |
| navigation | covered | US-101-AC1, US-101-AC6 | Browser selects and inspects requests |
| keyboard-overlays | not-applicable | No modal, menu, popover or keyboard overlay exists | Native form controls and visible focus remain required |
| async-actions | covered | US-101-AC2, US-101-AC4 | Busy guards, stale refresh and explicit original outcome check |
| forms | covered | US-101-AC1 | Labeled required summary, edit and decision controls |
| data-states | covered | US-101-AC1, US-101-AC3 | Empty, permitted, denied and final record states |
| destructive-actions | covered | US-101-AC2 | Decisions are conditional on an inspected pending revision |

## Completion observation

On 2026-11-02 the installed native/browser suite passed both named tests. The
common fast gate passed 18 cases; the function census remains 17. Final lint,
strict Python/TypeScript checking, import/export/shape gates and governed artifact
validation passed. [Local execution evidence](../local-execution.json) records
the exact original platform source, wheel hashes, observed behaviors and limits.
Registry desktop/mobile renders were inspected locally; the thumbnail loaded and
the mobile view had no horizontal overflow. Full corpus and receiver qualification
remain separate, and no inventory flag is treated as executable proof.
