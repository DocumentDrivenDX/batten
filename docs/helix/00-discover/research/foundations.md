---
ddx:
  id: batten.research.foundations
  type: resource-summary
  activity: discover
  authoring:
    home: repo
  links: []
---

# Novirhyza foundation survey

## Source

- Sources: local UMF product vision and README; Tether, Weft, and Arras READMEs.
- Repository URLs: [UMF](https://github.com/DocumentDrivenDX/umf),
  [Tether](https://github.com/DocumentDrivenDX/tether),
  [Weft](https://github.com/DocumentDrivenDX/weft),
  [Arras](https://github.com/DocumentDrivenDX/arras).
- Accessed: 2026-10-29. Local documentation was inspected; remote parity was not checked.

## Summary

The four named foundations cover data meaning, agent execution, query compilation,
and an application interface over typed data and actions. Their documented
surfaces provide composition candidates for Batten. The inspected documentation
qualifies support by version and subset and retains application/host obligations.

## Relevant Findings

- UMF is a machine-readable metamodel and schema interchange fabric. Its vision
  emphasizes preserving native meaning and reporting translation loss.
- Tether is a Python agent-harness library with typed tools, policy, and durable
  sessions. Its inspected README names Pydantic AI Agent integration and scoped
  local/PostgreSQL runtime evidence.
- Weft compiles SQL using supplied UMF modules into backend SQL, parameters,
  result types, decoding instructions, and diagnostics. Its README identifies
  Rust, Python bindings, browser WebAssembly, and selected backend profiles.
- Arras is an interface to an ontology with UMF-defined types/actions, backend
  contracts, and a React operator console/Graph Browser. Its host supplies
  identity and configuration.
- Inference: these surfaces are relevant to the proposed data/action/UI authoring
  experience. A fresh composition must define who handles the retained host duties.

## HELIX Usage

Informs `batten.product-vision` and requirements intake. Use the foundation roles
to identify questions and candidate integration boundaries, then inspect the
selected upstream contracts and version evidence before design commitments.

## Authority Boundary

This is a bounded documentation survey, not code or contract qualification.
Sibling implementation, languages, licenses, and release claims do not become
Batten requirements. The owner has not yet defined cleanroom reuse boundaries
or required compatibility. Batten requirements and designs own those decisions.
