---
title: Database Adapters
description: Drizzle adapter for D1 and PostgreSQL, Kysely adapter for D1, Cloudflare Workers factory pattern for per-request auth instances
tags: [database, drizzle, kysely, prisma, d1, cloudflare-workers, adapters]
---

# Database Adapters

**Direct connections:** Pass `pg.Pool`, `mysql2` pool, `better-sqlite3`, or `bun:sqlite` instance.

**ORM adapters:** Import from `better-auth/adapters/drizzle`, `better-auth/adapters/prisma`, `better-auth/adapters/mongodb`.

**Critical:** Better Auth uses adapter model names, NOT underlying table names. If Prisma model is `User` mapping to table `users`, use `modelName: "user"` (Prisma reference), not `"users"`.

## Drizzle Adapter (Recommended for D1)

```ts
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { drizzle } from 'drizzle-orm/d1';

const db = drizzle(env.DB, { schema });
export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: 'sqlite' }),
});
```

## Kysely Adapter (Alternative for D1)

```ts
import { Kysely } from 'kysely';
import { D1Dialect } from 'kysely-d1';

export const auth = betterAuth({
  database: {
    db: new Kysely({
      dialect: new D1Dialect({ database: env.DB }),
    }),
    type: 'sqlite',
  },
});
```

## Cloudflare Workers: Factory Pattern Required

D1 database bindings are only available inside the request handler. Use a factory function:

```ts
// WRONG - DB binding not available outside request
const db = drizzle(env.DB, { schema });
export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: 'sqlite' }),
});

// CORRECT - Create auth instance per-request
export default {
  fetch(request, env, ctx) {
    const db = drizzle(env.DB, { schema });
    const auth = betterAuth({
      database: drizzleAdapter(db, { provider: 'sqlite' }),
    });
    return auth.handler(request);
  },
};
```
