---
title: Sync Engines
description: Comparison of sync engines for local-first apps including ElectricSQL, Zero, PowerSync, Replicache, LiveStore, and Triplit
tags:
  [
    sync,
    electric,
    zero,
    powersync,
    replicache,
    livestore,
    triplit,
    comparison,
    selection,
  ]
---

## Comparison Table

| Feature             | ElectricSQL             | Zero            | PowerSync             | Replicache      | LiveStore            | Triplit               |
| ------------------- | ----------------------- | --------------- | --------------------- | --------------- | -------------------- | --------------------- |
| DB backend          | Postgres                | Postgres        | Postgres, MongoDB     | Any             | SQLite (client-only) | Built-in (Triplit DB) |
| Sync model          | Read-only shapes        | Full read+write | Read sync + write API | Push/pull       | Event-sourced        | Full read+write       |
| Conflict resolution | Server-wins (your API)  | Built-in        | Built-in              | Custom (server) | Event replay         | Built-in (LWW)        |
| Client storage      | In-memory / TanStack DB | IndexedDB       | SQLite (WASM)         | IndexedDB       | SQLite (OPFS)        | IndexedDB             |
| React integration   | TanStack DB, hooks      | Custom hooks    | React hooks           | React hooks     | Framework-agnostic   | React hooks           |
| License             | Apache 2.0              | ISC             | Apache 2.0            | BSL 1.1         | MIT                  | AGPL / Commercial     |
| Maturity            | Production              | Early           | Production            | Production      | Early                | Production            |
| Bundle size         | Small (shapes client)   | Medium          | Medium (SQLite WASM)  | Small           | Medium (SQLite WASM) | Medium                |

## ElectricSQL

Postgres-native sync engine that streams partial replication (Shapes) from Postgres to clients. The read path syncs data to the client via Shapes. The write path is your own API — Electric does not sync writes back to Postgres.

**Key differentiator:** Uses Postgres logical replication directly. No separate sync server to manage. Reads sync automatically; writes go through your existing API.

**Best fit:** Apps with an existing Postgres backend that want to add real-time sync for reads while keeping server-authoritative writes.

```ts
import { ShapeStream, Shape } from '@electric-sql/client';

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'todos',
    where: 'completed = false',
  },
});

const shape = new Shape(stream);

shape.subscribe((data) => {
  console.log('Todos:', [...data.values()]);
});
```

With TanStack DB integration:

```ts
import { createCollection, createTanStackDB } from '@tanstack/db';
import { ElectricProvider } from '@tanstack/db/electric';

const todos = createCollection<Todo>({
  id: 'todos',
  schema: todoSchema,
  sync: {
    provider: new ElectricProvider({
      url: 'http://localhost:3000/v1/shape',
      table: 'todos',
    }),
  },
});

const db = createTanStackDB({ collections: { todos } });

// Reads: local, reactive, instant
const activeTodos = db.useQuery((q) =>
  q.from('todos').where('completed', '=', false),
);

// Writes: go through your API, sync back via Electric
async function createTodo(todo: NewTodo) {
  db.mutate.todos.insert({
    id: crypto.randomUUID(),
    ...todo,
  });

  await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  });
}
```

## Zero

Full-stack sync engine with both read and write sync. Uses Postgres as the backend and provides a custom query language for the client. Built by the team behind Replicache.

**Key differentiator:** True read+write sync with built-in conflict resolution. Single system handles both directions.

**Best fit:** New apps that want full local-first with minimal custom sync code and are comfortable with an early-stage project.

```ts
import { Zero } from '@rocicorp/zero';

const z = new Zero({
  userID: 'user-123',
  server: 'http://localhost:4848',
  schema,
  kvStore: 'idb',
});

// Reads: reactive queries
const todos = z.query.todo
  .where('completed', '=', false)
  .orderBy('createdAt', 'desc')
  .materialize();

todos.addListener((data) => {
  console.log('Todos:', data);
});

// Writes: sync automatically
await z.mutate.todo.insert({
  id: crypto.randomUUID(),
  title: 'New todo',
  completed: false,
});
```

## PowerSync

Sync engine focused on Postgres (and MongoDB) with SQLite on the client. Strong focus on mobile (Flutter, React Native) with growing web support.

**Key differentiator:** SQLite on the client gives full SQL query capability. Strong mobile-first focus with offline-first design.

**Best fit:** Mobile-first apps (React Native, Flutter) that need reliable offline support with Postgres or MongoDB backends.

```ts
import { PowerSyncDatabase, column, Schema, Table } from '@powersync/web';

const todosTable = new Table({
  title: column.text,
  completed: column.integer,
  created_at: column.text,
});

const schema = new Schema({ todos: todosTable });

const db = new PowerSyncDatabase({
  schema,
  database: { dbFilename: 'app.db' },
});

await db.init();

// Reads: full SQL queries against local SQLite
const todos = await db.getAll(
  'SELECT * FROM todos WHERE completed = 0 ORDER BY created_at DESC',
);

// Reactive queries
db.watch('SELECT * FROM todos WHERE completed = 0', [], {
  onResult: (results) => console.log('Todos:', results.rows?._array),
});

// Writes: local SQLite + upload queue
await db.execute('INSERT INTO todos (id, title, completed) VALUES (?, ?, ?)', [
  crypto.randomUUID(),
  'New todo',
  0,
]);
```

## Replicache

Client-side transactional cache that works with any backend. Uses a push/pull model where the client pushes mutations and pulls the latest state from a custom server endpoint.

**Key differentiator:** Backend-agnostic. Works with any database and any server framework. Proven at scale (used by Linear, Figma-like apps).

