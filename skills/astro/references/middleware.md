---
title: Middleware
description: Request handling with onRequest, chaining middleware with sequence, setting locals, and common patterns
tags:
  [middleware, onRequest, sequence, locals, authentication, redirect, headers]
---

# Middleware

Astro middleware runs before every page and API route. Define middleware in `src/middleware.ts` (or `src/middleware/index.ts`).

## Basic Middleware

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();
  return response;
});
```

## Setting Locals

Pass data from middleware to pages and endpoints via `context.locals`.

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const sessionToken = context.cookies.get('session')?.value;

  if (sessionToken) {
    const user = await validateSession(sessionToken);
    context.locals.user = user;
  }

  return next();
});
```

Access locals in any page or endpoint:

```astro
---
const { user } = Astro.locals;
---
{user ? (
  <p>Welcome, {user.name}</p>
) : (
  <a href="/login">Sign in</a>
)}
```

### Type-Safe Locals

Declare the locals type in `src/env.d.ts`:

```ts
declare namespace App {
  interface Locals {
    user?: {
      id: string;
      name: string;
      email: string;
    };
  }
}
```

## Chaining Middleware with sequence()

Compose multiple middleware functions that run in order.

```ts
import { defineMiddleware, sequence } from 'astro:middleware';

const logger = defineMiddleware(async (context, next) => {
  const start = performance.now();
  const response = await next();
  const duration = performance.now() - start;
  console.log(
    `${context.request.method} ${context.url.pathname} ${duration.toFixed(0)}ms`,
  );
  return response;
});

const auth = defineMiddleware(async (context, next) => {
  const protectedPaths = ['/dashboard', '/settings', '/api/private'];
  const isProtected = protectedPaths.some((p) =>
    context.url.pathname.startsWith(p),
  );

  if (isProtected && !context.locals.user) {
    return context.redirect('/login');
  }

  return next();
});

export const onRequest = sequence(logger, auth);
```

## Modifying Responses

### Adding Headers

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();

  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
});
```

### Returning Early

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  if (context.url.pathname.startsWith('/api/')) {
    const apiKey = context.request.headers.get('x-api-key');
    if (apiKey !== import.meta.env.API_KEY) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  return next();
});
```

## Redirects

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const redirects: Record<string, string> = {
    '/old-page': '/new-page',
    '/blog/old-slug': '/blog/new-slug',
  };

  const redirect = redirects[context.url.pathname];
  if (redirect) {
    return context.redirect(redirect, 301);
  }

  return next();
});
```

## Cookies

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const theme = context.cookies.get('theme')?.value ?? 'light';
  context.locals.theme = theme;

  const response = await next();

  context.cookies.set('visited', 'true', {
    path: '/',
    maxAge: 60 * 60 * 24 * 365,
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
  });

  return response;
});
```
