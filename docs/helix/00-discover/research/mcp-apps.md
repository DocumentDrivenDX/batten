---
ddx:
  id: batten.research.mcp-apps
  type: resource-summary
  activity: discover
  authoring:
    home: repo
  links: []
---

# Tool and UI composition in MCP Apps

## Source

- URL: [OpenAI MCP server and UI quickstart](https://developers.openai.com/plugins/build/app-quickstart).
- Accessed: 2026-10-29; current documentation, not a pinned software release.

## Summary

The Model Context Protocol (MCP) Apps flow connects tool calls and interactive UI
resources through a host. OpenAI's quickstart illustrates a to-do workflow using
an MCP server and a UI component.

## Relevant Findings

- Tools and UI resources can be exposed through one host-facing integration.
- The tutorial still requires a reachable server endpoint for connection.
- Inference for Batten: a tool/UI contract and a deployment experience address
  distinct parts of the app author's work.

## HELIX Usage

Informs `batten.product-vision` and the question of which delivery/integration
responsibilities Batten handles. This is adjacent prior art; the owner's phrase
“apps SDK” has not been interpreted as requiring ChatGPT or MCP compatibility.

## Authority Boundary

This source describes an external application-host model. It establishes no Batten
protocol, provider, embedding, authentication, deployment, or compatibility choice.
The PRD and architecture will own any selected host contract.
