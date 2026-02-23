---
title: Queries and Transactions
description: Parameterized queries, sql tagged template, exec, transactions, COPY support, listen/notify, dumpDataDir and loadDataDir
tags: [query, sql, exec, transaction, COPY, listen, notify, dump, load, params]
---

# Queries and Transactions

## Parameterized Queries

The `query` method executes a single SQL statement with optional parameters. Parameters use `$1`, `$2` positional placeholders.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
  )
`);

const result = await db.query<{ id: number; name: string; email: string }>(
  'SELECT * FROM users WHERE email = $1',
  ['alice@example.com'],
);
```

The `QueryResult<T>` type provides:

```ts
interface QueryResult<T> {
  rows: T[];
  fields: { name: string; dataTypeID: number }[];
  affectedRows: number;
}
```

## SQL Tagged Template

The `sql` tagged template literal auto-parameterizes interpolated values, preventing SQL injection.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();
const name = 'Alice';
const email = 'alice@example.com';

const result = await db.sql`
  INSERT INTO users (name, email) VALUES (${name}, ${email})
  RETURNING *
`;
```

Interpolated values become query parameters. Do not use template literals for table or column names; those must be hardcoded in the SQL string.

## Multi-Statement Exec

The `exec` method runs multiple SQL statements in a single call. It does not support parameters and returns void.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.exec(`
  CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );

  CREATE INDEX idx_posts_created ON posts (created_at);
`);
```

Best for schema migrations and setup scripts where parameterization is not needed.

## Transactions

Transactions provide full ACID guarantees. Use `db.transaction()` with an async callback that receives a transaction object.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.transaction(async (tx) => {
  const { rows } = await tx.query<{ balance: number }>(
    'SELECT balance FROM accounts WHERE id = $1 FOR UPDATE',
    [1],
  );

  if (rows[0].balance < 100) {
    throw new Error('Insufficient funds');
  }

  await tx.query(
    'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
    [100, 1],
  );
  await tx.query(
    'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
    [100, 2],
  );
});
```

Throwing inside the callback automatically rolls back the transaction. The `tx` object supports `query`, `sql`, and `exec` with the same signatures as the main `db` instance.

## COPY Support

PGlite supports the Postgres COPY protocol for bulk data import and export.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.exec(`
  CREATE TABLE logs (id SERIAL, message TEXT, level TEXT)
`);

const csvData = `1,Server started,info
2,Connection failed,error
3,Request received,info`;

await db.query(
  "COPY logs (id, message, level) FROM '/dev/blob' WITH (FORMAT csv)",
  [],
  { blob: new Blob([csvData]) },
);
```

## Listen / Notify

PGlite supports Postgres LISTEN/NOTIFY for event-driven communication.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

const unsubscribe = await db.listen('order_created', (payload) => {
  console.log('New order:', payload);
});

await db.query("NOTIFY order_created, 'order-123'");

unsubscribe();
```

Combine with triggers for automatic notifications:

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.exec(`
  CREATE OR REPLACE FUNCTION notify_changes() RETURNS trigger AS $$
  BEGIN
    PERFORM pg_notify('table_changed', TG_TABLE_NAME || ':' || NEW.id);
    RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER orders_notify
    AFTER INSERT ON orders
    FOR EACH ROW EXECUTE FUNCTION notify_changes();
`);
```

## Data Export and Import

### Dump Data Directory

Export the entire database as a compressed blob for backup or transfer.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create('idb://my-app');

const dump = await db.dumpDataDir('gzip');
```

The returned `File` object can be stored in IndexedDB, sent to a server, or saved locally.

### Load Data Directory

Restore a database from a previous dump.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create({
  loadDataDir: previousDump,
});
```

This replaces the entire data directory. Any existing data at the storage location is overwritten.

## Query Result Types

Type query results with a generic parameter for type-safe row access.

```ts
import { PGlite } from '@electric-sql/pglite';

interface User {
  id: number;
  name: string;
  email: string;
  created_at: Date;
}

const db = await PGlite.create();

const { rows } = await db.query<User>('SELECT * FROM users WHERE id = $1', [1]);

const user = rows[0];
```

## Close and Cleanup

Close the database when done to free WASM memory and release storage locks.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.close();
```
