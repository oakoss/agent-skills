---
title: Conflict Resolution
description: Conflict resolution strategies for concurrent edits in local-first apps including LWW, CRDTs, server-wins, field-level merge, and event sourcing
tags:
  [
    conflict,
    lww,
    crdt,
    yjs,
    automerge,
    server-wins,
    field-merge,
    event-sourcing,
    convergence,
  ]
---

## Overview Table

| Strategy          | Complexity | Data Loss Risk | Best Use Case                    | Implementation Effort |
| ----------------- | ---------- | -------------- | -------------------------------- | --------------------- |
| Last-Write-Wins   | Low        | Medium         | Independent fields, settings     | Minimal               |
| CRDTs             | High       | None           | Collaborative text, shared lists | Significant           |
| Server-Wins       | Low        | Low            | Business-critical data           | Low                   |
| Field-Level Merge | Medium     | Low            | Form data, record editing        | Medium                |
| Event Sourcing    | High       | None           | Audit trails, undo/redo          | Significant           |

## Last-Write-Wins (LWW)

Simplest conflict resolution. When two clients edit the same record, the last write (by timestamp) wins. Earlier writes are silently discarded.

### Wall-Clock Implementation

```ts
type LWWRecord<T> = {
  value: T;
  updatedAt: number;
};

function lwwMerge<T>(local: LWWRecord<T>, remote: LWWRecord<T>): LWWRecord<T> {
  if (remote.updatedAt > local.updatedAt) {
    return remote;
  }
  return local;
}

// Usage
const localTodo: LWWRecord<Todo> = {
  value: { id: '1', title: 'Buy milk', completed: true },
  updatedAt: Date.now(),
};

const remoteTodo: LWWRecord<Todo> = {
  value: { id: '1', title: 'Buy oat milk', completed: false },
  updatedAt: Date.now() + 100,
};

const resolved = lwwMerge(localTodo, remoteTodo);
// Remote wins because it has a later timestamp
```

**Wall-clock problem:** Client clocks can drift. A client with a clock set 5 minutes ahead will always win.

### Logical Clock (Lamport Timestamp)

Use a logical clock to avoid wall-clock drift issues. Each operation increments a counter.

```ts
type LamportClock = {
  counter: number;
  nodeId: string;
};

function compareClock(a: LamportClock, b: LamportClock): number {
  if (a.counter !== b.counter) {
    return a.counter - b.counter;
  }
  return a.nodeId.localeCompare(b.nodeId);
}

function incrementClock(clock: LamportClock): LamportClock {
  return { ...clock, counter: clock.counter + 1 };
}

function mergeClock(local: LamportClock, remote: LamportClock): LamportClock {
  return {
    counter: Math.max(local.counter, remote.counter) + 1,
    nodeId: local.nodeId,
  };
}

type LWWValue<T> = {
  value: T;
  clock: LamportClock;
};

function lwwMergeLogical<T>(
  local: LWWValue<T>,
  remote: LWWValue<T>,
): LWWValue<T> {
  if (compareClock(remote.clock, local.clock) > 0) {
    return remote;
  }
  return local;
}
```

**When to use LWW:** Settings, preferences, status fields, any field where the latest value is always correct.

**When to avoid LWW:** Collaborative text editing, counters, lists where concurrent additions should merge.

## CRDTs (Conflict-Free Replicated Data Types)

Data structures that mathematically guarantee convergence. Any two replicas that have seen the same set of operations will have the same state, regardless of order.

### Counter CRDTs

**G-Counter (grow-only):** Each node tracks its own count. Total is the sum of all nodes.

```ts
type GCounter = Record<string, number>;

function increment(counter: GCounter, nodeId: string): GCounter {
  return {
    ...counter,
    [nodeId]: (counter[nodeId] ?? 0) + 1,
  };
}

function value(counter: GCounter): number {
  return Object.values(counter).reduce((sum, n) => sum + n, 0);
}

function merge(a: GCounter, b: GCounter): GCounter {
  const result: GCounter = { ...a };
  for (const [node, count] of Object.entries(b)) {
    result[node] = Math.max(result[node] ?? 0, count);
  }
  return result;
}
```

**PN-Counter (add and subtract):** Two G-Counters — one for increments, one for decrements.

```ts
type PNCounter = {
  positive: GCounter;
  negative: GCounter;
};

function pnIncrement(counter: PNCounter, nodeId: string): PNCounter {
  return { ...counter, positive: increment(counter.positive, nodeId) };
}

function pnDecrement(counter: PNCounter, nodeId: string): PNCounter {
  return { ...counter, negative: increment(counter.negative, nodeId) };
}

function pnValue(counter: PNCounter): number {
  return value(counter.positive) - value(counter.negative);
}

function pnMerge(a: PNCounter, b: PNCounter): PNCounter {
  return {
    positive: merge(a.positive, b.positive),
    negative: merge(a.negative, b.negative),
  };
}
```

