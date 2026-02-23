---
title: Adapter Setup
description: Configuring tRPC with standalone HTTP, Express, Fastify, and Hono adapters
tags:
  [adapter, standalone, express, fastify, hono, createHTTPServer, middleware]
---

# Adapter Setup

## Standalone HTTP Server

Minimal setup with no framework dependency:

```ts
import { createHTTPServer } from '@trpc/server/adapters/standalone';
import { appRouter } from './routers/_app';
import { createContext } from './context';

const server = createHTTPServer({
  router: appRouter,
  createContext,
  onError({ error, path }) {
    console.error(`Error on ${path}:`, error.message);
  },
});

server.listen(3000);
```

### With CORS

```ts
import { createHTTPServer } from '@trpc/server/adapters/standalone';
import cors from 'cors';

const server = createHTTPServer({
  middleware: cors(),
  router: appRouter,
  createContext,
});
```

## Express Adapter

```ts
import express from 'express';
import * as trpcExpress from '@trpc/server/adapters/express';
import { appRouter } from './routers/_app';

function createContext({ req, res }: trpcExpress.CreateExpressContextOptions) {
  return {
    req,
    res,
    session: req.session,
  };
}

const app = express();

app.use(
  '/trpc',
  trpcExpress.createExpressMiddleware({
    router: appRouter,
    createContext,
    onError({ error, path }) {
      console.error(`Error on ${path}:`, error.message);
    },
  }),
);

app.listen(3000);
```

## Fastify Adapter

```ts
import fastify from 'fastify';
import {
  fastifyTRPCPlugin,
  type FastifyTRPCPluginOptions,
} from '@trpc/server/adapters/fastify';
import { appRouter, type AppRouter } from './routers/_app';
import { createContext } from './context';

const server = fastify({ maxParamLength: 5000 });

server.register(fastifyTRPCPlugin, {
  prefix: '/trpc',
  trpcOptions: {
    router: appRouter,
    createContext,
    onError({ path, error }) {
      console.error(`Error on ${path}:`, error.message);
    },
  } satisfies FastifyTRPCPluginOptions<AppRouter>['trpcOptions'],
});

async function start() {
  try {
    await server.listen({ port: 3000 });
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
}

start();
```

## Hono Adapter

```ts
import { Hono } from 'hono';
import { trpcServer } from '@hono/trpc-server';
import { appRouter } from './routers/_app';

const app = new Hono();

app.use(
  '/trpc/*',
  trpcServer({
    router: appRouter,
    createContext: (_opts, c) => ({
      req: c.req,
    }),
  }),
);

export default app;
```

## Next.js App Router

```ts
// src/app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from '~/server/routers/_app';
import { createContext } from '~/server/context';

function handler(req: Request) {
  return fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext,
  });
}

export { handler as GET, handler as POST };
```

## Fetch Adapter (Generic)

Works with any runtime supporting the Web Fetch API (Cloudflare Workers, Deno, Bun):

```ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from './routers/_app';

export default {
  async fetch(request: Request): Promise<Response> {
    return fetchRequestHandler({
      endpoint: '/trpc',
      req: request,
      router: appRouter,
      createContext: () => ({}),
    });
  },
};
```

## Common Configuration

All adapters share these options:

| Option             | Description                                             |
| ------------------ | ------------------------------------------------------- |
| `router`           | The root `AppRouter` instance                           |
| `createContext`    | Factory function creating per-request context           |
| `onError`          | Error callback with `{ error, path, type, ctx, input }` |
| `batching.enabled` | Enable/disable request batching (default: true)         |
| `responseMeta`     | Customize response headers and status codes             |
