---
title: Error Handling
description: ShapeStream error handling, FetchError patterns, HTTP status codes, control messages, txid mismatch handling, retry strategies, and debug logging
tags:
  [
    onError,
    FetchError,
    retry,
    must-refetch,
    409,
    401,
    429,
    5xx,
    txid,
    control-messages,
    backoff,
    debug,
  ]
---

# Error Handling

## ShapeStream onError Callback

The `onError` handler controls retry behavior. Return an object to retry with modified params/headers, or return void to stop syncing.

```ts
import { ShapeStream, FetchError } from '@electric-sql/client';

const stream = new ShapeStream({
  url: '/api/shapes',
  params: { table: 'items' },
  onError: (error) => {
    if (error instanceof FetchError && error.status === 401) {
      return {
        headers: {
          Authorization: `Bearer ${getNewToken()}`,
        },
      };
    }

    if (error instanceof FetchError && error.status === 403) {
      console.error('Access denied, stopping sync');
      return;
    }

    return {};
  },
});
```

### onError Return Types

| Return Value         | Behavior                                           |
| -------------------- | -------------------------------------------------- |
| `void` (no return)   | Stop syncing permanently                           |
| `{}`                 | Retry with same params and headers                 |
| `{ headers: {...} }` | Retry with updated headers (e.g., refreshed token) |
| `{ params: {...} }`  | Retry with updated shape params                    |

The handler can also be async:

```ts
onError: async (error) => {
  if (error instanceof FetchError && error.status === 401) {
    const token = await refreshAccessToken();
    return {
      headers: { Authorization: `Bearer ${token}` },
    };
  }
  return {};
};
```

## FetchError Handling for 401

Token refresh is the most common error recovery pattern:

```ts
import { ShapeStream, FetchError } from '@electric-sql/client';

let accessToken = await getAccessToken();

const stream = new ShapeStream({
  url: '/api/shapes',
  params: { table: 'items' },
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
  onError: async (error) => {
    if (error instanceof FetchError && error.status === 401) {
      accessToken = await refreshAccessToken();
      return {
        headers: { Authorization: `Bearer ${accessToken}` },
      };
    }
    console.error('Unrecoverable shape error:', error);
    return;
  },
});
```

### Dynamic Auth Headers Alternative

Instead of handling 401 in `onError`, use a header function that always provides a fresh token:

```ts
const stream = new ShapeStream({
  url: '/api/shapes',
  params: { table: 'items' },
  headers: {
    Authorization: async () => {
      const token = await getAccessToken();
      return `Bearer ${token}`;
    },
  },
});
```

## HTTP 409: Must-Refetch

A 409 response means the shape has been invalidated on the server. The client must discard its local state and re-sync from scratch with a new handle.

ShapeStream handles this automatically — it resets the offset and handle, then restarts the sync. If you subscribe to messages, you will see a `must-refetch` control message.

```ts
stream.subscribe((messages) => {
  for (const msg of messages) {
    if (msg.headers.control === 'must-refetch') {
      clearLocalCache();
    }
  }
});
```

Causes of 409:

- Server-side shape definition changed
- Electric restarted and lost shape state
- Shape compaction invalidated the previous handle

## Automatic Backoff for 5xx and 429

ShapeStream includes built-in exponential backoff for transient errors:

- **5xx responses**: Server errors trigger automatic retry with backoff
- **429 Too Many Requests**: Rate limiting triggers automatic retry with backoff

No custom `onError` handling is needed for these cases. The stream reconnects automatically with increasing delays.

If you need to observe these retries:

```ts
const stream = new ShapeStream({
  url: '/api/shapes',
  params: { table: 'items' },
  onError: (error) => {
    if (error instanceof FetchError) {
      if (error.status >= 500 || error.status === 429) {
        console.warn(`Transient error ${error.status}, will auto-retry`);
        return {};
      }
    }
    return {};
  },
});
```

## Control Messages

### up-to-date

Signals that the client has received all current changes and is caught up with the server:

```ts
stream.subscribe((messages) => {
  for (const msg of messages) {
    if (msg.headers.control === 'up-to-date') {
      setIsSynced(true);
    }
  }
});
```

### must-refetch

Shape invalidated. ShapeStream handles this internally by resetting and re-syncing. Subscribe to observe it:

```ts
stream.subscribe((messages) => {
  for (const msg of messages) {
    if (msg.headers.control === 'must-refetch') {
      setIsSynced(false);
    }
  }
});
```

### snapshot-end

Marks the end of the initial snapshot batch. All rows from the initial sync have been delivered:

```ts
let snapshotComplete = false;

stream.subscribe((messages) => {
  for (const msg of messages) {
    if (msg.headers.control === 'snapshot-end') {
      snapshotComplete = true;
    }
  }
});
```

## Transaction ID (txid) Handling

After a write, the server returns a `txid` so the client can confirm when Electric has synced the mutation. The txid must come from the **same transaction** as the mutation.

### Correct: txid in Same Transaction

```ts
app.post('/api/todos', async (req, res) => {
  const result = await db.transaction(async (tx) => {
    const [todo] = await tx
      .insert(todos)
      .values({ title: req.body.title, userId: req.user.id })
      .returning();

    const [{ txid }] = await tx.execute<{ txid: string }>(
      sql`SELECT pg_current_xact_id()::text AS txid`,
    );

    return { todo, txid };
  });

  res.json(result);
});
```

### Common txid Pitfalls

**Querying txid in a separate transaction:**

```ts
const [todo] = await db.insert(todos).values(data).returning();
const [{ txid }] = await db.execute(
  sql`SELECT pg_current_xact_id()::text AS txid`,
);
```

This returns the wrong txid because `pg_current_xact_id()` runs in a different transaction than the insert. The client will wait for a txid that does not correspond to its mutation.

**Not awaiting txid confirmation on the client:**

```ts
const result = await createTodo({ data: newTodo });
```

Without passing `result.txid` to the Electric collection's `onInsert` return, the client cannot confirm when the mutation is synced.

### Client-Side txid Flow

```ts
import { createCollection } from '@tanstack/react-db';
import { electricCollectionOptions } from '@tanstack/electric-db-collection';

const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: { url: '/api/shapes/todos' },
    onInsert: async ({ transaction }) => {
      const newTodo = transaction.mutations[0].modified;
      const result = await createTodo({ data: newTodo });
      return { txid: result.txid };
    },
    onUpdate: async ({ transaction }) => {
      const changed = transaction.mutations[0].modified;
      const result = await updateTodo({ data: changed });
      return { txid: result.txid };
    },
  }),
);
```

## Debug Logging for txid Flow

Track the full txid lifecycle to diagnose sync confirmation issues:

```ts
app.post('/api/todos', async (req, res) => {
  const result = await db.transaction(async (tx) => {
    const [todo] = await tx
      .insert(todos)
      .values({ title: req.body.title, userId: req.user.id })
      .returning();

    const [{ txid }] = await tx.execute<{ txid: string }>(
      sql`SELECT pg_current_xact_id()::text AS txid`,
    );

    console.log(`[txid] Mutation committed: txid=${txid}, todoId=${todo.id}`);
    return { todo, txid };
  });

  res.json(result);
});
```

On the client:

```ts
onInsert: async ({ transaction }) => {
  const newTodo = transaction.mutations[0].modified;
  const result = await createTodo({ data: newTodo });
  console.log(`[txid] Awaiting sync confirmation: txid=${result.txid}`);
  return { txid: result.txid };
},
```

## Client-Side Sync Failure Tracking

Monitor error rates to detect persistent sync issues:

```ts
function createSyncMonitor(stream: ShapeStream) {
  let errorCount = 0;
  let lastErrorAt: Date | null = null;
  const ERROR_THRESHOLD = 5;
  const WINDOW_MS = 60_000;

  stream.subscribe(() => {
    errorCount = 0;
  });

  return {
    onError: (error: Error) => {
      errorCount++;
      lastErrorAt = new Date();

      if (errorCount >= ERROR_THRESHOLD) {
        console.error(`[sync] ${errorCount} errors in monitoring window`, {
          lastError: error.message,
          since: lastErrorAt,
        });
      }

      return {};
    },
    getStatus: () => ({
      errorCount,
      lastErrorAt,
      isHealthy: errorCount < ERROR_THRESHOLD,
    }),
  };
}

const monitor = createSyncMonitor(stream);
const stream = new ShapeStream({
  url: '/api/shapes',
  params: { table: 'items' },
  onError: monitor.onError,
});
```
