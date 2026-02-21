---
title: Testing and Evaluation
description: MCP server testing with Inspector, unit and integration tests, evaluation frameworks, tool contract validation, load testing, and CI integration
tags:
  [
    testing,
    evaluation,
    mcp-inspector,
    vitest,
    contract-testing,
    ci,
    load-testing,
  ]
---

# Testing and Evaluation

## MCP Inspector

The MCP Inspector is the primary debugging tool for MCP servers. It connects to a server, lists capabilities, and lets you invoke tools interactively without an LLM.

### Setup and Basic Usage

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

The Inspector opens a web UI where you can:

- Browse `tools/list`, `resources/list`, and `prompts/list` responses
- Invoke tools with manually crafted JSON inputs
- Inspect raw JSON-RPC messages on the wire
- Verify structured output matches declared `outputSchema`

### Connecting to Different Transports

```bash
# Stdio server (local)
npx @modelcontextprotocol/inspector node dist/index.js

# Streamable HTTP server (remote)
npx @modelcontextprotocol/inspector --url http://localhost:3000/mcp

# With environment variables
API_KEY=test-key npx @modelcontextprotocol/inspector node dist/index.js
```

### Inspector Checklist

Before connecting to any LLM host, verify in the Inspector:

1. `tools/list` returns all expected tools with descriptions on every field
2. Tool calls with valid inputs return expected results
3. Tool calls with invalid inputs return helpful error strings (not stack traces)
4. `resources/list` shows correct URIs with proper templates
5. Structured outputs match the declared `outputSchema` shape
6. Pagination returns `has_more` and `next_cursor` correctly

## Unit Testing MCP Tools

Test tool handlers in isolation by calling them directly with mock context objects.

### Test Setup

```ts
import { describe, expect, it, vi } from 'vitest';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';

function createTestClient() {
  const server = new McpServer({ name: 'test-server', version: '0.0.1' });
  const [clientTransport, serverTransport] =
    InMemoryTransport.createLinkedPair();

  return { server, clientTransport, serverTransport };
}
```

### Testing Tool Responses

```ts
describe('get_weather tool', () => {
  it('returns structured weather data', async () => {
    const { server, clientTransport, serverTransport } = createTestClient();

    server.tool('get_weather', { city: z.string() }, async ({ city }) => ({
      content: [{ type: 'text', text: JSON.stringify({ temp: 72, city }) }],
    }));

    const client = new Client({ name: 'test-client', version: '0.0.1' });
    await Promise.all([
      client.connect(clientTransport),
      server.connect(serverTransport),
    ]);

    const result = await client.callTool({
      name: 'get_weather',
      arguments: { city: 'Portland' },
    });

    expect(result.isError).toBeFalsy();
    const parsed = JSON.parse(
      (result.content as Array<{ text: string }>)[0].text,
    );
    expect(parsed.temp).toBe(72);
    expect(parsed.city).toBe('Portland');
  });
});
```

### Testing Error Responses

```ts
describe('error handling', () => {
  it('returns helpful error for missing required field', async () => {
    const { server, clientTransport, serverTransport } = createTestClient();

    server.tool(
      'search_docs',
      { query: z.string().min(3).describe('Search query (min 3 chars)') },
      async ({ query }) => ({
        content: [{ type: 'text', text: `Results for: ${query}` }],
      }),
    );

    const client = new Client({ name: 'test-client', version: '0.0.1' });
    await Promise.all([
      client.connect(clientTransport),
      server.connect(serverTransport),
    ]);

    const result = await client.callTool({
      name: 'search_docs',
      arguments: { query: 'ab' },
    });

    expect(result.isError).toBe(true);
  });

  it('does not expose stack traces', async () => {
    const { server, clientTransport, serverTransport } = createTestClient();

    server.tool('failing_tool', {}, async () => {
      throw new Error('Database connection failed');
    });

    const client = new Client({ name: 'test-client', version: '0.0.1' });
    await Promise.all([
      client.connect(clientTransport),
      server.connect(serverTransport),
    ]);

    const result = await client.callTool({
      name: 'failing_tool',
      arguments: {},
    });

    expect(result.isError).toBe(true);
    const text = (result.content as Array<{ text: string }>)[0].text;
    expect(text).not.toContain('at Object.');
    expect(text).not.toContain('.ts:');
  });
});
```

## Integration Testing

Integration tests verify the full server lifecycle including transport setup, capability negotiation, and multi-tool workflows.

### Full Lifecycle Test

```ts
describe('server lifecycle', () => {
  it('initializes and lists tools', async () => {
    const { server, clientTransport, serverTransport } = createTestClient();

    server.tool('ping', {}, async () => ({
      content: [{ type: 'text', text: 'pong' }],
    }));

    const client = new Client({ name: 'test-client', version: '0.0.1' });
    await Promise.all([
      client.connect(clientTransport),
      server.connect(serverTransport),
    ]);

    const tools = await client.listTools();
    expect(tools.tools).toHaveLength(1);
    expect(tools.tools[0].name).toBe('ping');
  });

  it('handles sequential tool calls', async () => {
    const { server, clientTransport, serverTransport } = createTestClient();

    const items: string[] = [];

    server.tool('add_item', { name: z.string() }, async ({ name }) => {
      items.push(name);
      return { content: [{ type: 'text', text: `Added: ${name}` }] };
    });

    server.tool('list_items', {}, async () => ({
      content: [{ type: 'text', text: JSON.stringify(items) }],
    }));

    const client = new Client({ name: 'test-client', version: '0.0.1' });
    await Promise.all([
      client.connect(clientTransport),
      server.connect(serverTransport),
    ]);

    await client.callTool({ name: 'add_item', arguments: { name: 'first' } });
    await client.callTool({ name: 'add_item', arguments: { name: 'second' } });

    const result = await client.callTool({
      name: 'list_items',
      arguments: {},
    });
    const list = JSON.parse(
      (result.content as Array<{ text: string }>)[0].text,
    );
    expect(list).toEqual(['first', 'second']);
  });
});
```

