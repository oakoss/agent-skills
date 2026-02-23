---
title: Drizzle Integration
description: Drizzle ORM setup with libSQL driver, schema definition for SQLite, and embedded replica configuration
tags: [drizzle-orm, libsql, drizzle, sqlite, schema, driver]
---

# Drizzle Integration

## Installation

```bash
npm install drizzle-orm @libsql/client
npm install -D drizzle-kit
```

## Remote Connection

```ts
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';

const turso = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

export const db = drizzle(turso);
```

## Embedded Replica Connection

```ts
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';

const turso = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  syncInterval: 60,
});

export const db = drizzle(turso);
```

## Schema Definition

Drizzle uses SQLite column types with the `drizzle-orm/sqlite-core` module:

```ts
import {
  sqliteTable,
  text,
  integer,
  real,
  blob,
} from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: text('created_at')
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const posts = sqliteTable('posts', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  content: text('content'),
  authorId: integer('author_id')
    .notNull()
    .references(() => users.id),
});
```

## Querying with Drizzle

```ts
import { eq } from 'drizzle-orm';
import { db } from './db';
import { users, posts } from './schema';

const allUsers = await db.select().from(users);

const user = await db
  .select()
  .from(users)
  .where(eq(users.email, 'alice@example.com'));

await db.insert(users).values({
  name: 'Alice',
  email: 'alice@example.com',
});

await db.update(users).set({ name: 'Alice Smith' }).where(eq(users.id, 1));

await db.delete(users).where(eq(users.id, 1));
```

## Relations

```ts
import { relations } from 'drizzle-orm';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

Enable relational queries by passing the schema:

```ts
import * as schema from './schema';

export const db = drizzle(turso, { schema });

const userWithPosts = await db.query.users.findFirst({
  with: { posts: true },
  where: eq(users.id, 1),
});
```

## Drizzle Kit Configuration

```ts
import { type Config } from 'drizzle-kit';

export default {
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'turso',
  dbCredentials: {
    url: process.env.TURSO_DATABASE_URL!,
    authToken: process.env.TURSO_AUTH_TOKEN,
  },
} satisfies Config;
```

## Migration Commands

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
npx drizzle-kit push
npx drizzle-kit studio
```

## Local Development with Drizzle

For local development without a cloud database:

```ts
import { type Config } from 'drizzle-kit';

export default {
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: {
    url: 'file:local.db',
  },
} satisfies Config;
```
