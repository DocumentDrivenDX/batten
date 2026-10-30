---
ddx:
  id: CONTRACT-007
  type: contract
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-011
      kind: informed_by
    - id: CONTRACT-001
      kind: informed_by
    - id: CONTRACT-003
      kind: informed_by
  schemas:
    - id: batten.messaging.values
      version: "0.1.0"
      title: Batten messaging boundary values
      path: docs/helix/02-design/schemas/messaging.schema.json
      schemaFormat: json-schema
---

# CONTRACT-007: Messaging

**Contract ID**: CONTRACT-007
**Type**: asynchronous library boundary
**Version**: 0.1.0; capability `batten.messaging.channels/1`
**Related**: PRD FR-19/20/22/45; CONTRACT-001/003/004; ADR-011

## Purpose

Expose durable publication and subscription consumption without exposing database
tables, broker destinations, credentials or backend-specific acknowledgements.
PostgreSQL 18 is the first implementation. Future providers must satisfy the
selected capability profile or refuse admission.

## Scope and Boundaries

Applications name channels, payload profiles and subscriptions. Operators bind
them to providers and finite budgets. Batten owns authorization, admission,
delivery lifecycle and safe errors. UMF owns business schema and action meaning;
qualified codecs own native instance encoding and validation.

These are Python application-hook and embedded-host clients. Browser clients use
admitted declared operations through Batten's existing host boundary; this contract
does not expose a database/broker connection or a new browser queue protocol.

The interface covers durable work distribution and fan-out to declared durable
subscriptions. Chat history, arbitrary SQL, ephemeral broadcast, broker management,
wildcard subscriptions, replay/seek, distributed transactions, saga orchestration
and automatic action execution are outside version 1.

Owner direction selects PostgreSQL first and preserves future Kafka, Amazon Simple
Queue Service (SQS) and NATS options. ADR-011 records design choices; provider and
codec qualification are evidence obligations, not inferred owner decisions.

## Normative Surface

`messaging.schema.json` owns serialized boundary values and configuration shapes.
The protocols below own Python signatures and process-local capabilities. Python
values are immutable; `body_base64` maps to `bytes` named `body`. Wire tokens are
not Python object references. No JSON wire transport is selected by this contract.

### Declarations and binding

Place `requirement` at CONTRACT-003 `CapabilityRequirement.settings.messaging`,
with parent interface `{id: batten.messaging.channels, version: '1'}`. Parent
requirement ID and payload `resource` MUST match. Generic core preserves settings;
the messaging module validates them without importing application code or doing I/O.

A channel has mode `queue` or `topic`. A queue has exactly one durable subscription,
named `work`; its consumers compete. A topic has one or more explicitly declared
subscriptions; each receives its own logical delivery. Consumers sharing a
subscription compete; different subscriptions progress independently. There is no
payload filter or implicit consumer registration. All subscriptions accept the
channel's declared payload profiles. Fan-out requires feature `fanout`.

Subscriptions exist before publication. Newly provisioned subscriptions receive
future publications only. Subscription IDs and channel IDs survive host restart;
changing payload acceptance or topology requires explicit reviewed reconciliation.
Provisioning is host maintenance, never a side effect of publish/receive/start.
Removing a subscription with outstanding work refuses until an explicit drain or
authorized destructive retirement. No publish silently succeeds with zero targets.

The host supplies one `postgresBinding` per resource at `binding.settings.messaging`
through CONTRACT-004. It selects a trusted connection reference, managed namespace,
resolved limits and immutable payload profile catalog. Requirement and binding
resource IDs MUST agree. Later providers introduce their own versioned binding
schemas; application requirements MUST NOT contain backend settings.

Every profile pins an original UMF artifact ID/digest, native selector, encoding
and exact codec ID/version. `selector` is interpreted only by that qualified codec
against the pinned artifact; it is never executable code. Dependencies needed to
resolve the type MUST be in the admitted artifact closure. A profile change needs
a new profile ID; the same ID MUST NOT acquire different schema/encoding meaning.
Profile aliases are scoped to the admitted application revision and provider
catalog digest, not resolved from a mutable external registry at delivery time.
The provider MUST retain the exact profile/schema/codec closure while any retained
delivery can require it. An application upgrade cannot reinterpret pending bytes;
missing historical support refuses readiness for affected consumers. Retiring
that closure requires draining or explicitly authorized terminal retirement.

### Scoped clients

