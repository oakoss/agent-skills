---
title: File Organization
description: Entry points, plugin configuration, execution boundary functions, feature-based project structure, naming rules, import aliases, barrel exports, and environment configuration
tags:
  [
    file,
    organization,
    entry-point,
    client,
    server,
    tanstackStart,
    plugin,
    createServerOnlyFn,
    createClientOnlyFn,
    createIsomorphicFn,
    environment,
    VITE_,
    zod,
    env-validation,
    server-ts,
    feature,
    naming,
    imports,
    barrel,
  ]
---

# File Organization

## Entry Points

Every TanStack Start app requires three entry files:

```ts
// src/client.tsx — Client entry point (hydrates the app)
import { StartClient } from '@tanstack/react-start/client';
import { StrictMode } from 'react';
import { hydrateRoot } from 'react-dom/client';

hydrateRoot(
  document,
  <StrictMode>
    <StartClient />
  </StrictMode>,
);
```

```ts
// src/server.ts — Server entry point (handles incoming requests)
import handler, { createServerEntry } from '@tanstack/react-start/server-entry';

export default createServerEntry({
  fetch(request) {
    return handler.fetch(request);
  },
});
```

```ts
// src/start.ts — Global configuration (optional)
import { createStart } from '@tanstack/react-start';

export default createStart({
  requestMiddleware: [],
});
```

## Plugin Configuration

The `tanstackStart()` Vite plugin accepts configuration options:

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import viteReact from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    tanstackStart({
      srcDirectory: 'src',
      router: {
        routesDirectory: 'app',
      },
    }),
    viteReact(),
  ],
});
```

| Option                   | Default    | Description                     |
| ------------------------ | ---------- | ------------------------------- |
| `srcDirectory`           | `'src'`    | Root source directory           |
| `router.routesDirectory` | `'routes'` | Directory for file-based routes |

## Execution Boundaries

TanStack Start uses function-level APIs to enforce server/client separation — not file suffixes.

| Function               | Runs On         | Client Can Call? | Use For                                    |
| ---------------------- | --------------- | ---------------- | ------------------------------------------ |
| `createServerFn()`     | Server          | Yes (RPC stub)   | Data fetching, mutations, server logic     |
| `createServerOnlyFn()` | Server          | No (throws)      | Secrets, DB connections, server utilities  |
| `createClientOnlyFn()` | Client          | N/A              | localStorage, DOM APIs, browser-only logic |
| `createIsomorphicFn()` | Server + Client | N/A              | Different implementations per environment  |

All imported from `@tanstack/react-start`.

## Execution Boundary Examples

```ts
import {
  createServerFn,
  createServerOnlyFn,
  createClientOnlyFn,
  createIsomorphicFn,
} from '@tanstack/react-start';

// RPC: runs on server, callable from client via network request
const fetchUser = createServerFn().handler(async () => {
  return await db.users.findFirst();
});

// Server-only: crashes if called from client
const getSecret = createServerOnlyFn(() => process.env.DATABASE_URL);

// Client-only: crashes if called from server
const saveToStorage = createClientOnlyFn((data: unknown) => {
  localStorage.setItem('data', JSON.stringify(data));
});

// Different implementations per environment
const logger = createIsomorphicFn()
  .server((msg: string) => serverLogger.info(msg))
  .client((msg: string) => console.log(`[CLIENT]: ${msg}`));
```

## Server Function File Convention

For larger applications, split server-side code using a three-file naming convention:

| Suffix          | Purpose                          | Safe to import from                           |
| --------------- | -------------------------------- | --------------------------------------------- |
| `.ts`           | Client-safe code (types/schemas) | Anywhere                                      |
| `.server.ts`    | Server-only code (DB, secrets)   | Only inside server function handlers          |
| `.functions.ts` | `createServerFn` wrappers        | Anywhere (build creates RPC stubs for client) |

```ts
// users.functions.ts
import { createServerFn } from '@tanstack/react-start';
import { findUserById } from './users.server';

export const getUser = createServerFn({ method: 'GET' })
  .inputValidator((data: { id: string }) => data)
  .handler(async ({ data }) => {
    return findUserById(data.id);
  });
```

```ts
// users.server.ts
import { db } from '@/lib/db.server';

export async function findUserById(id: string) {
  return db.users.findUnique({ where: { id } });
}
```

Static imports of `.functions.ts` files are safe in client components — the build replaces server function implementations with RPC stubs.

## Import Protection Pitfalls

### Loaders Run on Both Server AND Client

Route loaders execute on the server during SSR and on the client during client-side navigation. Never access `process.env` directly in a loader — it leaks secrets to the client bundle:

```tsx
// ❌ Loader runs on BOTH server and client — secret exposed
export const Route = createFileRoute('/users')({
  loader: () => {
    const secret = process.env.SECRET; // Bundled into client code
    return fetch(`/api/users?key=${secret}`);
  },
});

