---
title: Architecture Patterns
description: Decision framework for local-first vs server-based vs hybrid architecture, CQRS patterns, read/write path strategies, and progressive enhancement
tags:
  [
    architecture,
    cqrs,
    read-path,
    write-path,
    hybrid,
    progressive-enhancement,
    migration,
    decision-tree,
  ]
---

## When to Go Local-First

Evaluate these four criteria to determine the right architecture model:

| Criteria               | Server-Based          | Local-First                | Hybrid                       |
| ---------------------- | --------------------- | -------------------------- | ---------------------------- |
| Offline needs          | None                  | Must work offline          | Selective offline support    |
| Latency sensitivity    | Tolerates round-trip  | Needs instant response     | Critical paths need instant  |
| Collaboration          | Single-user or turns  | Real-time multi-user       | Mix of single and multi-user |
| Data size per client   | Minimal client state  | Manageable local dataset   | Some data fits locally       |
| Conflict tolerance     | N/A (server is truth) | Can handle merge conflicts | Selective conflict handling  |
| Development complexity | Low                   | High                       | Medium                       |

**Go local-first when** at least two of these are true:

1. Users need to work offline or on unreliable networks
2. UI interactions must feel instant (no loading spinners on common actions)
3. Multiple users edit the same data concurrently
4. The working dataset per client fits in browser storage (typically < 500MB)

**Stay server-based when:**

- Data freshness from the server is critical on every render
- Business rules require server-authoritative validation (payments, inventory)
- The app is content-heavy with minimal interactivity
- Simple CRUD with reliable connectivity

## Architecture Models

### Server-Based (Traditional)

All reads and writes go through the server. The client has no persistent local state.

```ts
async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos');
  return response.json();
}

async function createTodo(todo: NewTodo): Promise<Todo> {
  const response = await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  });
  return response.json();
}
```

### Local-First

All reads come from a local database. All writes go to the local database first, then sync to the server in the background.

```ts
import { createCollection, createTanStackDB } from '@tanstack/db';
import { ElectricProvider } from '@tanstack/db/electric';

const db = createTanStackDB({ collections: { todos } });
const todos = createCollection<Todo>({
  id: 'todos',
  schema: todoSchema,
  sync: {
    provider: new ElectricProvider({ url: electricUrl, table: 'todos' }),
  },
});

function useTodos() {
  return db.useQuery((q) => q.from('todos').where('completed', '=', false));
}

function useCreateTodo() {
  return (todo: NewTodo) => {
    db.mutate.todos.insert({ id: crypto.randomUUID(), ...todo });
  };
}
```

### Hybrid

Server-first for most features. Local-first for high-value interactions where latency or offline matters.

```ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () => fetch('/api/settings').then((r) => r.json()),
  });
}

function useTodos() {
  return db.useQuery((q) => q.from('todos').orderBy('createdAt', 'desc'));
}
```

## CQRS in Local-First

Local-first architecture naturally implements CQRS (Command Query Responsibility Segregation). Reads and writes follow completely different paths.

```text
Read Path:                        Write Path:
┌────────┐                        ┌────────┐
│   UI   │ ← reads from           │   UI   │ ← user action
└────┬───┘                        └────┬───┘
     │                                 │
┌────▼───┐                        ┌────▼────────┐
│Local DB│                        │ Local Write  │ ← always succeeds
└────────┘                        └────┬─────────┘
     ▲                                 │
     │                            ┌────▼─────┐
     │                            │ Sync Layer│ ← background
     │                            └────┬──────┘
     │                                 │
     │                            ┌────▼──────┐
     │                            │  Server   │
     │                            └────┬──────┘
     │                                 │
     └─────── sync back ──────────────┘
```

The read path never touches the network. The write path writes locally first, then syncs. The server processes the write and syncs the resolved state back.

## Read Path Patterns

### Direct Server Fetch

Simplest approach. Every read is a network request.

```tsx
function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/todos')
      .then((r) => r.json())
      .then(setTodos)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;
  return (
    <ul>
      {todos.map((t) => (
        <TodoItem key={t.id} todo={t} />
      ))}
    </ul>
  );
}
```

**Tradeoff:** Simple but shows loading spinners on every navigation. Fails completely offline.

### Cache-Then-Network

Show cached data immediately, then update when the network responds.

```tsx
function TodoList() {
  const { data: todos, isLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: () => fetch('/api/todos').then((r) => r.json()),
    staleTime: 30_000,
  });

  if (isLoading) return <Spinner />;
  return (
    <ul>
      {todos.map((t) => (
        <TodoItem key={t.id} todo={t} />
      ))}
    </ul>
  );
}
```

**Tradeoff:** Fast subsequent reads, but first load still blocks. No offline support without persistence plugin.

### Local-First Read

Reads always come from the local database. The sync engine keeps it up to date.

