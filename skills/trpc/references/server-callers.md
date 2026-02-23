---
title: Server-Side Callers and Vanilla Client
description: Using createCallerFactory for server-side calls, vanilla tRPC client without React, and link configuration
tags:
  [
    createCallerFactory,
    createCaller,
    createTRPCClient,
    vanilla,
    links,
    httpBatchLink,
    server-side,
  ]
---

# Server-Side Callers and Vanilla Client

## createCallerFactory

The recommended way to call procedures from the server:

```ts
// src/server/trpc.ts
import { initTRPC } from '@trpc/server';

const t = initTRPC.context<Context>().create();

export const createCallerFactory = t.createCallerFactory;
```

```ts
// src/server/routers/_app.ts
import { createCallerFactory, router } from '../trpc';
import { userRouter } from './user';
import { postRouter } from './post';

export const appRouter = router({
  user: userRouter,
  post: postRouter,
});

export const createCaller = createCallerFactory(appRouter);
export type AppRouter = typeof appRouter;
```

## Using Server-Side Callers

```ts
import { createContext } from '../context';
import { createCaller } from '../routers/_app';

async function handleWebhook(req: Request) {
  const ctx = await createContext({ req });
  const caller = createCaller(ctx);

  const user = await caller.user.byId('user-123');
  await caller.post.create({ title: 'From webhook', authorId: user.id });
}
```

## Next.js Server Component Usage

```tsx
import { createCaller } from '~/server/routers/_app';
import { createContext } from '~/server/context';

export default async function UsersPage() {
  const ctx = await createContext();
  const caller = createCaller(ctx);
  const users = await caller.user.list();

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

## Error Handling with Callers

```ts
import { TRPCError } from '@trpc/server';
import { getHTTPStatusCodeFromError } from '@trpc/server/http';

try {
  const result = await caller.user.byId('nonexistent');
} catch (cause) {
  if (cause instanceof TRPCError) {
    const httpCode = getHTTPStatusCodeFromError(cause);
    return new Response(cause.message, { status: httpCode });
  }
  return new Response('Internal error', { status: 500 });
}
```

## Vanilla Client (No React)

For non-React environments or Node.js scripts:

```ts
import { createTRPCClient, httpBatchLink } from '@trpc/client';
import { type AppRouter } from '../server/routers/_app';

const client = createTRPCClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'http://localhost:3000/api/trpc',
    }),
  ],
});

const users = await client.user.list.query();
const newUser = await client.user.create.mutate({
  name: 'Alice',
  email: 'alice@example.com',
});
```

## Custom Links

Links form a chain that transforms requests and responses:

```ts
import { createTRPCClient, httpBatchLink, loggerLink } from '@trpc/client';

const client = createTRPCClient<AppRouter>({
  links: [
    loggerLink({
      enabled: (opts) =>
        (process.env.NODE_ENV === 'development' &&
          typeof window !== 'undefined') ||
        (opts.direction === 'down' && opts.result instanceof Error),
    }),
    httpBatchLink({
      url: '/api/trpc',
      headers() {
        return {
          authorization: `Bearer ${getToken()}`,
        };
      },
    }),
  ],
});
```

## Split Link

Route different procedure types to different transports:

```ts
import {
  createTRPCClient,
  httpBatchLink,
  splitLink,
  wsLink,
  createWSClient,
} from '@trpc/client';

const wsClient = createWSClient({
  url: 'ws://localhost:3001',
});

const client = createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => op.type === 'subscription',
      true: wsLink({ client: wsClient }),
      false: httpBatchLink({ url: '/api/trpc' }),
    }),
  ],
});
```

## Data Transformers

Use superjson to serialize Dates, Maps, Sets, and other non-JSON types:

```ts
// Server
import superjson from 'superjson';

const t = initTRPC.create({
  transformer: superjson,
});
```

```ts
// Client
import superjson from 'superjson';

const client = createTRPCClient<AppRouter>({
  links: [
    httpBatchLink({
      url: '/api/trpc',
      transformer: superjson,
    }),
  ],
});
```

Both server and client must use the same transformer.
