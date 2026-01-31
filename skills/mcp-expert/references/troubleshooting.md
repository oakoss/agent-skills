---
title: Troubleshooting
description: MCP debugging with Inspector, common error resolution, host log locations, environment injection issues, and transport-specific problems
tags:
  [
    troubleshooting,
    mcp-inspector,
    debugging,
    errors,
    stdio,
    streamable-http,
    logs,
  ]
---

# Troubleshooting

## Local Debugging with MCP Inspector

Use the MCP Inspector tool to test your server without an LLM:

```bash
npx @modelcontextprotocol/inspector <your-server-command>
```

Verify these in the Inspector:

- `tools/list` returns the expected schema with descriptions
- `resources/list` shows correct URIs
- Tool calls with manual JSON inputs produce expected results
- Structured outputs match the declared `outputSchema`

## Common Errors

### Method Not Found

- **Cause**: The server does not implement the requested JSON-RPC method (e.g., `prompts/list`)
- **Fix**: Update your SDK and ensure all required handlers are registered. Check that your server declares the correct capabilities in the `initialize` response.

### Tool Call Timed Out

- **Cause**: The operation took longer than the host environment timeout (usually 30-60 seconds)
- **Fix**: Implement progress notifications for long-running operations, use the async Tasks primitive (2025-11-25 spec), or optimize the backend logic

### LLM Hallucinated Arguments

- **Cause**: The tool description is vague or ambiguous
- **Fix**: Add example usage and strict constraints to the tool description field. Use Zod enums for fixed-value parameters. Use `.describe()` on every schema field.

### Invalid Session ID (HTTP 404)

- **Cause**: Client sent a request with an expired or unknown `Mcp-Session-Id` header
- **Fix**: Re-initialize the connection. The server may have restarted or the session expired.

### OAuth 401 Unauthorized

- **Cause**: Missing, expired, or invalid access token on an HTTP-based transport
- **Fix**: Check that the client completed the OAuth 2.1 flow. Verify the token audience matches the MCP server. Ensure PKCE was used with S256.

## Host Log Locations

Check the logs of your host environment:

- **Claude Desktop**: `~/Library/Logs/Claude/mcp.log`
- **Claude Code**: Check stderr output in the terminal where the server was launched
- **VS Code (Copilot)**: Check the Output panel for MCP-related channels
- **Cursor**: Check the Output panel for MCP logs

## Environment Injection Issues

If your tools fail due to missing API keys:

- Check your `.mcp.json` or MCP configuration file for the correct environment variable names
- Ensure keys are passed through the `env` object in the MCP server configuration
- Verify the shell environment has the variables set before launching the host
- For Stdio transport, environment variables are the primary auth mechanism

## Stdio Transport Issues

- **Symptoms**: Server fails silently, no tool responses
- **Common cause**: Writing non-JSON-RPC output to stdout (debug logs, progress bars, print statements)
- **Fix**: Route all diagnostic output to stderr. In Node.js, use `console.error()` for logging. In Python, use `sys.stderr.write()`.
- **Validation**: Run with MCP Inspector to see raw JSON-RPC traffic

## Streamable HTTP Transport Issues

- **Connection refused**: Verify the server is listening on the correct port and the MCP endpoint path is correct
- **CORS errors**: Configure appropriate CORS headers if the client is browser-based
- **Session lost**: Check that `Mcp-Session-Id` headers are being forwarded correctly through any proxies or load balancers
- **SSE stream drops**: The server may close the SSE stream; clients should handle reconnection using the `Last-Event-ID` header
- **Stateless mode**: If the server does not return a session ID, the client should not send one

## Debugging Checklist

1. Test with MCP Inspector before connecting to an LLM host
2. Verify the server starts without errors on stderr
3. Check that all tool schemas have descriptions on every field
4. Confirm the transport matches the deployment model (Stdio for local, Streamable HTTP for remote)
5. For OAuth issues, verify the authorization server metadata at `.well-known/oauth-authorization-server`
6. For elicitation issues, ensure the schema is flat (no nested objects)
