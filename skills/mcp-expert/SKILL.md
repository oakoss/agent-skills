---
name: mcp-expert
description: 'Architects and orchestrates Model Context Protocol (MCP) ecosystems including server development, tool design, and interactive MCP Apps. Use when building MCP servers, designing agentic tool interfaces, configuring MCP transports, implementing OAuth security, or troubleshooting MCP connectivity. Use for outcome-oriented tools, Zod validation, progressive disclosure resources, and HITL gates.'
---

# MCP Expert

## Overview

Definitive resource for building and managing Model Context Protocol ecosystems. Covers the full lifecycle from proactive onboarding and server development to MCP App interactive UIs and zero-trust security. Designs agent-first tool interfaces that minimize token usage and maximize LLM accuracy.

**When to use:** Building MCP servers, designing tool interfaces, configuring transports (Stdio/SSE), implementing OAuth, troubleshooting connectivity, creating MCP Apps.

**When NOT to use:** Application-level business logic, non-MCP API design, frontend UI components.

## Quick Reference

| Pattern                | API/Approach                             | Key Points                                  |
| ---------------------- | ---------------------------------------- | ------------------------------------------- |
| Outcome-oriented tools | Single-call operations                   | Avoid chatty multi-step APIs                |
| Argument flattening    | Flat Zod schemas with descriptions       | Reduce model hallucination                  |
| Progressive disclosure | Return `mcp://` URIs for large data      | Agent reads partially via `resources/read`  |
| Retryable tools        | Return `retry_with` suggestions          | Help LLM self-correct on bad inputs         |
| Helpful errors         | Descriptive strings with fix guidance    | Never return raw exceptions or stack traces |
| Pagination             | `has_more` + `next_cursor` metadata      | 20-50 records per call maximum              |
| Stdio transport        | Local tools, stderr-only logging         | Never write to stdout except JSON-RPC       |
| SSE transport          | Remote/cloud tools                       | Requires proper CORS and HTTP headers       |
| OAuth 2.1 with PKCE    | Enterprise data access                   | Token verification on every tool call       |
| Capability scopes      | `read:docs`, `write:code`, `admin:users` | Granular permission boundaries              |
| HITL gate              | `confirmation_required` flag             | Manual approval for destructive actions     |
| MCP Apps               | `application/mcp-app+json` resources     | Interactive UI rendered in host environment |

## Onboarding Protocol

When an agent needs a new capability:

1. **Validation**: Check if the required MCP server is already active
2. **Guide**: If missing, provide the user with a direct installation path
3. **Config**: Use `uvx` for zero-install execution where possible

## Common Mistakes

| Mistake                                                    | Correct Pattern                                                          |
| ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| Designing chatty APIs that require many round-trips        | Build outcome-oriented tools that accomplish tasks in a single call      |
| Logging to stdout which breaks the Stdio transport channel | Log only to stderr to keep the transport channel clean                   |
| Returning raw exceptions and stack traces to the LLM       | Return helpful error strings with suggested corrections                  |
| Building monolithic servers with dozens of tools           | Keep servers focused with 5-15 tools for discoverability and maintenance |
| Hardcoding secrets in MCP server configuration             | Use environment variable mapping for all sensitive values                |
| Returning large datasets in a single tool call             | Use pagination (20-50 records) or resource URIs for large data           |
| Vague tool descriptions causing LLM hallucination          | Add example usage and strict constraints to the tool description field   |

## Delegation

- **Discover and audit existing MCP server configurations**: Use `Explore` agent to check active servers, verify connectivity, and identify missing capabilities
- **Build and deploy a new MCP server with validation and auth**: Use `Task` agent to scaffold the server, implement Zod validation, and configure OAuth
- **Design MCP ecosystem architecture for multi-agent workflows**: Use `Plan` agent to map tool boundaries, transport selection, and security scoping

## References

- [Server development, tool design, argument flattening, pagination, and error handling](references/server-development.md)
- [Security, OAuth integration, capability scopes, HITL gates, and audit trails](references/security-auth.md)
- [MCP Apps architecture, interactive UI rendering, and state synchronization](references/mcp-apps.md)
- [Troubleshooting guide, MCP Inspector, common errors, and transport debugging](references/troubleshooting.md)
