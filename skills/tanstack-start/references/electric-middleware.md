---
title: Electric Middleware
description: Middleware patterns for ElectricSQL auth in TanStack Start — reusable auth middleware, shape proxy authorization, global middleware config, middleware execution order, and sendContext
tags:
  [
    middleware,
    electric,
    electricsql,
    auth,
    createMiddleware,
    shape-proxy,
    requestMiddleware,
    functionMiddleware,
    sendContext,
  ]
---

# Electric Middleware

## Reusable Auth Middleware

Base auth middleware that extracts and validates the session:

```ts
import { createMiddleware } from '@tanstack/react-start';
import { getRequestHeader } from '@tanstack/react-start/server';

export const authMiddleware = createMiddleware().server(async ({ next }) => {
  const authHeader = getRequestHeader('Authorization');
  const session = await validateSession(authHeader);

  return next({
    context: {
      session,
      user: session?.user ?? null,
    },
  });
});
```

## Require Auth Middleware

Compose on `authMiddleware` to enforce authentication:

```ts
import { redirect } from '@tanstack/react-router';

export const requireAuthMiddleware = createMiddleware()
  .middleware([authMiddleware])
  .server(async ({ next, context }) => {
    if (!context.user) {
      throw redirect({ to: '/login' });
    }
    return next({
      context: { user: context.user },
    });
  });
```

## Shape Proxy with Auth Middleware

Use middleware in server functions that proxy Electric shape requests:

```ts
import { createServerFn } from '@tanstack/react-start';
import { z } from 'zod';

const shapeProxySchema = z.object({
  table: z.string(),
  offset: z.string().optional(),
  handle: z.string().optional(),
  live: z.enum(['true', 'false']).optional(),
  columns: z.string().optional(),
});

export const getShape = createServerFn()
  .middleware([requireAuthMiddleware])
  .inputValidator(shapeProxySchema)
  .handler(async ({ data, context }) => {
    const params = new URLSearchParams({
      table: data.table,
      where: `user_id = '${context.user.id}'`,
      offset: data.offset ?? '-1',
    });

    if (data.handle) params.set('handle', data.handle);
    if (data.live) params.set('live', data.live);
    if (data.columns) params.set('columns', data.columns);

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

## Centralizing Shape Auth Across Server Functions

Multiple shape proxies can share the same middleware chain:

```ts
export const getTodoShape = createServerFn()
  .middleware([requireAuthMiddleware])
  .inputValidator(z.object({ offset: z.string().optional() }))
  .handler(async ({ data, context }) => {
    return proxyShape({
      table: 'todos',
      where: `user_id = '${context.user.id}'`,
      offset: data.offset,
    });
  });

export const getNoteShape = createServerFn()
  .middleware([requireAuthMiddleware])
  .inputValidator(z.object({ offset: z.string().optional() }))
  .handler(async ({ data, context }) => {
    return proxyShape({
      table: 'notes',
      where: `user_id = '${context.user.id}'`,
      offset: data.offset,
    });
  });

async function proxyShape(opts: {
  table: string;
  where: string;
  offset?: string;
}) {
  const electricUrl = process.env.ELECTRIC_URL ?? 'http://localhost:3000';
  const secret = process.env.ELECTRIC_SECRET;

  const params = new URLSearchParams({
    table: opts.table,
    where: opts.where,
    offset: opts.offset ?? '-1',
  });

  const response = await fetch(`${electricUrl}/v1/shape?${params.toString()}`, {
    headers: secret ? { Authorization: `Bearer ${secret}` } : {},
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      'Content-Type':
        response.headers.get('Content-Type') ?? 'application/json',
      'electric-handle': response.headers.get('electric-handle') ?? '',
      'electric-offset': response.headers.get('electric-offset') ?? '',
    },
  });
}
```

## Write Server Functions with Auth

Pair shape proxies (read path) with authenticated write functions:

```ts
export const createTodo = createServerFn({ method: 'POST' })
  .middleware([requireAuthMiddleware])
  .inputValidator(z.object({ title: z.string().min(1).max(200) }))
  .handler(async ({ data, context }) => {
    const result = await db.transaction(async (tx) => {
      const [todo] = await tx
        .insert(todos)
        .values({ title: data.title, userId: context.user.id })
        .returning();

      const [{ txid }] = await tx.execute<{ txid: string }>(
        sql`SELECT pg_current_xact_id()::text AS txid`,
      );

      return { todo, txid };
    });

    return result;
  });
```

## Global Middleware Configuration

Apply middleware to all requests or all server functions in `src/start.ts`:

```ts
import { createStart } from '@tanstack/react-start';
import { logMiddleware, authMiddleware } from './middleware';

export default createStart({
  requestMiddleware: [logMiddleware, authMiddleware],
});
```

### requestMiddleware vs functionMiddleware

| Type                 | Scope                            | Use For                         |
| -------------------- | -------------------------------- | ------------------------------- |
| `requestMiddleware`  | All incoming HTTP requests       | Logging, CORS, rate limiting    |
| `functionMiddleware` | All `createServerFn` invocations | Auth context, tenant resolution |

```ts
export default createStart({
  requestMiddleware: [logMiddleware],
  functionMiddleware: [authMiddleware],
});
```

`requestMiddleware` runs on every request including static assets and API routes. `functionMiddleware` runs only when a server function is invoked.

## Middleware Execution Order

Middleware executes dependency-first. When a middleware declares `.middleware([dep])`, the dependency runs before it:

```text
Request
  → logMiddleware (global requestMiddleware)
  → authMiddleware (global functionMiddleware or composed dep)
  → requireAuthMiddleware (depends on authMiddleware)
  → handler
  → requireAuthMiddleware (after next())
  → authMiddleware (after next())
  → logMiddleware (after next())
Response
```

Each middleware wraps the next. Code before `await next()` runs on the way in, code after runs on the way out.

## sendContext for Server-to-Client Data

Pass context data from middleware to the client via `sendContext`:

```ts
export const authMiddleware = createMiddleware().server(async ({ next }) => {
  const session = await getSession();
  return next({
    context: { user: session?.user ?? null },
    sendContext: { isAuthenticated: !!session?.user },
  });
});
```

Access `sendContext` values in the client after the server function returns:

```ts
const getUser = createServerFn()
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    return context.user;
  });

const result = await getUser();
```

`sendContext` is serialized and sent to the client. Only include serializable, non-sensitive data. Never put tokens, secrets, or database connections in `sendContext`.

## Function-Level Middleware for Shape Validation

Use `type: 'function'` middleware to validate shape-specific input:

```ts
const shapeAuthMiddleware = createMiddleware({ type: 'function' })
  .middleware([requireAuthMiddleware])
  .inputValidator(z.object({ table: z.string() }))
  .server(async ({ next, data, context }) => {
    const allowedTables = ['todos', 'notes', 'tags'];
    if (!allowedTables.includes(data.table)) {
      throw new Error(`Table '${data.table}' is not allowed`);
    }
    return next({
      context: { allowedTable: data.table, userId: context.user.id },
    });
  });

export const getShapeByTable = createServerFn()
  .middleware([shapeAuthMiddleware])
  .handler(async ({ context }) => {
    return proxyShape({
      table: context.allowedTable,
      where: `user_id = '${context.userId}'`,
    });
  });
```
