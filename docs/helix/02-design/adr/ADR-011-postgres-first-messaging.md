---
ddx:
  id: ADR-011
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: ADR-001
      kind: informed_by
    - id: ADR-002
      kind: informed_by
---

# ADR-011: PostgreSQL first behind a scoped messaging interface

## Problem

Batten's durable work queue and declared events need publication, competing
consumers and independent subscriptions. Direct table access would expose storage
and authority. Kafka's log positions, SQS visibility and NATS acknowledgements
are different mechanisms; copying one into the client API would constrain others.

## Decision

Define CONTRACT-007 in optional stdlib-only `batten.messaging`. It owns portable
values/protocols, validation and scoped resolvers. `batten.postgres.messaging`
implements it with PostgreSQL 18 using the existing public psycopg dependency.
Core runtime sees generic capability lifecycle and durable-work coordination;
it does not import messaging or provider types. Host composition injects codecs,
authorization, native connection ownership and provider settings.

Expose channels and durable subscriptions with at-least-once unordered delivery.
Publish returns durable acceptance; explicit acknowledgement completes only one
subscription delivery. PostgreSQL messages and per-subscription deliveries commit
together. One subscription serves a work queue; independent subscriptions provide
fan-out. Extend the existing FR-19 durable-work service through this provider,
without introducing a second scheduler or automatic action executor.

Require explicit capabilities for fan-out, publish deduplication, delayed retry,
visibility extension and same-store transaction participation. Reject ordering,
replay and exactly-once requirements in version 1. Provider-specific stronger
features need a separate qualified contract, never a native-client escape hatch.

Reuse UMF schema artifacts for business payloads and qualified codecs for their
instances. Keep bytes plus a pinned payload profile in the transport envelope.
Initial codec qualification targets JSON with UMF JSON Schema; native Protobuf and
Avro instances need their own pinned codec evidence. A new UMF messaging extension
is unnecessary for payload shape. General channel/operation relationships may
justify one later; local Batten settings suffice for this SDK boundary.

## Why We Chose This

### Over a publicly shared table

A protocol can enforce scope, preserve uncertain outcomes and hide receipt/lease
mechanisms. PostgreSQL still supplies row locking and same-transaction publication;
clients do not depend on table names or credentials. An explicit transaction bridge
must qualify the exact participating executor before stronger guarantees are claimed.

### Over selecting a broker now

PostgreSQL is already a Batten platform dependency and fits durable application
work. A broker may later suit independently scaled event infrastructure. Queue
contention, retained volume and fan-out costs must be measured before changing
the provider; no unmeasured throughput threshold or fleet capacity is assumed.

### Over claiming transparent broker equivalence

Kafka consumer groups track partition offsets; out-of-order completion needs a
safe commit frontier or durable acknowledgement tracking. SQS can redeliver within
visibility windows; fan-out needs additional routing. NATS requires JetStream
durability and explicit acknowledgements, rather than Core NATS alone.
Each adapter must qualify retention, recovery and topology semantics, including
any auxiliary durable state, or refuse the profile. These are design constraints,
not claims that adapters exist.

## Consequences

**Good**: Application code keeps named channels, exact payload schema identity,
scoped authority and explicit recovery across selected providers. Messaging-free
applications do not acquire a driver or codec dependency.

**Trade-offs**: PostgreSQL queue churn, vacuum, pending-byte accounting and fan-out
consume database capacity. Native broker replay/ordering remains outside version 1.
Durable work needs active consumers or a qualified host wake mechanism; tables and
notifications alone do not run handlers. Codec availability in Python is qualified
separately from UMF schema import/export support.

**Drift signals to watch**: Exposed SQL/offset/queue URLs; payload coercion to JSON;
implicit actor headers; invented transaction contexts; automatic broker fallback;
core importing messaging types; two independent retry policies for scheduled work.

## Assumptions

PostgreSQL capacity and host-managed polling fit the first workload. Native load,
restart and fairness measurements can invalidate that assumption. Lakebase is a
candidate deployment of the same adapter, requiring separate qualification.

## Validation

**Result**: not tested.
**Evidence**: CONTRACT-007 and TP-001 MSG allocation define required observations.
Source inspection supports schema reuse, not installed codec or provider behavior.

Primary references: [PostgreSQL 18 locking](https://www.postgresql.org/docs/18/sql-select.html),
[Kafka 4.1 offset tracking](https://kafka.apache.org/41/implementation/distribution/),
[SQS visibility](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html),
[NATS JetStream](https://docs.nats.io/concepts/jetstream), and
[Lakebase compatibility](https://docs.databricks.com/aws/en/oltp/projects/compatibility).
