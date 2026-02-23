---
title: Plugins
description: Vite plugin authoring API, hook lifecycle, virtual modules, and popular community plugins
tags:
  [
    plugin,
    transform,
    resolveId,
    load,
    configureServer,
    handleHotUpdate,
    virtual-module,
    enforce,
  ]
---

# Plugins

## Plugin Structure

A Vite plugin is a function returning an object with a `name` and hook methods:

```ts
import type { Plugin } from 'vite';

export default function myPlugin(options: { debug?: boolean } = {}): Plugin {
  return {
    name: 'vite-plugin-my-plugin',
    enforce: 'pre',

    transform(code, id) {
      if (!id.endsWith('.custom')) return;
      return {
        code: `export default ${JSON.stringify(code)}`,
        map: null,
      };
    },
  };
}
```

## Plugin Ordering

| `enforce` | Execution Order          |
| --------- | ------------------------ |
| `'pre'`   | Before Vite core plugins |
| (none)    | After Vite core plugins  |
| `'post'`  | After Vite build plugins |

## Conditional Application

Restrict a plugin to serve or build with `apply`:

```ts
export default function devOnlyPlugin(): Plugin {
  return {
    name: 'vite-plugin-dev-only',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/debug', (req, res) => {
        res.end('Debug info');
      });
    },
  };
}
```

`apply` can also be a function for fine-grained control:

```ts
apply(config, { command, mode }) {
  return command === 'build' && mode !== 'test'
}
```

## Core Hooks

### config

Modify user config before resolution:

```ts
config(userConfig, { command, mode }) {
  return {
    define: {
      __PLUGIN_ENABLED__: true,
    },
  }
}
```

### configResolved

Access the final resolved config (read-only):

```ts
let config: ResolvedConfig

configResolved(resolvedConfig) {
  config = resolvedConfig
}
```

### resolveId + load (Virtual Modules)

Virtual modules generate code at build time without filesystem files:

```ts
const VIRTUAL_ID = 'virtual:my-module';
const RESOLVED_ID = '\0virtual:my-module';

export default function virtualPlugin(): Plugin {
  return {
    name: 'vite-plugin-virtual',

    resolveId(id) {
      if (id === VIRTUAL_ID) return RESOLVED_ID;
    },

    load(id) {
      if (id === RESOLVED_ID) {
        return `export const timestamp = ${Date.now()}`;
      }
    },
  };
}
```

The `\0` prefix is a Rollup convention that tells other plugins not to process the module.

### transform

Transform module source code:

```ts
transform(code, id) {
  if (!id.endsWith('.ts')) return

  return {
    code: code.replace(/__TIMESTAMP__/g, String(Date.now())),
    map: null,
  }
}
```

### configureServer

Add custom middleware to the dev server:

```ts
configureServer(server) {
  server.middlewares.use('/health', (req, res) => {
    res.end('OK')
  })

  // Return a function to add middleware AFTER Vite internals
  return () => {
    server.middlewares.use((req, res, next) => {
      if (!res.writableEnded) {
        res.statusCode = 404
        res.end('Not Found')
      }
    })
  }
}
```

### transformIndexHtml

Inject scripts/tags into the HTML entry:

```ts
transformIndexHtml: {
  order: 'pre',
  handler(html, ctx) {
    return {
      html,
      tags: [
        {
          tag: 'script',
          attrs: { type: 'module' },
          children: `window.__BUILD_TIME__ = "${new Date().toISOString()}"`,
          injectTo: 'head',
        },
      ],
    }
  },
}
```

### handleHotUpdate

Control HMR behavior for file changes:

```ts
handleHotUpdate(ctx) {
  if (ctx.file.endsWith('.config.json')) {
    ctx.server.ws.send({
      type: 'custom',
      event: 'config-update',
      data: { file: ctx.file },
    })
    return []
  }
}
```

Returning an empty array prevents default HMR for that file.

## Popular Plugins

| Plugin                         | Purpose                                     |
| ------------------------------ | ------------------------------------------- |
| `@vitejs/plugin-react`         | React Fast Refresh + JSX                    |
| `@vitejs/plugin-react-swc`     | React with SWC (faster builds)              |
| `@vitejs/plugin-vue`           | Vue 3 SFC support                           |
| `vite-plugin-dts`              | Generate `.d.ts` for library mode           |
| `vite-plugin-pwa`              | Progressive Web App support                 |
| `vite-plugin-svgr`             | Import SVGs as React components             |
| `@sveltejs/vite-plugin-svelte` | Svelte support                              |
| `vite-tsconfig-paths`          | Resolve TS path aliases from tsconfig       |
| `unplugin-auto-import`         | Auto-import APIs (Vue, React, etc.)         |
| `vite-plugin-checker`          | TypeScript/ESLint checking in worker thread |

## Using Plugins

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import checker from 'vite-plugin-checker';

export default defineConfig({
  plugins: [react(), checker({ typescript: true })],
});
```

Plugins are applied in order. Use `enforce` to control relative ordering with Vite internals.
