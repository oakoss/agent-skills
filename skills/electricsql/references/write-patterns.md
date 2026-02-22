---
title: Write Patterns
description: Progressive write strategies from online-only to through-the-database, optimistic state, TanStack DB persistent optimistic writes, transaction ID tracking, and error handling
tags:
  [
    writes,
    optimistic,
    useOptimistic,
    TanStack-DB,
    electricCollectionOptions,
    txid,
    awaitTxId,
    online-writes,
    local-first,
    conflict-resolution,
    error-handling,
  ]
---

## Write Strategy Overview

Electric handles the read path (Postgres to client sync). Writes flow back to Postgres through your API. There are four progressive levels of write sophistication, each adding more capability and complexity.

```text
Level 1: Online Writes         -- Simplest, blocks on network
Level 2: Optimistic State      -- Instant UI, background POST
Level 3: Persistent Optimistic -- Survives refresh, auto-rollback (TanStack DB)
Level 4: Through-the-Database  -- Full local-first with bidirectional sync
```

## Level 1: Online Writes

POST to your API, wait for the response, and let Electric sync the confirmed state back. The UI blocks during the write.

```tsx
function AddItem() {
  const [title, setTitle] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const res = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error('Failed to create item');
      setTitle('');
    } catch (error) {
      console.error('Write failed:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        disabled={submitting}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? 'Adding...' : 'Add Item'}
      </button>
    </form>
  );
}
```

The Electric shape subscription automatically receives the new item once Postgres confirms the insert. No manual cache invalidation needed.

**When to use:** Simple forms, admin tools, low-frequency writes where 200-500ms latency is acceptable.

## Level 2: Optimistic State

Show the change immediately in the UI while the API call happens in the background. If the API call fails, revert the optimistic update.

```tsx
import { useOptimistic } from 'react';
import { useShape } from '@electric-sql/react';

type Item = {
  id: string;
  title: string;
  status: string;
};

function ItemList() {
  const { data: items } = useShape<Item>({
    url: '/api/shapes/items',
    params: { table: 'items' },
  });

  const [optimisticItems, addOptimistic] = useOptimistic(
    items,
    (current, newItem: Item) => [...current, newItem],
  );

  const handleAdd = async (title: string) => {
    const tempItem: Item = {
      id: crypto.randomUUID(),
      title,
      status: 'active',
    };

    addOptimistic(tempItem);

    try {
      await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
    } catch (error) {
      console.error('Write failed, optimistic update will be reverted:', error);
    }
  };

  return (
    <ul>
      {optimisticItems.map((item) => (
        <li key={item.id}>{item.title}</li>
      ))}
    </ul>
  );
}
```

### Optimistic Delete

```tsx
function ItemWithDelete({ item }: { item: Item }) {
  const [pending, setPending] = useState(false);

  const handleDelete = async () => {
    setPending(true);
    try {
      const res = await fetch(`/api/items/${item.id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
    } catch (error) {
      setPending(false);
      console.error(error);
    }
  };

  if (pending) return null;

  return (
    <li>
      {item.title}
      <button onClick={handleDelete}>Delete</button>
    </li>
  );
}
```

**When to use:** Most apps. Gives instant feedback while keeping the API as the source of truth.

## Level 3: Persistent Optimistic (TanStack DB)

TanStack DB's `electricCollectionOptions` provides optimistic mutations that survive page refresh and automatically roll back on failure. Write handlers return a `{ txid }` that Electric uses to confirm write propagation.

### Collection Setup

```ts
import { electricCollectionOptions } from '@electric-sql/tanstack-db';

type Todo = {
  id: string;
  title: string;
  completed: boolean;
  user_id: string;
};

