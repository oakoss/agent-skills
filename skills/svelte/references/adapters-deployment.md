---
title: Adapters and Deployment
description: SvelteKit adapter configuration for Node, static, Vercel, Cloudflare, and other deployment targets
tags:
  [
    adapters,
    deployment,
    node,
    static,
    vercel,
    cloudflare,
    auto,
    prerender,
    build,
  ]
---

# Adapters and Deployment

## Adapter Overview

SvelteKit adapters transform the build output for specific deployment targets.

| Adapter                        | Target                       | SSR | Static | Serverless |
| ------------------------------ | ---------------------------- | --- | ------ | ---------- |
| `@sveltejs/adapter-auto`       | Auto-detect (Vercel, etc.)   | Yes | Yes    | Yes        |
| `@sveltejs/adapter-node`       | Node.js server               | Yes | No     | No         |
| `@sveltejs/adapter-static`     | Static hosting (Netlify, S3) | No  | Yes    | No         |
| `@sveltejs/adapter-vercel`     | Vercel                       | Yes | Yes    | Yes        |
| `@sveltejs/adapter-cloudflare` | Cloudflare Pages/Workers     | Yes | Yes    | Yes        |

## adapter-auto (Default)

Automatically selects the best adapter for the deployment environment. Good for getting started.

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter(),
  },
};

export default config;
```

## adapter-node

Self-hosted Node.js server. Produces a standalone `build/` directory.

```bash
npm install -D @sveltejs/adapter-node
```

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: true,
      envPrefix: 'APP_',
    }),
  },
};

export default config;
```

Run the server:

```bash
node build
```

### Environment variables for adapter-node

| Variable          | Default    | Description           |
| ----------------- | ---------- | --------------------- |
| `PORT`            | `3000`     | Server port           |
| `HOST`            | `0.0.0.0`  | Server host           |
| `ORIGIN`          | (required) | Canonical URL         |
| `BODY_SIZE_LIMIT` | `512K`     | Max request body size |

## adapter-static

Fully pre-rendered static site. Every route must be prerenderable.

```bash
npm install -D @sveltejs/adapter-static
```

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: '404.html',
      precompress: false,
      strict: true,
    }),
  },
};

export default config;
```

Enable prerendering for all pages:

```ts
// src/routes/+layout.ts
export const prerender = true;
```

### SPA mode with adapter-static

For single-page apps, set a fallback page:

```ts
// svelte.config.js
adapter: adapter({
  fallback: 'index.html',
});
```

```ts
// src/routes/+layout.ts
export const ssr = false;
```

## adapter-vercel

```bash
npm install -D @sveltejs/adapter-vercel
```

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-vercel';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      runtime: 'nodejs22.x',
      regions: ['iad1'],
      split: false,
    }),
  },
};

export default config;
```

### Per-route Vercel configuration

```ts
// src/routes/api/heavy/+server.ts
export const config = {
  runtime: 'nodejs22.x',
  maxDuration: 60,
};
```

## adapter-cloudflare

```bash
npm install -D @sveltejs/adapter-cloudflare
```

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-cloudflare';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      routes: {
        include: ['/*'],
        exclude: ['<all>'],
      },
    }),
  },
};

export default config;
```

Access Cloudflare platform bindings:

```ts
// +page.server.ts
export const load = async ({ platform }) => {
  const value = await platform.env.MY_KV.get('key');
  return { value };
};
```

## Project Setup

### Create a new SvelteKit project

```bash
npx sv create my-app
cd my-app
npm install
npm run dev
```

### svelte.config.js full example

```ts
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    alias: {
      $components: 'src/lib/components',
      $server: 'src/lib/server',
    },
    csrf: {
      checkOrigin: true,
    },
    env: {
      dir: '.',
      publicPrefix: 'PUBLIC_',
    },
  },
};

export default config;
```

### Docker deployment with adapter-node

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
```
