---
ddx:
  id: TD-006
  type: technical-design
  activity: design
  authoring:
    home: repo
  links:
    - id: CONTRACT-006
      kind: derived_from
    - id: CONTRACT-100
      kind: derived_from
    - id: ADR-010
      kind: informed_by
---

# TD-006: Local managed object storage

**User Story**: [[US-006]] | **Feature**: [[FEAT-006]] | **Solution Design**: [[SD-001]]

## Scope

Implement the local backend and portable storage interface under CONTRACT-006/008.
The owner authorizes specification integration, quality adoption and this backend.
Migration, messaging, Databricks implementation and the complete host runtime are
separate work. Existing pending specifications remain part of the reviewed main packet.

## Technical Approach

Use a separate namespace wheel for batten.storage; core and other adapters never
import the local implementation. Immutable blobs plus atomically replaced pointer
records provide old-or-new publication. Descriptor-relative no-follow access and
encoded segments preserve containment and exact key identity on POSIX systems.
A filesystem lock serializes commits across cooperating processes. The qualified
concurrency domain is adapter-managed; external writers are forbidden.

Async transfers spool bounded chunks to private files without blocking the event
loop. Conditions are checked under the commit lock. Reads open immutable generations.
Multipart sessions preserve ordered receipt identity, expiry and completion outcomes.
A dedicated managed layout separates objects, staging, upload state and locks.
No database, cloud client, model library or environment lookup is required.

## Component Changes

| Component | Files | Ownership and dependencies |
| --- | --- | --- |
| Portable storage | packages/batten-storage/src/batten/storage | Values, protocols and resource resolver; stdlib only; no eager local imports. |
| Local provider | same package, local/ | Private descriptor/record/transfer/listing/upload units; public construction through CONTRACT-100. |
| Quality tools | scripts/, pyproject.toml, justfile | Real import/shape/export/test census and strict analysis; no product dependency on tools. |
| Behavioral proof | tests/storage/, tests/quality/ | Public-boundary whole outcomes, native competing providers/processes and installed-wheel proof. |

## API/Interface Design

CONTRACT-006 owns operations, conditional/range/integrity/session behavior and
schema values. CONTRACT-100 owns construction and host injection. This slice
implements those surfaces without filling unrelated runtime APIs with placeholders.

## Security

Host authority is injected and checked before access and every continuation.
Root and component access refuses symlinks/special files; metadata exceptions are
translated to safe storage outcomes. No original key or object bytes enter safe
outcome observations. A trusted local process owner can bypass files directly;
this is permission containment, not a hostile-code sandbox.

## Performance

Shallow key listing enumerates native entries without per-object stat enrichment.
Opaque cursors retain progress under finite bounds. Sources, reads, parts and
parallelism share the caller's explicit limits. No throughput target is invented.

## Testing

Realize US-006-AC1–AC6 through the STO-01–15 allocation. Allocate STO-01–15 to public conformance, authorization, filesystem containment,
competing commits, range/integrity, upload recovery and listing behaviors. Verify
installed imports without Databricks or any platform dependencies. Establish the
first measured suite only after review; later test counts can only decrease.
Negative gate fixtures exercise allowed/forbidden imports, cycles, private access,
missing baseline and raised ceilings through the actual checker.

## Diagnostic Wiring

CONTRACT-100 authority observation delegates trusted correlation/capture to the
host. Failure is visible, and post-publication failure retains uncertainty. Local
sink tests qualify this port only, not an OpenTelemetry receiver integration.

## Schema Basis

Reuse CONTRACT-006's schema and pinned UMF inspection receipt. Filesystem pointer
records are private storage metadata, not a portable application schema. Application
metadata remains in UMF. Shared value shapes are not redefined here.

## Implementation Sequence

Establish the gate and negative controls before dependent source. Then implement
portable values, native containment and publication, followed by streams/listing,
conditional ranges and upload lifecycle. Run the common quality recipe, native
behavioral suite and installed wheel observation before source-work closeout.

## Risks

| Risk | Mitigation |
| --- | --- |
| Cancellation outlives a worker operation | Await/reconcile worker completion and retain uncertainty before unwinding. |
| Filesystem semantics differ | Qualify explicit POSIX primitives and managed authority; refuse unsupported profiles. |
| Native state and outcome capture diverge | Preserve original receipt/session identity; never infer completion from matching bytes. |
