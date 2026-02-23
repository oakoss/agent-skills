---
title: Multi-Collection Patterns
description: Cross-collection transactions, joins, mutation merging, batching, and collection lifecycle
tags:
  [
    multi-collection,
    transactions,
    joins,
    batching,
    lifecycle,
    cross-collection,
    merging,
    pacing,
  ]
---

# Multi-Collection Patterns

TanStack DB supports coordinated operations across multiple collections through explicit transactions, cross-collection live query joins, and lifecycle management.

## Cross-Collection Transactions

Use `createTransaction` to group mutations across multiple collections into a single atomic unit. All mutations succeed or all roll back:

```ts
import { createTransaction } from '@tanstack/db';

const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    await api.createProjectWithTasks({
      project: transaction.mutations
        .filter((m) => m.collection === 'projects')
        .map((m) => m.modified),
      tasks: transaction.mutations
        .filter((m) => m.collection === 'tasks')
        .map((m) => m.modified),
    });
  },
});

tx.mutate(() => {
  projectCollection.insert({
    id: 'proj-1',
    name: 'New Project',
    status: 'active',
  });
  taskCollection.insert({
    id: 'task-1',
    projectId: 'proj-1',
    title: 'Setup',
    done: false,
  });
  taskCollection.insert({
    id: 'task-2',
    projectId: 'proj-1',
    title: 'Implementation',
    done: false,
  });
});

tx.commit();

try {
  await tx.isPersisted.promise;
} catch {
  // All mutations across both collections rolled back
}
```

## Auto-Commit Control

By default, transactions auto-commit after each `mutate()` call. Set `autoCommit: false` to accumulate mutations across multiple `mutate()` calls before committing:

```ts
const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    await api.saveBatch(transaction.mutations);
  },
  autoCommit: false,
});

// First batch of mutations
tx.mutate(() => {
  projectCollection.insert({ id: 'p1', name: 'Alpha', status: 'active' });
});

// Second batch based on user input
tx.mutate(() => {
  taskCollection.insert({
    id: 't1',
    projectId: 'p1',
    title: 'First task',
    done: false,
  });
});

// Commit all accumulated mutations at once
tx.commit();
```

## Mutation Merging Rules

When multiple mutations target the same item within a single transaction, TanStack DB merges them:

| First Mutation | Second Mutation | Result                             |
| -------------- | --------------- | ---------------------------------- |
| insert         | update          | Single insert with updated values  |
| insert         | delete          | Both mutations cancel out (no-op)  |
| update         | update          | Single update with merged changes  |
| update         | delete          | Single delete                      |
| delete         | insert          | Single update (delete then re-add) |

```ts
const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    // transaction.mutations contains merged results
    await api.saveBatch(transaction.mutations);
  },
  autoCommit: false,
});

tx.mutate(() => {
  // Insert then immediately update = single insert with final values
  todoCollection.insert({ id: '1', text: 'Draft', completed: false });
  todoCollection.update('1', (draft) => {
    draft.text = 'Final text';
  });
});

tx.commit();
// The handler receives one insert mutation with text: 'Final text'
```

## Cross-Collection Live Query Joins

Live queries can join data across collections with type-safe results:

### Left Join

```ts
import { useLiveQuery } from '@tanstack/react-db';
import { eq } from '@tanstack/db';

function ProjectsWithTasks() {
  const { rows } = useLiveQuery((q) =>
    q
      .from({ project: projectCollection })
      .join(
        { task: taskCollection },
        ({ project, task }) => eq(project.id, task.projectId),
        'left',
      )
      .select(({ project, task }) => ({
        projectName: project.name,
        taskTitle: task.title,
        taskDone: task.done,
      })),
  );

  return (
    <ul>
      {rows.map((row, i) => (
        <li key={i}>
          {row.projectName}: {row.taskTitle ?? 'No tasks'}
        </li>
      ))}
    </ul>
  );
}
```

### Inner Join

```ts
const { rows } = useLiveQuery((q) =>
  q
    .from({ project: projectCollection })
    .join(
      { task: taskCollection },
      ({ project, task }) => eq(project.id, task.projectId),
      'inner',
    )
    .where(({ task }) => eq(task.done, false))
    .orderBy(({ project }) => project.name, 'asc'),
);
```

## All-or-Nothing Rollback

When a cross-collection transaction fails, all mutations across all collections roll back atomically:

```ts
const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    // If this throws, both the project insert and task inserts revert
    await api.createProjectWithTasks(transaction.mutations);
  },
});

tx.mutate(() => {
  projectCollection.insert({ id: 'p1', name: 'Project', status: 'active' });
  taskCollection.insert({
    id: 't1',
    projectId: 'p1',
    title: 'Task A',
    done: false,
  });
  taskCollection.insert({
    id: 't2',
    projectId: 'p1',
    title: 'Task B',
    done: false,
  });
});

tx.commit();
```

## Chunked Batching for Provider Limits

When a provider has request size limits, chunk mutations into smaller batches within the persistence handler:

```ts
function chunk<T>(arr: Array<T>, size: number): Array<Array<T>> {
  const chunks: Array<Array<T>> = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['items'],
    queryFn: fetchItems,
    getKey: (item) => item.id,
    onInsert: async ({ transaction }) => {
      const batches = chunk(transaction.mutations, 25);
      for (const batch of batches) {
        await api.createItems(batch.map((m) => m.modified));
      }
    },
  }),
);
```

## Paced Mutations for Rate-Limited Providers

Add delays between batches when the backend enforces rate limits:

```ts
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['items'],
    queryFn: fetchItems,
    getKey: (item) => item.id,
    onUpdate: async ({ transaction }) => {
      const batches = chunk(transaction.mutations, 10);
      for (let i = 0; i < batches.length; i++) {
        if (i > 0) await delay(100);
        await api.updateItems(
          batches[i].map((m) => ({ id: m.key, changes: m.changes })),
        );
      }
    },
  }),
);
```

## Collection Lifecycle

### Lazy Initialization

Collections initialize lazily when first accessed by a live query or mutation. No data is fetched until the collection is used.

### Garbage Collection

Collections support automatic cleanup via `gcTime`. When no live queries reference a collection, it is garbage collected after the specified duration:

```ts
const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['items'],
    queryFn: fetchItems,
    getKey: (item) => item.id,
    gcTime: 5 * 60 * 1000, // 5 minutes after last subscriber
  }),
);
```

### Manual Cleanup

Call `cleanup()` to immediately dispose of a collection and release its resources:

```ts
// Tear down collection manually
collection.cleanup();
```

Use manual cleanup for collections tied to a specific view or workflow that should not persist in memory after navigation.
