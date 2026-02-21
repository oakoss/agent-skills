---
title: API Routes
description: Server routes with createFileRoute server handlers, REST patterns, route-level middleware, webhook handlers, health checks, and when to use API routes vs server functions
tags:
  [
    API,
    routes,
    REST,
    server,
    handlers,
    middleware,
    CRUD,
    webhook,
    health-check,
    GET,
    POST,
    PATCH,
    DELETE,
  ]
---

# API Routes

## Basic Server Route

Server routes use `createFileRoute` with a `server` property containing `handlers`:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/hello')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return new Response('Hello, World!');
      },
    },
  },
});
```

## REST API with Multiple Methods

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/users')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const page = parseInt(url.searchParams.get('page') || '1');
        const limit = parseInt(url.searchParams.get('limit') || '10');

        const users = await db.users.findMany({
          skip: (page - 1) * limit,
          take: limit,
        });
        const total = await db.users.count();

        return Response.json({
          data: users,
          pagination: { page, limit, total },
        });
      },
      POST: async ({ request }) => {
        const body = await request.json();
        const parsed = createUserSchema.safeParse(body);
        if (!parsed.success) {
          return Response.json(
            { error: parsed.error.flatten() },
            { status: 400 },
          );
        }
        const user = await db.users.create({ data: parsed.data });
        return Response.json(user, { status: 201 });
      },
    },
  },
});
```

## RESTful Resource with PATCH and DELETE

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/posts/$id')({
  server: {
    handlers: {
      GET: async ({ params }) => {
        const post = await db.posts.findUnique({ where: { id: params.id } });
        if (!post)
          return Response.json({ error: 'Not found' }, { status: 404 });
        return Response.json(post);
      },
      PATCH: async ({ params, request, context }) => {
        if (!context.user) {
          return Response.json({ error: 'Unauthorized' }, { status: 401 });
        }
        const body = await request.json();
        const parsed = updatePostSchema.safeParse(body);
        if (!parsed.success) {
          return Response.json(
            { error: parsed.error.flatten() },
            { status: 400 },
          );
        }
        const updated = await db.posts.update({
          where: { id: params.id, authorId: context.user.id },
          data: parsed.data,
        });
        if (!updated) {
          return Response.json(
            { error: 'Not found or forbidden' },
            { status: 404 },
          );
        }
        return Response.json(updated);
      },
      DELETE: async ({ params, context }) => {
        if (!context.user) {
          return Response.json({ error: 'Unauthorized' }, { status: 401 });
        }
        await db.posts.delete({
          where: { id: params.id, authorId: context.user.id },
        });
        return new Response(null, { status: 204 });
      },
    },
  },
});
```

## Route-Level Middleware

Apply middleware to all handlers on a route, or per-handler:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/posts')({
  server: {
    middleware: [authMiddleware, loggerMiddleware],
    handlers: {
      GET: async ({ request }) => {
        return Response.json(await db.posts.findMany());
      },
      POST: {
        middleware: [validationMiddleware],
        handler: async ({ request }) => {
          const body = await request.json();
          return Response.json(await db.posts.create({ data: body }), {
            status: 201,
          });
        },
      },
    },
  },
});
```

## Factory Form with `createHandlers`

For per-handler middleware, use the `createHandlers` factory instead of the plain object form:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/posts')({
  server: {
    middleware: [authMiddleware],
    handlers: ({ createHandlers }) =>
      createHandlers({
        GET: {
          handler: async ({ request }) => {
            return Response.json(await db.posts.findMany());
          },
        },
        POST: {
          middleware: [validationMiddleware],
          handler: async ({ request }) => {
            const body = await request.json();
            return Response.json(await db.posts.create({ data: body }), {
              status: 201,
            });
          },
        },
      }),
  },
});
```

Route-level middleware runs first for all methods, then per-handler middleware runs before that specific handler.

## Webhook Handler

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/webhooks/stripe')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.text();
        const signature = request.headers.get('stripe-signature');
        if (!signature) {
          return Response.json({ error: 'Missing signature' }, { status: 400 });
        }

        try {
          const event = stripe.webhooks.constructEvent(
            body,
            signature,
            process.env.STRIPE_WEBHOOK_SECRET!,
          );

          switch (event.type) {
            case 'checkout.session.completed':
              await handleCheckoutComplete(event.data.object);
              break;
            case 'customer.subscription.updated':
              await handleSubscriptionUpdate(event.data.object);
              break;
          }

          return Response.json({ received: true });
        } catch (error) {
          console.error('Webhook error:', error);
          return Response.json({ error: 'Webhook failed' }, { status: 400 });
        }
      },
    },
  },
});
```

## Health Check

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/health')({
  server: {
    handlers: {
      GET: async () => {
        try {
          await db.$queryRaw`SELECT 1`;
          return Response.json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
          });
        } catch (error) {
          return Response.json(
            {
              status: 'unhealthy',
              error: error instanceof Error ? error.message : 'Unknown',
            },
            { status: 503 },
          );
        }
      },
    },
  },
});
```

## Handler Context

Each handler receives:

| Property  | Type      | Description                                         |
| --------- | --------- | --------------------------------------------------- |
| `request` | `Request` | Standard Web Fetch API Request object               |
| `params`  | `object`  | Dynamic path parameters (e.g., `$id` → `params.id`) |
| `context` | `object`  | Data from middleware (e.g., `context.user`)         |

## When to Use Server Routes vs Server Functions

| Use Case         | Pattern                                  |
| ---------------- | ---------------------------------------- |
| RPC-style calls  | `createServerFn` (server functions)      |
| REST API routes  | `createFileRoute` with `server.handlers` |
| Webhooks         | `createFileRoute` with `server.handlers` |
| Form submissions | `createServerFn` (easier integration)    |
| Route loaders    | `createServerFn` + loader                |