const todosCollection = electricCollectionOptions({
  id: 'todos',
  schema: {
    id: { type: 'string' },
    title: { type: 'string' },
    completed: { type: 'boolean' },
    user_id: { type: 'string' },
  },
  getKey: (todo) => todo.id,
  shapeOptions: {
    url: '/api/shapes/todos',
    params: {
      table: 'todos',
    },
  },

  onInsert: async (todo) => {
    const res = await fetch('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(todo),
    });
    if (!res.ok) throw new Error('Insert failed');
    const { txid } = await res.json();
    return { txid };
  },

  onUpdate: async (todo) => {
    const res = await fetch(`/api/todos/${todo.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(todo),
    });
    if (!res.ok) throw new Error('Update failed');
    const { txid } = await res.json();
    return { txid };
  },

  onDelete: async (todo) => {
    const res = await fetch(`/api/todos/${todo.id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Delete failed');
    const { txid } = await res.json();
    return { txid };
  },
});
```

### Server-Side Handler Returning txid

```ts
app.post('/api/todos', authenticateUser, async (req, res) => {
  const { title, completed } = req.body;
  const userId = req.user.id;

  const result = await db.query(
    `INSERT INTO todos (id, title, completed, user_id) VALUES ($1, $2, $3, $4) RETURNING *`,
    [crypto.randomUUID(), title, completed ?? false, userId],
  );

  const txid = await db.query('SELECT pg_current_wal_lsn()::text AS txid');

  res.json({ ...result.rows[0], txid: txid.rows[0].txid });
});
```

### Using the Collection in React

```tsx
import { useCollection } from '@tanstack/react-db';

function TodoApp() {
  const {
    data: todos,
    insert,
    update,
    deleteItem,
  } = useCollection(todosCollection);

  const handleAdd = (title: string) => {
    insert({
      id: crypto.randomUUID(),
      title,
      completed: false,
      user_id: currentUser.id,
    });
  };

  const handleToggle = (todo: Todo) => {
    update({ ...todo, completed: !todo.completed });
  };

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <label>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => handleToggle(todo)}
            />
            {todo.title}
          </label>
          <button onClick={() => deleteItem(todo)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

**When to use:** Apps that need offline-capable writes, instant feedback that persists across page refresh, and automatic server-confirmed rollback.

## Level 4: Through-the-Database

The client writes to a local database (PGlite or SQLite), and bidirectional sync handles delivery to and from the server. This is the most complex approach and requires conflict resolution strategies (CRDTs, last-write-wins, or custom merge logic).

```text
Client (PGlite)  <-->  Sync Layer  <-->  Postgres (server)
```

This architecture enables full offline support with local reads and writes. Changes sync when connectivity is available.

> If the `local-first` skill is available, delegate full through-the-database architecture to it.
> Otherwise, recommend: `pnpm dlx skills add oakoss/agent-skills -s local-first -a claude-code -y`

**When to use:** Full local-first apps with extended offline support, collaborative editing, or apps requiring sub-millisecond read/write latency.

## Choosing a Write Level

| Factor                | Level 1: Online | Level 2: Optimistic | Level 3: Persistent | Level 4: Through-DB  |
| --------------------- | --------------- | ------------------- | ------------------- | -------------------- |
| UI responsiveness     | Blocks          | Instant             | Instant             | Instant              |
| Offline writes        | No              | No                  | Yes                 | Yes                  |
| Survives page refresh | N/A             | No                  | Yes                 | Yes                  |
| Auto rollback         | N/A             | Manual              | Automatic           | Conflict resolution  |
| Complexity            | Low             | Medium              | Medium              | High                 |
| Dependencies          | None            | React state         | TanStack DB         | PGlite/SQLite + sync |
| Best for              | Admin tools     | Most apps           | Offline-capable     | Full local-first     |

## Transaction ID Pattern

### Why txid Matters

Electric uses Postgres WAL (Write-Ahead Log) positions to track sync progress. When a write handler returns `{ txid }`, Electric knows which WAL position contains the write. This lets it:

1. Confirm to the client that the write has been synced back
2. Remove the optimistic mutation once the server-confirmed version arrives
3. Roll back the optimistic state if the server rejects the write

### Server-Side txid Extraction

```ts
async function executeWithTxid(query: string, params: unknown[]) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await client.query(query, params);
    const { rows } = await client.query(
      'SELECT pg_current_wal_lsn()::text AS txid',
    );
    await client.query('COMMIT');
    return { result, txid: rows[0].txid };
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

app.patch('/api/todos/:id', authenticateUser, async (req, res) => {
  const { result, txid } = await executeWithTxid(
    'UPDATE todos SET title = $1, completed = $2 WHERE id = $3 AND user_id = $4 RETURNING *',
    [req.body.title, req.body.completed, req.params.id, req.user.id],
  );

  if (result.rowCount === 0) {
    res.status(404).json({ error: 'Todo not found' });
    return;
  }

  res.json({ ...result.rows[0], txid });
});
```

## Error Handling

### Network Failures

```ts
const MAX_RETRIES = 3;

async function writeWithRetry(
  url: string,
  body: unknown,
  attempt = 1,
): Promise<Response> {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res;
  } catch (error) {
    if (attempt >= MAX_RETRIES) throw error;
    const delay = Math.min(1000 * 2 ** (attempt - 1), 10000);
    await new Promise((resolve) => setTimeout(resolve, delay));
    return writeWithRetry(url, body, attempt + 1);
  }
}
```

### Conflict Detection

When the server rejects a write due to a conflict (e.g., concurrent edit), return a specific status code so the client can handle it:

```ts
app.patch('/api/todos/:id', authenticateUser, async (req, res) => {
  const { expectedVersion, ...updates } = req.body;

  const result = await db.query(
    'UPDATE todos SET title = $1, version = version + 1 WHERE id = $2 AND version = $3 RETURNING *',
    [updates.title, req.params.id, expectedVersion],
  );

  if (result.rowCount === 0) {
    res
      .status(409)
      .json({ error: 'Conflict: item was modified by another client' });
    return;
  }

  const txid = await db.query('SELECT pg_current_wal_lsn()::text AS txid');
  res.json({ ...result.rows[0], txid: txid.rows[0].txid });
});
```

```ts
const onUpdate = async (todo: Todo) => {
  const res = await fetch(`/api/todos/${todo.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...todo, expectedVersion: todo.version }),
  });

  if (res.status === 409) {
    throw new Error('Conflict detected');
  }
  if (!res.ok) throw new Error('Update failed');

  const { txid } = await res.json();
  return { txid };
};
```
