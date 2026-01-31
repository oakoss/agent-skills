---
title: RPC Client
description: Type-safe RPC client with hc(), end-to-end type safety, route type export, and monorepo configuration
tags: [rpc, hc, client, type-safety, AppType, monorepo, hono-client]
---

# RPC Client

Hono's RPC mode provides end-to-end type safety between server and client. The server exports route types, and the `hc` client infers endpoints, parameters, and response types automatically.

## Server Setup

Chain route methods and export the type of the result:

```ts
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';

const app = new Hono();

const route = app
  .get('/api/hello', (c) => {
    return c.json({ message: 'Hello!' });
  })
  .post(
    '/api/posts',
    zValidator(
      'json',
      z.object({
        title: z.string(),
        body: z.string(),
      }),
    ),
    (c) => {
      const data = c.req.valid('json');
      return c.json({ id: '1', ...data }, 201);
    },
  )
  .get('/api/posts/:id', (c) => {
    const id = c.req.param('id');
    return c.json({ id, title: 'Post', body: 'Content' });
  });

export type AppType = typeof route;
export default app;
```

Export `typeof route` (the chained result), not `typeof app`.

## Client Usage

```ts
import { hc } from 'hono/client';
import { type AppType } from './server';

const client = hc<AppType>('http://localhost:8787');

const helloRes = await client.api.hello.$get();
const helloData = await helloRes.json();

const createRes = await client.api.posts.$post({
  json: {
    title: 'New Post',
    body: 'Post content',
  },
});
const createData = await createRes.json();

const postRes = await client.api.posts[':id'].$get({
  param: { id: '1' },
});
const postData = await postRes.json();
```

The client provides autocompletion for all endpoints, methods, parameters, and response types.

## Path Parameters

```ts
const route = app.get(
  '/posts/:id',
  zValidator('query', z.object({ page: z.coerce.number().optional() })),
  (c) => {
    return c.json({ title: 'Post', body: 'Content' });
  },
);

const res = await client.posts[':id'].$get({
  param: { id: '123' },
  query: { page: '1' },
});
```

Path and query parameters are passed as strings in the client.

## Grouped Routes

Structure larger applications with separate routers:

```ts
// authors.ts
import { Hono } from 'hono';

const app = new Hono()
  .get('/', (c) => c.json([]))
  .post('/', (c) => c.json({ id: '1' }, 201))
  .get('/:id', (c) => c.json({ id: c.req.param('id') }));

export default app;
```

```ts
// books.ts
import { Hono } from 'hono';

const app = new Hono()
  .get('/', (c) => c.json([]))
  .get('/:id', (c) => c.json({ id: c.req.param('id') }));

export default app;
```

```ts
// index.ts
import { Hono } from 'hono';
import authors from './authors';
import books from './books';

const app = new Hono();
const routes = app.route('/authors', authors).route('/books', books);

export default app;
export type AppType = typeof routes;
```

```ts
// client.ts
import { hc } from 'hono/client';
import { type AppType } from './index';

const client = hc<AppType>('http://localhost:8787');

const authorsRes = await client.authors.$get();
const bookRes = await client.books[':id'].$get({ param: { id: '1' } });
```

## Monorepo Configuration

For RPC types to work in a monorepo, both client and server `tsconfig.json` files must have:

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

## Performance Optimization

For large APIs, type inference can slow down the IDE. Pre-calculate types at compile time:

```ts
import { hc } from 'hono/client';
import { type AppType } from './server';

const hcWithType = (...args: Parameters<typeof hc<AppType>>) =>
  hc<AppType>(...args);

const client = hcWithType('http://localhost:8787');
```

Run `tsc` to compile the server app with the client. This lets `tsc` handle type instantiation at build time, keeping the IDE fast.

## Response Parsing

The client returns standard `Response` objects. Parse them with `.json()`, `.text()`, etc.:

```ts
const res = await client.api.posts.$get();

if (res.ok) {
  const data = await res.json();
  console.log(data.title);
} else {
  console.error('Request failed:', res.status);
}
```

## Custom Headers and Options

Pass fetch options including custom headers:

```ts
const client = hc<AppType>('http://localhost:8787', {
  headers: {
    Authorization: 'Bearer my-token',
  },
});
```

Per-request headers:

```ts
const res = await client.api.posts.$get(undefined, {
  headers: {
    'X-Custom-Header': 'value',
  },
});
```
