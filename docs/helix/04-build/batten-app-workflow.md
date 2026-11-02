---
ddx:
  id: batten.app-workflow
  type: implementation-plan
  activity: build
  authoring:
    home: repo
  links:
    - id: CONTRACT-011
      kind: informed_by
    - id: ADR-014
      kind: informed_by
    - id: ADR-015
      kind: informed_by
---

# Batten application workflow

## Scope

Specialize the installed HELIX workflow for a single Batten app, from business
intent to independently qualified behavior. This is a repository-owned workflow,
not a forked methodology catalog or an installed `helix-batten` plugin.
Governing artifacts: CONTRACT-003/004/005/011, ADR-005/014/015, the selected app's
PRD/story/test plan, and the SDK's test plan and selected concerns.

## Shared Constraints

Read the nearest `.helix.yml` and scope all governed app artifacts to its `specs/`
root. Read the shared workflow path in the app instructions. Use the installed
HELIX catalog for every artifact template, prompt and metadata file. Local links
resolve inside that app scope; explicit platform file dependencies do not change
app identity. Fabricated data only. User policy and source/deployment authority
remain separate. Do not install dependencies or grant access during startup.

Use UMF + PostgreSQL 18 for tables and UMF + Truss for graph access. Prefer the
existing platform capabilities over a new ORM, query compiler, saga engine or
agent runtime. Initial UI delivery is a TypeScript app with a public host client;
ux-builder integration must preserve its original design assets and public APIs.

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate |
| --- | --- | --- | --- | --- |
| APP-01 | Discover/frame the chosen business outcome | App PRD and story | Scoped marker | Personas, rules, denied/uncertain outcomes and explicit owner assumptions |
| APP-02 | Select integration closure | CONTRACT-003/004, upstream source evidence | APP-01 | Exact UMF/provider packages and admitted subset; no private imports or guessed capability |
| APP-03 | Author native models/actions and host contracts | App design/contracts, original UMF | APP-02 | Upstream validation; exact table/graph access, transaction/policy limits and model references |
| APP-04 | Specify TypeScript UI or headless surface | ADR-015, CONTRACT-005, ux-builder sources | APP-03 | User journeys, client boundaries and accessibility allocation; no declarative renderer claim |
| APP-05 | Allocate conformance and independent oracle | App test plan and story test plans | APP-03/04 | Every acceptance criterion mapped; known-broken controls; bounded replay and cohort matrix |
| APP-06 | Implement integration and app slice | App technical design and build plan | APP-05 and owner build authorization | Boundary checks first; installed artifacts; real pgserver/Truss/host and browser paths |
| APP-07 | Qualify and package | CONTRACT-011 and app evidence | APP-06 | Complete positive/negative journeys, exact revisions, native policies and safe diagnostics |
| APP-08 | Evolve or move to another host | ADR-005, app baseline and candidate binding | APP-07 | Same app semantics requalified; migrations/applies separately authorized |

## Execution Contract

The owner authorizes the corpus, gap queue and this workflow. It does not authorize
all reference app runtimes, production applies, secret access or migrations.
Later app implementation requires a bounded app build instruction and a qualified
platform integration closure. Specs remain useful when that closure is unavailable;
qualification must refuse rather than invent a local replacement or scripted host.
Token usage, spending and duration budgets are unknown; Erik supplies any ceiling.
Available task tooling supplies no reliable billing meter. Verification is part
of each authorized implementation slice.

## Continuation Evidence

Use the app-specific plan, diff and test evidence to resume an app, with its own
artifact identities. Use the SDK integration queue for upstream dependencies.
Never propagate one app's green result to another app or new cohort. Run
`python scripts/check_micro_apps.py` from the SDK root for inventory integrity;
strict qualification remains a separate fail-closed check.

## Validation Plan

Validate governed artifacts against the installed catalog. Validate the aggregate
corpus through the common quality command. For runtime work, require independent
business expectations and real public client/host/provider observations. CLI
properties cover native declarative actions; authored TypeScript UI has explicit
browser journeys. Model fixtures do not prove a live model API integration.
Do not raise the current test-function ceiling; parameterize shared scenarios
while preserving each app's distinct invariants and their traceability.

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
| --- | --- | --- | --- |
| Wrong scope selected | Edits another product | Resolve nearest marker and state app identity | Revert only affected app changes |
| Upstream schema/access gap | False portability | Bind exact subset or explicit refusal | Preserve original native artifacts |
| UI ahead of host security | Client-derived authority | Qualify server authorization before app journey completion | Disable affected binding |
| Candidate changes durable semantics | Unsafe migration | Re-run independent app properties and native recovery | Use only a qualified recovery route |

## Exit Criteria

A scoped app specification has complete business expectations and test allocation.
A qualified app additionally has an admitted integration closure, installed/native
and actual browser/CLI evidence, complete required coverage and safe telemetry.
No inventory check or component-only receipt substitutes for the latter gates.
