---
title: Error Handling
description: Error class hierarchy, transaction states, handler errors, schema validation, and rollback patterns
tags:
  [
    errors,
    error-handling,
    transactions,
    rollback,
    validation,
    schema,
    retry,
    NonRetriableError,
  ]
---

# Error Handling

TanStack DB provides a structured error hierarchy for diagnosing mutation failures, schema violations, and query issues. All errors extend `TanStackDBError`.

## Error Class Hierarchy

```text
TanStackDBError (base)
├── MissingInsertHandlerError
├── MissingUpdateHandlerError
├── MissingDeleteHandlerError
├── TransactionNotPendingMutateError
├── TransactionNotPendingCommitError
├── SchemaValidationError
├── DuplicateKeyError
├── UpdateKeyNotFoundError
├── DeleteKeyNotFoundError
├── KeyUpdateNotAllowedError
├── NonRetriableError
├── InvalidWhereExpressionError
└── DuplicateDbInstanceError
```

## Transaction States

Transactions move through a defined lifecycle:

| State        | Description                                             |
| ------------ | ------------------------------------------------------- |
| `pending`    | Transaction created, accepting mutations via `mutate()` |
| `persisting` | Committed and running persistence handlers              |
| `completed`  | All handlers succeeded, changes confirmed               |
| `failed`     | A handler threw, changes rolled back                    |

```ts
import { createTransaction } from '@tanstack/db';

const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    await api.saveBatch(transaction.mutations);
  },
});

tx.mutate(() => {
  todoCollection.insert({ id: '1', text: 'Task', completed: false });
});

tx.commit();

const result = await tx.isPersisted.promise;
if (result.status === 'completed') {
  console.log('Transaction persisted');
} else {
  console.error('Transaction failed:', result.error);
}
```

## Missing Handler Errors

Thrown when a mutation targets a collection that lacks the corresponding persistence handler:

```ts
const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['items'],
    queryFn: fetchItems,
    getKey: (item) => item.id,
    // No onInsert defined
  }),
);

// MissingInsertHandlerError: No onInsert handler for collection
collection.insert({ id: '1', name: 'Item' });
```

| Error                       | Trigger                                  |
| --------------------------- | ---------------------------------------- |
| `MissingInsertHandlerError` | `collection.insert()` without `onInsert` |
| `MissingUpdateHandlerError` | `collection.update()` without `onUpdate` |
| `MissingDeleteHandlerError` | `collection.delete()` without `onDelete` |

These errors indicate the collection is missing a persistence handler. For local-only collections that do not sync, use `localOnlyCollectionOptions` instead.

## Schema Validation Errors

`SchemaValidationError` fires when data fails schema validation. The `issues` array contains details per field:

```ts
import { z } from 'zod';

const todoSchema = z.object({
  id: z.string().uuid(),
  text: z.string().min(1),
  completed: z.boolean(),
});

const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    getKey: (item) => item.id,
    schema: todoSchema,
    onInsert: async ({ transaction }) => {
      await api.createTodos(transaction.mutations.map((m) => m.modified));
    },
  }),
);

try {
  // Fails: text is empty string, id is not a UUID
  collection.insert({ id: 'bad', text: '', completed: false });
} catch (error) {
  if (error instanceof SchemaValidationError) {
    console.error(error.type); // 'insert' | 'update'
    for (const issue of error.issues) {
      console.error(issue.path, issue.message);
    }
  }
}
```

## Key Errors

| Error                      | Cause                                             |
| -------------------------- | ------------------------------------------------- |
| `DuplicateKeyError`        | Inserting an item with a key that already exists  |
| `UpdateKeyNotFoundError`   | Updating an item with a key not in the collection |
| `DeleteKeyNotFoundError`   | Deleting an item with a key not in the collection |
| `KeyUpdateNotAllowedError` | Changing the key field inside an update draft     |

```ts
// DuplicateKeyError
todoCollection.insert({ id: 'existing-id', text: 'Dup', completed: false });

// UpdateKeyNotFoundError
todoCollection.update('nonexistent-id', (draft) => {
  draft.text = 'Updated';
});

// KeyUpdateNotAllowedError
todoCollection.update('todo-1', (draft) => {
  draft.id = 'new-id'; // Cannot change key field
});
```

## NonRetriableError

Wrap errors in `NonRetriableError` inside persistence handlers to signal that the operation should not be retried. The transaction fails immediately and rolls back:

```ts
import { NonRetriableError } from '@tanstack/db';

const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    getKey: (item) => item.id,
    onInsert: async ({ transaction }) => {
      const response = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(transaction.mutations.map((m) => m.modified)),
      });

      if (response.status === 409) {
        throw new NonRetriableError('Conflict: item already exists on server');
      }

      if (!response.ok) {
        // Regular errors may be retried
        throw new Error(`Server error: ${response.status}`);
      }
    },
  }),
);
```

## Handler Error Handling and Rollback

When a persistence handler throws, the transaction enters the `failed` state and all optimistic changes roll back:

```ts
const collection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    getKey: (item) => item.id,
    onUpdate: async ({ transaction }) => {
      const updates = transaction.mutations.map((m) => ({
        id: m.key,
        changes: m.changes,
      }));

      const response = await api.updateTodos(updates);

      if (!response.ok) {
        // Throwing triggers automatic rollback of all mutations in this transaction
        throw new Error('Update failed');
      }
    },
  }),
);
```

### Awaiting Transaction Results

Use `tx.isPersisted.promise` to determine whether a transaction succeeded or failed:

```ts
const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    await api.saveBatch(transaction.mutations);
  },
});

tx.mutate(() => {
  todoCollection.insert({ id: '1', text: 'New', completed: false });
  todoCollection.update('2', (draft) => {
    draft.completed = true;
  });
});

tx.commit();

try {
  await tx.isPersisted.promise;
  showToast('Changes saved');
} catch (error) {
  showToast('Save failed, changes reverted');
}
```

## Transaction State Errors

| Error                              | Cause                                       |
| ---------------------------------- | ------------------------------------------- |
| `TransactionNotPendingMutateError` | Calling `tx.mutate()` after commit/rollback |
| `TransactionNotPendingCommitError` | Calling `tx.commit()` after commit/rollback |

```ts
const tx = createTransaction({
  mutationFn: async ({ transaction }) => {
    await api.save(transaction.mutations);
  },
});

tx.mutate(() => {
  todoCollection.insert({ id: '1', text: 'Task', completed: false });
});

tx.commit();

// TransactionNotPendingMutateError: transaction already committed
tx.mutate(() => {
  todoCollection.insert({ id: '2', text: 'Another', completed: false });
});
```

## InvalidWhereExpressionError

Thrown when using JavaScript equality operators instead of TanStack DB filter functions in `where` clauses:

```ts
import { useLiveQuery } from '@tanstack/react-db';
import { eq } from '@tanstack/db';

// WRONG: uses JavaScript === (always returns boolean, not a filter expression)
const result = useLiveQuery((q) =>
  q.from({ todo: todoCollection }).where(({ todo }) => todo.status === 'done'),
);

// CORRECT: uses eq() filter function
const result = useLiveQuery((q) =>
  q.from({ todo: todoCollection }).where(({ todo }) => eq(todo.status, 'done')),
);
```

## DuplicateDbInstanceError

Thrown when multiple instances of `@tanstack/db` are loaded simultaneously, typically caused by bundler misconfiguration or duplicate dependencies:

```text
DuplicateDbInstanceError: Multiple instances of @tanstack/db detected
```

Fix by deduplicating the package in your dependency tree:

```bash
pnpm dedupe @tanstack/db
```
