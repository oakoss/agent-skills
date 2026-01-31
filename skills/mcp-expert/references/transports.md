---
title: Transports
description: MCP transport configuration including Stdio for local tools, Streamable HTTP for remote servers, session management, and migration from deprecated SSE
tags: [stdio, streamable-http, sse, transport, session, migration, json-rpc]
---

# Transports

## Transport Overview

MCP uses JSON-RPC 2.0 over two standard transports. All messages must be UTF-8 encoded.

- **Stdio**: Communication over standard input/output for local process-based servers
- **Streamable HTTP**: HTTP POST and GET requests with optional SSE streaming for remote servers

The standalone HTTP+SSE transport from the 2024-11-05 spec is deprecated as of 2025-03-26.

## Stdio Transport

Stdio is the preferred transport for local tools. The client launches the server as a child process and communicates via stdin/stdout.

### Configuration

```json
{
  "my-server": {
    "command": "npx",
    "args": ["-y", "@example/mcp-server"],
    "env": {
      "API_KEY": "your-key-here"
    }
  }
}
```

### Critical Rules

- **stdout is reserved for JSON-RPC only** -- never write debug output, progress messages, or logs to stdout
- **Use stderr for all logging** -- diagnostic output goes to stderr where the host can capture it
- Messages are delimited by newlines; each JSON-RPC message is one line
- The server should exit cleanly when stdin closes

### Common Patterns

```ts
const server = new McpServer({ name: 'my-server', version: '1.0.0' });

const transport = new StdioServerTransport();
await server.connect(transport);
```

For Python servers, `uvx` provides zero-install execution:

```json
{
  "my-python-server": {
    "command": "uvx",
    "args": ["my-mcp-server"],
    "env": { "API_KEY": "your-key-here" }
  }
}
```

## Streamable HTTP Transport

Streamable HTTP is the standard transport for remote and cloud-hosted MCP servers. The server exposes a single HTTP endpoint (e.g., `https://example.com/mcp`) that accepts both POST and GET methods.

### How It Works

- **POST**: Client sends JSON-RPC requests/notifications. Server responds with JSON-RPC responses, or optionally opens an SSE stream to send multiple messages.
- **GET**: Client opens an SSE stream to receive server-initiated messages (notifications, requests). Server may return 405 if it does not support server-initiated communication.

### Session Management

Servers may assign a session ID during initialization via the `Mcp-Session-Id` response header. When present:

- Clients must include the `Mcp-Session-Id` header on all subsequent requests
- The session ID must be globally unique and cryptographically secure
- Servers should return HTTP 404 for unknown session IDs
- Clients can terminate sessions with an HTTP DELETE to the endpoint

Stateless servers can omit session IDs entirely.

### Server Implementation

```ts
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import express from 'express';

const app = express();
const server = new McpServer({ name: 'remote-server', version: '1.0.0' });

const transport = new StreamableHTTPServerTransport({
  sessionIdGenerator: () => randomUUID(),
});
await server.connect(transport);

app.post('/mcp', (req, res) => transport.handleRequest(req, res));
app.get('/mcp', (req, res) => transport.handleRequest(req, res));
app.delete('/mcp', (req, res) => transport.handleRequest(req, res));

app.listen(3000);
```

### Required Headers

- Client must send `Accept: application/json, text/event-stream` on POST requests
- Client must send `Accept: text/event-stream` on GET requests
- Server returns `Content-Type: application/json` for single responses or `Content-Type: text/event-stream` for streamed responses

## Migrating from Deprecated HTTP+SSE

The legacy HTTP+SSE transport required two separate endpoints (one for SSE stream, one for POST messages) and a long-lived SSE connection. This caused problems with:

- High concurrency and latency under load
- Security tokens exposed in URL query strings
- Connection management complexity

### Migration Steps

1. Replace the separate SSE and POST endpoints with a single MCP endpoint
2. Move from `SSEServerTransport` to `StreamableHTTPServerTransport`
3. Add session management via `Mcp-Session-Id` headers if needed
4. Update client configuration to point to the single endpoint URL

### Backwards Compatibility

Servers can support both transports during migration:

- Keep the legacy SSE and POST endpoints active alongside the new MCP endpoint
- Clients can detect the transport by attempting a POST to the server URL first -- if it succeeds, the server supports Streamable HTTP; if it returns 4xx, fall back to legacy SSE

## Transport Selection Guide

| Factor            | Stdio                          | Streamable HTTP             |
| ----------------- | ------------------------------ | --------------------------- |
| Deployment        | Local, same machine            | Remote, cloud, multi-tenant |
| Latency           | Minimal (no network)           | Network-dependent           |
| Auth              | Environment variables          | OAuth 2.1 with PKCE         |
| Session state     | Implicit (process lifetime)    | Explicit (`Mcp-Session-Id`) |
| Server management | Client manages process         | Independent process         |
| Scaling           | One client per server instance | Multiple clients per server |