// ✅ Use a server function — secret stays on server
const getUsers = createServerFn().handler(async () => {
  const secret = process.env.SECRET;
  return fetch(`/api/users?key=${secret}`);
});

export const Route = createFileRoute('/users')({
  loader: () => getUsers(),
});
```

### Direct process.env Access Outside Server Functions

Any `process.env` reference outside of `createServerFn` or `createServerOnlyFn` risks client exposure:

```ts
// ❌ Top-level — bundled into client
const apiKey = process.env.SECRET_KEY;

// ✅ Wrapped in server-only function
const apiKey = createServerOnlyFn(() => process.env.SECRET_KEY);
```

### Safe Import Patterns

| Import Source               | Safe in Client? | Why                      |
| --------------------------- | --------------- | ------------------------ |
| `.functions.ts`             | Yes             | Build creates RPC stubs  |
| `.server.ts`                | No              | Contains raw server code |
| `.ts` (types/schemas)       | Yes             | No server-only code      |
| `createServerFn` return     | Yes             | Serialized RPC call      |
| `createServerOnlyFn` return | No              | Throws on client         |

## Environment Variables

`VITE_` prefixed variables are inlined into the client bundle at build time. Non-prefixed variables are server-only — accessing them via `import.meta.env` on the client returns `undefined` (security feature).

```bash
# .env
# Server-only (no prefix) — never sent to browser
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
JWT_SECRET=super-secret-key
STRIPE_SECRET_KEY=sk_live_...

# Client-safe (VITE_ prefix) — inlined into client bundle
VITE_APP_NAME=My App
VITE_API_URL=https://api.example.com
VITE_SENTRY_DSN=https://...
```

### Access Patterns

| Context            | Access                     | Available Variables              |
| ------------------ | -------------------------- | -------------------------------- |
| Server function    | `process.env.VAR`          | All variables                    |
| Client component   | `import.meta.env.VITE_VAR` | Only `VITE_` prefixed            |
| Loader (runs both) | Neither directly           | Use `createServerFn` for secrets |

```ts
// Server function — can access any variable
const getUser = createServerFn().handler(async () => {
  const db = await connect(process.env.DATABASE_URL);
  return db.user.findFirst();
});

// Client component — only VITE_ prefixed variables
export function AppHeader() {
  return <h1>{import.meta.env.VITE_APP_NAME}</h1>;
}

// Feature flags via VITE_ prefix
export function FeatureGated({ children }: { children: React.ReactNode }) {
  if (import.meta.env.VITE_ENABLE_NEW_DASHBOARD !== 'true') return null;
  return <>{children}</>;
}
```

### Build-Time Inlining

`VITE_` variables must be available at build time. They are statically replaced during the build — not read at runtime:

```bash
# ❌ Variable not set during build — inlined as undefined
npm run build

# ✅ Variable available at build time
VITE_API_URL=https://api.example.com npm run build
```

Restart the dev server after changing `.env` files — Vite only reads them on startup.

### Validated Environment (Zod)

Validate server-side variables at startup to fail fast on misconfiguration:

```ts
// src/lib/env.server.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development'),
});

export const env = envSchema.parse(process.env);
```

Use `*.server.ts` suffix for env files to prevent accidental client import:

```ts
// src/lib/db.server.ts — only importable in server context
import { env } from './env.server';
import { drizzle } from 'drizzle-orm/postgres-js';

export const db = drizzle(env.DATABASE_URL);
```

### TypeScript Declarations

```ts
// env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_API_URL: string;
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_ENABLE_NEW_DASHBOARD?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      readonly DATABASE_URL: string;
      readonly JWT_SECRET: string;
      readonly NODE_ENV: 'development' | 'production' | 'test';
    }
  }
}

export {};
```

## Project Structure

Organize by feature for medium-to-large applications. Use `@/*` path aliases to avoid deep relative imports.

```sh
src/
├── features/
│   ├── auth/
│   │   ├── api/              # queries, mutations, server functions
│   │   ├── components/       # LoginForm.tsx, AuthGuard.tsx
│   │   ├── hooks/            # useAuth.ts
│   │   ├── types.ts
│   │   └── index.ts          # barrel export (public API)
│   └── users/
├── shared/                   # cross-feature components, hooks, utils
├── lib/                      # api-client.ts, query-client.ts
└── config/                   # env.ts, constants.ts
```

### Naming Conventions

| Category    | Convention           | Example              |
| ----------- | -------------------- | -------------------- |
| Components  | `PascalCase.tsx`     | `UserCard.tsx`       |
| Hooks       | `camelCase.ts`       | `useUserProfile.ts`  |
| Utils       | `kebab-case.ts`      | `format-date.ts`     |
| Queries     | `feature.queries.ts` | `users.queries.ts`   |
| Routes      | `kebab-case.tsx`     | `user-profile.tsx`   |
| Server code | `*.server.ts`        | `db.server.ts`       |
| Server fns  | `*.functions.ts`     | `users.functions.ts` |
