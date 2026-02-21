---
title: Server Development
description: MCP server scaffolding, tool implementation with Zod, resource URIs, prompt templates, outcome-oriented design, structured outputs, pagination, error handling, and async tasks
tags:
  [
    mcp-server,
    tool-design,
    zod,
    pagination,
    error-handling,
    structured-outputs,
    tasks,
    resources,
    prompts,
    scaffold,
  ]
---

# Server Development

## Project Scaffold

### Directory Structure

```sh
my-mcp-server/
├── src/
│   ├── index.ts          # Entry point, transport setup
│   ├── tools/            # Tool handlers
│   │   ├── search.ts
│   │   └── manage.ts
│   ├── resources/        # Resource providers
│   │   └── docs.ts
│   └── prompts/          # Prompt templates
│       └── workflows.ts
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

### package.json

```json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": { "my-mcp-server": "./dist/index.js" },
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts",
    "test": "vitest run"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.12.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.7.0",
    "vitest": "^3.0.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src"]
}
```

### Entry Point (Stdio)

```ts
#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { registerTools } from './tools/search.js';
import { registerResources } from './resources/docs.js';

const server = new McpServer({
  name: 'my-mcp-server',
  version: '1.0.0',
});

registerTools(server);
registerResources(server);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Entry Point (Streamable HTTP)

```ts
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { randomUUID } from 'node:crypto';
import express from 'express';

const app = express();
app.use(express.json());

const server = new McpServer({ name: 'my-mcp-server', version: '1.0.0' });

const transport = new StreamableHTTPServerTransport({
  sessionIdGenerator: () => randomUUID(),
});
await server.connect(transport);

app.post('/mcp', (req, res) => transport.handleRequest(req, res));
app.get('/mcp', (req, res) => transport.handleRequest(req, res));
app.delete('/mcp', (req, res) => transport.handleRequest(req, res));

app.listen(3000, () => {
  console.error('MCP server listening on port 3000');
});
```

## Tool Implementation Pattern

Register tools with Zod schemas for input validation, descriptions on every field, and structured error handling:

```ts
import { type McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

export function registerTools(server: McpServer) {
  server.tool(
    'search_documents',
    'Search documents by keyword. Returns matching titles and snippets.',
    {
      query: z.string().min(2).describe('Search keyword (min 2 chars)'),
      limit: z.number().min(1).max(50).default(20).describe('Max results'),
      cursor: z
        .string()
        .optional()
        .describe('Pagination cursor from previous call'),
    },
    async ({ query, limit, cursor }) => {
      try {
        const results = await searchIndex(query, limit, cursor);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                items: results.items,
                has_more: results.hasMore,
                next_cursor: results.nextCursor,
              }),
            },
          ],
        };
      } catch (error) {
        return {
          isError: true,
          content: [
            {
              type: 'text',
              text: `Search failed for query "${query}". Verify the index is available and try again.`,
            },
          ],
        };
      }
    },
  );
}
```

### Error Handling Pattern

Wrap tool handlers to catch exceptions and return actionable messages:

```ts
function safeTool<T>(
  handler: (
    args: T,
  ) => Promise<{ content: Array<{ type: string; text: string }> }>,
) {
  return async (args: T) => {
    try {
      return await handler(args);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unknown error occurred';
      return {
        isError: true as const,
        content: [{ type: 'text' as const, text: `Error: ${message}` }],
      };
    }
  };
}
```

## Resource Implementation

Resources expose data via URI templates that agents can read on demand. Use resources for large datasets, configuration, and documentation that tools can reference.

### Static Resources

```ts
export function registerResources(server: McpServer) {
  server.resource('project-config', 'config://project', async (uri) => ({
    contents: [
      {
        uri: uri.href,
        mimeType: 'application/json',
        text: JSON.stringify({
          version: '1.0.0',
          environment: process.env.NODE_ENV ?? 'development',
        }),
      },
    ],
  }));
}
```

### Resource Templates

Resource templates use URI patterns with parameters. Agents discover available templates via `resources/list` and read specific resources by filling in parameters:

```ts
server.resource(
  'document',
  'docs://documents/{docId}',
  { list: undefined },
  async (uri, { docId }) => {
    const doc = await db.documents.findUnique({ where: { id: docId } });

    if (!doc) {
      throw new Error(`Document ${docId} not found`);
    }

    return {
      contents: [
        {
          uri: uri.href,
          mimeType: 'text/markdown',
          text: doc.content,
        },
      ],
    };
  },
);
```

### Resource List Callback

Provide a list callback so agents can discover available resources:

```ts
server.resource(
  'document',
  'docs://documents/{docId}',
  {
    list: async () => {
      const docs = await db.documents.findMany({
        select: { id: true, title: true },
      });
      return {
        resources: docs.map((doc) => ({
          uri: `docs://documents/${doc.id}`,
          name: doc.title,
          mimeType: 'text/markdown',
        })),
      };
    },
  },
  async (uri, { docId }) => {
    const doc = await db.documents.findUnique({ where: { id: docId } });
    return {
      contents: [
        { uri: uri.href, mimeType: 'text/markdown', text: doc!.content },
      ],
    };
  },
);
```

## Prompt Templates

Prompts are server-defined templates that provide structured context for common workflows. Agents select prompts by name and fill in arguments.

```ts
server.prompt(
  'summarize-document',
  'Summarize a document by ID with a specified detail level',
  {
    docId: z.string().describe('Document ID to summarize'),
    detail: z
      .enum(['brief', 'detailed', 'executive'])
      .default('brief')
      .describe('Summary detail level'),
  },
  async ({ docId, detail }) => {
    const doc = await db.documents.findUnique({ where: { id: docId } });

    if (!doc) {
      throw new Error(`Document ${docId} not found`);
    }

    return {
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Summarize the following document at "${detail}" detail level:\n\n${doc.content}`,
          },
        },
      ],
    };
  },
);
```

### Multi-Message Prompts

Prompts can include system context and embedded resources:

```ts
server.prompt(
  'code-review',
  'Review code changes with project style guidelines',
  { diff: z.string().describe('Git diff to review') },
  async ({ diff }) => ({
    messages: [
      {
        role: 'user',
        content: {
          type: 'text',
          text: `Review this diff for correctness, style, and potential issues:\n\n${diff}`,
        },
      },
    ],
  }),
);
```

## Tool Design: Outcomes Over Operations

Do not mirror your REST API as individual tools. Agents struggle with excessive orchestration.

- **Bad**: `get_user_id`, `get_user_email`, `update_user_field` (three calls for one task)
- **Good**: `sync_user_profile` (handles identification and multi-field updates in one call)

Design each tool to accomplish a meaningful outcome rather than a single CRUD operation.

### Tool Annotations

The 2025-03-26 spec added tool annotations that help clients understand tool behavior without parsing descriptions:

```ts
server.tool(
  'delete_records',
  { ids: z.array(z.string()).describe('Record IDs to delete') },
  { destructiveHint: true, idempotentHint: false, openWorldHint: false },
  async ({ ids }) => {
    await db.deleteMany(ids);
    return {
      content: [{ type: 'text', text: `Deleted ${ids.length} records` }],
    };
  },
);
```

Annotations are hints, not guarantees. Clients should not rely on them for security decisions.

## Argument Flattening and Type Safety

Use flat schemas with strict types to reduce model hallucination:

```ts
const sendAlertSchema = z.object({
  channelId: z.string().describe('Target channel UUID'),
  message: z.string().min(10).describe('Alert content (min 10 chars)'),
  severity: z.enum(['low', 'high', 'critical']),
});
```

Flat schemas with descriptive field annotations produce fewer hallucinated arguments than nested objects. Use `z.enum()` for fixed-value parameters and `.describe()` on every field.

## Structured Tool Outputs

Since the 2025-06-18 spec, tools can declare an `outputSchema` to return typed JSON instead of plain text:

```ts
server.tool(
  'get_weather',
  {
    city: z.string().describe('City name'),
  },
  {
    outputSchema: z.object({
      temperature: z.number(),
      humidity: z.number(),
      condition: z.string(),
    }),
  },
  async ({ city }) => {
    const data = await fetchWeather(city);
    return {
      structuredContent: {
        temperature: data.temp,
        humidity: data.humidity,
        condition: data.condition,
      },
    };
  },
);
```

When `outputSchema` is defined, return `structuredContent` instead of `content`. Clients can process the result programmatically without parsing text.

## Pagination and Resource Management

Never return large datasets in a single tool call. Large responses blow out the LLM context window.

- **Standard Limit**: 20-50 records per call
- **Metadata**: Always include `has_more` and `next_cursor` fields
- **Resource URIs**: For large files, return an `mcp://` URI that the agent can read partially using `resources/read`

## Helpful Error Strings

Agents can self-correct if you give them a path forward:

- **Bad**: `Error: 400 Bad Request`
- **Good**: `Error: 'startDate' must be before 'endDate'. Please adjust your parameters and try again.`

Include the field name, the constraint violated, and a suggested correction. Set `isError: true` in the tool result to signal failure.

## Async Tasks (Experimental)

The 2025-11-25 spec introduces the Tasks primitive for long-running operations. Instead of blocking until completion, return a task handle:

- Server returns a task ID when the operation will exceed typical timeout thresholds
- Clients poll with `tasks/get` to check status and retrieve results
- Servers can publish progress updates via notifications
- Clients can cancel with `tasks/cancel`

This is particularly useful for document processing, indexing, analytics jobs, and model inference.

## Development Stack

- **Runtime**: Bun or Node.js with native TypeScript support
- **SDK**: `@modelcontextprotocol/sdk` (TypeScript) or `mcp` (Python)
- **Validation**: Zod or Valibot for runtime schema enforcement
- **Server Size**: Keep servers focused with 5-15 tools for discoverability and maintenance
- **Spec Version**: Target 2025-11-25 for the latest features
