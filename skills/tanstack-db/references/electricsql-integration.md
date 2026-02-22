---
title: ElectricSQL Integration
description: Electric collection options, real-time Postgres sync, write handlers with txid, sync modes, and error handling for TanStack DB with ElectricSQL
tags:
  [
    electricsql,
    electric-collection,
    electricCollectionOptions,
    sync,
    txid,
    shapes,
    real-time,
    postgres,
  ]
---

# ElectricSQL Integration

## Installation

```bash
npm install @tanstack/react-db @tanstack/electric-db-collection
```

The Electric collection package connects TanStack DB to ElectricSQL's shape-based sync. Data flows from Postgres → Electric → ShapeStream → collection, with live queries reacting to every change.

## Basic Electric Collection

```ts
import { createCollection } from '@tanstack/react-db';
import { electricCollectionOptions } from '@tanstack/electric-db-collection';

type Todo = {
  id: string;
  title: string;
  completed: boolean;
  user_id: string;
  created_at: string;
};

const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: 'http://localhost:3000/v1/shape',
      params: {
        table: 'todos',
      },
    },
  }),
);
```

## electricCollectionOptions API

| Option         | Required | Type                                             | Description                                            |
| -------------- | -------- | ------------------------------------------------ | ------------------------------------------------------ |
| `id`           | Yes      | `string`                                         | Unique collection identifier                           |
| `getKey`       | Yes      | `(row: T) => string \| number`                   | Extract unique key from each row                       |
| `shapeOptions` | Yes      | `ShapeStreamOptions`                             | ElectricSQL shape configuration                        |
| `schema`       | No       | `ZodSchema`                                      | Runtime validation for incoming rows                   |
| `onInsert`     | No       | `(ctx: MutationContext<T>) => Promise<TxResult>` | Handler for optimistic inserts                         |
| `onUpdate`     | No       | `(ctx: MutationContext<T>) => Promise<TxResult>` | Handler for optimistic updates                         |
| `onDelete`     | No       | `(ctx: MutationContext<T>) => Promise<TxResult>` | Handler for optimistic deletes                         |
| `syncMode`     | No       | `'eager' \| 'on-demand' \| 'progressive'`        | How data loads on collection init (default: `'eager'`) |

## Shape Options

The `shapeOptions` object maps directly to ElectricSQL's ShapeStream configuration:

```ts
const filteredCollection = createCollection(
  electricCollectionOptions({
    id: 'active-todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: '/api/shapes/todos',
      params: {
        table: 'todos',
        where: 'completed = false',
        columns: 'id,title,completed,created_at',
      },
    },
  }),
);
```

| Shape Param | Description                                      |
| ----------- | ------------------------------------------------ |
| `table`     | Postgres table name                              |
| `where`     | SQL where clause for server-side filtering       |
| `columns`   | Comma-separated column names to sync             |
| `replica`   | Set to `'full'` for complete row data on updates |
| `log`       | Set to `'changes_only'` to skip initial snapshot |

## Write Handlers with txid

Write handlers persist optimistic mutations to your API. Returning `{ txid }` tells TanStack DB to keep the optimistic state until Electric confirms the write has propagated back through the sync stream.

```ts
const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: '/api/shapes/todos',
      params: { table: 'todos' },
    },
    onInsert: async ({ transaction }) => {
      const newTodo = transaction.mutations[0].modified;
      const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTodo),
      });
      const { txid } = await response.json();
      return { txid };
    },
    onUpdate: async ({ transaction }) => {
      const { original, modified, changes } = transaction.mutations[0];
      const response = await fetch(`/api/todos/${original.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changes),
      });
      const { txid } = await response.json();
      return { txid };
    },
    onDelete: async ({ transaction }) => {
      const key = transaction.mutations[0].key;
      const response = await fetch(`/api/todos/${key}`, {
        method: 'DELETE',
      });
      const { txid } = await response.json();
      return { txid };
    },
  }),
);
```

## txid Flow

The transaction ID (`txid`) connects the write path to the read path:

1. Client calls `collection.insert(item)` — UI updates immediately (optimistic)
2. `onInsert` handler sends data to your API
3. API writes to Postgres, returns `txid` (e.g., the LSN or a UUID)
4. Handler returns `{ txid }` to TanStack DB
5. TanStack DB watches the Electric shape stream for this `txid`
6. When Electric syncs the confirmed row back, optimistic state is replaced with server state
7. If `txid` is not returned, optimistic state is discarded on next shape sync

## Batch Mutations

Write handlers receive all mutations in a transaction, enabling batch operations:

```ts
onInsert: async ({ transaction }) => {
  const newItems = transaction.mutations.map((m) => m.modified)
  const response = await fetch('/api/todos/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: newItems }),
  })
  const { txid } = await response.json()
  return { txid }
},
```

## Sync Modes

```ts
const eagerCollection = createCollection(
  electricCollectionOptions({
    id: 'small-dataset',
    getKey: (row: Todo) => row.id,
    syncMode: 'eager',
    shapeOptions: {
      url: '/api/shapes/todos',
      params: { table: 'todos' },
    },
  }),
);