`batten.messaging.for_resource(context, resource)` returns a `Channel` without I/O.
`batten.messaging.payloads(context)` returns `Payloads` without I/O. Context is
host-authenticated invocation context; clients cannot supply actor IDs or roles.
These handles are valid only during their invocation. A host-owned consumer loop
opens a fresh trusted background invocation, with declared application/owner
authority, for each bounded receive/handler cycle. It cannot retain a user's
request handle or impersonate the original producer.

```python
class Payloads(Protocol):
    async def encode(self, profile: str, value: object) -> EncodedPayload: ...
    async def decode(self, payload: EncodedPayload) -> object: ...

class PayloadCodec(Protocol):
    async def encode(self, profile: PayloadProfile, value: object) -> bytes: ...
    async def decode(self, profile: PayloadProfile, body: bytes) -> object: ...
    async def validate(self, profile: PayloadProfile, body: bytes) -> None: ...

class Channel(Protocol):
    async def publish(self, message: OutgoingMessage) -> PublicationReceipt: ...
    def subscription(self, name: str) -> Subscription: ...
    async def lookup(self, message_id: str) -> PublicationReceipt | None: ...
    async def stage(self, message: OutgoingMessage, *,
                    transaction: TransactionContext) -> StagedPublication: ...

class Subscription(Protocol):
    async def receive(self, *, limit: int, wait_ms: int,
                      visibility_ms: int) -> tuple[Delivery, ...]: ...
    async def ack(self, receipt: str) -> SettlementReceipt: ...
    async def retry(self, receipt: str, *, delay_ms: int,
                    reason: str) -> SettlementReceipt: ...
    async def reject(self, receipt: str, *, reason: str) -> SettlementReceipt: ...
    async def extend(self, receipt: str, *, visibility_ms: int) -> LeaseReceipt: ...
```

`subscription` is a pure resolver and confers no new permissions. There is no
automatic acknowledgement on context exit or successful decode. Cancellation
leaves unsettled deliveries eligible for later redelivery. No method exposes a
native client, SQL transaction, offset, queue URL or database credential.

`PayloadCodec` is a host-injected provider protocol, never an application escape
hatch. `Payloads` resolves profiles and checks current scope before calling it.
`batten.postgres.messaging.create_provider` is a pure host factory receiving resolved
binding values, public `ConnectionSource`, codecs keyed by exact ID/version, trusted
authorization and explicit owned/borrowed service lifetimes. `prepare` does native
readiness I/O; construction does not. Native errors translate at that boundary.

### Payloads and UMF

An `EncodedPayload` contains `profile` and exact bytes. `OutgoingMessage` supplies
`message_id`, payload, bounded string headers and nullable correlation/causation
IDs. IDs are opaque application identities, not ordering positions or grants.
`Delivery` adds the logical subscription, opaque delivery identity and receipt,
nullable attempt count, observed publication time and visibility deadline.
Publisher identity is attached by the trusted host and retained privately for
audit; client headers MUST NOT confer identity or operation authority.

`encode`/`decode` MUST use the admitted codec and preserve its declared native
semantics. Their Python object shape is the codec's public typed access shape;
no universal dict conversion is promised. Initial qualification targets a JSON
instance profile backed by UMF JSON Schema. Binary Protobuf and Avro profiles
require separately qualified instance codecs, framing and full schema closure.
Protobuf descriptor import and Avro schema export alone do not qualify codecs.

`json-utf8` is one UTF-8 JSON instance, without a byte-order mark. Its codec MUST
reject duplicate object keys and preserve the selected schema's numeric meaning.
`protobuf-binary` is one native instance of the selected message type, without a
length prefix. `avro-binary` is one native datum under the pinned writer schema,
without an object-container or schema-registry header. A codec must consume the
whole payload and qualify native unknown-field behavior. These encoding names
specify framing, not automatic conversion between schema families.

Publish MUST validate the payload against its exact writer profile before effects;
raw bytes do not bypass validation. Receive preserves the original bytes and
profile. Decode refuses an unsupported profile; it MUST NOT transcode, apply a
newest-schema lookup, drop unknown fields or substitute JSON. Exact-profile
matching is version 1's compatibility rule. Reader/writer evolution needs an
explicit later qualified capability; a broker's schema registry is not implied.

No new `umf.messaging` vocabulary is required to describe business payloads.
Existing UMF core and JSON Schema/Protobuf/Avro extensions retain their schemas.
Channel topology and delivery policy are local Batten capability settings. A
future general messaging vocabulary may replace that declaration layer through
an explicit migration; it MUST NOT redefine existing payloads or action meaning.

