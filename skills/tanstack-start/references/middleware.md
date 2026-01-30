---
title: Middleware
description: Middleware composition patterns including logging, auth, admin chains, function-level middleware with validation, and global request middleware
tags:
  [
    middleware,
    createMiddleware,
    composition,
    auth,
    logging,
    admin,
    function-level,
    global,
    requestMiddleware,
    context,
  ]
---

# Middleware

## Basic Middleware

```ts
import { createMiddleware } from '@tanstack/react-start';

export const logMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const start = Date.now();
    const result = await next();
    console.log(`${request.method} ${request.url} - ${Date.now() - start}ms`);
    return result;
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

## Function-Level Middleware with Validation

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