### Yjs (Collaborative Text and Data)

Yjs is a high-performance CRDT implementation for collaborative editing. Supports text, arrays, maps, and XML.

```ts
import * as Y from 'yjs';

const doc = new Y.Doc();

// Shared text
const ytext = doc.getText('document');
ytext.insert(0, 'Hello, world!');

// Observe changes
ytext.observe((event) => {
  console.log('Text changed:', ytext.toString());
});

// Shared map (like a record)
const ymap = doc.getMap<string>('todo');
ymap.set('title', 'Buy groceries');
ymap.set('completed', 'false');

// Shared array (like a list)
const yarray = doc.getArray<string>('tags');
yarray.push(['urgent']);
yarray.insert(0, ['important']);
```

Sync between peers:

```ts
import * as Y from 'yjs';

function syncDocuments(local: Y.Doc, remote: Y.Doc): void {
  const localState = Y.encodeStateVector(local);
  const remoteState = Y.encodeStateVector(remote);

  const localUpdate = Y.encodeStateAsUpdate(local, remoteState);
  const remoteUpdate = Y.encodeStateAsUpdate(remote, localState);

  Y.applyUpdate(local, remoteUpdate);
  Y.applyUpdate(remote, localUpdate);
}
```

With a WebSocket provider:

```ts
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const doc = new Y.Doc();
const provider = new WebsocketProvider(
  'wss://your-server.com',
  'document-room-id',
  doc,
);

provider.on('status', ({ status }: { status: string }) => {
  console.log('Connection status:', status);
});

const ytext = doc.getText('content');
```

### Automerge

Document-based CRDT library. Tracks changes as a history of operations, enabling merge, undo, and time travel.

```ts
import * as Automerge from '@automerge/automerge';

type TodoDoc = {
  todos: Array<{ id: string; title: string; completed: boolean }>;
};

let doc = Automerge.init<TodoDoc>();

doc = Automerge.change(doc, (d) => {
  d.todos = [];
});

doc = Automerge.change(doc, (d) => {
  d.todos.push({ id: '1', title: 'Buy milk', completed: false });
});

// Fork for offline editing
let fork = Automerge.clone(doc);

doc = Automerge.change(doc, (d) => {
  d.todos[0].title = 'Buy oat milk';
});

fork = Automerge.change(fork, (d) => {
  d.todos[0].completed = true;
});

// Merge: both changes are preserved
doc = Automerge.merge(doc, fork);
// Result: { id: '1', title: 'Buy oat milk', completed: true }
```

**When to use CRDTs:** Collaborative text editing, shared lists where concurrent additions should merge, counters, any data where losing concurrent edits is unacceptable.

## Server-Wins

Client sends writes to the server. The server resolves any conflicts authoritatively. The resolved state syncs back to the client, overwriting local state.

This is the model used by ElectricSQL: reads sync from the server via Shapes, writes go through your API, and the server's state is the final truth.

```ts
// Client: write through API, let sync update local state
async function updateTodo(id: string, updates: Partial<Todo>): Promise<void> {
  db.mutate.todos.update({
    where: { id },
    set: updates,
  });

  const response = await fetch(`/api/todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    console.error('Server rejected update, sync will correct local state');
  }
}
```

Server-side conflict resolution:

```ts
// Server: resolve conflicts with business logic
async function handleTodoUpdate(
  id: string,
  clientUpdates: Partial<Todo>,
  _clientTimestamp: number,
): Promise<Todo> {
  const current = await db.query('SELECT * FROM todos WHERE id = $1', [id]);

  const resolved: Partial<Todo> = {};

  if (clientUpdates.title !== undefined) {
    resolved.title = clientUpdates.title;
  }

  // Server-authoritative: completed status follows business rules
  if (clientUpdates.completed !== undefined) {
    const canComplete = await validateCompletion(id);
    resolved.completed = canComplete
      ? clientUpdates.completed
      : current.completed;
  }

  const result = await db.query(
    'UPDATE todos SET title = COALESCE($1, title), completed = COALESCE($2, completed) WHERE id = $3 RETURNING *',
    [resolved.title, resolved.completed, id],
  );

  return result.rows[0];
}
```

**When to use server-wins:** Payment processing, inventory management, approval workflows, any data where business rules must be enforced authoritatively.

## Field-Level Merge

Instead of resolving conflicts at the record level, merge at individual field granularity. If two clients edit different fields of the same record, both edits are preserved.

```ts
type FieldTimestamp = Record<string, number>;

type MergeableRecord<T> = {
  value: T;
  fieldTimestamps: FieldTimestamp;
};

