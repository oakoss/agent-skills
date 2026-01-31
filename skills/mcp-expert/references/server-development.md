---
title: Server Development
description: MCP server engineering including outcome-oriented tool design, argument flattening, structured outputs, pagination, helpful error strings, and async tasks
tags:
  [
    mcp-server,
    tool-design,
    zod,
    pagination,
    error-handling,
    structured-outputs,
    tasks,
  ]
---

# Server Development

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
