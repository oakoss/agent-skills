---
title: Subscriptions
description: WebSocket subscriptions, Server-Sent Events, observable pattern, and real-time data streaming
tags:
  [subscription, websocket, sse, observable, wsLink, real-time, createWSClient]
---

# Subscriptions

## Defining Subscriptions

Subscriptions use the `subscription` procedure type and return an observable or async iterable:

```ts
import { observable } from '@trpc/server/observable';
import { z } from 'zod';
import { publicProcedure, router } from './trpc';
import { EventEmitter } from 'events';

const ee = new EventEmitter();

export const appRouter = router({
  onPostCreated: publicProcedure.subscription(() => {
    return observable<{ id: string; title: string }>((emit) => {
      const handler = (data: { id: string; title: string }) => {
        emit.next(data);
      };
      ee.on('post.created', handler);
      return () => {
        ee.off('post.created', handler);
      };
    });
  }),

  createPost: publicProcedure
    .input(z.object({ title: z.string() }))
    .mutation(async ({ input }) => {
      const post = await db.post.create({ data: input });
      ee.emit('post.created', post);
      return post;
    }),
});
```

## Subscriptions with Input

```ts
const onMessageInRoom = publicProcedure
  .input(z.object({ roomId: z.string() }))
  .subscription(({ input }) => {
    return observable<Message>((emit) => {
      const handler = (msg: Message) => {
        if (msg.roomId === input.roomId) {
          emit.next(msg);
        }
      };
      ee.on('message', handler);
      return () => {
        ee.off('message', handler);
      };
    });
  });
```

## WebSocket Server Setup

```ts
import { applyWSSHandler } from '@trpc/server/adapters/ws';
import { WebSocketServer } from 'ws';
import { appRouter } from './routers/_app';
import { createContext } from './context';

const wss = new WebSocketServer({ port: 3001 });

const handler = applyWSSHandler({
  wss,
  router: appRouter,
  createContext,
});

process.on('SIGTERM', () => {
  handler.broadcastReconnectNotification();
  wss.close();
});
```

## Client WebSocket Configuration

```ts
import { createTRPCClient, createWSClient, wsLink } from '@trpc/client';
import { type AppRouter } from '../server/routers/_app';

const wsClient = createWSClient({
  url: 'ws://localhost:3001',
});

const client = createTRPCClient<AppRouter>({
  links: [wsLink({ client: wsClient })],
});
```

## Split Link for Mixed Transport

Route subscriptions over WebSocket, everything else over HTTP:

```ts
import {
  createTRPCClient,
  httpBatchLink,
  splitLink,
  wsLink,
  createWSClient,
} from '@trpc/client';

const wsClient = createWSClient({ url: 'ws://localhost:3001' });

const client = createTRPCClient<AppRouter>({
  links: [
    splitLink({
      condition: (op) => op.type === 'subscription',
      true: wsLink({ client: wsClient }),
      false: httpBatchLink({ url: 'http://localhost:3000/trpc' }),
    }),
  ],
});
```

## Subscribing from React

```tsx
function PostFeed() {
  const [posts, setPosts] = useState<Post[]>([]);

  trpc.onPostCreated.useSubscription(undefined, {
    onData(post) {
      setPosts((prev) => [post, ...prev]);
    },
    onError(err) {
      console.error('Subscription error:', err);
    },
  });

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## Server-Sent Events (SSE)

Alternative to WebSocket using HTTP streaming:

```ts
import { httpBatchStreamLink } from '@trpc/client';

const client = createTRPCClient<AppRouter>({
  links: [
    httpBatchStreamLink({
      url: '/api/trpc',
    }),
  ],
});
```

SSE subscriptions work through the standard HTTP adapter without a separate WebSocket server.

## Async Iterable Subscriptions

Modern alternative to the observable pattern:

```ts
const onTick = publicProcedure.subscription(async function* () {
  let i = 0;
  while (true) {
    yield { tick: i++ };
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
});
```

Async iterables automatically clean up when the client disconnects.
