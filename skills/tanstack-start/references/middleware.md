---
title: Middleware
description: Middleware composition patterns including logging, auth, admin chains, function-level middleware with validation, route-level middleware, global request middleware, and rate limiting
tags:
  [
    middleware,
    createMiddleware,
    composition,
    auth,
    logging,
    admin,
    function-level,
    route-level,
    global,
    requestMiddleware,
    context,
    rate-limiting,
  ]
---

# Middleware

## Basic Middleware

```ts
import { createMiddleware } from '@tanstack/react-start';

export const logMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const start = Date.now();
    const requestId = crypto.randomUUID();

    console.log(`[${requestId}] ${request.method} ${request.url}`);

    try {
      const result = await next({ context: { requestId } });
      console.log(`[${requestId}] Completed in ${Date.now() - start}ms`);
      return result;
    } catch (error) {
      console.error(`[${requestId}] Error:`, error);
      throw error;
    }
  },
);

export const authMiddleware = createMiddleware().server(async ({ next }) => {
  const session = await getSession();
  return next({
    context: { session, user: session?.user ?? null },
  });
});
```

## Middleware Composition

Chain middleware using `.middleware([dep])`:

```ts
export const requireAuthMiddleware = createMiddleware()
  .middleware([authMiddleware])
  .server(async ({ next, context }) => {
    if (!context.user) {
      throw redirect({ to: '/login' });
    }
    return next({ context: { user: context.user } });
  });

export const adminMiddleware = createMiddleware()
  .middleware([requireAuthMiddleware])
  .server(async ({ next, context }) => {
    if (context.user.role !== 'admin') {
      throw new Error('Admin access required');
    }
    return next({ context: { isAdmin: true } });
  });
```

Use in server functions:

```ts
const adminAction = createServerFn({ method: 'POST' })
  .middleware([adminMiddleware])
  .handler(async ({ context }) => {
    return await performAdminAction(context.user.id);
  });
```

## Function-Level Middleware with Validation

Use `type: 'function'` for middleware that validates input specific to server functions:

```ts
const workspaceMiddleware = createMiddleware({ type: 'function' })
  .inputValidator(z.object({ workspaceId: z.string() }))
  .server(async ({ next, data }) => {
    const workspace = await db.workspaces.findUnique({
      where: { id: data.workspaceId },
    });
    if (!workspace) throw new Error('Workspace not found');
    return next({ context: { workspace } });
  });

const getWorkspaceData = createServerFn()
  .middleware([authMiddleware, workspaceMiddleware])
  .handler(async ({ context }) => {
    return await fetchWorkspaceData(context.workspace.id);
  });
```

## Route-Level Middleware

Apply middleware to server route handlers:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/posts')({
  server: {
    middleware: [authMiddleware, logMiddleware],
    handlers: {
      GET: async ({ request }) => {
        return Response.json(await db.posts.findMany());
      },
      POST: {
        middleware: [validationMiddleware],
        handler: async ({ request }) => {
          const body = await request.json();
          return Response.json(await db.posts.create({ data: body }));
        },
      },
    },
  },
});
```

Route-level `middleware` applies to all handlers. Per-handler `middleware` runs after route-level middleware, only for that method.

## Global Middleware

Apply middleware to all server functions in `src/start.ts`:

```ts
import { createStart } from '@tanstack/react-start';

export default createStart({
  requestMiddleware: [logMiddleware, authMiddleware],
});
```

## Rate Limiting Middleware

```ts
const rateLimitStore = new Map<string, { count: number; resetAt: number }>();

export const rateLimitMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
    const now = Date.now();
    const windowMs = 60 * 1000;
    const maxRequests = 100;

    let record = rateLimitStore.get(ip);

    if (!record || record.resetAt < now) {
      record = { count: 0, resetAt: now + windowMs };
    }

    record.count++;
    rateLimitStore.set(ip, record);

    if (record.count > maxRequests) {
      throw new Response('Too Many Requests', { status: 429 });
    }

    return next();
  },
);
```

## Middleware Execution Order

Middleware forms a chain where each wraps the next:

```text
Request -> Middleware 1 -> Middleware 2 -> Handler -> Middleware 2 -> Middleware 1 -> Response
```

The first middleware in the array wraps the entire chain. Each middleware calls `next()` to proceed to the next middleware or the handler. Code before `await next()` runs on the way in, code after runs on the way out.