```tsx
function TodoList() {
  const todos = db.useQuery((q) =>
    q.from('todos').where('completed', '=', false).orderBy('createdAt', 'desc'),
  );

  return (
    <ul>
      {todos.map((t) => (
        <TodoItem key={t.id} todo={t} />
      ))}
    </ul>
  );
}
```

**Tradeoff:** Always instant, works offline, but requires sync infrastructure. No loading state needed for reads.

## Write Path Patterns

### Server Mutation

Write goes to the server. UI updates after the server responds.

```tsx
function useCreateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (todo: NewTodo) =>
      fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(todo),
      }).then((r) => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}
```

**Tradeoff:** Simple and correct, but the UI feels sluggish. Button disables during the request. Fails offline.

### Optimistic Update (Rollback on Failure)

Assume the write will succeed. Update the UI immediately. Rollback if the server rejects it.

```tsx
function useCreateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (todo: NewTodo) =>
      fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(todo),
      }).then((r) => r.json()),
    onMutate: async (newTodo) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      const previous = queryClient.getQueryData<Todo[]>(['todos']);
      queryClient.setQueryData<Todo[]>(['todos'], (old = []) => [
        { id: crypto.randomUUID(), ...newTodo, completed: false },
        ...old,
      ]);
      return { previous };
    },
    onError: (_err, _todo, context) => {
      queryClient.setQueryData(['todos'], context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}
```

**Tradeoff:** Feels instant but has complexity around rollback. Still fails offline.

### Local-First Write

Write to the local database. It always succeeds. Sync delivers it to the server in the background.

```tsx
function useCreateTodo() {
  return (todo: NewTodo) => {
    db.mutate.todos.insert({
      id: crypto.randomUUID(),
      ...todo,
      completed: false,
      createdAt: new Date().toISOString(),
    });
  };
}

async function syncTodoWrite(todo: Todo) {
  await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  });
}
```

**Tradeoff:** Always instant, works offline, but the server may reject the write later. Conflict resolution is needed.

## Progressive Enhancement Strategy

Start server-first. Add local-first incrementally for high-value interactions.

**Step 1: Identify candidates.** Audit your app for interactions where latency or offline matters most.

| Interaction      | Latency Sensitive | Offline Needed | Local-First Candidate |
| ---------------- | ----------------- | -------------- | --------------------- |
| Todo CRUD        | Yes               | Yes            | Yes                   |
| User settings    | No                | No             | No                    |
| Chat messages    | Yes               | Yes            | Yes                   |
| Payment checkout | No                | No             | No                    |
| Document editing | Yes               | Yes            | Yes                   |
| Admin dashboard  | No                | No             | No                    |

**Step 2: Add local-first to one feature.** Keep everything else server-based.

```ts
const todos = createCollection<Todo>({
  id: 'todos',
  schema: todoSchema,
  sync: {
    provider: new ElectricProvider({ url: electricUrl, table: 'todos' }),
  },
});

// Settings still uses server-based approach
function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
  });
}
```

**Step 3: Expand gradually.** Move more features to local-first as confidence grows.

## Data Model Considerations

### Normalized Tables

Best for relational queries. Works well with SQL-based sync engines (ElectricSQL, PowerSync).

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  owner_id UUID REFERENCES users(id)
);

CREATE TABLE todos (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  title TEXT NOT NULL,
  completed BOOLEAN DEFAULT false
);
```

### Document Store

Best for offline-friendly blobs. Works well with document-based sync (Replicache, Triplit).

```ts
type TodoDocument = {
  id: string;
  title: string;
  completed: boolean;
  project: {
    id: string;
    name: string;
  };
  tags: string[];
  metadata: Record<string, unknown>;
};
```

### Hybrid Approach

Normalized tables for relational data. Embedded documents for self-contained entities.

```sql
CREATE TABLE todos (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  title TEXT NOT NULL,
  completed BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}'
);
```

## Migration Path: Server-Based to Local-First

Evolve incrementally without rewriting your app.

**Phase 1: Add a local cache layer.** Use TanStack Query with persistence.

```ts
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { persistQueryClient } from '@tanstack/react-query-persist-client';

const persister = createSyncStoragePersister({
  storage: window.localStorage,
});

persistQueryClient({ queryClient, persister });
```

**Phase 2: Introduce a local database for high-value data.**

```ts
const todos = createCollection<Todo>({
  id: 'todos',
  schema: todoSchema,
  sync: {
    provider: new ElectricProvider({ url: electricUrl, table: 'todos' }),
  },
});
```

**Phase 3: Move writes to local-first for synced collections.**

```ts
// Before: server mutation
const mutation = useMutation({
  mutationFn: (todo: NewTodo) => api.createTodo(todo),
});

// After: local-first write
function createTodo(todo: NewTodo) {
  db.mutate.todos.insert({ id: crypto.randomUUID(), ...todo });
}
```

**Phase 4: Remove server-fetch code for synced data.** The local database is now the source of truth. Server fetches are replaced by sync.
