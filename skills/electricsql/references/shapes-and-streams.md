---
title: Shapes and Streams
description: Shape concept, HTTP API cycle, ShapeStream and Shape classes, React useShape hook, where clauses, column selection, progressive loading, and message types
tags:
  [
    Shape,
    ShapeStream,
    useShape,
    where-clause,
    columns,
    offset,
    handle,
    subscribe,
    live-updates,
    SSE,
    parser,
    control-messages,
  ]
---

## Shape Concept

A Shape is a defined subset of a single Postgres table that syncs to clients. It combines three dimensions:

- **Table**: Which Postgres table to sync from
- **Where clause**: Which rows to include (optional filter)
- **Columns**: Which columns to sync (optional projection)

Electric streams the shape's data to clients and keeps it up-to-date in real-time using Postgres logical replication. Shapes are read-only on the client; writes flow through your API back to Postgres.

## HTTP API

### Initial Sync

```text
GET /v1/shape?table=items&offset=-1
```

Returns the full current state of the shape as a batch of insert messages, ending with an `up-to-date` control message. The response includes headers:

- `electric-handle`: Unique identifier for this shape instance
- `electric-offset`: Position in the log to resume from

### Live Updates (Long Polling)

After initial sync, poll for changes:

```text
GET /v1/shape?table=items&live=true&handle=3948593&offset=0_5
```

The request blocks until new changes arrive or a timeout occurs. Each response includes updated `electric-offset` for the next request.

### Live Updates (Server-Sent Events)

For persistent streaming instead of long polling:

```text
GET /v1/shape?table=items&live=true&live_sse=true&handle=3948593&offset=0_5
```

Returns a persistent SSE connection that pushes changes as they occur.

### Request Lifecycle

```text
1. Client sends:    GET /v1/shape?table=items&offset=-1
2. Electric returns: Full snapshot + electric-handle + electric-offset
3. Client sends:    GET /v1/shape?table=items&live=true&handle=<handle>&offset=<offset>
4. Electric returns: New changes (or blocks until changes arrive)
5. Repeat step 3-4
```

## ShapeStream

Low-level streaming client that handles the HTTP lifecycle automatically.

### Constructor

```ts
import { ShapeStream } from '@electric-sql/client';

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
    where: "status = 'active'",
    columns: 'id,title,status,updated_at',
    replica: 'full',
  },
  headers: {
    Authorization: 'Bearer my-token',
  },
});
```

### Subscribe to Messages

```ts
const unsubscribe = stream.subscribe((messages) => {
  for (const msg of messages) {
    if (msg.headers.operation === 'insert') {
      console.log('Insert:', msg.key, msg.value);
    }
    if (msg.headers.operation === 'update') {
      console.log('Update:', msg.key, msg.value);
    }
    if (msg.headers.operation === 'delete') {
      console.log('Delete:', msg.key);
    }
    if (msg.headers.control === 'up-to-date') {
      console.log('Caught up with Postgres');
    }
    if (msg.headers.control === 'must-refetch') {
      console.log('Shape invalidated, refetching');
    }
  }
});

unsubscribe();
```

### Error Handling

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'items' },
  onError: (error) => {
    if (error instanceof FetchError && error.status === 401) {
      console.log('Token expired, refreshing...');
      return;
    }
    console.error('Stream error:', error);
  },
});
```

### Dynamic Auth Headers

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'items' },
  headers: {
    Authorization: async () => {
      const token = await getAccessToken();
      return `Bearer ${token}`;
    },
  },
});
```

## Shape Class

Materializes a ShapeStream into an in-memory `Map` of current values. The Shape maintains the latest state by applying inserts, updates, and deletes from the stream.

```ts
import { Shape, ShapeStream } from '@electric-sql/client';

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'items' },
});

const shape = new Shape(stream);

shape.subscribe((data) => {
  const rows = [...data.values()];
  console.log(`${rows.length} items synced`);
});

const currentData = shape.currentValue;
```

`currentValue` returns a `Map<string, Row>` keyed by the row's primary key. Each subscription fires when the map changes.

## React Hook: useShape