### Baseline guarantees and capability requirements

The baseline is durable, bounded, at-least-once delivery with explicit settlement
and no ordering guarantee. Duplicates may occur even during visibility intervals;
clients MUST make effects idempotent. Eventual delivery assumes continuing service,
consumer authority and capacity, within configured retention and retry budgets.
Expiration and exhausted work remain observable terminal outcomes, not success.

| Feature | Requirement and behavior |
| --- | --- |
| `fanout` | Publication durably covers every declared subscription in the accepted topology revision. No partial fan-out may be reported as accepted. |
| `idempotent_publish` | `message_id` deduplicates within channel/application scope for at least `dedup_ms` after acceptance. Identical retry returns the original receipt; changed content returns `id_conflict`. Includes `lookup`. |
| `delayed_retry` | `retry(delay_ms > 0)` makes work ineligible until the requested delay elapses. Zero-delay retry belongs to the baseline. |
| `extend_visibility` | `extend` adjusts a current delivery deadline, bounded by the original claim's maximum lifetime. It does not prove exclusive processing. |
| `transactional_publish` | `stage` joins an exact admitted same-store transaction. Standalone publish never implicitly joins an ambient transaction. |

Unsupported features refuse during assessment when required, and before effects
when called without a grant. Postgres implements the baseline and the first four
features. `transactional_publish` additionally requires a qualified transaction
issuer/executor binding. FIFO, partition ordering, replay and exactly-once effects
are absent from version 1; requesting them refuses rather than silently degrades.

Publication acceptance means durable provider acceptance for the bound topology,
not handler completion. Receipts expose no subscriber count or hidden identity.
`accepted_at` is the original provider acceptance time. `dedup_until` is the
guaranteed end of the dedup window, or null without that feature. Timestamps are
UTC RFC 3339 values. Identical retries preserve these timestamps and set
`deduplicated=true`; first acceptance sets it false. `lookup` returns the retained
original acceptance with `deduplicated=false` because it performs no publication.
For `idempotent_publish`, equality covers profile, original bytes, headers and
correlation/causation IDs; map insertion order is irrelevant. Applications retain
the same ID and content for recovery. After the dedup window, a retry can be a new
publication. `lookup` returns null when no retained acceptance exists; that does
not prove a publication never occurred. No automatic retry follows an uncertain
publish without qualified deduplication and an unexpired recovery window.

`receive` returns at most `limit` deliveries; an empty response means no work was
observed before its bounded wait ended, not that the subscription is drained.
Lease time begins at native claim, not at response delivery. A delayed response
can carry an expired receipt; callers MUST handle `lease_lost`. `attempt` is null
when a provider cannot report a reliable count. Client-supplied count is never
used for retry policy. Retry/reject reasons are registered safe reason codes,
not exception text or payload excerpts.

`retry` schedules eligibility at provider time plus `delay_ms`, bounded by
`max_retry_delay_ms` and message expiry. `extend` sets a deadline at provider time
plus `visibility_ms`, bounded by `max_visibility_ms` and the original claim's
`max_claim_lifetime_ms`. It never shortens a deadline. A request outside those
bounds refuses before mutation. No background automatic renewal is implied.

`ack` completes one subscription delivery. `retry` releases it for another attempt;
`reject` makes it terminal for operator inspection. They return an observed durable
settlement, never a claim about external effects. A settlement receipt ID is not
an authorization token. Repeating the same settlement with its receipt returns
the original result while retained; a conflicting settlement returns
`settlement_conflict`. Expired or superseded receipts return `lease_lost` unless
that exact settlement was already recorded. Every call still rechecks authority.
`extend` on a settled receipt returns `lease_lost`; it never resurrects work.
Settlement identity includes the method, reason and delay where applicable;
changing those parameters on a retained receipt is a conflict. `reason` MUST be
one of the host binding's `reason_codes`, checked before mutation.

### Transaction participation

`TransactionContext` is a process-local opaque capability issued by the host's
qualified same-store executor. Its private binding covers actor/application,
database, connection, active transaction, scope and lifetime. It has no public
constructor, driver access, serialization or permission-widening behavior.
Async tasks MUST NOT share it concurrently. Application input cannot mint one.

