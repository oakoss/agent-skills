---
title: Schema Migrations
description: Schema management strategies, migration patterns, database seeding, and schema-from-database workflows
tags: [migration, schema, alter-table, seed, dump, schema-from-db]
---

# Schema Migrations

## Manual Migration Pattern

For direct SQL migrations without an ORM:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### TypeScript Migration Runner

```ts
import { createClient } from '@libsql/client';

interface Migration {
  version: number;
  sql: string;
}

const migrations: Migration[] = [
  {
    version: 1,
    sql: `CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL
    )`,
  },
  {
    version: 2,
    sql: `ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT (datetime('now'))`,
  },
  {
    version: 3,
    sql: `CREATE INDEX idx_users_email ON users(email)`,
  },
];

async function migrate(client: ReturnType<typeof createClient>) {
  await client.execute(`
    CREATE TABLE IF NOT EXISTS schema_migrations (
      version INTEGER PRIMARY KEY,
      applied_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
  `);

  const applied = await client.execute(
    'SELECT version FROM schema_migrations ORDER BY version',
  );
  const appliedVersions = new Set(applied.rows.map((r) => r.version as number));

  const pending = migrations.filter((m) => !appliedVersions.has(m.version));

  for (const migration of pending) {
    await client.batch(
      [
        migration.sql,
        {
          sql: 'INSERT INTO schema_migrations (version) VALUES (?)',
          args: [migration.version],
        },
      ],
      'write',
    );
  }

  return pending.length;
}
```

## SQLite Schema Constraints

SQLite has limited `ALTER TABLE` support:

| Operation          | Supported | Alternative                              |
| ------------------ | --------- | ---------------------------------------- |
| Add column         | Yes       | `ALTER TABLE t ADD COLUMN c TYPE`        |
| Rename column      | Yes       | `ALTER TABLE t RENAME COLUMN old TO new` |
| Drop column        | Yes       | `ALTER TABLE t DROP COLUMN c`            |
| Change column type | No        | Recreate table with new schema           |
| Add constraint     | No        | Recreate table with constraint           |
| Rename table       | Yes       | `ALTER TABLE old RENAME TO new`          |

### Table Recreation Pattern

For unsupported alterations, recreate the table:

```sql
BEGIN TRANSACTION;

CREATE TABLE users_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active'
);

INSERT INTO users_new (id, email, name)
  SELECT id, email, name FROM users;

DROP TABLE users;

ALTER TABLE users_new RENAME TO users;

COMMIT;
```

## Database Seeding

```ts
async function seed(client: ReturnType<typeof createClient>) {
  await client.batch(
    [
      {
        sql: 'INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)',
        args: ['admin@example.com', 'Admin'],
      },
      {
        sql: 'INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)',
        args: ['demo@example.com', 'Demo User'],
      },
    ],
    'write',
  );
}
```

## Schema from Existing Database

### Dump Full Schema

```bash
turso db shell my-app .schema > schema.sql
```

### Create Database from Dump

```bash
turso db create my-app-staging
turso db shell my-app-staging < schema.sql
```

### Clone Database

```bash
turso db create my-app-staging --from-db my-app
```

## Environment-Specific Configuration

```ts
import { createClient } from '@libsql/client';

function createDbClient() {
  if (process.env.NODE_ENV === 'test') {
    return createClient({ url: ':memory:' });
  }

  if (process.env.NODE_ENV === 'development') {
    return createClient({ url: 'file:dev.db' });
  }

  return createClient({
    url: process.env.TURSO_DATABASE_URL!,
    authToken: process.env.TURSO_AUTH_TOKEN!,
  });
}

export const client = createDbClient();
```
