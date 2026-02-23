---
title: SSR Configuration
description: Vite server-side rendering setup, Express integration, externals, and streaming
tags:
  [
    ssr,
    server-side-rendering,
    express,
    external,
    noExternal,
    ssrLoadModule,
    streaming,
  ]
---

# SSR Configuration

## SSR Build Config

Configure Vite for SSR output:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    ssr: true,
    rollupOptions: {
      input: './src/entry-server.ts',
    },
  },
  ssr: {
    external: ['express'],
    noExternal: ['my-ui-library'],
  },
});
```

## SSR Options

| Option           | Purpose                                                                    |
| ---------------- | -------------------------------------------------------------------------- |
| `ssr.external`   | Dependencies to externalize (not bundled, resolved at runtime)             |
| `ssr.noExternal` | Dependencies to bundle (useful for ESM-only packages or packages with CSS) |
| `ssr.target`     | SSR target environment: `'node'` (default) or `'webworker'`                |

By default, Vite externalizes all `node_modules` during SSR builds. Use `noExternal` for packages that need transformation (e.g., packages shipping uncompiled CSS or ESM-only code).

## Express Integration (Development)

Set up a dev server with SSR rendering:

```ts
// server.ts
import express from 'express';
import fs from 'node:fs';
import { createServer as createViteServer } from 'vite';

async function createServer() {
  const app = express();

  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'custom',
  });

  app.use(vite.middlewares);

  app.use('*', async (req, res) => {
    const url = req.originalUrl;

    try {
      let template = fs.readFileSync('./index.html', 'utf-8');
      template = await vite.transformIndexHtml(url, template);

      const { render } = await vite.ssrLoadModule('/src/entry-server.ts');
      const appHtml = await render(url);
      const html = template.replace('<!--app-html-->', appHtml);

      res.status(200).set({ 'Content-Type': 'text/html' }).end(html);
    } catch (e) {
      vite.ssrFixStacktrace(e as Error);
      console.error(e);
      res.status(500).end((e as Error).message);
    }
  });

  app.listen(3000);
}

createServer();
```

### Key APIs

| API                                                  | Purpose                                              |
| ---------------------------------------------------- | ---------------------------------------------------- |
| `createServer({ server: { middlewareMode: true } })` | Run Vite as middleware (no built-in HTTP server)     |
| `vite.middlewares`                                   | Connect middleware instance for HMR and static files |
| `vite.transformIndexHtml(url, html)`                 | Apply Vite HTML transforms (plugin injections)       |
| `vite.ssrLoadModule(path)`                           | Load and execute a module in SSR context with HMR    |
| `vite.ssrFixStacktrace(error)`                       | Fix stack traces to map to original source           |

## Entry Files

### Client Entry

```ts
// src/entry-client.ts
import { hydrateRoot } from 'react-dom/client'
import { App } from './App'

hydrateRoot(document.getElementById('app')!, <App />)
```

### Server Entry

```ts
// src/entry-server.ts
import { renderToString } from 'react-dom/server'
import { App } from './App'

export function render(url: string) {
  return renderToString(<App />)
}
```

## Production SSR Server

In production, serve the pre-built SSR bundle without Vite:

```ts
// server-prod.ts
import express from 'express';
import fs from 'node:fs';
import { resolve } from 'node:path';

const app = express();
const distPath = resolve(import.meta.dirname, 'dist/client');

app.use(express.static(distPath, { index: false }));

const template = fs.readFileSync(resolve(distPath, 'index.html'), 'utf-8');
const { render } = await import('./dist/server/entry-server.js');

app.use('*', async (req, res) => {
  const appHtml = await render(req.originalUrl);
  const html = template.replace('<!--app-html-->', appHtml);
  res.status(200).set({ 'Content-Type': 'text/html' }).end(html);
});

app.listen(3000);
```

## Streaming SSR

For React 18+ streaming with `renderToPipeableStream`:

```ts
// src/entry-server.ts
import { renderToPipeableStream } from 'react-dom/server'
import { App } from './App'

export function render(url: string, res: import('express').Response) {
  const { pipe } = renderToPipeableStream(<App />, {
    onShellReady() {
      res.setHeader('Content-Type', 'text/html')
      pipe(res)
    },
    onError(err) {
      console.error(err)
    },
  })
}
```

## Build Scripts

Typical `package.json` scripts for SSR:

```json
{
  "scripts": {
    "dev": "node server.ts",
    "build": "pnpm build:client && pnpm build:server",
    "build:client": "vite build --outDir dist/client",
    "build:server": "vite build --outDir dist/server --ssr src/entry-server.ts",
    "preview": "node server-prod.ts"
  }
}
```

## Conditional Logic for SSR vs Client

Use `import.meta.env.SSR` to branch logic:

```ts
if (import.meta.env.SSR) {
  // Server-only code (tree-shaken from client bundle)
} else {
  // Client-only code (tree-shaken from SSR bundle)
}
```