`stage` MUST validate all ordinary publish authority/limits, verify the matching
transaction issuer, and stage message plus deliveries on that exact transaction.
A failure poisons the enclosing unit of work; the executor MUST roll it back.
`StagedPublication` contains only `message_id`; it is not an acceptance receipt.
Commit makes publication visible atomically with other participating same-store
effects; rollback makes neither visible. Unknown commit retains uncertainty.
Recovery uses the same ID through `lookup`, requiring `idempotent_publish` too.
Acknowledgement is not transaction-enlisted in version 1.

No current Batten contract establishes a UMF table-action transaction issuer.
Consequently that composition MUST refuse `transactional_publish` until its exact
public executor bridge and native evidence exist. Two connections to the same
database, a Lakebase binding or an UMF `single-store` declaration are insufficient.
Kafka transactions and an outbox relay to a broker are different guarantees;
neither may advertise atomic database-plus-broker delivery under this feature.

### PostgreSQL 18 binding profile

The binding MUST use logged durable storage and direct transaction-capable client
connections. Namespace identifiers are host-managed, validated and quoted; no
application string becomes SQL syntax. The host explicitly provisions schema,
roles and indexes through separately authorized maintenance. `prepare` checks
version/schema compatibility and permissions without migrating or adopting tables.

Publication MUST commit the immutable message, all subscription deliveries and
deduplication record together. A scoped unique constraint serializes duplicate
publication IDs; compare content on conflict, never enqueue extra deliveries.
For staged duplicates, resolve within the same transaction. Topology changes and
publication MUST serialize against one topology revision.

Receive MUST claim eligible rows in a short transaction using row locks with
`SKIP LOCKED`, install a fresh unpredictable receipt generation and deadline,
and commit before returning payloads. Handle work outside that transaction;
never hold row locks while executing an application handler. Settlement/extension
MUST condition on scope, current generation and an unexpired native deadline.
Expired claims become reclaimable; a stale generation cannot settle a new claim.
Recorded exact settlement results survive response loss for `recovery_ms`.
Database time controls eligibility; polling uses a monotonic wait deadline.
Attempts start at one and increment on each committed claim, including reclaim
after expiration. When a claim would exceed `max_attempts`, the delivery becomes
terminal instead. A message reaching its retention deadline makes every remaining
delivery terminal. Terminal reasons distinguish rejection, exhaustion and expiry.

Message retention MUST NOT delete outstanding delivery payloads early. Limits
include payload/headers, batch/wait/visibility, per-owner in-flight work, pending
bytes, attempts, message retention, deduplication and recovery retention. Claim
and expiration transitions count attempts exactly for Postgres. Exhausted or
expired work moves to retained terminal records, available to authorized host
operators. Operator redrive uses a new publication ID and original causation ID;
version 1 exposes no client purge, redrive or history-list API.

`LISTEN/NOTIFY` MAY wake polling, carrying no payload, tenant or message identity.
Periodic bounded polling and reconnect preserve correctness when notifications
are missed. Lakebase uses this same SQL adapter with injected authority; direct
session, restart and scale-to-zero behavior require independent qualification.

### Authority, limits and lifecycle

Admission intersects declared operations/subscriptions, authenticated actor policy
and native provider authority. Every publish, lookup, receive and settlement MUST
recheck current authority before existence disclosure or effects. Receipt scope
binds application, channel and subscription; possessing it never grants access.
Revocation prevents further authorized operations; already received bytes/effects
cannot be recalled. Revoked work may expire and be retried under a permitted actor.

Resolved limits MUST be finite positive integers, with zero allowed only for
`wait_ms`/`delay_ms` requests. Durations are milliseconds. Visibility/recovery and
dedup windows MUST fit within message/terminal retention. Admission MUST refuse
unhonorable bounds. Oversized publish is rejected before persistence. No unbounded
prefetch, receive loop, queue scan or SDK retry is allowed. Shared host scheduling
must preserve FR-19 fairness; `SKIP LOCKED` alone does not establish fairness.
Publish reserves `max_pending_bytes` capacity atomically with acceptance; claim
enforces the in-flight budget. Capacity accounting includes payload copies needed
for fan-out. `max_operation_ms` bounds codec/native calls and total receive work;
`wait_ms` cannot exceed it. Poll intervals/scans, header bytes and codec recursion
are bounded by their corresponding schema limits. Header bytes mean the sum of
UTF-8 key/value bytes; payload bytes are decoded body length, not base64 length.
All strings must contain Unicode scalar values; base64 must decode strictly.
`max_visibility_ms <= max_claim_lifetime_ms <= message_retention_ms`,
`dedup_ms <= message_retention_ms`, `recovery_ms <= terminal_retention_ms` and
`max_wait_ms <= max_operation_ms` MUST hold. Deduplication records remain available
for their entire promised window even if every delivery finishes earlier.

