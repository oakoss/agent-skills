---
title: MCP Orchestration
description: Model Context Protocol architecture, resources, tools, prompts, multi-server orchestration, and bidirectional sampling
tags: [mcp, model-context-protocol, tools, resources, prompts, sampling]
---

# MCP Orchestration

MCP (Model Context Protocol) provides a standardized way for agents to connect to servers that host tools, resources, and prompts.

## MCP Architecture

### Resources

Readable data sources like files, database schemas, or API documentation. Subagents should use `list_resources` to discover what is available before reading specific resources.

Examples:

- File system contents
- Database schemas
- API documentation
- Configuration files
- Environment information

### Tools

Executable functions with JSON-Schema validated arguments. MCP standardizes argument typing and validation.

Examples:

- Database queries
- File operations
- API calls
- Code analysis
- Build commands

### Prompts

Servers can provide prompt templates that guide agents on how to use specific tools effectively. These encode domain expertise into reusable instructions.

## Multi-Server Orchestration

An orchestrator often connects to multiple MCP servers simultaneously.

### Unified Toolset Pattern

The parent agent acts as a gateway, exposing a unified set of tools to subagents. The parent routes tool calls to the correct MCP server.

```text
Parent Agent (Gateway)
  ├── MCP Server: PostgreSQL (database tools)
  ├── MCP Server: GitHub (repository tools)
  ├── MCP Server: Filesystem (file tools)
  └── Subagent (sees unified toolset)
```

### Server Selection

| Server Type | Use Case                        | Tools Provided                 |
| ----------- | ------------------------------- | ------------------------------ |
| Database    | Schema queries, data operations | query, insert, update, migrate |
| Repository  | Code management, PR operations  | read_file, create_pr, search   |
| Filesystem  | Local file operations           | read, write, list, search      |
| API         | External service integration    | request, webhook, authenticate |

### Configuration

MCP servers are configured per project. The orchestrator discovers available servers and their capabilities at startup.

Key configuration:

- Server endpoints and authentication
- Available tools per server
- Resource access patterns
- Rate limits and quotas

## Bidirectional Communication (Sampling)

MCP servers can request the agent to generate text as part of tool execution. This enables complex workflows where tool execution requires AI reasoning mid-stream.

### Protocol Flow

1. Agent calls Tool A on Server X
2. Tool A starts executing
3. Tool A sends a `sampling/createMessage` request back to the Agent
4. Agent generates a response
5. Tool A receives the response and finishes execution

### Use Cases

- Code analysis tool asks agent to explain a pattern
- Database tool asks agent to generate a migration
- Review tool asks agent to summarize findings

## Best Practices

| Practice                            | Rationale                                  |
| ----------------------------------- | ------------------------------------------ |
| Use MCP servers for all tool access | Standardized, typed, validated interfaces  |
| Never build custom tool adapters    | MCP handles protocol, auth, and validation |
| Discover resources before reading   | Avoid assumptions about available data     |
| Configure per-project servers       | Different projects need different tools    |
| Set appropriate rate limits         | Prevent runaway tool calls                 |
