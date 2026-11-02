---
ddx:
  id: CONTRACT-011
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: informed_by
    - id: ADR-014
      kind: informed_by
    - id: ADR-015
      kind: informed_by
---

# CONTRACT-011: Reference-app conformance and workflow binding

**Contract ID**: CONTRACT-011
**Type**: authoring and qualification boundary
**Version**: 0.1.0

## Purpose

Keep reference apps independently governed while sharing platform conformance.
Make specification integrity, component evidence and complete application
execution distinguishable and prevent missing runtime support from passing.

## Scope and Boundaries

Batten owns the corpus, workflow specialization and shared test allocation.
Each app owns its requirements and business expectations. UMF owns models,
actions, typed access and saga semantics; Truss owns graph execution; ux-builder
owns its design tooling. App UI delivery follows ADR-015. No runtime DSL,
frontend framework, second ORM or generator is introduced by this contract.

## Normative Surface

`docs/helix/reference-apps/catalog.json` is the corpus inventory. Its JSON objects
have only the following fields; unknown fields MUST fail the inventory checker.

| Element | Type / Shape | Required | Rules |
| --- | --- | --- | --- |
| catalog.version | integer | yes | Exactly 1; inventory format, not SDK series |
| catalog.workflow | relative file path | yes | Shared Batten implementation-plan workflow |
| catalog.apps | nonempty array | yes | Stable unique app IDs and roots; removal requires owner review |
| app.id | string | yes | `MA-` followed by three digits; identity survives renaming |
| app.slug | string | yes | Unique lowercase kebab-case directory name |
| app.ui | string | yes | `typescript` or `headless`; not a renderer qualification claim |
| app.modules | nonempty array of unique strings | yes | Integration requirement tags, not import names, install instructions or grants |
| app.root | relative directory path | yes | Exactly the app directory under `docs/helix/reference-apps/` |
| app.story | string | yes | Stable local story ID; corpus lookup is qualified by app ID |
| app.obligations | array of unique strings | yes | Contains every shared obligation below |

Each app directory MUST have its own `.helix.yml`, `AGENTS.md`, `fixtures.json`
and `specs/` tree. The marker MUST bind exactly `id: helix`, `root: specs/`.
Generated markers use JSON, a YAML subset, so the stdlib inventory checker needs
no YAML dependency. The `x-batten-app` marker metadata MUST identify the matching app and workflow;
it is a repository convention interpreted through the app instructions, not a
new HELIX resolver API. The installed HELIX catalog supplies templates/prompts.
The app PRD, feature, story and test plan MUST exist with explicit acceptance criteria.

Fixtures MUST be fabricated JSON data, not executable models or role grants.
Their `application` matches the app ID, `record` supplies a fabricated local ID,
owner and starting state, and `actors` distinguishes permitted and foreign users.
Fixtures add no real customer/user identities or service credentials.

| Shared obligation | Required observable proof |
| --- | --- |
| AUTH | Server binds current actor; foreign/anonymous/revoked access discloses no private result |
| IDENTITY | App/model/resource/profile revisions and effective identity remain attributable |
| COMMANDS | Query has no business mutation; stale, duplicate and uncertain commands preserve declared outcomes |
| LIFECYCLE | Cancellation, restart and dependency failure retain actual effects and resource ownership |
| LIMITS | Bounded pages, payloads, work and model budgets; no implicit privilege escalation |
| PARITY | Same business operation across supported surfaces and candidate cohorts; unsupported surfaces refuse |
| OBSERVABILITY | Durable safe audit and required telemetry; capture failure is visible |

App-specific story criteria supplement these obligations. Shared policy scenarios
may be parameterized; domain expectations MUST come from independent app intent,
not from capturing whatever the runtime returns. Browser apps require actual
TypeScript client journeys, including pending/invalid/denied/success/uncertain
states, keyboard/focus/navigation and authorized downloads where applicable.

### Commands and qualification levels

`python scripts/check_micro_apps.py` MUST verify inventory, roots, artifacts,
fixture identity and obligation completeness without importing apps or providers.
It prints `inventory only`; success establishes no application execution.
`--require-execution` MUST additionally fail whenever complete app qualification
is unavailable. It MUST NOT invent receipts, treat refusal of a required positive
case as a pass, or silently skip missing app/provider/UI implementations.

Complete qualification requires exact source/model/action/refinement/UI/cohort and
host-profile inputs, native table/graph policies, independent expected outcomes,
real CLI/client/host/provider results, replay seeds/traces and exploration bounds,
original uncertain invocation identity, required telemetry and negative controls.
Evidence must be verified by a trusted runner; application-authored success flags
or static fixtures cannot confer execution support. There is no accepted evidence
ingestion API selected by this version; strict mode refuses until that contract
and runner are qualified. Local storage evidence remains component-only evidence.

## Precedence and Compatibility

Native UMF and provider semantics remain authoritative. Platform contracts govern
bindings; app specs govern business outcomes. A conflict refuses qualification
rather than changing an app's oracle. Inventory format evolution requires a
contract change. A fixture change invalidates dependent execution evidence.
SDK/cohort compatibility remains governed by ADR-005, independently of format 1.

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
| --- | --- | --- | --- |
| Invalid inventory, escaped path or mismatched marker | Inventory failure, nonzero exit | After correction | No code or service effects |
| Missing required app execution | Qualification unavailable, nonzero exit | After runner/integration qualification | Never a skip or green support claim |
| Foreign/anonymous/revoked request | Safe denial | After legitimate policy change | No existence or hidden count disclosure |
| Unknown write outcome | Retain original uncertainty | Observe original attempt | No fresh blind command retry |

## Examples

Open `docs/helix/reference-apps/approval-desk/`, read its marker and `AGENTS.md`,
then ask HELIX to evolve the app's approval requirement. Its `specs/` artifacts
use installed catalog templates; the SDK's PRD is not edited as that app's PRD.
Run the inventory command from the Batten repository root. Requesting execution
qualification with no trusted complete-app runner produces a nonzero result.

## Schema Basis

The inspected UMF source receipt is `schemas/upstream-schema-basis.json`, UMF
core 0.10.0/actions 0.1.0 at its recorded source digest. Its native document,
action and artifact identities remain app-model authorities. Corpus inventory,
local paths and fabricated input data are test bookkeeping; they are deliberately
not UMF model declarations or a portable business-rule language. Native models
and UI artifacts require fresh exact upstream inspection in each app build.