Invocation close invalidates handles and bounds active I/O; it does not ack work,
purge data or close borrowed host pools. Provider shutdown drains under the host's
deadline and preserves uncertain native operations. No newly started work is
admitted during drain. All I/O and codec work must avoid blocking the event loop.

## Precedence and Compatibility

PRD governs scope; schema owns value structure; this contract owns semantics and
signatures. CONTRACT-001 governs lifecycle, CONTRACT-003/004 composition, and
ADR-005 cohort compatibility. Exact interface major, settings schema version,
payload profile and provider evidence are assessed independently. Unknown settings
are retained; relevant unrecognized meaning refuses admission. No provider swap
silently changes required features, topology, encoding, authority or finite bounds.

## Error Semantics

Methods raise `MessagingError` with schema `error` values. `effect` is `none` only
when no mutation occurred, otherwise `unknown`. Completed operations return their
receipt. Native cancellation propagates while invocation tracking retains any
possible effect and incident ID. Errors/logs MUST omit payloads, receipt strings,
headers, broker addresses, credentials and native exception bodies.

| Condition | Code | Recovery |
| --- | --- | --- |
| Invalid message/profile/limit | `invalid_request` | Correct input; no effect. |
| Unsupported codec/schema meaning | `payload_unsupported` | Qualify exact profile; preserve bytes. |
| Payload invalid for selected profile | `payload_invalid` | Correct payload; no publication. |
| Missing authority/resource visibility | `denied` | No existence disclosure. |
| Missing required feature/binding | `unsupported` | Repair admission; no fallback. |
| Reused retained ID with changed content | `id_conflict` | Reconcile original publication. |
| Stale claim or consumer epoch | `lease_lost` | Stop settlement; effects may already exist. |
| Different settlement already recorded | `settlement_conflict` | Reconcile original outcome. |
| Full queue/in-flight/bounds | `limit_exceeded` | Bounded backpressure; no accepted partial publish. |
| Invalid/foreign/closed transaction | `transaction_invalid` | Refuse before staging; poison valid enclosing scope. |
| Topology/profile revision changed | `binding_changed` | Reassess; no silent reinterpretation. |
| Provider unavailable/deadline/I/O | `unavailable` / `timeout` / `io_failure` | Preserve uncertainty; reconcile by ID/receipt within retention. |

## Examples

Illustrative application hooks; `context` and a background invocation are supplied
by the host. All data is fabricated. Names denote the proposal, not installed APIs.

```python
from batten.messaging import OutgoingMessage, for_resource, payloads

channel = for_resource(context, "review-requests")
codec = payloads(context)
payload = await codec.encode("review-request-json-v1", review_value)
accepted = await channel.publish(OutgoingMessage(
    message_id="review-demo-001", payload=payload, headers={},
    correlation_id=None, causation_id=None))

# In a separately authorized background invocation:
channel = for_resource(worker_context, "review-requests")
subscription = channel.subscription("work")
deliveries = await subscription.receive(limit=1, wait_ms=1000, visibility_ms=30000)
for delivery in deliveries:
    value = await payloads(worker_context).decode(delivery.message.payload)
    await process_idempotently(value, key=delivery.message.message_id)
    await subscription.ack(delivery.receipt)
```

For a topic, `notification` and `indexing` are separate declared subscriptions.
Completing one does not complete the other. After a lost publish response, retry
the identical message ID/content only within qualified dedup retention. A handler
failure must explicitly retry/reject or leave the lease to expire; catching an
exception does not imply its external effects rolled back.

## Schema Basis

`messaging-schema-basis.json` pins inspected UMF core 0.10.0, actions 0.1.0,
JSON Schema 0.1.0, Protobuf 0.1.0, Avro 0.1.0 and medical pack 1.2.0 sources.
Reuse original UMF schema artifacts, native encoding meaning, action references
and CONTRACT-003 artifact identity. The local schema describes transport boundary
values, payload profile references and delivery policy; it defines no business
payload fields and no competing action or saga language.

No inspected definition specifies durable channels, subscription settlement or
opaque leases. That is the local gap. Schema validation cannot prove codecs,
permissions, delivery durability, atomicity or provider equivalence. Those require
the MSG acceptance allocation in TP-001 and native provider evidence.
