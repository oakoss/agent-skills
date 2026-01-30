---
title: Prisma Architecture
description: Prisma TypedSQL, relation mode, extensions for soft deletes and audit logs, edge-first query engine, and distinct operations
tags: [prisma, typedsql, extensions, edge, relation-mode, soft-delete]
---

# Prisma Architecture

## TypedSQL

Replace raw strings with `.sql` files that generate fully typed functions.

Workflow:

1. Create `prisma/sql/get_active_users.sql`
2. Run `prisma generate`
3. Use in code with full type safety:

```ts
const users = await prisma.$queryRawTyped(get_active_users());
```

## Relation Mode (Emulated Integrity)

In environments that do not support foreign keys (PlanetScale, certain Vitess setups), use emulated relation mode:

```prisma
datasource db {
  provider     = "postgresql"
  url          = env("DATABASE_URL")
  relationMode = "prisma"
}
```

You MUST manually create indices for all scalar fields used in relations to prevent full table scans.

## Extensions for Cross-Cutting Concerns

Use Prisma Extensions for soft deletes, automatic auditing, and other middleware patterns:

```ts
const prisma = new PrismaClient().$extends({
  model: {
    user: {
      async softDelete(id: string) {
        return prisma.user.update({
          where: { id },
          data: { deletedAt: new Date() },
        });
      },
    },
  },
});
```

## Edge-First Query Engine

Prisma uses the TypeScript/WASM engine by default, eliminating the need for bulky Rust binaries in Edge Functions. Ensure `prisma generate` is run with the correct engine target for your deployment platform (Vercel, Cloudflare).

## Native Distinct and Skip Scan

Leverage PostgreSQL performance improvements by using native Prisma filters:

```ts
const uniqueUsers = await prisma.user.findMany({
  distinct: ['email'],
  take: 10,
});
```
