---
title: Live Queries
description: Reactive live queries, incremental queries for large datasets, and change-tracking with live.changes()
tags:
  [
    live,
    reactive,
    live.query,
    live.incrementalQuery,
    live.changes,
    subscription,
    callback,
  ]
---

# Live Queries

## Setup

The live extension must be loaded at construction time.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({
  extensions: { live },
});
```

## live.query()

Re-runs the full query whenever underlying data changes. Best for small to medium result sets.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

await db.exec(`
  CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    done BOOLEAN DEFAULT false
  )
`);

const { rows, unsubscribe } = await db.live.query<{
  id: number;
  task: string;
  done: boolean;
}>('SELECT * FROM todos WHERE done = $1 ORDER BY id', [false], (result) => {
  console.log('Updated todos:', result.rows);
});
```

The callback fires with the full result set each time the query result changes. The initial call returns the current rows.

### Unsubscribing

```ts
unsubscribe();
```

Always unsubscribe when the query is no longer needed to prevent memory leaks.

## live.incrementalQuery()

Computes diffs against previous results instead of re-running the full query. Designed for large result sets where full re-execution is expensive.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

const { rows, unsubscribe } = await db.live.incrementalQuery<{
  id: number;
  title: string;
  body: string;
}>('SELECT * FROM articles ORDER BY id', [], 'id', (result) => {
  console.log('Updated articles:', result.rows);
});
```

The third argument is the **key** column name. This column must uniquely identify each row and is used to compute the diff between result sets. Typically a primary key column.

### When to Use Incremental vs Standard

| Scenario                      | Recommended               |
| ----------------------------- | ------------------------- |
| Small result set (<100 rows)  | `live.query()`            |
| Large result set (100+ rows)  | `live.incrementalQuery()` |
| Need insert/update/delete ops | `live.changes()`          |
| Simple reactive binding       | `live.query()`            |

## live.changes()

Returns raw change operations (insert, update, delete) instead of the full result set. Useful for building custom sync logic or applying granular updates to UI state.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

const { fields, unsubscribe } = await db.live.changes<{
  id: number;
  task: string;
  done: boolean;
}>('SELECT * FROM todos ORDER BY id', [], 'id', (changes) => {
  for (const change of changes) {
    switch (change.__changed__) {
      case 'insert':
        console.log('New row:', change);
        break;
      case 'update':
        console.log('Updated row:', change);
        break;
      case 'delete':
        console.log('Deleted row:', change);
        break;
    }
  }
});
```

Each change object includes the row data plus a `__changed__` field indicating the operation type.

## Windowed / Paginated Live Queries

Combine `live.query()` with `LIMIT` and `OFFSET` for paginated reactive data.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

const PAGE_SIZE = 20;
let currentPage = 0;

const { rows, unsubscribe } = await db.live.query<{
  id: number;
  task: string;
}>(
  'SELECT * FROM todos ORDER BY id LIMIT $1 OFFSET $2',
  [PAGE_SIZE, currentPage * PAGE_SIZE],
  (result) => {
    renderPage(result.rows);
  },
);
```

To change pages, unsubscribe from the current query and create a new one with updated offset parameters.

## Combining Live Queries with Listen/Notify

Live queries automatically detect changes from any query on the same PGlite instance. They do not require explicit NOTIFY calls. The live extension internally tracks table modifications.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

const { unsubscribe } = await db.live.query<{ count: number }>(
  'SELECT count(*)::int as count FROM todos WHERE done = false',
  [],
  (result) => {
    updateBadge(result.rows[0].count);
  },
);

await db.query('INSERT INTO todos (task) VALUES ($1)', ['New task']);
```

## Error Handling

Live query callbacks do not receive errors directly. Handle errors in the initial setup.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({ extensions: { live } });

try {
  const { unsubscribe } = await db.live.query(
    'SELECT * FROM nonexistent_table',
    [],
    (result) => {
      console.log(result.rows);
    },
  );
} catch (error) {
  console.error('Live query setup failed:', error);
}
```

SQL errors in the query itself are thrown at setup time, not in the callback.
