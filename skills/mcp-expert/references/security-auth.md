---
title: Security and Auth
description: OAuth 2.1 with PKCE for MCP authorization, elicitation for server-initiated user input, capability scopes, HITL gates, secret management, and audit trails
tags:
  [
    oauth,
    security,
    pkce,
    elicitation,
    hitl,
    capability-scopes,
    secret-management,
    cimd,
  ]
---

# Security and Auth

## OAuth 2.1 Authorization

MCP uses OAuth 2.1 for HTTP-based transports. The architecture separates three roles:

- **MCP Server**: Acts as an OAuth 2.1 resource server -- validates tokens, never issues them
- **MCP Client**: Acts as an OAuth 2.1 client -- requests tokens on behalf of the user
- **Authorization Server**: External identity provider that handles user authentication and token issuance

This separation was formalized in the 2025-06-18 spec. MCP servers must never implement their own auth server.

### Authorization Flow

1. Client connects to MCP server and receives HTTP 401 with `WWW-Authenticate` header
2. Client discovers the authorization server via RFC 9728 (Protected Resource Metadata)
3. Client initiates OAuth 2.1 authorization code flow with mandatory PKCE (S256)
4. User authenticates in the browser and grants consent
5. Client receives access token and includes it in subsequent MCP requests
6. Server validates the token on every request, checking audience and scopes

### PKCE Requirement

All clients must use PKCE with the S256 code challenge method. This is mandatory, not optional. PKCE protects public clients (agents, CLI tools, serverless functions) that cannot securely store client secrets.

### Client ID Metadata Documents (CIMD)

The 2025-11-25 spec introduces CIMD as the preferred alternative to Dynamic Client Registration (DCR). Instead of registering with every server, clients publish a metadata document at a URL they control:

```json
{
  "client_id": "https://my-agent.example.com/client-metadata",
  "client_name": "My AI Agent",
  "redirect_uris": ["https://my-agent.example.com/callback"],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

Authorization servers fetch this document to learn about the client. This eliminates per-server registration friction.

### Stdio Transport Auth

Stdio servers should not use OAuth. Instead, retrieve credentials from environment variables passed through the MCP configuration `env` object.

## Elicitation

Elicitation (2025-06-18) allows MCP servers to request information from the user during execution. The server sends a flat schema describing what it needs, and the client renders a form.

### Three Response States

- **Accept**: User provided the requested data (includes `content` matching the schema)
- **Decline**: User understood the request and explicitly refused
- **Cancel**: User dismissed the dialog without making a decision

### Schema Design

Elicitation uses a flat schema -- no nested objects. This maps directly to a form UI:

```ts
const result = await ctx.elicit({
  message: 'Which database should I connect to?',
  requestedSchema: {
    type: 'object',
    properties: {
      host: { type: 'string', default: 'localhost' },
      port: { type: 'number', default: 5432 },
      database: { type: 'string' },
    },
    required: ['host', 'database'],
  },
});
```

### URL Mode Elicitation

The 2025-11-25 spec added URL mode elicitation for secure credential collection. Instead of collecting secrets through the client, redirect the user to a browser:

```ts
const result = await ctx.elicitUrl({
  message: 'Please authenticate with the payment provider',
  url: 'https://payments.example.com/auth',
  reason: 'Required to process transactions',
});
```

Credentials never transit through the MCP client. Use URL mode for API keys, passwords, and any PCI-compliant flows.

### Security Boundary

Servers must not request sensitive information through standard elicitation. Elicitation is for configuration parameters and operational choices, not authentication credentials.

## Capability-Based Security

Define granular scopes for your tools:

- `read:docs` -- Agent can see documents but not edit
- `write:code` -- Agent can suggest changes to code
- `admin:users` -- Agent can manage permissions (requires manual approval)

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
- Pass secrets through the `env` object in MCP configuration, never hardcoded
- Rotate server-to-server tokens on a regular schedule
- MCP servers must never forward received access tokens to upstream APIs (confused deputy prevention)

## Audit Trails

Log every MCP interaction with:

- Timestamp
- Agent ID
- Tool name
- Arguments (masking sensitive fields)
- Outcome (success/failure and result summary)

Audit trails enable forensic analysis when agent behavior needs investigation.
