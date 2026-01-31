---
title: MSW Handlers
description: MSW v2 request handlers, HTTP and GraphQL interceptors, response resolvers, server setup, and per-test overrides
tags:
  [msw, mock-service-worker, http, graphql, handler, server, interceptor, mock]
---

# MSW Handlers

## Server Setup

Create a shared MSW server for Node.js tests:

```ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

Wire the server into your test setup file (referenced by `vitest.config.ts` `setupFiles`):

```ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

The `onUnhandledRequest: 'error'` option throws when a request has no matching handler, preventing silent test gaps.

## Vitest Configuration

Register the setup file in your Vitest config:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./src/mocks/setup.ts'],
  },
});
```

## HTTP Handlers

MSW v2 uses the `http` namespace (replacing `rest` from v1):

```ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
    ]);
  }),

  http.get('/api/users/:id', ({ params }) => {
    const { id } = params;
    return HttpResponse.json({ id, name: 'Alice' });
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '3', ...body }, { status: 201 });
  }),

  http.patch('/api/users/:id', async ({ params, request }) => {
    const { id } = params;
    const updates = await request.json();
    return HttpResponse.json({ id, ...updates });
  }),

  http.delete('/api/users/:id', () => {
    return new HttpResponse(null, { status: 204 });
  }),
];
```

## Response Resolver Parameters

The resolver receives a single object with these properties:

```ts
http.post('/api/items', async ({ request, params, cookies }) => {
  const url = new URL(request.url);
  const page = url.searchParams.get('page');

  const body = await request.json();

  const sessionId = cookies.session_id;

  return HttpResponse.json({ created: true });
});
```

| Property  | Type      | Description                          |
| --------- | --------- | ------------------------------------ |
| `request` | `Request` | Standard Fetch API Request object    |
| `params`  | `object`  | Path parameters from `:param` syntax |
| `cookies` | `object`  | Parsed request cookies               |

## GraphQL Handlers

Intercept GraphQL operations by name:

```ts
import { graphql, HttpResponse } from 'msw';

export const graphqlHandlers = [
  graphql.query('GetUsers', () => {
    return HttpResponse.json({
      data: {
        users: [
          { id: '1', name: 'Alice' },
          { id: '2', name: 'Bob' },
        ],
      },
    });
  }),

  graphql.mutation('CreateUser', ({ variables }) => {
    const { name } = variables;
    return HttpResponse.json({
      data: {
        createUser: { id: '3', name },
      },
    });
  }),
];
```

Scope handlers to specific GraphQL endpoints with `graphql.link()`:

```ts
const github = graphql.link('https://api.github.com/graphql');
const stripe = graphql.link('https://api.stripe.com/graphql');

export const handlers = [
  github.query('GetRepos', () => {
    return HttpResponse.json({
      data: { repos: [{ name: 'my-repo' }] },
    });
  }),

  stripe.query('GetCharges', () => {
    return HttpResponse.json({
      data: { charges: [] },
    });
  }),
];
```

## Per-Test Handler Overrides

Override default handlers for specific test scenarios:

```ts
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

it('handles server error', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json(
        { error: 'Internal Server Error' },
        { status: 500 },
      );
    }),
  );

  const response = await fetch('/api/users');
  expect(response.status).toBe(500);
});
```

Overrides are automatically cleared by `server.resetHandlers()` in `afterEach`.

## One-Time Handlers

Handlers that auto-remove after the first match:

```ts
server.use(
  http.get(
    '/api/users',
    () => {
      return HttpResponse.json({ users: [] }, { status: 200 });
    },
    { once: true },
  ),
);
```

Useful for testing retry logic where the first request fails but the second succeeds:

```ts
it('retries on failure', async () => {
  server.use(
    http.get(
      '/api/data',
      () => {
        return HttpResponse.error();
      },
      { once: true },
    ),
  );

  // First request triggers the one-time error handler
  // Second request falls through to the default success handler
});
```

## Network Error Simulation

```ts
http.get('/api/data', () => {
  return HttpResponse.error();
});
```

`HttpResponse.error()` simulates a network-level failure (connection refused, DNS failure). The request never completes.

## Response Delay

```ts
import { http, HttpResponse, delay } from 'msw';

http.get('/api/slow', async () => {
  await delay(2000);
  return HttpResponse.json({ data: 'slow response' });
});

// Use 'infinite' delay for timeout testing
http.get('/api/timeout', async () => {
  await delay('infinite');
  return HttpResponse.json({ data: 'never reached' });
});
```

## Custom Response Headers

```ts
http.get('/api/data', () => {
  return HttpResponse.json(
    { items: [] },
    {
      headers: {
        'X-Total-Count': '42',
        'Cache-Control': 'no-cache',
      },
    },
  );
});
```

## TypeScript Type Safety

Use generic arguments for type-safe handlers:

```ts
import { http, HttpResponse } from 'msw';

type UserParams = { id: string };
type CreateUserBody = { name: string; email: string };
type UserResponse = { id: string; name: string; email: string };

export const handlers = [
  http.get<UserParams, never, UserResponse>('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Alice',
      email: 'alice@example.com',
    });
  }),

  http.post<never, CreateUserBody, UserResponse>(
    '/api/users',
    async ({ request }) => {
      const body = await request.json();
      return HttpResponse.json({
        id: '1',
        name: body.name,
        email: body.email,
      });
    },
  ),
];
```

## Handler Organization

Structure handlers by resource for maintainability:

```ts
import { userHandlers } from './handlers/users';
import { postHandlers } from './handlers/posts';
import { authHandlers } from './handlers/auth';

export const handlers = [...authHandlers, ...userHandlers, ...postHandlers];
```

Keep default handlers representing the happy path. Override with `server.use()` for error and edge-case tests.

## Life-Cycle Events

Observe network traffic without affecting responses:

```ts
server.events.on('request:start', ({ request }) => {
  console.log('Outgoing:', request.method, request.url);
});

server.events.on('response:mocked', ({ request, response }) => {
  console.log('Mocked:', request.url, response.status);
});
```

Useful for debugging which requests are intercepted during test runs.
