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

## Environment Variables

`VITE_` prefixed variables are client-accessible. Non-prefixed variables are server-only.

```bash
# .env
# Server-only (no prefix)
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
JWT_SECRET=super-secret-key
STRIPE_SECRET_KEY=sk_live_...

# Client-safe (VITE_ prefix)
VITE_APP_NAME=My App
VITE_API_URL=https://api.example.com
```

Access patterns:

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
```

Validated environment with Zod (recommended for server-side):

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

Use `*.server.ts` suffix for files that must never be imported by client code. Vite tree-shakes server-only imports, but the suffix makes intent explicit and prevents accidental bundling:

```ts
// src/lib/db.server.ts — only importable in server context
import { env } from './env.server';
import { drizzle } from 'drizzle-orm/postgres-js';

export const db = drizzle(env.DATABASE_URL);
```

Type-safe environment variables:

```ts
// env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_API_URL: string;
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

## Feature-Based Structure

For medium-to-large applications, organize code by feature:

```sh
src/
├── features/
│   ├── auth/
│   │   ├── api/
│   │   │   ├── index.ts
│   │   │   ├── auth.queries.ts
│   │   │   └── auth.mutations.ts
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── AuthGuard.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── types.ts
│   │   └── index.ts
│   └── users/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       └── index.ts
├── shared/
│   ├── components/
│   │   ├── ui/
│   │   └── layout/
│   ├── hooks/
│   ├── utils/
│   └── types/
├── lib/
│   ├── api-client.ts
│   └── query-client.ts
└── config/
    ├── env.ts
    └── constants.ts
```

## File Naming Rules

```sh
Components:     PascalCase.tsx       -> UserCard.tsx
Hooks:          camelCase.ts         -> useUserProfile.ts
Utils:          kebab-case.ts        -> format-date.ts
Types:          kebab-case.ts        -> user.types.ts
Queries:        feature.queries.ts   -> users.queries.ts
Mutations:      feature.mutations.ts -> users.mutations.ts
Routes:         kebab-case.tsx       -> user-profile.tsx
```

## Import Path Aliases

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@/features/*": ["./src/features/*"],
      "@/shared/*": ["./src/shared/*"]
    }
  }
}
```

Use absolute imports to avoid deep relative paths:

```ts
import { UserCard } from '@/features/users';
import { Button } from '@/shared/components/ui';
```

## Barrel Exports

```ts
// features/users/index.ts — PUBLIC API
export { UserCard } from './components/UserCard';
export { UserList } from './components/UserList';
export { userQueries } from './api/users.queries';
export type { User, UserFilter } from './types';
```

## Module Boundaries

```sh
features/auth/ can import from:
  @/shared/*
  @/lib/*
  @/features/users/*  (cross-feature — avoid when possible)

If cross-feature imports grow, lift shared code to shared/
```

## When to Split Files

- Types shared across 3+ files: extract to `types.ts`
- More than 5 queries: split by domain
- Component over 200 lines: extract sub-components
- Hook used in 3+ places: move to `shared/hooks/`
- Keep component and its props type colocated when only used together
