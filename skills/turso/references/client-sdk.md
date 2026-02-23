---
title: Client SDK
description: libSQL client setup, connection modes, configuration options, query execution, and data type handling
tags: [createClient, execute, libsql, connection, authToken, intMode, url]
---

# Client SDK

## Installation

```bash
npm install @libsql/client
```

## Connection Modes

### Remote (Turso Cloud)

```ts
import { createClient } from '@libsql/client';

const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
});
```

### Local File

```ts
import { createClient } from '@libsql/client';

const client = createClient({
  url: 'file:local.db',
});
```

### In-Memory (Testing)

```ts
import { createClient } from '@libsql/client';

const client = createClient({
  url: ':memory:',
});
```

### Encrypted Local Database

```ts
import { createClient } from '@libsql/client';

const client = createClient({
  url: 'file:secure.db',
  encryptionKey: process.env.DB_ENCRYPTION_KEY!,
});
```

## Executing Queries

### Simple Query

```ts
const result = await client.execute('SELECT * FROM users');
console.log(result.rows);
console.log(result.columns);
```

### Positional Parameters

```ts
const result = await client.execute({
  sql: 'SELECT * FROM users WHERE age > ? AND city = ?',
  args: [18, 'New York'],
});
```

### Named Parameters

```ts
const result = await client.execute({
  sql: 'SELECT * FROM users WHERE created_at > $year AND status = $status',
  args: { year: 2020, status: 'active' },
});
```

### Insert with Result

```ts
const result = await client.execute({
  sql: 'INSERT INTO users (name, email) VALUES (?, ?)',
  args: ['Alice Smith', 'alice@example.com'],
});

console.log(result.rowsAffected);
console.log(result.lastInsertRowid);
```

## Result Set Structure

```ts
interface ResultSet {
  columns: string[];
  columnTypes: string[];
  rows: Row[];
  rowsAffected: number;
  lastInsertRowid: bigint | undefined;
}
```

Row values are accessible by column name or index:

```ts
const result = await client.execute(
  'SELECT id, name, email FROM users LIMIT 1',
);
const row = result.rows[0];

row.name;
row[1];
row.length;
```

## Integer Mode Configuration

```ts
const client = createClient({
  url: 'file:local.db',
  intMode: 'bigint',
});
```

| Mode       | Return Type | Use Case                        |
| ---------- | ----------- | ------------------------------- |
| `'number'` | `number`    | Default, safe for values < 2^53 |
| `'bigint'` | `bigint`    | Large integers, row IDs         |
| `'string'` | `string`    | Interop with JSON serialization |

## Data Type Mapping

| SQLite Type | TypeScript Type   | Notes                |
| ----------- | ----------------- | -------------------- |
| TEXT        | `string`          | Strings, dates, JSON |
| INTEGER     | `number`/`bigint` | Depends on `intMode` |
| REAL        | `number`          | Floating-point       |
| BLOB        | `ArrayBuffer`     | Binary data, vectors |
| NULL        | `null`            | Nullable columns     |

## Working with Binary Data

```ts
await client.execute({
  sql: 'INSERT INTO files (data) VALUES (?)',
  args: [new Uint8Array([0x48, 0x65, 0x6c, 0x6c, 0x6f])],
});

const result = await client.execute('SELECT data FROM files WHERE id = 1');
const blob = new Uint8Array(result.rows[0].data as ArrayBuffer);
```

## Cleanup

```ts
client.close();
```

Always close the client when the application shuts down to release resources and flush pending operations.
