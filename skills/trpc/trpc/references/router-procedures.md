---
title: Router and Procedures
description: Defining routers, queries, mutations, input validation, output validation, and nested routers
tags:
  [
    router,
    procedure,
    query,
    mutation,
    input,
    output,
    zod,
    nested-router,
    mergeRouters,
  ]
---

# Router and Procedures

## Initialization

```ts
import { initTRPC } from '@trpc/server';

const t = initTRPC.create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const createCallerFactory = t.createCallerFactory;
```

## Basic Router

```ts
import { z } from 'zod';
import { publicProcedure, router } from './trpc';

export const appRouter = router({
  userList: publicProcedure.query(async () => {
    return db.user.findMany();
  }),

  userById: publicProcedure.input(z.string()).query(async ({ input }) => {
    return db.user.findById(input);
  }),

  userCreate: publicProcedure
    .input(z.object({ name: z.string().min(1), email: z.string().email() }))
    .mutation(async ({ input }) => {
      return db.user.create(input);
    }),
});

export type AppRouter = typeof appRouter;
```

## Input Validation

Procedures accept any Zod schema (or Valibot/ArkType) via `.input()`:

```ts
const createPost = publicProcedure
  .input(
    z.object({
      title: z.string().min(1).max(200),
      content: z.string(),
      published: z.boolean().default(false),
      tags: z.array(z.string()).optional(),
    }),
  )
  .mutation(async ({ input }) => {
    return db.post.create({ data: input });
  });
```

Multiple `.input()` calls merge schemas (intersection):

```ts
const updatePost = publicProcedure
  .input(z.object({ id: z.string() }))
  .input(
    z.object({ title: z.string().optional(), content: z.string().optional() }),
  )
  .mutation(async ({ input }) => {
    return db.post.update({ where: { id: input.id }, data: input });
  });
```

## Output Validation

Use `.output()` to validate and strip extra fields from procedure responses:

```ts
const getUser = publicProcedure
  .input(z.string())
  .output(
    z.object({
      id: z.string(),
      name: z.string(),
      email: z.string(),
    }),
  )
  .query(async ({ input }) => {
    return db.user.findById(input);
  });
```

## Nested Routers

Organize procedures into sub-routers using dot notation in keys or nested `router()` calls:

```ts
const userRouter = router({
  list: publicProcedure.query(async () => db.user.findMany()),
  byId: publicProcedure
    .input(z.string())
    .query(async ({ input }) => db.user.findById(input)),
  create: publicProcedure
    .input(z.object({ name: z.string(), email: z.string().email() }))
    .mutation(async ({ input }) => db.user.create(input)),
});

const postRouter = router({
  list: publicProcedure.query(async () => db.post.findMany()),
  byId: publicProcedure
    .input(z.string())
    .query(async ({ input }) => db.post.findById(input)),
});

export const appRouter = router({
  user: userRouter,
  post: postRouter,
});
```

Client calls use dot notation: `trpc.user.list.useQuery()`.

## Merge Routers

Flatten multiple routers into a single namespace:

```ts
import { t } from './trpc';

const mergedRouter = t.mergeRouters(analyticsRouter, billingRouter);
```

All procedures from both routers share the same namespace.

## Procedure Chaining

Build reusable procedure bases by chaining middleware and input:

```ts
const authedProcedure = publicProcedure.use(isAuthed);

const adminProcedure = authedProcedure.use(isAdmin);

const adminCreateUser = adminProcedure
  .input(z.object({ name: z.string(), role: z.enum(['user', 'admin']) }))
  .mutation(async ({ input, ctx }) => {
    return db.user.create({ data: { ...input, createdBy: ctx.user.id } });
  });
```