**Best fit:** Teams with existing non-Postgres backends or complex server logic that want local-first reads with server-authoritative conflict resolution.

```ts
import { Replicache } from 'replicache';

const rep = new Replicache({
  name: 'user-123',
  licenseKey: REPLICACHE_LICENSE_KEY,
  pushURL: '/api/replicache/push',
  pullURL: '/api/replicache/pull',
  mutators: {
    async createTodo(tx, todo: NewTodo) {
      const id = crypto.randomUUID();
      await tx.set(`todo/${id}`, { id, ...todo, completed: false });
    },
    async toggleTodo(tx, { id }: { id: string }) {
      const todo = (await tx.get(`todo/${id}`)) as Todo;
      await tx.set(`todo/${id}`, { ...todo, completed: !todo.completed });
    },
  },
});

// Reads: subscribe to local data
rep.subscribe(
  async (tx) => {
    const todos = await tx.scan({ prefix: 'todo/' }).values().toArray();
    return todos as Todo[];
  },
  (todos) => console.log('Todos:', todos),
);

// Writes: call mutators (local + queued for push)
await rep.mutate.createTodo({ title: 'New todo' });
```

Server push endpoint (simplified):

```ts
import type { MutationV1 } from 'replicache';

export async function handlePush(req: Request) {
  const push = await req.json();

  for (const mutation of push.mutations as MutationV1[]) {
    switch (mutation.name) {
      case 'createTodo':
        await db.insert('todos', mutation.args);
        break;
      case 'toggleTodo':
        await db.update('todos', mutation.args.id, {
          completed: db.raw('NOT completed'),
        });
        break;
    }
  }

  return new Response('OK');
}
```

## LiveStore

SQLite-based reactive store that uses event sourcing under the hood. Framework-agnostic with OPFS for persistence. All state is derived from an append-only event log.

**Key differentiator:** Event-sourced architecture gives full audit trail, undo/redo, and time-travel debugging. Uses SQLite WASM on OPFS for high-performance persistence.

**Best fit:** Apps that benefit from event sourcing (audit trails, undo/redo) and want a framework-agnostic reactive store.

```ts
import { createLiveStore } from '@livestore/livestore';
import { makeSqliteDeps } from '@livestore/wa-sqlite';

const store = await createLiveStore({
  deps: makeSqliteDeps(),
  schema: {
    events: {
      todoCreated: { id: 'string', title: 'string' },
      todoToggled: { id: 'string' },
    },
    state: {
      todos: {
        select: `SELECT * FROM todos WHERE completed = 0`,
      },
    },
    migrations: [
      `CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0
      )`,
    ],
  },
});

// Reads: reactive queries derived from event log
store.query$.todos.subscribe((todos) => {
  console.log('Todos:', todos);
});

// Writes: dispatch events (appended to event log, projected to state)
store.dispatch('todoCreated', {
  id: crypto.randomUUID(),
  title: 'New todo',
});
```

## Triplit

Full-stack database with built-in sync, schema definition, auth, and real-time queries. Can run as cloud-hosted or self-hosted.

**Key differentiator:** Full-stack DB that handles both client and server storage with built-in auth and real-time sync. Schema-defined with TypeScript.

**Best fit:** Teams that want an all-in-one solution without stitching together separate database, sync, and auth layers.

```ts
import { TriplitClient } from '@triplit/client';
import { schema } from './schema';

const client = new TriplitClient({
  schema,
  serverUrl: 'http://localhost:6543',
  token: AUTH_TOKEN,
});

// Reads: reactive queries
const query = client.query('todos').where('completed', '=', false).build();

client.subscribe(query, (results) => {
  console.log('Todos:', [...results.values()]);
});

// React hook
function useTodos() {
  const { results } = useQuery(
    client,
    client.query('todos').where('completed', '=', false),
  );
  return results ? [...results.values()] : [];
}

// Writes: sync automatically
await client.insert('todos', {
  title: 'New todo',
  completed: false,
});
```

Schema definition:

```ts
import { Schema as S } from '@triplit/client';

export const schema = {
  todos: {
    schema: S.Schema({
      id: S.Id(),
      title: S.String(),
      completed: S.Boolean({ default: false }),
      createdAt: S.Date({ default: S.Default.now() }),
    }),
  },
};
```

## Selection Criteria

Use this decision matrix to narrow your choice:

| If you need...                     | Consider                           |
| ---------------------------------- | ---------------------------------- |
| Postgres read sync + own write API | ElectricSQL                        |
| Full read+write sync with Postgres | Zero, Triplit                      |
| Mobile-first with SQLite on client | PowerSync                          |
| Any backend, proven at scale       | Replicache                         |
| Event sourcing with audit trail    | LiveStore                          |
| All-in-one DB + sync + auth        | Triplit                            |
| TanStack DB integration            | ElectricSQL                        |
| Open source (permissive license)   | ElectricSQL, PowerSync, LiveStore  |
| Production-proven maturity         | ElectricSQL, Replicache, PowerSync |

**Decision flow:**

1. **Do you have Postgres?** If yes, start with ElectricSQL (read sync) or Zero (full sync). If no, consider Replicache or Triplit.
2. **Do you need write sync?** If reads-only, ElectricSQL is simplest. If full sync, evaluate Zero, PowerSync, or Triplit.
3. **What client platform?** Web-only favors ElectricSQL or Zero. Mobile needs PowerSync or Replicache.
4. **Team size?** Small teams benefit from all-in-one solutions (Triplit). Larger teams can stitch together components.
5. **Maturity requirement?** Production-critical apps should lean toward ElectricSQL, Replicache, or PowerSync.
