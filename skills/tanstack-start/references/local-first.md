---
title: Local-First Integration
description: Shape proxy server functions, mixing server-based and local-first data loading, ElectricSQL integration with TanStack Start, and deployment considerations
tags:
  [local-first, electricsql, shape-proxy, createServerFn, sync, offline, hybrid]
---

# Local-First Integration

## Server-Based vs Local-First Data Loading

TanStack Start traditionally loads data via server functions in route loaders. Local-first adds a second path where data syncs continuously from Postgres via ElectricSQL, with the client reading from a local collection instead of fetching on navigation.

| Aspect         | Server-Based (Traditional)                 | Local-First (Electric + TanStack DB)              |
| -------------- | ------------------------------------------ | ------------------------------------------------- |
| Read path      | `createServerFn` → fetch → render          | Electric shape → local collection → render        |
| Write path     | `createServerFn({ method: 'POST' })` → API | `collection.insert()` → `onInsert` handler → API  |
| Navigation     | Loader runs on every route transition      | Data already local, instant render                |
| Offline        | Fails without network                      | Reads work offline, writes queue                  |
| Initial load   | Server renders with data                   | SSR for first paint, Electric syncs after hydrate |
| Cache strategy | TanStack Query `staleTime` / `gcTime`      | Always fresh via continuous sync                  |

## Shape Proxy with createServerFn

Never expose Electric directly to clients. Use a server function as a proxy that validates auth and injects per-user filtering:

```ts
import { createServerFn } from '@tanstack/react-start';
import { getRequestHeader } from '@tanstack/react-start/server';
import { z } from 'zod';

const shapeProxySchema = z.object({
  table: z.string(),
  offset: z.string().optional(),
  handle: z.string().optional(),
  live: z.enum(['true', 'false']).optional(),
  cursor: z.string().optional(),
});

export const getShape = createServerFn()
  .inputValidator(shapeProxySchema)
  .handler(async ({ data }) => {
    const authHeader = getRequestHeader('Authorization');
    const session = await validateSession(authHeader);
    if (!session) {
      throw new Error('Unauthorized');
    }

    const params = new URLSearchParams({
      table: data.table,
      where: `user_id = '${session.userId}'`,
      offset: data.offset ?? '-1',
    });

    if (data.handle) params.set('handle', data.handle);
    if (data.live) params.set('live', data.live);

    const electricUrl = process.env.ELECTRIC_URL ?? 'http://localhost:3000';
    const secret = process.env.ELECTRIC_SECRET;

    const response = await fetch(
      `${electricUrl}/v1/shape?${params.toString()}`,
      {
        headers: secret ? { Authorization: `Bearer ${secret}` } : {},
      },
    );

    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type':
          response.headers.get('Content-Type') ?? 'application/json',
        'electric-handle': response.headers.get('electric-handle') ?? '',
        'electric-offset': response.headers.get('electric-offset') ?? '',
      },
    });
  });
```

## API Route Shape Proxy

For shape streaming, API routes work better than server functions because they support long-polling and SSE natively:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/shapes/$table')({
  server: {
    handlers: {
      GET: async ({ request, params }) => {
        const url = new URL(request.url);
        const session = await getSession(request);
        if (!session) {
          return new Response('Unauthorized', { status: 401 });
        }

        const electricUrl = process.env.ELECTRIC_URL ?? 'http://localhost:3000';
        const secret = process.env.ELECTRIC_SECRET;

        const shapeParams = new URLSearchParams();
        shapeParams.set('table', params.table);
        shapeParams.set('where', `user_id = '${session.userId}'`);

        for (const [key, value] of url.searchParams) {
          if (
            ['offset', 'handle', 'live', 'live_sse', 'columns'].includes(key)
          ) {
            shapeParams.set(key, value);
          }
        }

        const response = await fetch(
          `${electricUrl}/v1/shape?${shapeParams.toString()}`,
          {
            headers: {
              ...(secret && { Authorization: `Bearer ${secret}` }),
            },
          },
        );

        return new Response(response.body, {
          status: response.status,
          headers: {
            'Content-Type':
              response.headers.get('Content-Type') ?? 'application/json',
            'Cache-Control': response.headers.get('Cache-Control') ?? '',
            'electric-handle': response.headers.get('electric-handle') ?? '',
            'electric-offset': response.headers.get('electric-offset') ?? '',
          },
        });
      },
    },
  },
});
```

## Client-Side Collection with Proxy

Point the Electric collection at your proxy endpoint instead of Electric directly:

```ts
import { createCollection } from '@tanstack/react-db';
import { electricCollectionOptions } from '@tanstack/electric-db-collection';

