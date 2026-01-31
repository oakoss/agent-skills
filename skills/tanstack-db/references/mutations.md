---
title: Mutations
description: Optimistic mutations, persistence handlers, conflict resolution, and sync patterns
tags:
  [
    mutations,
    optimistic,
    insert,
    update,
    delete,
    sync,
    persistence,
    transactions,
  ]
---

# Mutations

TanStack DB mutations are optimistic by default. Changes apply instantly to the local collection and UI, then sync to the server via persistence handlers. If the server request fails, changes roll back automatically.

## Insert

```tsx
function AddTodo() {
  const addTodo = () => {
    todoCollection.insert({
      id: crypto.randomUUID(),
      text: 'New todo',
      completed: false,
      createdAt: new Date(),
    });
  };

  return <button onClick={addTodo}>Add Todo</button>;
}
```

## Update

Updates use an Immer-style draft pattern for immutable mutations:

```tsx
function ToggleTodo({ todo }: { todo: Todo }) {
  const toggleComplete = () => {
    todoCollection.update(todo.id, (draft) => {
      draft.completed = !draft.completed;
    });
  };

  const updateText = (newText: string) => {
    todoCollection.update(todo.id, (draft) => {
      draft.text = newText;
    });
  };

  return (
    <div>
      <button onClick={toggleComplete}>Toggle</button>
      <button onClick={() => updateText('Updated!')}>Edit</button>
    </div>
  );
}
```

## Delete

```tsx
function DeleteTodo({ todoId }: { todoId: string }) {
  const removeTodo = () => {
    todoCollection.delete(todoId);
  };

  return <button onClick={removeTodo}>Delete</button>;
}
```

## Persistence Handlers

Persistence handlers define how mutations sync to the server. Without them, mutations are local-only.

### Single Handler (onUpdate)

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

### Full CRUD Handlers

```ts
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

## Transaction Object

Each persistence handler receives a `transaction` with a `mutations` array. Each mutation contains:

| Property   | Description                             |
| ---------- | --------------------------------------- |
| `key`      | The item's unique key (from `getKey`)   |
| `original` | The item before the mutation            |
| `modified` | The item after the mutation             |
| `changes`  | Partial object with only changed fields |

## Refetch Control

Persistence handlers can control whether TanStack Query refetches after a mutation:

```ts
onInsert: async ({ transaction }) => {
  await api.createTodos(transaction.mutations.map((m) => m.modified))
  return { refetch: false }
},
```

Returning nothing or `{ refetch: true }` triggers an automatic refetch. Return `{ refetch: false }` to skip it when the server response confirms the data is already correct.

## Batch Mutations

When multiple items are mutated in quick succession, TanStack DB batches them into a single transaction. The `transaction.mutations` array contains all mutations in the batch:

```ts
onUpdate: async ({ transaction }) => {
  const updates = transaction.mutations.map((m) => ({
    id: m.key,
    changes: m.changes,
  }))
  await api.batchUpdate(updates)
},
```

## Optimistic Flow

1. **User action** triggers `collection.insert()`, `.update()`, or `.delete()`
2. **Instant UI update** via live queries reflecting optimistic state
3. **Persistence handler** runs asynchronously to sync with server
4. **On success** the optimistic state becomes confirmed state
5. **On failure** the optimistic state rolls back automatically

## ElectricSQL Mutations

For ElectricSQL collections, mutations sync through Electric's real-time sync engine:

```ts
const todoCollection = createCollection(
  electricCollectionOptions({
    id: 'todos',
    schema: todoSchema,
    shapeOptions: {
      url: 'https://api.electric-sql.cloud/v1/shape',
      params: { table: 'todos' },
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

Returning a `txid` from Electric mutations lets TanStack DB track when the server has processed the change, ensuring consistency between optimistic and confirmed state.
