---
title: Routing
description: Route definitions, path parameters, regex constraints, wildcards, grouped routes, method handlers, and basePath
tags: [routing, path-params, wildcard, regex, route-groups, basePath, methods]
---

# Routing

## Basic Routes

```ts
import { Hono } from 'hono';

const app = new Hono();

app.get('/', (c) => c.text('GET /'));
app.post('/', (c) => c.text('POST /'));
app.put('/', (c) => c.text('PUT /'));
app.delete('/', (c) => c.text('DELETE /'));
app.patch('/item', (c) => c.text('PATCH /item'));
```

## Match Any HTTP Method

```ts
app.all('/hello', (c) => c.text('Any method'));
```

## Custom and Multiple Methods

```ts
app.on('PURGE', '/cache', (c) => c.text('PURGE /cache'));

app.on(['PUT', 'DELETE'], '/post', (c) => c.text('PUT or DELETE /post'));
```

## Multiple Paths

```ts
app.on('GET', ['/hello', '/ja/hello', '/en/hello'], (c) => c.text('Hello'));
```

## Path Parameters

```ts
app.get('/user/:name', (c) => {
  const name = c.req.param('name');
  return c.text(`User: ${name}`);
});

app.get('/posts/:id/comment/:commentId', (c) => {
  const { id, commentId } = c.req.param();
  return c.json({ postId: id, commentId });
});
```

## Optional Parameters

```ts
app.get('/api/animal/:type?', (c) => {
  const type = c.req.param('type') || 'all';
  return c.text(`Animal type: ${type}`);
});
```

## Regex Constraints

Inline regex restricts what a parameter matches:

```ts
app.get('/post/:date{[0-9]+}/:title{[a-z]+}', (c) => {
  const { date, title } = c.req.param();
  return c.json({ date, title });
});
```

## Wildcards

```ts
app.get('/wild/*/card', (c) => c.text('Matched wildcard'));

app.get('/files/*', (c) => c.text('Any file path'));
```

## Route Grouping with `app.route()`

Split applications into modular sub-routers:

```ts
// authors.ts
import { Hono } from 'hono';

const app = new Hono()
  .get('/', (c) => c.json('list authors'))
  .post('/', (c) => c.json('create an author', 201))
  .get('/:id', (c) => c.json(`get ${c.req.param('id')}`));

export default app;
```

```ts
// books.ts
import { Hono } from 'hono';

const app = new Hono()
  .get('/', (c) => c.json('list books'))
  .post('/', (c) => c.json('create a book', 201))
  .get('/:id', (c) => c.json(`get ${c.req.param('id')}`));

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

Chain `.route()` calls and export the type of the chained result for RPC type inference.

## Base Path

Set a prefix for all routes in an app instance:

```ts
const api = new Hono().basePath('/api/v1');

api.get('/users', (c) => c.json([]));
```

This registers the handler at `/api/v1/users`.

## Handler Execution Order

Handlers and middleware execute in registration order. When a handler returns a response, processing stops. Place middleware before handlers and fallback handlers last:

```ts
app.use(logger());
app.get('/specific', (c) => c.text('matched'));
app.all('*', (c) => c.text('fallback', 404));
```

## Multiple Handlers per Route

Pass multiple handlers to a single route definition. Each handler can call `next()` or return a response:

```ts
app.get(
  '/protected',
  async (c, next) => {
    const token = c.req.header('Authorization');
    if (!token) return c.text('Unauthorized', 401);
    await next();
  },
  (c) => c.text('Secret content'),
);
```

## Error Handling

```ts
app.onError((err, c) => {
  console.error(err);
  return c.json({ error: 'Internal Server Error' }, 500);
});

app.notFound((c) => {
  return c.json({ error: 'Not Found' }, 404);
});
```
