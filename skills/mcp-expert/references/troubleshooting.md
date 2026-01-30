---
title: Troubleshooting
description: MCP debugging with Inspector, common error resolution, host log locations, environment injection issues, and transport-specific problems
tags: [troubleshooting, mcp-inspector, debugging, errors, stdio, sse, logs]
---

# Troubleshooting

## Local Debugging with MCP Inspector

Use the MCP Inspector tool to test your server without an LLM:

```bash
npx @modelcontextprotocol/inspector <your-server-command>
```

Verify these in the Inspector:

- `list_tools` returns the expected schema with descriptions
- `resources/list` shows correct URIs
- Tool calls with manual JSON inputs produce expected results

## Common Errors

### Method Not Found

- **Cause**: The server does not implement the requested JSON-RPC method (e.g., `prompts/list`)
- **Fix**: Update your SDK and ensure all required handlers are registered

### Tool Call Timed Out

- **Cause**: The operation took longer than the host environment timeout (usually 30-60 seconds)
- **Fix**: Implement progress notifications for long-running operations or optimize the backend logic

### LLM Hallucinated Arguments

- **Cause**: The tool description is vague or ambiguous
- **Fix**: Add example usage and strict constraints to the tool description field. Use Zod enums for fixed-value parameters.

## Host Log Locations

Check the logs of your host environment:

- **Claude Desktop**: `~/Library/Logs/Claude/mcp.log`
- **Gemini CLI**: Look for `mcp_error.log` in the project root
- **VS Code**: Check the Output panel for MCP-related channels

## Environment Injection Issues

If your tools fail due to missing API keys:

- Check your `.mcp.json` or `config.yaml` for the correct environment variable names
- Ensure keys are passed through the `env` object in the MCP server configuration
- Verify the shell environment has the variables set before launching the host

## Stdio vs SSE Transport Issues

- **Stdio**: Fast, best for local scripts. Fails if the server writes anything other than JSON-RPC to stdout. Always use stderr for logging.
- **SSE**: Better for remote tools. Requires proper CORS headers and HTTP configuration. Connection drops may need reconnection logic.
