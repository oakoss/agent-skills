---
title: Prisma Architecture
description: Prisma TypedSQL, relation mode, extensions for soft deletes and audit logs, edge-first query engine, and distinct operations
tags: [prisma, typedsql, extensions, edge, relation-mode, soft-delete]
---

# Prisma Architecture

## TypedSQL

Replace raw SQL strings with `.sql` files that generate fully typed functions. TypedSQL provides type-safe inputs and outputs while preserving full SQL flexibility.

Workflow:

1. Create a `.sql` file (the filename must be a valid JS identifier and cannot start with `$`):

```sql
-- prisma/sql/get_active_users.sql
SELECT u.id, u.name, COUNT(p.id) as "postCount"
FROM "User" u
LEFT JOIN "Post" p ON u.id = p."authorId"
GROUP BY u.id, u.name
```

2. Run `prisma generate` to produce typed functions
3. Import and execute with full type safety:

```ts
import { PrismaClient } from './generated/prisma/client';
import { getActiveUsers } from './generated/prisma/sql';

const prisma = new PrismaClient();
const users = await prisma.$queryRawTyped(getActiveUsers());
```

Parameters are passed as typed function arguments:

```ts
import { getUsersByAge } from './generated/prisma/sql';

const users = await prisma.$queryRawTyped(getUsersByAge(18, 30));
```

## Relation Mode (Emulated Integrity)

In environments that do not support foreign keys (PlanetScale, certain Vitess setups), use emulated relation mode. GA since Prisma 4.8.0.

Two modes are available:

- `"foreignKeys"` (default for relational databases) -- uses database-level foreign keys
- `"prisma"` -- emulates referential integrity in Prisma Client with additional queries

```prisma
datasource db {
  provider     = "mysql"
  url          = env("DATABASE_URL")
  relationMode = "prisma"
}
```

You MUST manually create indices for all scalar fields used in relations. Without foreign keys, the database does not auto-create these indices, leading to full table scans:

```prisma
model Post {
  id       Int @id @default(autoincrement())
  authorId Int
  author   User @relation(fields: [authorId], references: [id])

  @@index([authorId])
}
```

**Performance note:** Emulated mode uses additional queries per operation to maintain integrity. Prefer native foreign keys when the database supports them.

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

Use PostgreSQL performance improvements with native Prisma filters:

```ts
const uniqueUsers = await prisma.user.findMany({
  distinct: ['email'],
  take: 10,
});
```