```tsx
import { useShape } from '@electric-sql/react';

type Item = {
  id: string;
  title: string;
  status: string;
  created_at: string;
};

function ActiveItems() {
  const { data, isLoading, isError, error, lastSyncedAt } = useShape<Item>({
    url: 'http://localhost:3000/v1/shape',
    params: {
      table: 'items',
      where: "status = 'active'",
      columns: 'id,title,status,created_at',
    },
  });

  if (isLoading) return <div>Syncing...</div>;
  if (isError) return <div>Sync error: {error?.message}</div>;

  return (
    <div>
      <p>Last synced: {lastSyncedAt?.toLocaleTimeString()}</p>
      <ul>
        {data.map((item) => (
          <li key={item.id}>{item.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

### useShape Return Values

| Property       | Type                 | Description                          |
| -------------- | -------------------- | ------------------------------------ |
| `data`         | `T[]`                | Array of synced rows                 |
| `isLoading`    | `boolean`            | True during initial sync             |
| `isError`      | `boolean`            | True when stream encounters an error |
| `error`        | `Error \| undefined` | Error object if `isError` is true    |
| `lastSyncedAt` | `Date \| undefined`  | Timestamp of last successful sync    |

## Where Clauses

Filter rows server-side to sync only matching data.

### Basic Syntax

```text
?where=status='active'
?where=price > 100
?where=category='electronics' AND in_stock=true
```

### Supported Operators

| Operator      | Example                          |
| ------------- | -------------------------------- |
| `=`           | `status='active'`                |
| `!=`          | `status!='archived'`             |
| `>`, `>=`     | `price > 100`                    |
| `<`, `<=`     | `quantity <= 0`                  |
| `IN`          | `status IN ('active','pending')` |
| `IS NULL`     | `deleted_at IS NULL`             |
| `IS NOT NULL` | `assigned_to IS NOT NULL`        |
| `AND`         | `status='active' AND price > 50` |

### Parameterized Queries

Always use parameterized queries when the where clause includes user input:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
    where: 'user_id = $1 AND status = $2',
    'params[1]': userId,
    'params[2]': 'active',
  },
});
```

```tsx
const { data } = useShape<Item>({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
    where: 'user_id = $1',
    'params[1]': currentUser.id,
  },
});
```

## Column Selection

Reduce bandwidth by syncing only needed columns:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
    columns: 'id,title,status',
  },
});
```

The primary key column is always included even if not specified in `columns`.

## Progressive Loading

### Changes Only Mode

Skip the initial snapshot and receive only new changes going forward:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
  },
  offset: 'now',
});
```

### Full Replica Mode

By default, update and delete messages include only changed columns. Use `replica=full` to get complete row data on every change:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
    replica: 'full',
  },
});
```

## Custom Parsers

Override default type parsing for specific columns:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'items' },
  parser: {
    timestamptz: (value: string) => new Date(value),
    int4: (value: string) => Number(value),
    bool: (value: string) => value === 'true',
  },
});
```

## Message Types

### Data Messages

Every data message includes `headers` with an `operation` field and a `key` field.

**Insert:**

```ts
{
  headers: { operation: 'insert' },
  key: '"items"/"abc-123"',
  value: { id: 'abc-123', title: 'Buy groceries', status: 'active' },
  offset: '0_3'
}
```

**Update:**

```ts
{
  headers: { operation: 'update' },
  key: '"items"/"abc-123"',
  value: { status: 'completed' },
  offset: '0_4'
}
```

With `replica=full`, `value` contains all columns, not just changed ones.

**Delete:**

```ts
{
  headers: { operation: 'delete' },
  key: '"items"/"abc-123"',
  value: { id: 'abc-123' },
  offset: '0_5'
}
```

### Control Messages

**up-to-date**: Client has received all current changes and is caught up.

```ts
{
  headers: {
    control: 'up-to-date';
  }
}
```

**must-refetch**: Shape has been invalidated. Client must restart the sync from `offset=-1`.

```ts
{
  headers: {
    control: 'must-refetch';
  }
}
```

ShapeStream handles `must-refetch` automatically by resetting and re-syncing.

## Typed Shapes

```ts
type Todo = {
  id: string;
  title: string;
  completed: boolean;
  user_id: string;
  created_at: string;
};

const stream = new ShapeStream<Todo>({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'todos',
    where: 'user_id = $1',
    'params[1]': userId,
    columns: 'id,title,completed,user_id,created_at',
  },
});

const shape = new Shape<Todo>(stream);

shape.subscribe((data: Map<string, Todo>) => {
  const todos = [...data.values()];
  const incomplete = todos.filter((t) => !t.completed);
  console.log(`${incomplete.length} remaining todos`);
});
```
