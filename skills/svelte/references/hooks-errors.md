---
title: Hooks and Error Handling
description: SvelteKit server hooks, client hooks, universal hooks, error handling, and middleware patterns
tags:
  [hooks, handle, handleError, handleFetch, middleware, auth, redirect, error]
---

# Hooks and Error Handling

## Server Hooks (src/hooks.server.ts)

### handle

Intercepts every request. Use for authentication, redirects, response headers, and middleware logic.

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');

  if (session) {
    event.locals.user = await getUserFromSession(session);
  }

  if (event.url.pathname.startsWith('/dashboard') && !event.locals.user) {
    redirect(303, '/login');
  }

  const response = await resolve(event);

  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');

  return response;
};
```

### Sequencing multiple handlers

```ts
import { sequence } from '@sveltejs/kit/hooks';
import type { Handle } from '@sveltejs/kit';

const auth: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');
  event.locals.user = session ? await getUserFromSession(session) : null;
  return resolve(event);
};

const logger: Handle = async ({ event, resolve }) => {
  const start = performance.now();
  const response = await resolve(event);
  const duration = performance.now() - start;
  console.log(
    `${event.request.method} ${event.url.pathname} ${response.status} ${duration.toFixed(0)}ms`,
  );
  return response;
};

const security: Handle = async ({ event, resolve }) => {
  const response = await resolve(event);
  response.headers.set('X-Frame-Options', 'DENY');
  return response;
};

export const handle = sequence(auth, logger, security);
```

### handleFetch

Intercepts `fetch` calls made in server load functions. Useful for proxying, adding auth headers, or routing internal requests.

```ts
// src/hooks.server.ts
import type { HandleFetch } from '@sveltejs/kit';

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
  if (request.url.startsWith('https://api.internal.com')) {
    request.headers.set('Authorization', `Bearer ${event.locals.apiToken}`);
  }

  return fetch(request);
};
```

### handleError

Catches unexpected errors. Use for logging, error reporting (e.g., Sentry), and shaping the error response.

```ts
// src/hooks.server.ts
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({
  error,
  event,
  status,
  message,
}) => {
  const errorId = crypto.randomUUID();

  console.error(
    `[${errorId}] ${event.request.method} ${event.url.pathname}`,
    error,
  );

  return {
    message: 'An unexpected error occurred',
    errorId,
  };
};
```

## Client Hooks (src/hooks.client.ts)

### handleError (client-side)

Catches unhandled errors on the client.

```ts
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({
  error,
  event,
  status,
  message,
}) => {
  const errorId = crypto.randomUUID();
  console.error(`[${errorId}]`, error);

  return {
    message: 'Something went wrong',
    errorId,
  };
};
```

## Universal Hooks (src/hooks.ts)

### reroute

Remap incoming URLs to different routes. Runs on both server and client.

```ts
// src/hooks.ts
import type { Reroute } from '@sveltejs/kit';

const translations: Record<string, string> = {
  '/sobre': '/about',
  '/contacto': '/contact',
  '/tienda': '/shop',
};

export const reroute: Reroute = ({ url }) => {
  return translations[url.pathname] ?? url.pathname;
};
```

## Error Pages

### Per-route error boundaries

```svelte
<!-- src/routes/blog/[slug]/+error.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<h1>{$page.status}: {$page.error?.message}</h1>

{#if $page.status === 404}
  <p>This post could not be found.</p>
  <a href="/blog">Back to blog</a>
{:else}
  <p>Something went wrong loading this page.</p>
{/if}
```

### Root error page

```svelte
<!-- src/routes/+error.svelte -->
<script>
  import { page } from '$app/stores';
</script>

<div class="error-page">
  <h1>{$page.status}</h1>
  <p>{$page.error?.message ?? 'Unknown error'}</p>
  <a href="/">Go home</a>
</div>
```

## Throwing Errors in Load Functions

```ts
// +page.server.ts
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
  if (!locals.user) {
    redirect(303, '/login');
  }

  const post = await getPost(params.slug);

  if (!post) {
    error(404, { message: 'Not found' });
  }

  if (post.authorId !== locals.user.id) {
    error(403, { message: 'Forbidden' });
  }

  return { post };
};
```

## Typing app.d.ts

Extend the `App` namespace to type `locals`, `error`, and `pageData`.

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Error {
      message: string;
      errorId?: string;
    }

    interface Locals {
      user: { id: string; name: string; role: string } | null;
      db: Database;
    }

    interface PageData {
      user: { id: string; name: string } | null;
    }
  }
}

export {};
```

## Environment Variables

```ts
// Server-only (secrets, DB URLs)
import { DATABASE_URL, API_SECRET } from '$env/static/private';

// Public (exposed to client)
import { PUBLIC_API_URL } from '$env/static/public';

// Dynamic (runtime values)
import { env } from '$env/dynamic/private';
import { env as publicEnv } from '$env/dynamic/public';
```
