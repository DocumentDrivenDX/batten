# Batten design documents

Design records for the Batten application SDK. For what ships today read the
[README](../../README.md); for what is not built read the [roadmap](../../ROADMAP.md).

- [Product vision](00-discover/product-vision.md), [PRD](01-frame/prd.md),
  [concerns](01-frame/concerns.md), [feature specs](01-frame/features/) and
  [user stories](01-frame/user-stories/).
- [Architecture](02-design/architecture.md), [ADRs](02-design/adr/),
  [contracts](02-design/contracts/), [schemas](02-design/schemas/) and
  [technical designs](02-design/technical-designs/).
- [Developer guide](guide/developer/index.md) (source of the microsite) and the
  [microsite build](site/README.md).

The contracts and the PRD describe the intended design and are broader than the
shipped packages. Some prose cites ADR-005, ADR-007, ADR-014, CONTRACT-002 and
CONTRACT-011, which were removed with the 0.1.0a3 reset; they remain in git
history. The approval desk model lives with the example at
`examples/approval-desk/model/approval.umf.json`.
