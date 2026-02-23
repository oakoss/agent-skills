---
title: Configuration
description: Vite configuration fundamentals, defineConfig patterns, path aliases, conditional config, and shared options
tags: [defineConfig, vite.config.ts, resolve.alias, config, root, base, mode]
---

# Configuration

## Config File

Vite automatically resolves `vite.config.ts` (or `.js`, `.mjs`, `.cjs`) from the project root. Use `defineConfig` for type safety:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  root: './src',
  base: '/my-app/',
  plugins: [],
});
```

## Conditional Config

Pass a function to `defineConfig` for command/mode-aware configuration:

```ts
import { defineConfig } from 'vite';

export default defineConfig(({ command, mode }) => {
  if (command === 'serve') {
    return {
      server: { port: 3000 },
    };
  }
  return {
    build: { sourcemap: true },
  };
});
```

`command` is `'serve'` during dev and `'build'` during production. `mode` defaults to `'development'` for serve and `'production'` for build, overridable via `--mode`.

## Async Config

The config function can be async for dynamic imports or async setup:

```ts
import { defineConfig } from 'vite';

export default defineConfig(async ({ command, mode }) => {
  const data = await fetchSomething();
  return {
    define: {
      __DATA__: JSON.stringify(data),
    },
  };
});
```

## Path Aliases

Configure module resolution aliases via `resolve.alias`:

```ts
import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(import.meta.dirname, 'src'),
      '@components': resolve(import.meta.dirname, 'src/components'),
      '@utils': resolve(import.meta.dirname, 'src/utils'),
    },
  },
});
```

When using TypeScript, also add matching `paths` in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

## Define Global Constants

Replace expressions at build time with `define`:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __DEV__: JSON.stringify(process.env.NODE_ENV !== 'production'),
  },
});
```

Values must be JSON-serializable or valid JS expressions. Use `JSON.stringify` for strings.

## Shared Options Reference

| Option        | Default                          | Purpose                                           |
| ------------- | -------------------------------- | ------------------------------------------------- |
| `root`        | `process.cwd()`                  | Project root directory (where `index.html` lives) |
| `base`        | `'/'`                            | Public base path for assets                       |
| `publicDir`   | `'public'`                       | Static assets served as-is                        |
| `cacheDir`    | `'node_modules/.vite'`           | Cache directory for pre-bundled deps              |
| `mode`        | `'development'` / `'production'` | Overridable via CLI `--mode`                      |
| `logLevel`    | `'info'`                         | `'info'`, `'warn'`, `'error'`, `'silent'`         |
| `clearScreen` | `true`                           | Clear terminal on dev server start                |
| `envDir`      | `root`                           | Directory to load `.env` files from               |
| `envPrefix`   | `'VITE_'`                        | Env variables exposed to client code              |

## Multi-Config with Workspaces

In monorepos, each package can have its own `vite.config.ts`. Shared configuration can be extracted to a function:

```ts
// packages/shared/vite-config.ts
import { type UserConfig } from 'vite';

export function createConfig(overrides: UserConfig = {}): UserConfig {
  return {
    resolve: {
      alias: {
        '@': resolve(import.meta.dirname, 'src'),
      },
    },
    ...overrides,
  };
}
```

```ts
// packages/app/vite.config.ts
import { defineConfig } from 'vite';
import { createConfig } from '../shared/vite-config';

export default defineConfig(
  createConfig({
    server: { port: 3000 },
  }),
);
```

## Config Intellisense

For JavaScript config files, use the JSDoc type hint:

```js
/** @type {import('vite').UserConfig} */
export default {
  plugins: [],
};
```

Or use `defineConfig` which provides the same type safety without JSDoc.
