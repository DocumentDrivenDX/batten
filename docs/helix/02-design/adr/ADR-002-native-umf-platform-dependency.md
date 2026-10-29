---
ddx:
  id: ADR-002
  type: adr
  activity: design
  authoring:
    home: repo
  links:
    - id: batten.prd
      kind: derived_from
---

# ADR-002: Depend on native UMF authoring and compilation

## Problem

An SDK-owned modeling dialect and compiler creates a competing source of truth.
Moving to a platform dependency must preserve policy and lifecycle meaning, not
merely replace a parser import and lose behavior.

## Decision

Authors use native UMF documents, UMF's Python SDK/compiler, and typed access.
Weft remains the query compiler. Batten's tables module binds those public APIs
to the application's component lifecycle; it contains no copied or reimplemented
schema compiler, policy emitter, query engine, or legacy-format reader.

The owner has selected this authoring boundary. Any legacy-format/API translation
is owned by the consuming host and kept outside Batten. The platform's installed
release cohort supplies the libraries; application artifacts do not vendor them.

Qualification must cover the complete FR-12/14/16 capability matrix: constraints,
comments, indexes, deny-by-default row policy forms, scope changes, transactional,
concurrent, validation and reviewed data steps, forward evolution including
destructive changes, restart recovery and native typed batches/pages. The upstream
library owns generation/semantic validation; the native execution adapter owns
application of verified artifacts under explicit authority.

A missing upstream capability requires an upstream extension or a precise refusal
pending that extension; it never permits a silent scope cut or an SDK-local compiler.
No historical release number alone establishes this complete qualification.

## Why We Chose This

### Over carrying a private compiler copy

One platform implementation can preserve and qualify meaning across consumers.
A copied emitter creates independent policy and migration behavior to maintain.

### Over a public legacy-format adapter in Batten

The owner explicitly chose native authoring. Host-owned translation preserves
consumer compatibility without making the legacy dialect Batten's public model.

## Consequences

**Good**: Native types and platform semantics govern authoring consistently.

**Trade-offs**: Complete support depends on a qualified upstream cohort and may
require upstream work. Independent authoring changes do not establish legacy compatibility.

**Drift signals to watch**: SQL generation implemented in Batten, copied migration
syntax, silent loss of extension content, or a broad support claim from partial evidence.

## Concern Impact

This implements the native-platform-libraries concern and the owner's ruling.
Portable contracts/runtime remain independent of UMF and ontology-specific types.
