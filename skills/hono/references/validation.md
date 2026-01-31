---
title: Validation
description: Zod validator middleware for request body, query, params, and headers validation with error handling
tags:
  [
    validation,
    zod,
    zValidator,
    json,
    form,
    query,
    param,
    header,
    error-handling,
  ]
---

# Validation

Hono integrates with Zod through the `@hono/zod-validator` package for runtime validation with compile-time type inference.

## Installation

```bash
npm install @hono/zod-validator zod
```

## Basic JSON Body Validation

```ts
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';

const app = new Hono();

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1),
  published: z.boolean().optional(),
});

app.post('/api/posts', zValidator('json', createPostSchema), (c) => {
  const data = c.req.valid('json');
  return c.json({ id: '1', ...data }, 201);
});
```

## Form Data Validation

```ts
const uploadSchema = z.object({
  name: z.string(),
  email: z.string().email(),
});

app.post('/submit', zValidator('form', uploadSchema), (c) => {
  const { name, email } = c.req.valid('form');
  return c.json({ name, email });
});
```

## Query Parameter Validation

```ts
const searchSchema = z.object({
  q: z.string().min(1),
  page: z.coerce.number().int().positive().optional(),
  limit: z.coerce.number().int().min(1).max(100).optional(),
});

app.get('/api/search', zValidator('query', searchSchema), (c) => {
  const { q, page, limit } = c.req.valid('query');
  return c.json({ q, page: page ?? 1, limit: limit ?? 20 });
});
```

Query and path parameters are always strings. Use `z.coerce.number()` to convert to numbers.

## Path Parameter Validation

```ts
const idSchema = z.object({
  id: z.string().regex(/^[0-9]+$/),
});

app.get('/api/posts/:id', zValidator('param', idSchema), (c) => {
  const { id } = c.req.valid('param');
  return c.json({ id });
});
```

## Header Validation

```ts
const headerSchema = z.object({
  'x-api-key': z.string().min(1),
});

app.get('/api/data', zValidator('header', headerSchema), (c) => {
  const headers = c.req.valid('header');
  return c.json({ authenticated: true });
});
```

## Multiple Validators on One Route

Stack validators for different targets:

```ts
app.put(
  '/api/posts/:id',
  zValidator('param', z.object({ id: z.string() })),
  zValidator(
    'json',
    z.object({
      title: z.string().min(1),
      body: z.string().min(1),
    }),
  ),
  (c) => {
    const { id } = c.req.valid('param');
    const data = c.req.valid('json');
    return c.json({ id, ...data });
  },
);
```

## Custom Error Handling

Pass a hook function as the third argument to customize validation error responses:

```ts
app.post(
  '/api/items',
  zValidator('json', itemSchema, (result, c) => {
    if (!result.success) {
      return c.json(
        {
          error: 'Validation failed',
          issues: result.error.issues,
        },
        400,
      );
    }
  }),
  (c) => {
    const data = c.req.valid('json');
    return c.json(data, 201);
  },
);
```

If the hook returns a response, it short-circuits the handler. If it returns nothing on success, the handler proceeds.

## Reusable Validated Routes

Combine `zValidator` with route grouping for consistent validation:

```ts
const paginationSchema = z.object({
  page: z.coerce.number().int().positive().optional(),
  limit: z.coerce.number().int().min(1).max(100).optional(),
});

const withPagination = zValidator('query', paginationSchema);

app.get('/api/posts', withPagination, (c) => {
  const { page, limit } = c.req.valid('query');
  return c.json({ page: page ?? 1, limit: limit ?? 20 });
});

app.get('/api/comments', withPagination, (c) => {
  const { page, limit } = c.req.valid('query');
  return c.json({ page: page ?? 1, limit: limit ?? 20 });
});
```

## Validation Targets

| Target       | `zValidator(target, ...)` | Access                  | Description                   |
| ------------ | ------------------------- | ----------------------- | ----------------------------- |
| JSON body    | `'json'`                  | `c.req.valid('json')`   | Parsed JSON request body      |
| Form data    | `'form'`                  | `c.req.valid('form')`   | URL-encoded or multipart form |
| Query params | `'query'`                 | `c.req.valid('query')`  | URL query string              |
| Path params  | `'param'`                 | `c.req.valid('param')`  | Route path parameters         |
| Headers      | `'header'`                | `c.req.valid('header')` | Request headers               |
| Cookies      | `'cookie'`                | `c.req.valid('cookie')` | Request cookies               |

## Type Inference

Validated data is fully typed. The handler receives the exact shape defined by the Zod schema:

```ts
const schema = z.object({
  name: z.string(),
  age: z.coerce.number(),
});

app.post('/user', zValidator('json', schema), (c) => {
  const data = c.req.valid('json');
  return c.json({ name: data.name, age: data.age });
});
```
