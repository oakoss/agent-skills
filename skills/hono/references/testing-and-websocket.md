---
title: Testing and WebSocket
description: Testing with testClient helper, WebSocket upgrade handler, RPC-mode WebSocket, and JSX streaming with Suspense
tags:
  [
    testClient,
    testing,
    websocket,
    upgradeWebSocket,
    streaming,
    suspense,
    jsxRenderer,
  ]
---

# Testing and WebSocket

## Testing with testClient

The `testClient` helper provides a type-safe way to test Hono applications without starting an HTTP server.

### Basic Test Setup

```ts
import { Hono } from 'hono';
import { testClient } from 'hono/testing';

const app = new Hono()
  .get('/api/hello', (c) => c.json({ message: 'Hello!' }))
  .post('/api/posts', async (c) => {
    const body = await c.req.json();
    return c.json({ id: '1', ...body }, 201);
  });

const client = testClient(app);
```

### Testing GET Requests

```ts
import { describe, it, expect } from 'vitest';

describe('GET /api/hello', () => {
  it('returns hello message', async () => {
    const res = await client.api.hello.$get();
    expect(res.status).toBe(200);

    const data = await res.json();
    expect(data.message).toBe('Hello!');
  });
});
```

### Testing POST Requests

```ts
describe('POST /api/posts', () => {
  it('creates a post', async () => {
    const res = await client.api.posts.$post({
      json: { title: 'Test', body: 'Content' },
    });
    expect(res.status).toBe(201);

    const data = await res.json();
    expect(data.title).toBe('Test');
  });
});
```

### Testing with Path Parameters

```ts
const app = new Hono().get('/users/:id', (c) => {
  return c.json({ id: c.req.param('id') });
});

const client = testClient(app);

const res = await client.users[':id'].$get({
  param: { id: '42' },
});
const data = await res.json();
expect(data.id).toBe('42');
```

### Testing with Query Parameters

```ts
const app = new Hono().get('/search', (c) => {
  return c.json({ q: c.req.query('q') });
});

const client = testClient(app);

const res = await client.search.$get({
  query: { q: 'hono' },
});
```

### Testing with Environment Variables

```ts
type Env = {
  Bindings: { API_KEY: string };
};

const app = new Hono<Env>().get('/config', (c) => {
  return c.json({ hasKey: !!c.env.API_KEY });
});

const client = testClient(app, { API_KEY: 'test-key' });
```

## WebSocket Helper

Hono provides a WebSocket helper through runtime-specific adapters. The helper enables WebSocket upgrades within Hono route handlers.

### Cloudflare Workers WebSocket

```ts
import { Hono } from 'hono';
import { upgradeWebSocket } from 'hono/cloudflare-workers';

const app = new Hono();

app.get(
  '/ws',
  upgradeWebSocket((c) => ({
    onOpen(_event, ws) {
      console.log('Connection opened');
    },
    onMessage(event, ws) {
      ws.send(`Echo: ${event.data}`);
    },
    onClose() {
      console.log('Connection closed');
    },
    onError(event) {
      console.error('WebSocket error:', event);
    },
  })),
);

export default app;
```

### Bun WebSocket

```ts
import { Hono } from 'hono';
import { upgradeWebSocket, websocket } from 'hono/bun';

const app = new Hono();

app.get(
  '/ws',
  upgradeWebSocket((c) => ({
    onMessage(event, ws) {
      ws.send(`Echo: ${event.data}`);
    },
  })),
);

export default {
  fetch: app.fetch,
  websocket,
};
```

When using Bun, export the `websocket` handler alongside `fetch`.

### Deno WebSocket

```ts
import { Hono } from 'hono';
import { upgradeWebSocket } from 'hono/deno';

const app = new Hono();

app.get(
  '/ws',
  upgradeWebSocket((c) => ({
    onMessage(event, ws) {
      ws.send(`Echo: ${event.data}`);
    },
  })),
);

Deno.serve(app.fetch);
```

### WebSocket Event Handlers

| Handler     | Parameters    | Description                  |
| ----------- | ------------- | ---------------------------- |
| `onOpen`    | `(event, ws)` | Connection established       |
| `onMessage` | `(event, ws)` | Message received from client |
| `onClose`   | `(event, ws)` | Connection closed            |
| `onError`   | `(event)`     | WebSocket error occurred     |

### RPC-Mode WebSocket

WebSocket routes support RPC type inference for type-safe client connections.

```ts
const wsApp = app.get(
  '/ws',
  upgradeWebSocket((c) => ({
    onMessage(event, ws) {
      ws.send(event.data);
    },
  })),
);

export type WebSocketApp = typeof wsApp;
```

```ts
import { hc } from 'hono/client';
import { type WebSocketApp } from './server';

const client = hc<WebSocketApp>('http://localhost:8787');
const socket = client.ws.$ws();

socket.addEventListener('open', () => {
  socket.send('Hello from RPC client!');
});
```

## JSX Streaming with Suspense

The JSX Renderer middleware supports streaming responses when the `stream` option is enabled, allowing async components with Suspense boundaries.

### Enable Streaming

```tsx
import { Hono } from 'hono';
import { jsxRenderer } from 'hono/jsx-renderer';
import { Suspense } from 'hono/jsx';

const app = new Hono();

app.use(
  '*',
  jsxRenderer(
    ({ children }) => (
      <html>
        <body>
          <h1>SSR Streaming</h1>
          {children}
        </body>
      </html>
    ),
    { stream: true },
  ),
);
```

### Async Components with Suspense

```tsx
const AsyncUserList = async () => {
  const users = await fetchUsers();
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
};

app.get('/', (c) => {
  return c.render(
    <Suspense fallback={<div>Loading users...</div>}>
      <AsyncUserList />
    </Suspense>,
  );
});
```

The server streams the fallback immediately, then replaces it with the resolved content when the async component completes.
