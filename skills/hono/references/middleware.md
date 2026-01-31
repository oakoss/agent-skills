---
title: Middleware
description: Built-in middleware, custom middleware creation, middleware ordering, and createMiddleware for type safety
tags:
  [
    middleware,
    cors,
    logger,
    jwt,
    bearerAuth,
    basicAuth,
    compress,
    createMiddleware,
    ordering,
  ]
---

# Middleware

## Middleware Execution Order

Middleware executes in registration order. The code before `await next()` runs top-down; the code after `next()` runs bottom-up (onion model):

```ts
app.use(async (c, next) => {
  console.log('1: before');
  await next();
  console.log('1: after');
});

app.use(async (c, next) => {
  console.log('2: before');
  await next();
  console.log('2: after');
});

app.get('/', (c) => c.text('handler'));
```

Output order: `1: before` -> `2: before` -> handler -> `2: after` -> `1: after`.

## Built-in Middleware

### Logger

```ts
import { logger } from 'hono/logger';

app.use(logger());
```

### CORS

```ts
import { cors } from 'hono/cors';

app.use('/api/*', cors());

app.use(
  '/api/*',
  cors({
    origin: 'https://example.com',
    allowHeaders: ['Content-Type', 'Authorization'],
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
    maxAge: 600,
  }),
);
```

For dynamic origins from environment variables:

```ts
app.use('/api/*', (c, next) => {
  const corsMiddleware = cors({
    origin: c.env.ALLOWED_ORIGIN,
  });
  return corsMiddleware(c, next);
});
```

### Basic Auth

```ts
import { basicAuth } from 'hono/basic-auth';

app.use(
  '/admin/*',
  basicAuth({
    username: 'admin',
    password: 'secret',
  }),
);
```

### Bearer Auth

```ts
import { bearerAuth } from 'hono/bearer-auth';

app.use(
  '/api/*',
  bearerAuth({
    token: 'my-secret-token',
  }),
);
```

### JWT Auth

```ts
import { jwt } from 'hono/jwt';
import { type JwtVariables } from 'hono/jwt';

type Variables = JwtVariables;

const app = new Hono<{ Variables: Variables }>();

app.use(
  '/auth/*',
  jwt({
    secret: 'it-is-very-secret',
  }),
);

app.get('/auth/profile', (c) => {
  const payload = c.get('jwtPayload');
  return c.json(payload);
});
```

Use environment variables for the secret:

```ts
app.use('/auth/*', (c, next) => {
  const jwtMiddleware = jwt({ secret: c.env.JWT_SECRET });
  return jwtMiddleware(c, next);
});
```

### Compress

```ts
import { compress } from 'hono/compress';

app.use(compress());
```

Skip on Cloudflare Workers and Deno Deploy where compression is automatic.

### Secure Headers

```ts
import { secureHeaders } from 'hono/secure-headers';

app.use(secureHeaders());
```

### Powered By

```ts
import { poweredBy } from 'hono/powered-by';

app.use(poweredBy());
```

## Scoped Middleware

Apply middleware to specific paths:

```ts
app.use(logger());
app.use('/api/*', cors());
app.use('/admin/*', basicAuth({ username: 'admin', password: 'secret' }));
```

## Custom Middleware

Inline middleware:

```ts
app.use(async (c, next) => {
  const start = Date.now();
  await next();
  const duration = Date.now() - start;
  c.header('X-Response-Time', `${duration}ms`);
});
```

## Reusable Middleware with `createMiddleware`

Use `createMiddleware` from `hono/factory` for type-safe, reusable middleware:

```ts
import { createMiddleware } from 'hono/factory';

type Env = {
  Variables: {
    user: { id: string; role: string };
  };
};

const authMiddleware = createMiddleware<Env>(async (c, next) => {
  const token = c.req.header('Authorization');
  if (!token) return c.json({ error: 'Unauthorized' }, 401);

  c.set('user', { id: '1', role: 'admin' });
  await next();
});

const app = new Hono<Env>();
app.use(authMiddleware);

app.get('/me', (c) => {
  const user = c.get('user');
  return c.json(user);
});
```

## Factory Helper for Consistent Typing

Use `createFactory` to avoid repeating environment types:

```ts
import { createFactory } from 'hono/factory';

type Env = {
  Bindings: { DATABASE_URL: string };
  Variables: { requestId: string };
};

const factory = createFactory<Env>();

const requestIdMiddleware = factory.createMiddleware(async (c, next) => {
  c.set('requestId', crypto.randomUUID());
  await next();
});

const app = factory.createApp();
app.use(requestIdMiddleware);
```

## Error Handling in Middleware

Hono catches thrown errors and routes them to `app.onError()`. There is no need to wrap `next()` in try/catch:

```ts
app.use(async (c, next) => {
  await next();
});

app.onError((err, c) => {
  console.error(err);
  return c.json({ error: 'Internal Server Error' }, 500);
});
```

## Combine Middleware

Combine multiple middleware into one using the `combine` helper:

```ts
import { every, some } from 'hono/combine';

app.use('/api/*', every(cors(), bearerAuth({ token: 'secret' })));

app.use('/webhook/*', some(bearerAuth({ token: 'secret' }), ipRestriction()));
```

- `every()` requires all middleware to pass (AND logic)
- `some()` requires at least one to pass (OR logic)
