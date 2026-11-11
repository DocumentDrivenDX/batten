# Roadmap

What Batten does today is in the [README](README.md). This file lists what is
designed but not built. Nothing here is a claim about the current release.

## Not built yet

- **Lintel GraphQL/Relay API.** A read API over the approval desk: a Lintel
  execution port over `batten.umf_postgres.UmfTableProvider` (read-only
  `get_many`), mounted by `batten.asgi.create_app` under
  `/apps/approval-desk/graphql`. Batten host composition constructs the optional
  adapter; generic core and ASGI code import neither Lintel nor GraphQL, and
  resolvers never call providers around admission, permissions or audit.
  Needs a Lintel release that ships its public build API. No dependency on
  Lintel exists today.
- **Arras ontology provider.** There is no shared backend yet (Arras talks to
  Truss; Batten uses UMF Access tables), so this stays a design.
- **Truss graph storage.** A UMF/Truss graph binding alongside the PostgreSQL
  table binding. No dependency on Truss exists today.
- **Tether agent execution** and scoped retrieval.
- **ux-builder binding** for design artifacts. UI today is the authored
  TypeScript app in `examples/approval-desk`.
- **Messaging, jobs and schedules** on PostgreSQL (CONTRACT-007 describes the
  intended shape).
- **Remote object storage adapters.** Only the local filesystem store ships.
- **Production identity.** The local host uses loopback development identities.
- **More example apps.** Only the approval desk exists. Twelve were specified
  (service intake, case tracker, evidence library, document review, entity
  directory, knowledge assistant, inbox triage, data reconciliation, scheduled
  digest, access attestation, service handoff); those specifications were
  removed from the tree and remain in git history before the 0.1.0a3 reset.

## Design records kept

ADRs and contracts under `docs/helix/02-design/` describe the shipped packages
and the intended direction. ADR-005 (series/cohort compatibility), ADR-007
(quality ratchets), ADR-014 (reference-app specifications), CONTRACT-002
(boundaries and quality) and CONTRACT-011 (micro-app conformance) were removed:
the repository now has one version for all packages, plain CI instead of
ratchets, and no reference-app corpus. Remaining prose that cites those
identifiers is historical.
