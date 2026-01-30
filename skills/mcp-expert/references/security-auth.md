---
title: Security and Auth
description: OAuth 2.1 integration with PKCE, capability-based security scopes, HITL gates for destructive actions, secret management, and audit trails
tags: [oauth, security, pkce, hitl, capability-scopes, secret-management, audit]
---

# Security and Auth

## OAuth 2.1 Integration

MCP servers should not handle user passwords. Use OAuth with PKCE:

1. **Handshake**: Client (agent) requests access
2. **Consent**: Host environment opens a browser for user consent
3. **Token**: Server receives an encrypted access token
4. **Enforcement**: Every tool call must verify the token before execution

## Capability-Based Security

Define granular scopes for your tools:

- `read:docs` - Agent can see documents but not edit
- `write:code` - Agent can suggest changes to code
- `admin:users` - Agent can manage permissions (requires manual approval)

Scope boundaries prevent privilege escalation. An agent configured for read-only operations cannot accidentally execute write operations.

## Human-in-the-Loop (HITL) Gate

For high-risk operations (deleting databases, executing shell commands, modifying permissions), the MCP server should return a confirmation flag:

```ts
interface HitlResponse {
  is_done: false;
  status: 'awaiting_approval';
  message: 'I need to delete 50 files. Is this correct?';
  metadata: { risk: 'high' };
}
```

The host environment presents this to the user for explicit approval before proceeding.

## Secret Management

- Never log API keys or access tokens in any output
- Use an MCP-native secret manager to inject environment variables securely
- Rotate server-to-server tokens on a regular schedule
- Pass secrets through the `env` object in MCP configuration, never hardcoded

## Audit Trails

Log every MCP interaction with:

- Timestamp
- Agent ID
- Tool name
- Arguments (masking sensitive fields)
- Outcome (success/failure and result summary)

Audit trails enable forensic analysis when agent behavior needs investigation.
