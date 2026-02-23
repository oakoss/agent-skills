---
title: Migration Guide
description: Incremental migration from server-first to local-first architecture using TanStack DB and ElectricSQL
tags:
  [
    migration,
    tanstack-db,
    electric,
    incremental,
    rollback,
    feature-flag,
    pglite,
    testing,
  ]
---

## Incremental Adoption Path

Migrate one component or route at a time. The local-first stack coexists with existing server-first code — no big-bang rewrite required.

```text
Phase 1: Install TanStack DB alongside TanStack Query
Phase 2: Create query collections (reuse existing queryFn)
Phase 3: Replace useQuery with useLiveQuery
Phase 4: Swap query collections for Electric collections
```

## Step-by-Step Migration

### Step 1: Install TanStack DB

```bash
pnpm add @tanstack/db @tanstack/db-electric
```

### Step 2: Create a Query Collection

Reuse the existing `queryFn` from TanStack Query. No backend changes needed.

```ts
import { createQueryCollection } from '@tanstack/db';

const todosCollection = createQueryCollection({
  id: 'todos',
  queryFn: async () => {
    const response = await fetch('/api/todos');
    return response.json() as Promise<Todo[]>;
  },
  getId: (todo) => todo.id,
  schema: todoSchema,
});
```

### Step 3: Replace useQuery with useLiveQuery

```ts
// Before: server-first
const { data: todos } = useQuery({
  queryKey: ['todos'],
  queryFn: () => fetch('/api/todos').then((r) => r.json()),
});

// After: local-first (same data, instant reads)
const todos = useLiveQuery((q) =>
  q.from({ todosCollection }).where('@completed', '=', false).toArray(),
);
```

Component JSX stays identical. Only the data-fetching hook changes.

### Step 4: Swap to Electric Collection

When ready for real-time sync, replace the query collection with an Electric collection. No component changes required.

```ts
import { createElectricCollection } from '@tanstack/db-electric';

const todosCollection = createElectricCollection({
  id: 'todos',
  electricUrl: 'http://localhost:3000/v1/shape',
  electricParams: { table: 'todos' },
  getId: (todo) => todo.id,
  schema: todoSchema,
});
```

The `useLiveQuery` calls remain untouched.

## Database Preparation for Electric

ElectricSQL requires logical replication on Postgres.

### Postgres Configuration

```sql
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;
```

Restart Postgres after changing `wal_level`.

### Replication User

```sql
CREATE ROLE electric_user WITH LOGIN PASSWORD 'electric_pass' REPLICATION;
GRANT USAGE ON SCHEMA public TO electric_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO electric_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO electric_user;
```

### Docker Compose Example

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    command: >
      postgres
      -c wal_level=logical
      -c max_replication_slots=10
      -c max_wal_senders=10
    ports:
      - '5432:5432'

  electric:
    image: electricsql/electric
    environment:
      DATABASE_URL: postgresql://electric_user:electric_pass@postgres:5432/app
    ports:
      - '3000:3000'
    depends_on:
      - postgres
```

## Coexistence Patterns

Query collections and Electric collections can coexist in the same application. Use query collections for server-fetched data that doesn't need real-time sync, and Electric collections for locally-synced data.

### Cross-Collection Joins

```ts
const queryTodos = createQueryCollection({
  id: 'todos-query',
  queryFn: fetchTodos,
  getId: (t) => t.id,
  schema: todoSchema,
});

const electricUsers = createElectricCollection({
  id: 'users-electric',
  electricUrl: 'http://localhost:3000/v1/shape',
  electricParams: { table: 'users' },
  getId: (u) => u.id,
  schema: userSchema,
});

const todosWithUsers = useLiveQuery((q) =>
  q
    .from({ queryTodos })
    .join({ electricUsers }, '@userId', '=', '@id')
    .select('@queryTodos.*', '@electricUsers.name')
    .toArray(),
);
```

## Feature Flagging

Toggle between server-first and local-first per collection.

```ts
type SyncMode = 'query' | 'electric';

function createTodoCollection(mode: SyncMode) {
  if (mode === 'electric') {
    return createElectricCollection({
      id: 'todos',
      electricUrl: 'http://localhost:3000/v1/shape',
      electricParams: { table: 'todos' },
      getId: (t) => t.id,
      schema: todoSchema,
    });
  }

  return createQueryCollection({
    id: 'todos',
    queryFn: fetchTodos,
    getId: (t) => t.id,
    schema: todoSchema,
  });
}

const todosCollection = createTodoCollection(
  featureFlags.localFirst ? 'electric' : 'query',
);
```

## REST to Shape Mapping

| REST Pattern                   | Electric Shape Equivalent                              |
| ------------------------------ | ------------------------------------------------------ |
| `GET /todos`                   | `{ table: 'todos' }`                                   |
| `GET /todos?completed=false`   | `{ table: 'todos', where: 'completed = false' }`       |
| `GET /todos?fields=id,title`   | `{ table: 'todos', columns: ['id', 'title'] }`         |
| `GET /todos?userId=123`        | `{ table: 'todos', where: 'user_id = 123' }`           |
| `GET /todos?limit=50&offset=0` | Shapes sync all matching rows (paginate on the client) |
| `GET /todos?sort=created_at`   | Sort on the client after sync                          |

## Rollback Strategy

Swap `createElectricCollection` back to `createQueryCollection`. Component code using `useLiveQuery` does not change.

```ts
// Rollback: replace Electric collection with query collection
const todosCollection = createQueryCollection({
  id: 'todos',
  queryFn: fetchTodos,
  getId: (t) => t.id,
  schema: todoSchema,
});
```

No component-level changes are needed because `useLiveQuery` works with both collection types.

## Testing During Migration

### PGlite for Unit Tests

```ts
import { PGlite } from '@electric-sql/pglite';

async function createTestDB(): Promise<PGlite> {
  const pg = new PGlite();
  await pg.exec(`
    CREATE TABLE todos (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      title TEXT NOT NULL,
      completed BOOLEAN DEFAULT false
    )
  `);
  return pg;
}
```

### Dual-Write Verification

During migration, write to both the old server path and the new local-first path. Compare results to verify consistency.

```ts
async function dualWriteVerify(todo: Todo): Promise<{
  match: boolean;
  server: Todo;
  local: Todo;
}> {
  const [serverResult, localResult] = await Promise.all([
    fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify(todo),
      headers: { 'Content-Type': 'application/json' },
    }).then((r) => r.json() as Promise<Todo>),
    todosCollection.insert(todo),
  ]);

  return {
    match: serverResult.id === localResult.id,
    server: serverResult,
    local: localResult,
  };
}
```

### A/B Testing

Route a percentage of users to the local-first path and compare performance metrics.

```ts
function getCollectionForUser(userId: string): typeof todosCollection {
  const bucket = hashString(userId) % 100;
  const useLocalFirst = bucket < 10;
  return createTodoCollection(useLocalFirst ? 'electric' : 'query');
}
```

## Performance Comparison

| Metric               | Server-First | Local-First    | Improvement    |
| -------------------- | ------------ | -------------- | -------------- |
| Read latency         | 100-500ms    | <1ms           | 100-500x       |
| Write latency        | 100-500ms    | <1ms (local)   | 100-500x       |
| Offline reads        | Fails        | Works          | N/A            |
| Offline writes       | Fails        | Queues locally | N/A            |
| Initial load         | Fast         | Slower (sync)  | Tradeoff       |
| Data freshness       | Real-time    | Near real-time | ~50-200ms lag  |
| Bundle size increase | 0            | 50-200 KB      | Tradeoff       |
| Server load          | Higher       | Lower          | Fewer requests |
