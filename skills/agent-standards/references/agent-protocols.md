---
title: Agent Protocols
description: Standardized agent communication protocols including MCP, A2A, ACP, interaction standards, and metadata tagging
tags: [mcp, agent-to-agent, acp, json-rpc, sse, stdio, metadata]
---

# Agent Protocols

## Model Context Protocol (MCP)

The industry standard for agent-tool communication:

- **Core**: Universal framework for tools, resources, and prompts
- **Advantage**: Prevents vendor lock-in and allows agents to discover new capabilities dynamically
- **Transport**: JSON-RPC over Stdio (local) or SSE (remote)

## Agent-to-Agent (A2A)

Peer-to-peer collaboration between specialized agents:

- **Negotiation**: Agents can bid on tasks based on their specialized skills
- **Handoff**: Passing context and mission objectives from one agent to another (Architect to Engineer, Engineer to Reviewer)
- **Feedback Loop**: Results flow back to the orchestrator for verification

## Agent Communication Protocol (ACP)

Lightweight, REST-based messaging for interacting with legacy systems:

- **Simplicity**: Best for rapid prototyping and simple HTTP triggers
- **Integration**: Bridges modern agent ecosystems with existing infrastructure

## Interaction Standards

- **JSON-RPC**: The foundation of MCP messaging. All tool calls and responses use this format.
- **SSE (Server-Sent Events)**: For real-time updates and streaming results from remote tools.
- **Stdio**: The primary channel for local tool integration. Never mix logging with protocol messages on stdout.

## Metadata Tagging

Every agent interaction should include metadata for traceability and quality assessment:

- `agent_version`: The semantic version of the agent core
- `confidence_score`: The agent's own assessment of its plan quality
- `rationale`: A concise explanation of the chosen strategy
- `task_id`: Reference to the tracked task or ticket being addressed
