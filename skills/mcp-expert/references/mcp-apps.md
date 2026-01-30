---
title: MCP Apps
description: Interactive MCP App architecture, UI resource declaration, rendering in host environments, state synchronization, sandboxing, and use cases
tags: [mcp-apps, interactive-ui, json-rpc, sandboxing, state-sync, dashboard]
---

# MCP Apps

## Concept: Outcomes via Interaction

While tools perform operations, MCP Apps provide interactive outcomes. Instead of an agent describing a chart, an MCP App renders a live, zoomable chart that the user can manipulate.

- **Direct Expression**: Users can click buttons, toggle switches, or drag elements to express intent that is hard to put into words
- **Unified Standard**: Successor to earlier MCP-UI proposals, providing a single standard for embedding web-based components

## Architecture

An MCP App consists of a backend (the MCP Server) and a frontend (the UI component):

- **Registry**: The server declares its UI capabilities in the `initialize` handshake
- **Rendering**: The host environment fetches and mounts the component (React/Svelte snippet or sandboxed iframe)
- **Communication**: The UI talks back to the MCP server via standard JSON-RPC notifications and requests

## Server-Side Declaration

```ts
server.resource('dashboard-ui', 'mcp://app/dashboard', async (uri) => {
  return {
    contents: [
      {
        uri: uri.href,
        mimeType: 'application/mcp-app+json',
        text: JSON.stringify({
          component: 'SalesChart',
          props: { data: await getSalesData() },
        }),
      },
    ],
  };
});
```

## Best Practices

- **Sandboxing**: All UI components must run in strictly isolated environments to prevent XSS or host-level access
- **State Sync**: Ensure the UI state is reflected back to the LLM context so the agent remains aware of user interactions
- **Fallback to Text**: Always provide a meaningful text summary if the host environment does not support MCP Apps

## Use Cases

- **Data Visualization**: Live dashboards, charts, and maps
- **Form Orchestration**: Complex multi-step forms with validation
- **Content Creation**: Visual editors for images, videos, or documents
- **Selection Tools**: Visual pickers where clicking is easier than describing
