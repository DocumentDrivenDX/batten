---
ddx:
  id: US-006
  type: user-stories
  activity: frame
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
    - id: CONTRACT-006
      kind: informed_by
---

# US-006: Use managed local object storage

**Feature**: FEAT-006 — Platform resources
**Feature Requirements**: PRD FR-26
**PRD Requirements**: FR-26, FR-29
**Priority**: P0

## Story

**As a** local application developer
**I want** the storage capability to operate on a managed local namespace
**So that** I can exercise portable application behavior without a cloud account.

## Context

The first implementation uses explicit host authority and typed limits. It must
exercise the portable contract without placing a cloud dependency in core.

## Walkthrough

1. The host explicitly initializes a dedicated fabricated-data directory.
2. A trusted local invocation receives an authorized storage resource.
3. The application stores and reads a fabricated review attachment.
4. Concurrent updates, bounded listing and resumed transfers preserve the
   contract's version, authority and uncertainty outcomes.
5. Shutdown closes handles while retaining published data for the next start.

## Acceptance Criteria

- **US-006-AC1** — Given a prepared managed namespace, when an authorized app stores and reads fabricated bytes, then bytes and metadata round-trip under STO-01; its wheel imports without cloud libraries under STO-09.
- **US-006-AC2** — Authority loss and unsafe filesystem names cannot disclose or modify another scope under STO-02/03.
- **US-006-AC3** — Conditional and atomic publication preserve the qualified concurrent-writer/reader outcomes under STO-04/15.
- **US-006-AC4** — Stream, range and integrity outcomes remain bounded and preserve uncertainty under STO-05/10/13.
- **US-006-AC5** — Listing/caching preserve progress, limits and authority under STO-06/14.
- **US-006-AC6** — Upload lifecycle, recovery and shutdown preserve original outcomes and data under STO-07/08/11/12.

## Edge Cases

Interrupted mutation preserves uncertainty. An unsupported filesystem profile
refuses readiness. A borrowed provider outlives a closed request handle.

## Test Scenarios

TP-001's STO-01–15 allocation supplies the fabricated scenarios. CONTRACT-006/100
own exact call and outcome semantics; tests exercise those public boundaries.

## Dependencies

CONTRACT-002 quality adoption precedes source; CONTRACT-006/100 govern storage.
ADR-010 and SD-001 preserve platform ownership. No live cloud dependency is needed.

## Out of Scope

Databricks implementation, upstream migration and the complete host runtime remain
separate implementations; the public protocol permits those adapters later.
