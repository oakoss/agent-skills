---
title: Pages
description: Cloudflare Pages deployment, functions, _routes.json, build configuration, redirects, and headers
tags: [pages, functions, deploy, routes, redirects, headers, static, build]
---

# Pages

## Overview

Cloudflare Pages is a full-stack hosting platform for static sites and dynamic applications. It supports automatic builds from Git, Functions for server-side logic, and integrates with all Cloudflare bindings (KV, D1, R2, Durable Objects).

## Project Structure

```sh
my-pages-project/
├── public/              # Static assets
│   ├── index.html
│   └── assets/
├── functions/           # Server-side functions (file-based routing)
│   ├── api/
│   │   ├── users.ts     # /api/users
│   │   └── [id].ts      # /api/:id (dynamic route)
│   └── _middleware.ts    # Runs before all functions
├── _redirects           # Redirect rules
├── _headers             # Custom response headers
└── wrangler.toml        # Configuration (optional)
```

## Pages Functions

Functions use file-based routing in the `functions/` directory. Each file exports HTTP method handlers.

### Basic Function

```ts
interface Env {
  DB: D1Database;
  MY_KV: KVNamespace;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { request, env, params, waitUntil } = context;
  const users = await env.DB.prepare('SELECT * FROM users').all();
  return Response.json(users.results);
};

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = await context.request.json();
  await context.env.DB.prepare('INSERT INTO users (name) VALUES (?)')
    .bind(body.name)
    .run();
  return new Response('Created', { status: 201 });
};
```

### Dynamic Routes

File names with brackets create dynamic route parameters:

```ts
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const userId = context.params.id;
  const user = await context.env.DB.prepare('SELECT * FROM users WHERE id = ?')
    .bind(userId)
    .first();

  if (!user) {
    return new Response('Not Found', { status: 404 });
  }

  return Response.json(user);
};
```

### Catch-All Routes

Use `[[path]].ts` for catch-all segments:

```ts
export const onRequestGet: PagesFunction = async (context) => {
  const segments = context.params.path;
  return new Response(`Caught: ${segments}`);
};
```

### Middleware

`_middleware.ts` files run before functions at the same or deeper directory level:

```ts
const authMiddleware: PagesFunction<Env> = async (context) => {
  const token = context.request.headers.get('Authorization');

  if (!token) {
    return new Response('Unauthorized', { status: 401 });
  }

  const user = await validateToken(token, context.env);
  context.data.user = user;

  return context.next();
};

const loggingMiddleware: PagesFunction = async (context) => {
  const start = Date.now();
  const response = await context.next();
  const duration = Date.now() - start;
  console.log(
    `${context.request.method} ${context.request.url} - ${duration}ms`,
  );
  return response;
};

export const onRequest = [loggingMiddleware, authMiddleware];
```

## Routes Configuration

### \_routes.json

Controls which requests invoke Functions vs serve static assets. Placed in the build output directory. Auto-generated when a `functions/` directory is detected.

```json
{
  "version": 1,
  "include": ["/api/*"],
  "exclude": ["/assets/*", "/images/*"]
}
```

- `include` patterns invoke the Function
- `exclude` patterns serve static assets directly (unlimited free requests)
- Exclude patterns take priority over include patterns

### \_redirects

Place in the project root or build output. One rule per line.

```text
/old-page /new-page 301
/blog/* /posts/:splat 302
/home / 301
/docs https://docs.example.com 302
```

- Status codes: `301` (permanent), `302` (temporary), `200` (rewrite, serves content from target without changing URL)
- `:splat` captures wildcard matches
- Max 2,000 redirect rules

### \_headers

Custom response headers for static assets:

```text
/api/*
  Access-Control-Allow-Origin: *

/*.js
  Cache-Control: public, max-age=31536000, immutable

/secure/*
  X-Frame-Options: DENY
  Content-Security-Policy: default-src 'self'
```

## Build Configuration

### wrangler.toml for Pages

```toml
name = "my-pages-project"
pages_build_output_dir = "dist"
compatibility_date = "2024-09-23"

[vars]
API_URL = "https://api.example.com"

[[kv_namespaces]]
binding = "MY_KV"
id = "abc123"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "def456"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"
```

### Environment-Specific Config

```toml
[env.preview.vars]
API_URL = "https://staging-api.example.com"

[env.production.vars]
API_URL = "https://api.example.com"
```

## Deployment

### Git Integration

Connect a repository for automatic builds. Each push triggers a deployment:

- `main` / `production` branch deploys to production URL
- Other branches create preview deployments with unique URLs

### Wrangler CLI Deployment

```bash
npm run build

wrangler pages deploy dist

wrangler pages deploy dist --project-name=my-project

wrangler pages deploy dist --branch=staging
```

### Compile Functions Separately

When migrating or needing a single Worker script from Pages Functions:

```bash
wrangler pages functions build --outdir=dist/_worker.js
```

## Framework Integration

Pages auto-detects popular frameworks and sets build commands:

| Framework  | Build Command                   | Output Directory         |
| ---------- | ------------------------------- | ------------------------ |
| Next.js    | `npx @cloudflare/next-on-pages` | `.vercel/output/static`  |
| Astro      | `npm run build`                 | `dist`                   |
| Remix      | `npm run build`                 | `build/client`           |
| SvelteKit  | `npm run build`                 | `.svelte-kit/cloudflare` |
| Nuxt       | `npm run build`                 | `dist`                   |
| Vite/React | `npm run build`                 | `dist`                   |

## SPA Fallback

For single-page applications, Pages automatically serves `index.html` for any path that does not match a static file. No additional configuration required.