function fieldMerge<T extends Record<string, unknown>>(
  local: MergeableRecord<T>,
  remote: MergeableRecord<T>,
): MergeableRecord<T> {
  const merged = { ...local.value };
  const timestamps = { ...local.fieldTimestamps };

  for (const key of Object.keys(remote.value)) {
    const remoteTs = remote.fieldTimestamps[key] ?? 0;
    const localTs = local.fieldTimestamps[key] ?? 0;

    if (remoteTs > localTs) {
      (merged as Record<string, unknown>)[key] = remote.value[key];
      timestamps[key] = remoteTs;
    }
  }

  return { value: merged as T, fieldTimestamps: timestamps };
}

// Client A edits title at t=100
const clientA: MergeableRecord<Todo> = {
  value: { id: '1', title: 'Updated title', completed: false },
  fieldTimestamps: { title: 100, completed: 50 },
};

// Client B edits completed at t=110
const clientB: MergeableRecord<Todo> = {
  value: { id: '1', title: 'Original title', completed: true },
  fieldTimestamps: { title: 50, completed: 110 },
};

const result = fieldMerge(clientA, clientB);
// Result: { title: 'Updated title', completed: true }
// Both edits preserved because they touched different fields
```

**When to use field-level merge:** Form data where different users edit different fields, profile updates, settings where fields are independent.

## Event Sourcing

Store events (facts about what happened) rather than current state. Derive current state by replaying events. Enables audit trails, undo/redo, and time-travel debugging.

### Event Store Pattern

```ts
type TodoEvent =
  | { type: 'TodoCreated'; id: string; title: string; timestamp: number }
  | { type: 'TodoCompleted'; id: string; timestamp: number }
  | { type: 'TodoRenamed'; id: string; title: string; timestamp: number }
  | { type: 'TodoDeleted'; id: string; timestamp: number };

const eventLog: TodoEvent[] = [];

function appendEvent(event: TodoEvent): void {
  eventLog.push(event);
}

function getEventsSince(timestamp: number): TodoEvent[] {
  return eventLog.filter((e) => e.timestamp > timestamp);
}
```

### Projection Function

Derive current state from events:

```ts
type TodoState = Map<string, Todo>;

function projectTodos(events: TodoEvent[]): TodoState {
  const state: TodoState = new Map();
  for (const event of events) {
    const existing = state.get(event.id);
    switch (event.type) {
      case 'TodoCreated':
        state.set(event.id, {
          id: event.id,
          title: event.title,
          completed: false,
          createdAt: event.timestamp,
        });
        break;
      case 'TodoCompleted':
        if (existing) state.set(event.id, { ...existing, completed: true });
        break;
      case 'TodoRenamed':
        if (existing) state.set(event.id, { ...existing, title: event.title });
        break;
      case 'TodoDeleted':
        state.delete(event.id);
        break;
    }
  }
  return state;
}
```

### Sync and Undo via Event Exchange

```ts
function mergeEventLogs(local: TodoEvent[], remote: TodoEvent[]): TodoEvent[] {
  const seen = new Set(local.map((e) => `${e.type}-${e.timestamp}-${e.id}`));
  const newEvents = remote.filter(
    (e) => !seen.has(`${e.type}-${e.timestamp}-${e.id}`),
  );
  return [...local, ...newEvents].sort((a, b) => a.timestamp - b.timestamp);
}

function undo(events: TodoEvent[]): TodoState {
  return projectTodos(events.slice(0, -1));
}
```

**When to use event sourcing:** Audit trails (compliance, finance), undo/redo, time-travel debugging, or when change history matters as much as current state.

## Choosing a Strategy

| Data Type               | Recommended Strategy   | Rationale                                          |
| ----------------------- | ---------------------- | -------------------------------------------------- |
| User preferences        | LWW                    | Last setting is always correct                     |
| Status fields           | LWW or server-wins     | Simple, low conflict surface                       |
| Form fields             | Field-level merge      | Different users edit different fields              |
| Collaborative text      | CRDTs (Yjs, Automerge) | Concurrent edits must merge character-by-character |
| Shared lists            | CRDTs (OR-Set)         | Concurrent additions should all be preserved       |
| Counters (likes, votes) | CRDTs (PN-Counter)     | Concurrent increments must not be lost             |
| Payment amounts         | Server-wins            | Business rules must be enforced                    |
| Inventory quantities    | Server-wins            | Consistency is more important than availability    |
| Document history        | Event sourcing         | Need audit trail and undo                          |

## Hybrid Approach

Use different strategies for different fields in the same record:

```ts
const todoFieldStrategies: Record<string, string> = {
  title: 'lww',
  description: 'crdt',
  completed: 'server-wins',
  tags: 'crdt',
  priority: 'lww',
  assigneeId: 'server-wins',
};

function resolveField<T>(field: string, local: T, remote: T): T {
  const strategy = todoFieldStrategies[field] ?? 'lww';
  if (strategy === 'server-wins') return remote;
  return local;
}
```

Simple fields use LWW. Business-critical fields use server-wins. Collaborative content uses CRDTs.