const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: '/api/shapes/todos',
    },
    onInsert: async ({ transaction }) => {
      const newTodo = transaction.mutations[0].modified;
      const result = await createTodo({ data: newTodo });
      return { txid: result.txid };
    },
  }),
);
```

## Write-Path Server Functions

Pair the shape proxy (read path) with server functions for the write path:

```ts
import { createServerFn } from '@tanstack/react-start';
import { z } from 'zod';

const createTodoSchema = z.object({
  title: z.string().min(1).max(200),
  completed: z.boolean().default(false),
});

export const createTodo = createServerFn({ method: 'POST' })
  .inputValidator(createTodoSchema)
  .handler(async ({ data }) => {
    const session = await getAuthSession();
    if (!session) throw new Error('Unauthorized');

    const todo = await db.todos.create({
      data: { ...data, user_id: session.userId },
    });

    return { txid: todo.id, todo };
  });

export const updateTodo = createServerFn({ method: 'POST' })
  .inputValidator(
    z.object({
      id: z.string(),
      changes: z.object({
        title: z.string().optional(),
        completed: z.boolean().optional(),
      }),
    }),
  )
  .handler(async ({ data }) => {
    const session = await getAuthSession();
    if (!session) throw new Error('Unauthorized');

    const todo = await db.todos.update({
      where: { id: data.id, user_id: session.userId },
      data: data.changes,
    });

    return { txid: todo.id };
  });
```

## Mixing Server-Based and Local-First

Not every route needs local-first. Use server functions for admin pages, reports, and low-frequency data. Use Electric collections for collaborative, real-time, or offline-capable views.

```tsx
import { createFileRoute } from '@tanstack/react-router';
import { useLiveQuery } from '@tanstack/react-db';

export const Route = createFileRoute('/dashboard')({
  loader: async () => {
    const stats = await getDashboardStats();
    return { stats };
  },
  component: Dashboard,
});

function Dashboard() {
  const { stats } = Route.useLoaderData();

  const { data: recentTodos } = useLiveQuery((q) =>
    q
      .from({ todos: todoCollection })
      .orderBy(({ todos: t }) => t.created_at, 'desc')
      .limit(10),
  );

  return (
    <div>
      <StatsPanel stats={stats} />
      <RecentActivity todos={recentTodos} />
    </div>
  );
}
```

In this pattern, `stats` loads server-side via the route loader (SSR-friendly, not real-time), while `recentTodos` syncs live via the Electric collection (real-time, works offline after initial sync).

## SSR Considerations

Electric collections sync after hydration, so the first server render has no local data. Handle this with loading states or server-side prefetching:

```tsx
function TodoList() {
  const { data: todos, isLoading } = useLiveQuery((q) =>
    q.from({ todos: todoCollection }),
  );

  if (isLoading) return <TodoListSkeleton />;

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  );
}
```

For critical above-the-fold content, consider loading initial data via the route loader and transitioning to the live collection after hydration.

## Environment Configuration

```ts
import { z } from 'zod';

const envSchema = z.object({
  ELECTRIC_URL: z.string().url().default('http://localhost:3000'),
  ELECTRIC_SECRET: z.string().min(1),
  DATABASE_URL: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

Place this in a `.server.ts` file so environment variables are validated at startup and never leak to the client bundle.

## Deployment Checklist

| Item                 | Details                                                     |
| -------------------- | ----------------------------------------------------------- |
| Electric service     | Running alongside your app (Docker, cloud service, sidecar) |
| `ELECTRIC_URL`       | Internal URL from app to Electric (not exposed to clients)  |
| `ELECTRIC_SECRET`    | Set in production, never `ELECTRIC_INSECURE=true`           |
| Postgres `wal_level` | Must be `logical` for Electric to connect                   |
| Shape proxy endpoint | API route or server function proxying to Electric           |
| HTTPS termination    | TLS at the load balancer, not at Electric                   |
| Cloudflare Workers   | Electric proxy works, but long-poll may hit CPU limits      |
| Node.js / Docker     | Best fit for shape proxy with streaming support             |
