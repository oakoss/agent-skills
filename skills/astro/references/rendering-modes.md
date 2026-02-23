---
title: Rendering Modes
description: Static generation, server-side rendering, hybrid rendering, per-page prerender control, and adapter configuration
tags: [SSR, SSG, static, server, hybrid, prerender, adapter, output, rendering]
---

# Rendering Modes

Astro supports three rendering strategies controlled by the `output` config option and per-page `prerender` exports.

## Static (Default)

All pages are pre-rendered to HTML at build time. No server runtime needed.

```ts
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
});
```

Best for: blogs, documentation, marketing sites, portfolios.

## Server

All pages are server-rendered on each request. Requires a server adapter.

```ts
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

Best for: dashboards, apps with authentication, personalized content.

### Opt Individual Pages into Static

In server mode, add `prerender = true` to any page to pre-render it at build time.

```astro
---
export const prerender = true;
---
<html>
  <body>
    <h1>This page is pre-rendered at build time</h1>
  </body>
</html>
```

## Hybrid Rendering

Combine static and server rendering in the same project.

### Static Default, Opt-in SSR

Use `output: 'static'` (default) and opt individual pages into server rendering.

```astro
---
export const prerender = false;
---
<html>
  <body>
    <h1>This page is server-rendered</h1>
    <p>User: {Astro.locals.user?.name}</p>
  </body>
</html>
```

### Server Default, Opt-in Static

Use `output: 'server'` and opt individual pages into static rendering with `prerender = true`.

```ts
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

export default defineConfig({
  output: 'server',
  adapter: vercel(),
});
```

## Adapters

Server and hybrid modes require a deployment adapter.

```bash
npx astro add node
npx astro add vercel
npx astro add netlify
npx astro add cloudflare
```

### Node Adapter

```ts
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

### Vercel Adapter

```ts
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

export default defineConfig({
  output: 'server',
  adapter: vercel(),
});
```

## API Routes (Endpoints)

Server-rendered projects can define API endpoints.

```ts
import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ params, request }) => {
  const data = await fetchDataFromDB(params.id);
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json();
  const result = await saveToDatabase(body);
  return new Response(JSON.stringify(result), { status: 201 });
};
```

## Environment Variables

Access environment variables differently based on rendering context.

```ts
const publicKey = import.meta.env.PUBLIC_API_KEY;

const secretKey = import.meta.env.SECRET_API_KEY;
```

Variables prefixed with `PUBLIC_` are available on both server and client. All others are server-only.

## Choosing a Rendering Mode

| Scenario                         | Recommended Mode                               |
| -------------------------------- | ---------------------------------------------- |
| Blog, docs, marketing pages      | `static` (default)                             |
| Mostly static, few dynamic pages | `static` + `prerender = false`                 |
| App with auth, mostly dynamic    | `server` + `prerender = true` for static pages |
| Full dynamic application         | `server`                                       |
