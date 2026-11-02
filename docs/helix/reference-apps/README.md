# Enterprise micro-app library

These are fabricated application specifications, fixtures and qualification targets.
They are not twelve runnable apps. Batten currently supplies local object storage;
complete host, ORM, client and provider integration is tracked separately.

Each app has its own `.helix.yml` binding `specs/`, app instructions, PRD, user
story, test plan and fabricated data. Open an app directory to target it with the
installed HELIX skill and follow the shared [Batten app workflow](../04-build/batten-app-workflow.md).
This specializes HELIX without vendoring its catalog or installing another skill.

All initial interactive apps are TypeScript apps using public Batten operations;
ux-builder remains available for qualified design/tooling integration. Declarative
UI generation is a separate longer-term capability. An app may omit UI only after
its own scope and required evidence are revised explicitly.

| App | User outcome | Integration tags |
| --- | --- | --- |
| [Approval desk](approval-desk/specs/01-frame/prd.md) | Submit a request, inspect its revision, approve or reject, then observe the final decision. | tables,actions |
| [Service intake and routing](service-intake/specs/01-frame/prd.md) | Submit an intake form, classify it, route it to a permitted queue and acknowledge assignment. | tables,actions,messaging |
| [Case and task tracker](case-tracker/specs/01-frame/prd.md) | Open a case, relate a task, assign work, satisfy prerequisites and close the case. | tables,graphs,actions |
| [Evidence and attachment library](evidence-library/specs/01-frame/prd.md) | Upload fabricated evidence, verify bytes, link its immutable reference to a record and retrieve it. | tables,storage,actions |
| [Assisted document review](document-review/specs/01-frame/prd.md) | Upload a fabricated document, request extraction, inspect provenance, correct suggestions and accept a reviewed result. | tables,storage,agents,models,actions |
| [Entity and relationship directory](entity-directory/specs/01-frame/prd.md) | Register an entity, link a related entity, traverse authorized relationships and update approved attributes. | graphs,actions |
| [Grounded knowledge assistant](knowledge-assistant/specs/01-frame/prd.md) | Ask a question, retrieve authorized sources, inspect a grounded answer and open permitted citations. | tables,storage,agents,models,search |
| [AI-assisted inbox triage](model-triage/specs/01-frame/prd.md) | Receive an inbox item, classify it within a budget, review the suggestion and apply an authorized disposition. | tables,messaging,agents,models,actions |
| [Data reconciliation workbench](data-reconciliation/specs/01-frame/prd.md) | Compare bounded source snapshots, inspect discrepancies, approve a resolution and inspect the applied result. | tables,actions,jobs |
| [Scheduled operational digest](scheduled-digest/specs/01-frame/prd.md) | Schedule a bounded report, execute a due occurrence, publish its artifact and inspect delivery status. | tables,jobs,storage,messaging |
| [Access review and attestation](access-attestation/specs/01-frame/prd.md) | Capture a scoped access snapshot, review assignments, attest or request removal and inspect the outcome. | tables,graphs,actions |
| [Cross-application service handoff](service-handoff/specs/01-frame/prd.md) | Discover a permitted service, bind its exact interface, submit a request and observe receiving progress. | graphs,services,messaging,actions |

Shared obligations cover authority, attribution, commands, lifecycle, limits,
surface parity and observability. Each story adds a distinct business invariant.
Do not build new ORMs or engines to satisfy an example: integrate UMF/PostgreSQL,
UMF/Truss and the other existing platform projects through qualified public APIs.

Run `python scripts/check_micro_apps.py` from the SDK root for inventory validation.
`--require-execution` deliberately refuses until a trusted complete-app runner and
its evidence contract are qualified. Component-only receipts cannot make it green.
See [scope assessment](../01-frame/feasibility-study.md),
[corpus contract](../02-design/contracts/CONTRACT-011-micro-app-conformance.md), and
[integration queue](../04-build/integration-gaps.md).
