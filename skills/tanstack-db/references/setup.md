---
title: Setup and Configuration
description: Installation, package selection, creating collections, and configuring data sources for TanStack DB
tags:
  [
    installation,
    setup,
    collections,
    configuration,
    query-collection,
    electric-collection,
  ]
---

# Setup and Configuration

## Installation

Install the framework-specific package (it re-exports everything from `@tanstack/db`):

```bash
npm install @tanstack/react-db
```

For Vue applications:

```bash
npm install @tanstack/vue-db
```

Install collection type packages based on your data source:

```bash
npm install @tanstack/query-db-collection
npm install @tanstack/electric-db-collection
npm install @tanstack/trailbase-db-collection
npm install @tanstack/rxdb-db-collection
```

## Collection Types

| Package                             | Use Case                                         |
| ----------------------------------- | ------------------------------------------------ |
| `@tanstack/query-db-collection`     | REST APIs and GraphQL via TanStack Query         |
| `@tanstack/electric-db-collection`  | Real-time Postgres sync via ElectricSQL          |
| `@tanstack/trailbase-db-collection` | TrailBase backend integration                    |
| `@tanstack/rxdb-db-collection`      | RxDB reactive database integration               |
| Built-in: LocalStorage              | Persistent local data, syncs across browser tabs |
| Built-in: LocalOnly                 | Temporary in-memory data and UI state            |

## Query Collection (REST APIs)

The most common setup pairs TanStack DB with TanStack Query for REST APIs:

```ts
import { createCollection } from '@tanstack/react-db';
import { queryCollectionOptions } from '@tanstack/query-db-collection';

const todoCollection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: async () => {
      const response = await fetch('/api/todos');
      return response.json();
    },
    getKey: (item) => item.id,
    onUpdate: async ({ transaction }) => {
      const { original, modified } = transaction.mutations[0];
      await fetch(`/api/todos/${original.id}`, {
        method: 'PUT',
        body: JSON.stringify(modified),
      });
    },
  }),
);
```

Key options for `queryCollectionOptions`:

| Option     | Required | Description                                        |
| ---------- | -------- | -------------------------------------------------- |
| `queryKey` | Yes      | TanStack Query cache key                           |
| `queryFn`  | Yes      | Fetch function returning array of items            |
| `getKey`   | Yes      | Function returning unique identifier for each item |
| `onInsert` | No       | Handler called when items are inserted             |
| `onUpdate` | No       | Handler called when items are updated              |
| `onDelete` | No       | Handler called when items are deleted              |

## Query Collection with Full CRUD Handlers

```ts
import { createCollection } from '@tanstack/react-db';
import { queryCollectionOptions } from '@tanstack/query-db-collection';

const todosCollection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    queryClient,
    getKey: (item) => item.id,
    onInsert: async ({ transaction }) => {
      const newItems = transaction.mutations.map((m) => m.modified);
      await api.createTodos(newItems);
    },
    onUpdate: async ({ transaction }) => {
      const updates = transaction.mutations.map((m) => ({
        id: m.key,
        changes: m.changes,
      }));
      await api.updateTodos(updates);
    },
    onDelete: async ({ transaction }) => {
      const ids = transaction.mutations.map((m) => m.key);
      await api.deleteTodos(ids);
    },
  }),
);
```

## ElectricSQL Collection (Real-Time Sync)

For real-time sync from Postgres using ElectricSQL:

```ts
import { createCollection } from '@tanstack/react-db';
import { electricCollectionOptions } from '@tanstack/electric-db-collection';

const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    schema: todoSchema,
    shapeOptions: {
      url: 'https://api.electric-sql.cloud/v1/shape',
      params: {
        table: 'todos',
      },
    },
    getKey: (item) => item.id,
    onInsert: async ({ transaction }) => {
      const response = await api.todos.create(
        transaction.mutations[0].modified,
      );
      return { txid: response.txid };
    },
  }),
);
```

## TrailBase Collection

```ts
import { createCollection } from '@tanstack/react-db';
import { trailBaseCollectionOptions } from '@tanstack/trailbase-db-collection';

const todosCollection = createCollection(
  trailBaseCollectionOptions({
    id: 'todos',
    recordApi: trailBaseClient.records('todos'),
    getKey: (item) => item.id,
    onInsert: async ({ transaction }) => {
      const newTodo = transaction.mutations[0].modified;
    },
    onUpdate: async ({ transaction }) => {
      const { original, modified } = transaction.mutations[0];
    },
  }),
);
```

## Module-Level Declaration

Collections should be defined at module scope, not inside components:

```ts
import { createCollection } from '@tanstack/react-db';
import { queryCollectionOptions } from '@tanstack/query-db-collection';

const userCollection = createCollection(
  queryCollectionOptions({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then((r) => r.json()),
    getKey: (user) => user.id,
  }),
);

const postCollection = createCollection(
  queryCollectionOptions({
    queryKey: ['posts'],
    queryFn: () => fetch('/api/posts').then((r) => r.json()),
    getKey: (post) => post.id,
  }),
);

export { userCollection, postCollection };
```
