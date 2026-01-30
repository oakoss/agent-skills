---
title: Server Development
description: MCP server engineering including outcome-oriented tool design, argument flattening, pagination, helpful error strings, and development stack
tags: [mcp-server, tool-design, zod, pagination, error-handling, bun, stdio]
---

# Server Development

## Tool Design: Outcomes Over Operations

Do not mirror your REST API as individual tools. Agents struggle with excessive orchestration.

- **Bad**: `get_user_id`, `get_user_email`, `update_user_field` (three calls for one task)
- **Good**: `sync_user_profile` (handles identification and multi-field updates in one call)

Design each tool to accomplish a meaningful outcome rather than a single CRUD operation.

## Argument Flattening and Type Safety

Use flat schemas with strict types to reduce model hallucination:

```ts
const sendAlertSchema = z.object({
  channelId: z.string().describe('Target channel UUID'),
  message: z.string().min(10).describe('Alert content (min 10 chars)'),
  severity: z.enum(['low', 'high', 'critical']),
});
```

Flat schemas with descriptive field annotations produce fewer hallucinated arguments than nested objects.

## Pagination and Resource Management

Never return large datasets in a single tool call. Large responses blow out the LLM context window.

- **Standard Limit**: 20-50 records per call
- **Metadata**: Always include `has_more` and `next_cursor` fields
- **Resource URIs**: For large files, return an `mcp://` URI that the agent can read partially using `resources/read`

## Helpful Error Strings

Agents can self-correct if you give them a path forward:

- **Bad**: `Error: 400 Bad Request`
- **Good**: `Error: 'startDate' must be before 'endDate'. Please adjust your parameters and try again.`

Include the field name, the constraint violated, and a suggested correction.

## Development Stack

- **Runtime**: Bun (fastest startup, native TypeScript support)
- **Transport**: Stdio for local tools, SSE (Server-Sent Events) for remote/cloud tools
- **Validation**: Zod or Valibot for runtime schema enforcement
- **Server Size**: Keep servers focused with 5-15 tools for discoverability and maintenance
