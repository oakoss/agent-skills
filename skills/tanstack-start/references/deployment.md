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
```

Access bindings in server functions:

```ts
export const getUser = createServerFn().handler(async ({ request }) => {
  const env = request.context.cloudflare.env;
  const result = await env.DB.prepare('SELECT * FROM users').all();
  return result.results;
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

## Static Export

Use the Nitro plugin with `preset: 'static'`:

```ts
export default defineConfig({
  plugins: [tanstackStart(), nitro({ preset: 'static' }), viteReact()],
});
```

Output: `.output/public` (host on GitHub Pages, S3, any static host).

## Deployment Notes

- **Plugin ordering**: `tanstackStart()` must come before `viteReact()` in the plugins array
- Cloudflare and Netlify have dedicated Vite plugins — do not use Nitro for these platforms
- Nitro is under active development — report issues with reproductions
- Edge adapters have API limitations (no file system access)
- Static preset requires all routes to be prerenderable
- Test locally with `npm run build && npm run preview`
