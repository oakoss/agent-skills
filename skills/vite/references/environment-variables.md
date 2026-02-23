---
title: Environment Variables
description: Vite .env file handling, VITE_ prefix, loadEnv utility, mode-based configuration, and TypeScript types
tags: [env, dotenv, VITE_, loadEnv, import.meta.env, mode, environment]
---

# Environment Variables

## .env Files

Vite loads environment variables from `.env` files in the `envDir` (project root by default):

| File                | Loaded When                         |
| ------------------- | ----------------------------------- |
| `.env`              | Always                              |
| `.env.local`        | Always, git-ignored                 |
| `.env.[mode]`       | Only in specified mode              |
| `.env.[mode].local` | Only in specified mode, git-ignored |

Mode-specific files take priority over generic ones. The mode defaults to `'development'` for `vite dev` and `'production'` for `vite build`.

## Client-Side Variables

Only variables prefixed with `VITE_` are exposed to client code:

```text
# .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
SECRET_KEY=do-not-expose
DB_PASSWORD=do-not-expose
```

Access in application code via `import.meta.env`:

```ts
const apiUrl = import.meta.env.VITE_API_URL;
const title = import.meta.env.VITE_APP_TITLE;

// import.meta.env.SECRET_KEY is undefined (no VITE_ prefix)
```

Vite statically replaces `import.meta.env.VITE_*` at build time. The variable must be used with the full dot notation; destructuring does not work:

```ts
// Works
const url = import.meta.env.VITE_API_URL;

// Does NOT work (not statically analyzable)
const { VITE_API_URL } = import.meta.env;
const key = 'VITE_API_URL';
const url = import.meta.env[key];
```

## Built-in Variables

| Variable                   | Type      | Description                                            |
| -------------------------- | --------- | ------------------------------------------------------ |
| `import.meta.env.MODE`     | `string`  | Current mode (`'development'`, `'production'`, custom) |
| `import.meta.env.BASE_URL` | `string`  | Base URL from `base` config                            |
| `import.meta.env.PROD`     | `boolean` | `true` in production mode                              |
| `import.meta.env.DEV`      | `boolean` | `true` in development mode                             |
| `import.meta.env.SSR`      | `boolean` | `true` when running in SSR context                     |

## Loading Env in Config

Use `loadEnv` to access env variables inside `vite.config.ts` (where `import.meta.env` is not available):

```ts
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    define: {
      'process.env.API_KEY': JSON.stringify(env.SECRET_KEY),
    },
    server: {
      proxy: {
        '/api': {
          target: env.API_BACKEND_URL,
          changeOrigin: true,
        },
      },
    },
  };
});
```

### loadEnv Parameters

```ts
loadEnv(mode: string, envDir: string, prefixes?: string | string[])
```

| Parameter  | Purpose                                                            |
| ---------- | ------------------------------------------------------------------ |
| `mode`     | Which `.env.[mode]` files to load                                  |
| `envDir`   | Directory containing `.env` files                                  |
| `prefixes` | Filter by prefix; `''` loads all variables (including non-`VITE_`) |

The third argument defaults to `'VITE_'`. Pass `''` to load all env variables.

## Custom Mode

Run with a custom mode for staging or testing environments:

```bash
vite build --mode staging
```

This loads `.env.staging` and `.env.staging.local`, and sets `import.meta.env.MODE` to `'staging'`.

## Custom Env Prefix

Change the prefix for client-exposed variables:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  envPrefix: ['VITE_', 'PUBLIC_'],
});
```

This exposes both `VITE_*` and `PUBLIC_*` variables to client code.

## TypeScript Type Declarations

Extend `ImportMetaEnv` for type-safe env access:

```ts
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_APP_TITLE: string;
  readonly VITE_FEATURE_FLAGS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## Security Considerations

Never prefix secrets with `VITE_`. Client-side variables are embedded in the JavaScript bundle and visible to anyone:

```text
# SAFE - only accessible in vite.config.ts via loadEnv
DATABASE_URL=postgresql://...
API_SECRET=sk-...

# EXPOSED - embedded in client bundle
VITE_PUBLIC_API_KEY=pk-...
```

## HTML Env Replacement

Environment variables are also replaced in HTML files:

```html
<title>%VITE_APP_TITLE%</title> <link rel="icon" href="%VITE_FAVICON_URL%" />
```

Use the `%VARIABLE_NAME%` syntax. Only `VITE_`-prefixed variables (or custom prefix) are replaced.
