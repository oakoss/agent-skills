---
title: Context and Helpers
description: Context object, request parsing, response helpers, headers, status codes, and context variables
tags:
  [
    context,
    json,
    text,
    html,
    redirect,
    header,
    status,
    req,
    query,
    param,
    body,
    set,
    get,
    env,
  ]
---

# Context and Helpers

The Context object (`c`) is created for each request and available until the response is returned.

## Response Helpers

### JSON

```ts
app.get('/api/user', (c) => {
  return c.json({ id: '1', name: 'Alice' });
});

app.post('/api/user', (c) => {
  return c.json({ id: '2', name: 'Bob' }, 201);
});
```

### Text

```ts
app.get('/health', (c) => {
  return c.text('OK');
});
```

### HTML

```ts
app.get('/page', (c) => {
  return c.html('<h1>Hello</h1>');
});
```

### Redirect

```ts
app.get('/old', (c) => c.redirect('/new'));
app.get('/moved', (c) => c.redirect('/new-location', 301));
```

### Raw Response

```ts
app.get('/custom', (c) => {
  return new Response('raw body', {
    status: 200,
    headers: { 'Content-Type': 'application/octet-stream' },
  });
});
```

### No Content

```ts
app.delete('/item/:id', (c) => {
  return c.body(null, 204);
});
```

## Status and Headers

```ts
app.get('/data', (c) => {
  c.status(200);
  c.header('X-Request-Id', crypto.randomUUID());
  c.header('Cache-Control', 'max-age=3600');
  return c.json({ data: 'value' });
});
```

## Request Parsing

### Path Parameters

```ts
app.get('/user/:id', (c) => {
  const id = c.req.param('id');
  return c.json({ id });
});

app.get('/posts/:postId/comments/:commentId', (c) => {
  const { postId, commentId } = c.req.param();
  return c.json({ postId, commentId });
});
```

### Query Parameters

```ts
app.get('/search', (c) => {
  const q = c.req.query('q');
  const page = c.req.query('page');
  return c.json({ q, page });
});

app.get('/filter', (c) => {
  const queries = c.req.queries('tag');
  return c.json({ tags: queries });
});
```

### JSON Body

```ts
app.post('/api/items', async (c) => {
  const body = await c.req.json();
  return c.json({ received: body }, 201);
});
```

### Form Data

```ts
app.post('/upload', async (c) => {
  const body = await c.req.parseBody();
  const file = body['file'];
  return c.text(`Received: ${typeof file === 'string' ? file : file.name}`);
});
```

### Raw Body

```ts
app.post('/raw', async (c) => {
  const text = await c.req.text();
  const buffer = await c.req.arrayBuffer();
  return c.text('OK');
});
```

### Request Headers

```ts
app.get('/check', (c) => {
  const auth = c.req.header('Authorization');
  const contentType = c.req.header('Content-Type');
  return c.json({ auth: !!auth, contentType });
});
```

### Request URL and Method

```ts
app.all('/info', (c) => {
  return c.json({
    method: c.req.method,
    url: c.req.url,
    path: c.req.path,
  });
});
```

## Context Variables

Pass typed data between middleware and handlers:

```ts
type Env = {
  Variables: {
    user: { id: string; email: string };
    requestId: string;
  };
};

const app = new Hono<Env>();

app.use(async (c, next) => {
  c.set('requestId', crypto.randomUUID());
  await next();
});

app.get('/me', (c) => {
  const user = c.get('user');
  const requestId = c.get('requestId');
  return c.json({ user, requestId });
});
```

Values set with `c.set()` are scoped to the current request.

## Environment Bindings

Access platform bindings (Cloudflare KV, D1, R2, secrets) and environment variables:

```ts
type Env = {
  Bindings: {
    DATABASE: D1Database;
    KV_STORE: KVNamespace;
    API_KEY: string;
  };
};

const app = new Hono<Env>();

app.get('/data', async (c) => {
  const db = c.env.DATABASE;
  const kv = c.env.KV_STORE;
  const key = c.env.API_KEY;
  return c.json({ key });
});
```

## Adapter Helper for Cross-Runtime Env

```ts
import { env } from 'hono/adapter';

app.get('/config', (c) => {
  const { DATABASE_URL, API_KEY } = env<{
    DATABASE_URL: string;
    API_KEY: string;
  }>(c);
  return c.json({ configured: true });
});
```

Works across Cloudflare Workers, Node.js, Bun, Deno, and Vercel.

## Renderer

Set a layout for HTML responses:

```ts
app.use(async (c, next) => {
  c.setRenderer((content) => {
    return c.html(`<!DOCTYPE html><html><body>${content}</body></html>`);
  });
  await next();
});

app.get('/', (c) => {
  return c.render('<h1>Hello</h1>');
});
```

## Error Object

Access caught errors in `app.onError()`:

```ts
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return err.getResponse();
  }
  return c.json({ error: err.message }, 500);
});
```

## HTTPException

Throw HTTP errors from handlers or middleware:

```ts
import { HTTPException } from 'hono/http-exception';

app.get('/protected', (c) => {
  if (!authorized) {
    throw new HTTPException(401, { message: 'Unauthorized' });
  }
  return c.text('OK');
});
```
