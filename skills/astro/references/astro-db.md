---
title: Astro DB
description: Defining tables with astro:db, seeding data, querying with drizzle-like API, and database configuration
tags: [database, astro-db, drizzle, table, column, seed, query, SQL]
---

# Astro DB

Astro DB is a built-in SQL database designed for Astro projects. It uses a Drizzle-like API with type-safe table definitions and queries.

## Setup

```bash
npx astro add db
```

## Defining Tables

Define tables in `db/config.ts`:

```ts
import { defineDb, defineTable, column } from 'astro:db';

const Comment = defineTable({
  columns: {
    id: column.number({ primaryKey: true }),
    postSlug: column.text(),
    author: column.text(),
    body: column.text(),
    publishedAt: column.date({ default: new Date() }),
  },
});

const Like = defineTable({
  columns: {
    id: column.number({ primaryKey: true }),
    postSlug: column.text(),
    userId: column.text(),
  },
  indexes: [{ on: ['postSlug', 'userId'], unique: true }],
});

export default defineDb({
  tables: { Comment, Like },
});
```

## Column Types

| Type               | Usage                  |
| ------------------ | ---------------------- |
| `column.text()`    | String values          |
| `column.number()`  | Integer values         |
| `column.boolean()` | True/false             |
| `column.date()`    | Date objects           |
| `column.json()`    | JSON-serializable data |

### Column Options

```ts
const Post = defineTable({
  columns: {
    id: column.number({ primaryKey: true }),
    title: column.text(),
    views: column.number({ default: 0 }),
    metadata: column.json({ optional: true }),
    published: column.boolean({ default: false }),
  },
});
```

## Seeding Data

Create seed data in `db/seed.ts`:

```ts
import { db, Comment } from 'astro:db';

export default async function seed() {
  await db.insert(Comment).values([
    {
      postSlug: 'getting-started',
      author: 'Alice',
      body: 'Great introduction!',
      publishedAt: new Date('2024-01-15'),
    },
    {
      postSlug: 'getting-started',
      author: 'Bob',
      body: 'Very helpful, thanks!',
      publishedAt: new Date('2024-01-16'),
    },
  ]);
}
```

## Querying

### Select All

```astro
---
import { db, Comment } from 'astro:db';

const comments = await db.select().from(Comment);
---
<ul>
  {comments.map((c) => (
    <li>
      <strong>{c.author}</strong>: {c.body}
    </li>
  ))}
</ul>
```

### Filtered Query

```ts
import { db, Comment, eq } from 'astro:db';

const postComments = await db
  .select()
  .from(Comment)
  .where(eq(Comment.postSlug, 'getting-started'))
  .orderBy(Comment.publishedAt);
```

### Insert

```ts
import { db, Comment } from 'astro:db';

await db.insert(Comment).values({
  postSlug: slug,
  author: formData.get('author') as string,
  body: formData.get('body') as string,
});
```

### Update

```ts
import { db, Comment, eq } from 'astro:db';

await db
  .update(Comment)
  .set({ body: 'Updated comment text' })
  .where(eq(Comment.id, commentId));
```

### Delete

```ts
import { db, Comment, eq } from 'astro:db';

await db.delete(Comment).where(eq(Comment.id, commentId));
```

### Join

```ts
import { db, Comment, Like, eq } from 'astro:db';

const commentsWithLikes = await db
  .select()
  .from(Comment)
  .leftJoin(Like, eq(Comment.postSlug, Like.postSlug));
```

## Using in API Routes

Astro DB queries work in server-rendered pages and API endpoints.

```ts
import type { APIRoute } from 'astro';
import { db, Comment, eq } from 'astro:db';

export const GET: APIRoute = async ({ params }) => {
  const comments = await db
    .select()
    .from(Comment)
    .where(eq(Comment.postSlug, params.slug!));

  return new Response(JSON.stringify(comments), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const POST: APIRoute = async ({ request, params }) => {
  const body = await request.json();

  await db.insert(Comment).values({
    postSlug: params.slug!,
    author: body.author,
    body: body.body,
  });

  return new Response(JSON.stringify({ success: true }), { status: 201 });
};
```

## Remote Database

For production, connect to a hosted Astro Studio database or use the `@astrojs/db` libSQL remote driver.

```ts
import { defineConfig } from 'astro/config';
import db from '@astrojs/db';

export default defineConfig({
  integrations: [db()],
});
```

Run `astro db push` to apply schema changes to the remote database.
