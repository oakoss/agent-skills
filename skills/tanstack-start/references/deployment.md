---
title: Deployment
description: Platform-specific deployment via Vite plugins for Cloudflare Workers, Vercel, Netlify, Node.js/Docker, Bun, and static hosting, plus Cloudflare bindings access
tags:
  [
    deployment,
    cloudflare,
    workers,
    vercel,
    netlify,
    node,
    docker,
    static,
    bun,
    nitro,
    vite-plugin,
    wrangler,
    bindings,
    D1,
    KV,
    R2,
    adapter,
    prerender,
  ]
---

# Deployment

TanStack Start deploys via Vite plugins — Cloudflare and Netlify have dedicated plugins, all other platforms use the Nitro plugin with a preset.

## Cloudflare Workers

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { cloudflare } from '@cloudflare/vite-plugin';
import viteReact from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    cloudflare({ viteEnvironment: { name: 'ssr' } }),
    tanstackStart(),
    viteReact(),
  ],
});
```

```toml
# wrangler.toml
name = "my-app"
compatibility_date = "2026-01-21"
compatibility_flags = ["nodejs_compat"]
main = "@tanstack/react-start/server-entry"

# Optional: D1 database binding
[[d1_databases]]
binding = "DB"
database_name = "production-db"
database_id = "your-database-id"

# Optional: KV namespace binding
[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-id"

# Optional: R2 bucket binding
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# Optional: Environment variables
[vars]
ENVIRONMENT = "production"
```

Deploy with: `wrangler deploy`

Access bindings (D1, KV, R2) in server functions via `request.context.cloudflare.env`:

```ts
export const getUser = createServerFn().handler(async ({ request }) => {
  const env = request.context.cloudflare.env;

  // D1 database
  const result = await env.DB.prepare('SELECT * FROM users WHERE id = ?')
    .bind(userId)
    .first();

  // KV storage
  const cached = await env.CACHE.get('user:123', 'json');
  await env.CACHE.put('user:123', JSON.stringify(result), {
    expirationTtl: 3600,
  });

  // R2 object storage
  const file = await env.BUCKET.get('avatar.png');

  return result;
});
```

Conditional logic for prerendering with bindings (bindings are unavailable at build time):

```ts
export const Route = createFileRoute('/users')({
  loader: async ({ context }) => {
    if (typeof context.cloudflare === 'undefined') {
      return { users: [] };
    }
    const env = context.cloudflare.env;
    const { results } = await env.DB.prepare('SELECT * FROM users').all();
    return { users: results };
  },
});
```

Alternatively, disable prerendering on routes that use bindings:

```ts
export const Route = createFileRoute('/users')({
  prerender: false,
  loader: async ({ context }) => {
    const env = context.cloudflare.env;
    return { users: await env.DB.prepare('SELECT * FROM users').all() };
  },
});
```

## Netlify

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import netlify from '@netlify/vite-plugin-tanstack-start';
import viteReact from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [tanstackStart(), netlify(), viteReact()],
});
```

## Nitro (Vercel, Node.js, Bun, AWS Lambda, Static)

All other platforms use the `nitro/vite` plugin with a preset:

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { nitro } from 'nitro/vite';
import viteReact from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [tanstackStart(), nitro({ preset: 'vercel' }), viteReact()],
});
```

### Nitro Presets

| Preset        | Runtime | Use For                        |
| ------------- | ------- | ------------------------------ |
| `vercel`      | Node    | Vercel hosting                 |
| `node-server` | Node    | Docker, Railway, VPS           |
| `static`      | None    | GitHub Pages, S3, static hosts |
| `aws-lambda`  | Node    | AWS serverless                 |
| `bun`         | Bun     | Bun runtime (React 19 only)    |

## Vercel

Use the Nitro plugin with `preset: 'vercel'`. Vercel supports one-click deployment once configured.

## Node.js / Railway / Docker

Use the Nitro plugin with `preset: 'node-server'`.

Add scripts to `package.json`:

```json
{
  "scripts": {
    "build": "vite build",
    "start": "node .output/server/index.mjs"
  }
}
```

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY .output .output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

## Bun

Use the Nitro plugin with `preset: 'bun'`. Requires React 19 — if using React 18, use the `node-server` preset instead.

Run with: `bun .output/server/index.mjs`

## AWS Lambda

Use the Nitro plugin with `preset: 'aws-lambda'`:

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { nitro } from 'nitro/vite';
import viteReact from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    tanstackStart(),
    nitro({
      preset: 'aws-lambda',
      awsLambda: {
        streaming: true,
      },
    }),
    viteReact(),
  ],
});
```

Deploy with SST, Serverless Framework, or AWS CDK:

```yaml
# serverless.yml
service: my-tanstack-app

provider:
  name: aws
  runtime: nodejs20.x
  region: us-east-1

functions:
  app:
    handler: .output/server/index.handler
    events:
      - http: ANY /
      - http: ANY /{proxy+}
```

## Static Export

Use the Nitro plugin with `preset: 'static'`:

```ts
export default defineConfig({
  plugins: [tanstackStart(), nitro({ preset: 'static' }), viteReact()],
});
```

Output: `.output/public` (host on GitHub Pages, S3, any static host).

## Adapter Comparison

| Adapter            | Plugin                                 | Runtime | Edge | Static | Best For                     |
| ------------------ | -------------------------------------- | ------- | ---- | ------ | ---------------------------- |
| Cloudflare Workers | `@cloudflare/vite-plugin`              | Workers | Yes  | No     | Edge-first, D1/KV/R2         |
| Cloudflare Pages   | `@cloudflare/vite-plugin`              | Workers | Yes  | Yes    | Static + edge functions      |
| Vercel             | `nitro/vite` (`preset: 'vercel'`)      | Node    | No   | Yes    | One-click deploy, serverless |
| Netlify            | `@netlify/vite-plugin-tanstack-start`  | Node    | No   | Yes    | Netlify ecosystem            |
| Node.js / Docker   | `nitro/vite` (`preset: 'node-server'`) | Node    | No   | No     | VPS, Railway, self-hosted    |
| AWS Lambda         | `nitro/vite` (`preset: 'aws-lambda'`)  | Node    | No   | No     | AWS serverless               |
| Bun                | `nitro/vite` (`preset: 'bun'`)         | Bun     | No   | No     | Bun runtime (React 19 only)  |
| Static             | `nitro/vite` (`preset: 'static'`)      | None    | No   | Yes    | GitHub Pages, S3, CDN        |

## Deployment Notes

- **Plugin ordering**: `tanstackStart()` must come before `viteReact()` in the plugins array
- Cloudflare and Netlify have dedicated Vite plugins — do not use Nitro for these platforms
- Nitro is under active development — report issues with reproductions
- Edge adapters have API limitations (no file system access)
- Static preset requires all routes to be prerenderable
- Test locally with `npm run build && npm run preview`