## Evaluation Framework

Evaluation questions validate that your MCP server produces useful, well-structured responses that an LLM can act on.

### Evaluation Criteria

| Criterion           | Question                                             |
| ------------------- | ---------------------------------------------------- |
| Structured data     | Does the tool return parseable JSON, not free text?  |
| Actionable errors   | Can an LLM self-correct from the error message?      |
| Pagination          | Does `has_more` + `next_cursor` work end-to-end?     |
| Schema accuracy     | Does the response match the declared `outputSchema`? |
| Description quality | Would an LLM choose the right tool from description? |
| Edge case handling  | What happens with empty inputs, missing params?      |
| Token efficiency    | Is the response concise enough for LLM context?      |

### Automated Evaluation Suite

```ts
import { describe, expect, it } from 'vitest';

describe('tool evaluation', () => {
  it('returns structured JSON, not prose', async () => {
    const result = await client.callTool({
      name: 'search_users',
      arguments: { query: 'jane' },
    });

    const text = (result.content as Array<{ text: string }>)[0].text;
    expect(() => JSON.parse(text)).not.toThrow();
  });

  it('pagination terminates', async () => {
    let cursor: string | undefined;
    let pages = 0;
    const maxPages = 100;

    do {
      const result = await client.callTool({
        name: 'list_records',
        arguments: { cursor, limit: 10 },
      });

      const data = JSON.parse(
        (result.content as Array<{ text: string }>)[0].text,
      );
      cursor = data.next_cursor;
      pages++;
    } while (cursor && pages < maxPages);

    expect(pages).toBeLessThan(maxPages);
  });

  it('error messages suggest fixes', async () => {
    const result = await client.callTool({
      name: 'create_record',
      arguments: { title: '' },
    });

    expect(result.isError).toBe(true);
    const text = (result.content as Array<{ text: string }>)[0].text;
    expect(text).toMatch(/must|should|try|expected/i);
  });
});
```

## Tool Contract Testing

Contract tests verify that tool input schemas match documentation and that edge cases are handled.

```ts
describe('tool contract', () => {
  it('schema fields match tool description', async () => {
    const tools = await client.listTools();

    for (const tool of tools.tools) {
      expect(tool.description).toBeTruthy();
      if (tool.inputSchema.properties) {
        for (const [key, prop] of Object.entries(tool.inputSchema.properties)) {
          const schema = prop as { description?: string };
          expect(schema.description).toBeTruthy();
        }
      }
    }
  });

  it('handles missing optional params gracefully', async () => {
    const tools = await client.listTools();

    for (const tool of tools.tools) {
      const required = new Set(tool.inputSchema.required ?? []);
      const minimalArgs: Record<string, unknown> = {};

      for (const key of required) {
        minimalArgs[key] = getPlaceholderValue(
          (tool.inputSchema.properties as Record<string, { type: string }>)[
            key
          ],
        );
      }

      const result = await client.callTool({
        name: tool.name,
        arguments: minimalArgs,
      });

      expect(result.isError).not.toBe(true);
    }
  });
});

function getPlaceholderValue(schema: { type: string }): unknown {
  switch (schema.type) {
    case 'string':
      return 'test-value';
    case 'number':
      return 1;
    case 'boolean':
      return true;
    case 'array':
      return [];
    default:
      return {};
  }
}
```

## Load Testing

Validate server behavior under concurrent tool calls.

```ts
describe('load testing', () => {
  it('handles concurrent tool calls', async () => {
    const concurrency = 20;
    const calls = Array.from({ length: concurrency }, (_, i) =>
      client.callTool({
        name: 'get_record',
        arguments: { id: `record-${i}` },
      }),
    );

    const results = await Promise.all(calls);

    for (const result of results) {
      expect(result.isError).toBeFalsy();
    }
  });

  it('respects timeout thresholds', async () => {
    const start = Date.now();

    const result = await Promise.race([
      client.callTool({ name: 'slow_operation', arguments: {} }),
      new Promise((resolve) =>
        setTimeout(() => resolve({ isError: true, timedOut: true }), 30_000),
      ),
    ]);

    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(30_000);
  });
});
```

## CI Integration

### GitHub Actions Workflow

```yaml
name: MCP Server Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build
      - run: npx vitest run
      - name: MCP Inspector smoke test
        run: |
          timeout 10 npx @modelcontextprotocol/inspector node dist/index.js \
            --cli --method tools/list || true
```

### Health Check for Streamable HTTP Servers

```ts
import { describe, expect, it } from 'vitest';

describe('health check', () => {
  it('responds to initialization', async () => {
    const response = await fetch('http://localhost:3000/mcp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2025-11-25',
          capabilities: {},
          clientInfo: { name: 'health-check', version: '1.0.0' },
        },
      }),
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.result.serverInfo.name).toBeTruthy();
  });
});
```
