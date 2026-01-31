---
title: Adapters
description: Runtime adapters for Cloudflare Workers, Bun, Node.js, Deno, Vercel, and AWS Lambda
tags:
  [
    adapters,
    cloudflare-workers,
    bun,
    nodejs,
    deno,
    vercel,
    aws-lambda,
    serve,
    runtime,
  ]
---

# Adapters

Hono runs on any JavaScript runtime that supports Web Standards. Application code is identical across platforms; only the entry point differs.

## Cloudflare Workers

```ts
import { Hono } from 'hono';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Workers!'));

export default app;
```

No adapter needed. Cloudflare Workers natively support the `export default` pattern.

### With Bindings

```ts
type Env = {
  Bindings: {
    MY_KV: KVNamespace;
    DB: D1Database;
    MY_BUCKET: R2Bucket;
    SECRET_KEY: string;
  };
};

const app = new Hono<Env>();

app.get('/data', async (c) => {
  const value = await c.env.MY_KV.get('key');
  return c.json({ value });
});

export default app;
```

### Project Setup

```bash
npm create hono@latest my-app -- --template cloudflare-workers
```

```json
{
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy"
  }
}
```

## Bun

```ts
import { Hono } from 'hono';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Bun!'));

export default app;
```

Bun natively supports the default export. To customize the port:

```ts
export default {
  port: 3000,
  fetch: app.fetch,
};
```

### Project Setup

```bash
bun create hono@latest my-app
```

```bash
bun run dev
```

## Node.js

Node.js requires the `@hono/node-server` adapter:

```bash
npm install @hono/node-server
```

```ts
import { Hono } from 'hono';
import { serve } from '@hono/node-server';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Node.js!'));

serve({
  fetch: app.fetch,
  port: 3000,
});
```

### With Static Files

```bash
npm install @hono/node-server
```

```ts
import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { serveStatic } from '@hono/node-server/serve-static';

const app = new Hono();

app.use('/static/*', serveStatic({ root: './' }));

serve({ fetch: app.fetch, port: 3000 });
```

### Project Setup

```bash
npm create hono@latest my-app -- --template nodejs
```

## Deno

```ts
import { Hono } from 'https://deno.land/x/hono/mod.ts';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Deno!'));

Deno.serve(app.fetch);
```

Or with npm specifier:

```ts
import { Hono } from 'npm:hono';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Deno!'));

Deno.serve(app.fetch);
```

Pin all Hono imports to the same version to avoid type mismatches.

### Project Setup

```bash
deno run -A npm:create-hono@latest my-app
```

## Vercel

```ts
import { Hono } from 'hono';
import { handle } from 'hono/vercel';

const app = new Hono().basePath('/api');

app.get('/hello', (c) => c.json({ message: 'Hello from Vercel!' }));

export const GET = handle(app);
export const POST = handle(app);
```

### Project Setup

```bash
npm create hono@latest my-app -- --template vercel
```

## AWS Lambda

```ts
import { Hono } from 'hono';
import { handle } from 'hono/aws-lambda';

const app = new Hono();

app.get('/', (c) => c.text('Hello from Lambda!'));

export const handler = handle(app);
```

### With API Gateway Events

```ts
import { Hono } from 'hono';
import { handle, type LambdaEvent } from 'hono/aws-lambda';

const app = new Hono();

app.get('/', (c) => {
  const event = c.env.event as LambdaEvent;
  return c.json({ requestId: event.requestContext?.requestId });
});

export const handler = handle(app);
```

### Project Setup

```bash
npm create hono@latest my-app -- --template aws-lambda
```

## Runtime Detection

Detect the current runtime at execution time:

```ts
import { getRuntimeKey } from 'hono/adapter';

app.get('/runtime', (c) => {
  const runtime = getRuntimeKey();
  return c.json({ runtime });
});
```

## Cross-Runtime Environment Access

Use the `env()` helper for unified environment variable access:

```ts
import { env } from 'hono/adapter';

app.get('/config', (c) => {
  const { DATABASE_URL } = env<{ DATABASE_URL: string }>(c);
  return c.json({ configured: !!DATABASE_URL });
});
```

Works on Cloudflare Workers (`c.env`), Node.js (`process.env`), Bun (`Bun.env`), Deno (`Deno.env`), and Vercel.

## Starter Templates

| Runtime            | Command                                                   |
| ------------------ | --------------------------------------------------------- |
| Cloudflare Workers | `npm create hono@latest -- --template cloudflare-workers` |
| Cloudflare Pages   | `npm create hono@latest -- --template cloudflare-pages`   |
| Bun                | `bun create hono@latest`                                  |
| Node.js            | `npm create hono@latest -- --template nodejs`             |
| Deno               | `deno run -A npm:create-hono@latest`                      |
| Vercel             | `npm create hono@latest -- --template vercel`             |
| AWS Lambda         | `npm create hono@latest -- --template aws-lambda`         |