const onDemandCollection = createCollection(
  electricCollectionOptions({
    id: 'large-dataset',
    getKey: (row: Item) => row.id,
    syncMode: 'on-demand',
    shapeOptions: {
      url: '/api/shapes/items',
      params: { table: 'items' },
    },
  }),
);

const progressiveCollection = createCollection(
  electricCollectionOptions({
    id: 'progressive-dataset',
    getKey: (row: Item) => row.id,
    syncMode: 'progressive',
    shapeOptions: {
      url: '/api/shapes/items',
      params: { table: 'items' },
    },
  }),
);
```

| Mode          | Initial Load                     | Best For                        |
| ------------- | -------------------------------- | ------------------------------- |
| `eager`       | All records loaded immediately   | Small datasets (< 1k rows)      |
| `on-demand`   | Only loads what queries request  | Large datasets, filtered views  |
| `progressive` | Fast first paint, full sync next | Balanced UX with large datasets |

## Live Queries with Electric Collections

Electric collections work with all TanStack DB live query features:

```tsx
import { useLiveQuery } from '@tanstack/react-db';
import { eq, and, gt } from '@tanstack/db/query';

function RecentActiveTodos() {
  const { data: todos } = useLiveQuery((q) =>
    q
      .from({ todos: todoCollection })
      .where(({ todos: t }) =>
        and(eq(t.completed, false), gt(t.created_at, '2024-01-01')),
      )
      .orderBy(({ todos: t }) => t.created_at, 'desc'),
  );

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  );
}
```

## Cross-Collection Joins

Join Electric-synced collections with other collection types:

```tsx
import { useLiveQuery } from '@tanstack/react-db';
import { eq } from '@tanstack/db/query';

function TodosWithUsers() {
  const { data } = useLiveQuery((q) =>
    q
      .from({ todos: todoCollection })
      .join(
        { users: userCollection },
        ({ todos, users }) => eq(todos.user_id, users.id),
        'inner',
      )
      .select(({ todos, users }) => ({
        id: todos.id,
        title: todos.title,
        userName: users.name,
      })),
  );

  return (
    <ul>
      {data.map((item) => (
        <li key={item.id}>
          {item.title} — {item.userName}
        </li>
      ))}
    </ul>
  );
}
```

## Error Handling

```ts
const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: '/api/shapes/todos',
      params: { table: 'todos' },
      onError: async (error) => {
        if (error instanceof FetchError && error.status === 401) {
          const newToken = await refreshAuthToken();
          return { headers: { Authorization: `Bearer ${newToken}` } };
        }
        return {};
      },
    },
    onInsert: async ({ transaction }) => {
      try {
        const newTodo = transaction.mutations[0].modified;
        const response = await fetch('/api/todos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newTodo),
        });
        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const { txid } = await response.json();
        return { txid };
      } catch (error) {
        throw error;
      }
    },
  }),
);
```

When a write handler throws, TanStack DB automatically rolls back the optimistic mutation, restoring the collection to its pre-mutation state.

## Auth Proxy Pattern

In production, route shape requests through your API instead of exposing Electric directly:

```ts
const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    getKey: (row: Todo) => row.id,
    shapeOptions: {
      url: '/api/shapes/todos',
      params: { table: 'todos' },
      headers: {
        Authorization: async () => `Bearer ${await getAccessToken()}`,
      },
    },
  }),
);
```

The proxy server validates the token and forwards the request to Electric with appropriate where clause filtering per user.
