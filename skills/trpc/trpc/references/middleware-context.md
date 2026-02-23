---
title: Middleware and Context
description: Request context creation, middleware patterns, context extension, standalone middleware, and procedure composition
tags:
  [middleware, context, createContext, use, next, standalone-middleware, auth]
---

# Middleware and Context

## Context Creation

Context is created per-request and passed to all procedures:

```ts
import { initTRPC } from '@trpc/server';
import { type CreateExpressContextOptions } from '@trpc/server/adapters/express';

export async function createContext({ req, res }: CreateExpressContextOptions) {
  const session = await getSession(req.headers.authorization);
  return {
    session,
    db,
  };
}

type Context = Awaited<ReturnType<typeof createContext>>;

const t = initTRPC.context<Context>().create();
```

## Basic Middleware

Middleware runs before the procedure and can modify context:

```ts
const logger = t.middleware(async ({ path, type, next }) => {
  const start = Date.now();
  const result = await next();
  const durationMs = Date.now() - start;
  console.log(`${type} ${path} - ${durationMs}ms`);
  return result;
});

export const loggedProcedure = t.procedure.use(logger);
```

## Auth Middleware with Context Extension

Extend context by returning new values from `next({ ctx })`:

```ts
const isAuthed = t.middleware(async ({ ctx, next }) => {
  if (!ctx.session?.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({
    ctx: {
      user: ctx.session.user,
    },
  });
});

export const protectedProcedure = t.procedure.use(isAuthed);
```

Downstream procedures receive `ctx.user` with proper types.

## Chaining Middleware

Middleware chains execute in order:

```ts
const isAdmin = t.middleware(async ({ ctx, next }) => {
  if (ctx.user.role !== 'admin') {
    throw new TRPCError({ code: 'FORBIDDEN', message: 'Admin only' });
  }
  return next();
});

export const adminProcedure = t.procedure.use(isAuthed).use(isAdmin);
```

## Standalone Middleware

Reusable middleware with explicit type constraints:

```ts
import { experimental_standaloneMiddleware, TRPCError } from '@trpc/server';
import { z } from 'zod';

const projectAccessMiddleware = experimental_standaloneMiddleware<{
  ctx: { allowedProjects: string[] };
  input: { projectId: string };
}>().create(({ ctx, input, next }) => {
  if (!ctx.allowedProjects.includes(input.projectId)) {
    throw new TRPCError({ code: 'FORBIDDEN', message: 'No project access' });
  }
  return next();
});

const projectProcedure = protectedProcedure
  .input(z.object({ projectId: z.string() }))
  .use(projectAccessMiddleware);
```

Standalone middleware validates that the procedure context and input satisfy its constraints at the type level.

## Rate Limiting Middleware

```ts
import { TRPCError } from '@trpc/server';

const rateLimit = t.middleware(async ({ ctx, path, next }) => {
  const key = `${ctx.user.id}:${path}`;
  const allowed = await rateLimiter.check(key);
  if (!allowed) {
    throw new TRPCError({
      code: 'TOO_MANY_REQUESTS',
      message: 'Rate limit exceeded',
    });
  }
  return next();
});
```

## Timing Middleware with Headers

```ts
const timing = t.middleware(async ({ next }) => {
  const start = Date.now();
  const result = await next();
  result.ok &&
    result.ctx.resHeaders?.set(
      'Server-Timing',
      `proc;dur=${Date.now() - start}`,
    );
  return result;
});
```

## Organization Pattern

Keep middleware in dedicated files and export reusable procedure bases:

```ts
// src/server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { type Context } from './context';

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const createCallerFactory = t.createCallerFactory;

const isAuthed = t.middleware(async ({ ctx, next }) => {
  if (!ctx.session?.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({ ctx: { user: ctx.session.user } });
});

export const protectedProcedure = t.procedure.use(isAuthed);
```
