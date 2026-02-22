---
title: Testing Local-First Applications
description: Testing strategies for local-first apps covering conflict resolution, sync engine mocking, offline scenarios, multi-client convergence, and React component testing
tags:
  [
    testing,
    vitest,
    conflict-resolution,
    offline,
    sync,
    mock,
    crdt,
    indexeddb,
    multi-client,
    snapshot,
    electric,
    integration,
  ]
---

## Testing Challenges

| Challenge            | What Makes It Different                               | Testing Strategy                           |
| -------------------- | ----------------------------------------------------- | ------------------------------------------ |
| Async Sync           | Data arrives over time, not in a single request       | Mock streams with controlled emissions     |
| Eventual Consistency | Clients may see different states temporarily          | Assert convergence, not intermediate state |
| Offline States       | App must function without network                     | Simulate network loss, verify queue        |
| Conflict Resolution  | Concurrent edits produce divergent states             | Property-based testing for merge functions |
| Multi-Client         | Multiple clients editing the same data simultaneously | Deterministic two-client test harness      |
| IndexedDB            | Browser storage API unavailable in Node               | Use fake-indexeddb polyfill                |
| Time Dependency      | LWW and retry logic depend on timestamps              | Control time with vi.useFakeTimers         |

## Unit Testing Conflict Resolution

### LWW Merge Correctness

```ts
import { describe, expect, it } from 'vitest';

type LWWRecord<T> = { value: T; updatedAt: number };

function lwwMerge<T>(local: LWWRecord<T>, remote: LWWRecord<T>): LWWRecord<T> {
  return remote.updatedAt > local.updatedAt ? remote : local;
}

describe('lwwMerge', () => {
  it('picks the record with the later timestamp', () => {
    const local: LWWRecord<string> = { value: 'local', updatedAt: 100 };
    const remote: LWWRecord<string> = { value: 'remote', updatedAt: 200 };
    expect(lwwMerge(local, remote)).toEqual(remote);
  });

  it('keeps local when timestamps are equal', () => {
    const local: LWWRecord<string> = { value: 'local', updatedAt: 100 };
    const remote: LWWRecord<string> = { value: 'remote', updatedAt: 100 };
    expect(lwwMerge(local, remote)).toEqual(local);
  });

  it('is idempotent', () => {
    const a: LWWRecord<string> = { value: 'a', updatedAt: 100 };
    const b: LWWRecord<string> = { value: 'b', updatedAt: 200 };
    expect(lwwMerge(a, b)).toEqual(lwwMerge(lwwMerge(a, b), b));
  });
});
```

### Field-Level Merge with Property-Based Testing

```ts
import { describe, expect, it } from 'vitest';
import fc from 'fast-check';

type MergeableRecord<T> = { value: T; fieldTimestamps: Record<string, number> };

function fieldMerge<T extends Record<string, unknown>>(
  local: MergeableRecord<T>,
  remote: MergeableRecord<T>,
): MergeableRecord<T> {
  const merged = { ...local.value };
  const timestamps = { ...local.fieldTimestamps };
  for (const key of Object.keys(remote.value)) {
    if (
      (remote.fieldTimestamps[key] ?? 0) > (local.fieldTimestamps[key] ?? 0)
    ) {
      (merged as Record<string, unknown>)[key] = remote.value[key];
      timestamps[key] = remote.fieldTimestamps[key];
    }
  }
  return { value: merged as T, fieldTimestamps: timestamps };
}

describe('fieldMerge properties', () => {
  const recordArb = fc.record({
    value: fc.record({ title: fc.string(), done: fc.boolean() }),
    fieldTimestamps: fc.record({
      title: fc.nat({ max: 10000 }),
      done: fc.nat({ max: 10000 }),
    }),
  });

  it('is commutative when timestamps differ', () => {
    fc.assert(
      fc.property(recordArb, recordArb, (a, b) => {
        expect(fieldMerge(a, b).value).toEqual(fieldMerge(b, a).value);
      }),
    );
  });

  it('preserves both edits when fields have different winners', () => {
    const local = {
      value: { title: 'updated', done: false },
      fieldTimestamps: { title: 200, done: 50 },
    };
    const remote = {
      value: { title: 'original', done: true },
      fieldTimestamps: { title: 50, done: 200 },
    };
    const result = fieldMerge(local, remote);
    expect(result.value.title).toBe('updated');
    expect(result.value.done).toBe(true);
  });
});
```

## Mocking Sync Engines

### Mock ElectricSQL ShapeStream

```ts
type ShapeMessage = {
  headers: { operation?: string; control?: string };
  key?: string;
  value?: Record<string, unknown>;
  offset?: string;
};

type Subscriber = (messages: ShapeMessage[]) => void;

class MockShapeStream {
  subscribers: Subscriber[] = [];

  subscribe(callback: Subscriber): () => void {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter((s) => s !== callback);
    };
  }

  emit(messages: ShapeMessage[]): void {
    for (const sub of this.subscribers) sub(messages);
  }

  emitInsert(key: string, value: Record<string, unknown>): void {
    this.emit([{ headers: { operation: 'insert' }, key, value }]);
  }

  emitUpdate(key: string, value: Record<string, unknown>): void {
    this.emit([{ headers: { operation: 'update' }, key, value }]);
  }

  emitDelete(key: string): void {
    this.emit([{ headers: { operation: 'delete' }, key }]);
  }

  emitUpToDate(): void {
    this.emit([{ headers: { control: 'up-to-date' } }]);
  }
}

class MockShape<T extends Record<string, unknown>> {
  private data = new Map<string, T>();
  private listeners: Array<(data: Map<string, T>) => void> = [];

  constructor(stream: MockShapeStream) {
    stream.subscribe((messages) => {
      for (const msg of messages) {
        if (
          msg.headers.operation === 'insert' ||
          msg.headers.operation === 'update'
        ) {
          this.data.set(msg.key!, msg.value as T);
        }
        if (msg.headers.operation === 'delete') this.data.delete(msg.key!);
      }
      for (const listener of this.listeners) listener(new Map(this.data));
    });
  }

  subscribe(callback: (data: Map<string, T>) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  get currentValue(): Map<string, T> {
    return new Map(this.data);
  }
}
```

### Using Mocks in Tests

```ts
import { beforeEach, describe, expect, it } from 'vitest';

describe('todo sync', () => {
  let stream: MockShapeStream;
  let shape: MockShape<{ id: string; title: string; completed: boolean }>;

  beforeEach(() => {
    stream = new MockShapeStream();
    shape = new MockShape(stream);
  });

  it('materializes inserts into current state', () => {
    stream.emitInsert('"todos"/"1"', {
      id: '1',
      title: 'Buy milk',
      completed: false,
    });
    stream.emitInsert('"todos"/"2"', {
      id: '2',
      title: 'Walk dog',
      completed: false,
    });
    expect(shape.currentValue.size).toBe(2);
  });

  it('applies updates to existing records', () => {
    stream.emitInsert('"todos"/"1"', {
      id: '1',
      title: 'Buy milk',
      completed: false,
    });
    stream.emitUpdate('"todos"/"1"', {
      id: '1',
      title: 'Buy milk',
      completed: true,
    });
    expect(shape.currentValue.get('"todos"/"1"')?.completed).toBe(true);
  });

  it('removes deleted records', () => {
    stream.emitInsert('"todos"/"1"', {
      id: '1',
      title: 'Buy milk',
      completed: false,
    });
    stream.emitDelete('"todos"/"1"');
    expect(shape.currentValue.size).toBe(0);
  });
});
```

## Testing Offline Scenarios

### Write Queue with Offline Simulation

```ts
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

type QueuedWrite = {
  id: string;
  url: string;
  method: string;
  body: string;
  retries: number;
};

class WriteQueue {
  private queue: QueuedWrite[] = [];
  private online = true;

  setOnline(online: boolean): void {
    this.online = online;
    if (online) void this.drain();
  }

  async enqueue(write: Omit<QueuedWrite, 'retries'>): Promise<void> {
    this.queue.push({ ...write, retries: 0 });
    if (this.online) await this.drain();
  }

  async drain(): Promise<void> {
    const pending = [...this.queue];
    this.queue = [];
    for (const write of pending) {
      try {
        const res = await fetch(write.url, {
          method: write.method,
          body: write.body,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      } catch {
        if (write.retries < 3)
          this.queue.push({ ...write, retries: write.retries + 1 });
      }
    }
  }

  get pending(): number {
    return this.queue.length;
  }
}

describe('WriteQueue', () => {
  let queue: WriteQueue;

  beforeEach(() => {
    queue = new WriteQueue();
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => vi.restoreAllMocks());

  it('queues writes while offline', async () => {
    queue.setOnline(false);
    await queue.enqueue({
      id: '1',
      url: '/api/todos',
      method: 'POST',
      body: '{}',
    });
    expect(queue.pending).toBe(1);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('drains queue on reconnect', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response('ok', { status: 200 }));
    queue.setOnline(false);
    await queue.enqueue({
      id: '1',
      url: '/api/todos',
      method: 'POST',
      body: '{}',
    });
    queue.setOnline(true);
    await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(queue.pending).toBe(0);
  });

  it('drops writes after 3 retries', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('Network error'));
    await queue.enqueue({
      id: '1',
      url: '/api/todos',
      method: 'POST',
      body: '{}',
    });
    await queue.drain();
    await queue.drain();
    await queue.drain();
    expect(queue.pending).toBe(0);
  });
});
```

## Multi-Client Convergence Testing

```ts
import { describe, expect, it } from 'vitest';

type Todo = { id: string; title: string; completed: boolean };
type LWWRecord<T> = { value: T; updatedAt: number };

class MockClient {
  state = new Map<string, LWWRecord<Todo>>();

  write(id: string, value: Todo, timestamp: number): void {
    this.state.set(id, { value, updatedAt: timestamp });
  }

  sync(remote: MockClient): void {
    for (const [id, remoteRecord] of remote.state) {
      const local = this.state.get(id);
      if (!local || remoteRecord.updatedAt > local.updatedAt) {
        this.state.set(id, remoteRecord);
      }
    }
  }

  get(id: string): Todo | undefined {
    return this.state.get(id)?.value;
  }
}

describe('multi-client convergence', () => {
  it('converges after concurrent edits', () => {
    const clientA = new MockClient();
    const clientB = new MockClient();
    clientA.write('1', { id: '1', title: 'Buy milk', completed: false }, 100);
    clientB.write(
      '1',
      { id: '1', title: 'Buy almond milk', completed: false },
      200,
    );
    clientA.sync(clientB);
    clientB.sync(clientA);
    expect(clientA.get('1')).toEqual(clientB.get('1'));
    expect(clientA.get('1')?.title).toBe('Buy almond milk');
  });

  it('preserves independent writes from both clients', () => {
    const clientA = new MockClient();
    const clientB = new MockClient();
    clientA.write('1', { id: '1', title: 'Task A', completed: true }, 300);
    clientB.write('2', { id: '2', title: 'Task B', completed: false }, 250);
    clientA.sync(clientB);
    clientB.sync(clientA);
    expect(clientA.get('1')).toEqual(clientB.get('1'));
    expect(clientA.get('2')).toEqual(clientB.get('2'));
  });
});
```

## Testing React Components with useShape

```tsx
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('@electric-sql/react', () => ({ useShape: vi.fn() }));
import { useShape } from '@electric-sql/react';

type Todo = { id: string; title: string; completed: boolean };

function TodoList() {
  const { data, isLoading, isError, error } = useShape<Todo>({
    url: 'http://localhost:3000/v1/shape',
    params: { table: 'todos' },
  });
  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error?.message}</div>;
  return (
    <ul>
      {data.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  );
}

describe('TodoList', () => {
  afterEach(cleanup);

  it('shows loading state during initial sync', () => {
    vi.mocked(useShape).mockReturnValue({
      data: [],
      isLoading: true,
      isError: false,
      error: undefined,
      lastSyncedAt: undefined,
    });
    render(<TodoList />);
    expect(screen.getByText('Loading...')).toBeDefined();
  });

  it('renders synced todos', () => {
    vi.mocked(useShape).mockReturnValue({
      data: [
        { id: '1', title: 'Buy milk', completed: false },
        { id: '2', title: 'Walk dog', completed: true },
      ],
      isLoading: false,
      isError: false,
      error: undefined,
      lastSyncedAt: new Date(),
    });
    render(<TodoList />);
    expect(screen.getByText('Buy milk')).toBeDefined();
    expect(screen.getByText('Walk dog')).toBeDefined();
  });

  it('shows error on sync failure', () => {
    vi.mocked(useShape).mockReturnValue({
      data: [],
      isLoading: false,
      isError: true,
      error: new Error('Connection refused'),
      lastSyncedAt: undefined,
    });
    render(<TodoList />);
    expect(screen.getByText('Error: Connection refused')).toBeDefined();
  });
});
```

## Vitest Patterns

### IndexedDB Setup with fake-indexeddb

```ts
import 'fake-indexeddb/auto';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

class TodoStore {
  private dbPromise: Promise<IDBDatabase>;

  constructor(dbName: string) {
    this.dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(dbName, 1);
      req.onupgradeneeded = () =>
        req.result.createObjectStore('todos', { keyPath: 'id' });
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async put(todo: { id: string; title: string }): Promise<void> {
    const db = await this.dbPromise;
    return new Promise((resolve, reject) => {
      const tx = db.transaction('todos', 'readwrite');
      tx.objectStore('todos').put(todo);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async getAll(): Promise<Array<{ id: string; title: string }>> {
    const db = await this.dbPromise;
    return new Promise((resolve, reject) => {
      const req = db
        .transaction('todos', 'readonly')
        .objectStore('todos')
        .getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  close(): void {
    this.dbPromise.then((db) => db.close());
  }
}

describe('TodoStore', () => {
  let store: TodoStore;

  beforeEach(() => {
    store = new TodoStore(`test-${Date.now()}`);
  });

  afterEach(() => store.close());

  it('persists and retrieves todos', async () => {
    await store.put({ id: '1', title: 'Buy milk' });
    await store.put({ id: '2', title: 'Walk dog' });
    const todos = await store.getAll();
    expect(todos).toHaveLength(2);
  });
});
```

### Time Control for Retry Logic

```ts
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

function retryWithBackoff(
  fn: () => Promise<void>,
  maxRetries: number,
): Promise<void> {
  let attempt = 0;
  async function execute(): Promise<void> {
    try {
      await fn();
    } catch {
      attempt++;
      if (attempt >= maxRetries) throw new Error('Max retries exceeded');
      await new Promise((r) => setTimeout(r, 1000 * 2 ** attempt));
      return execute();
    }
  }
  return execute();
}

describe('retryWithBackoff', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('retries with exponential backoff', async () => {
    let calls = 0;
    const fn = vi.fn(async () => {
      calls++;
      if (calls < 3) throw new Error('Fail');
    });
    const promise = retryWithBackoff(fn, 5);
    await vi.advanceTimersByTimeAsync(2000);
    await vi.advanceTimersByTimeAsync(4000);
    await promise;
    expect(fn).toHaveBeenCalledTimes(3);
  });
});
```

## Snapshot Testing CRDT State

```ts
import { describe, expect, it } from 'vitest';

type GCounter = Record<string, number>;

function increment(counter: GCounter, nodeId: string): GCounter {
  return { ...counter, [nodeId]: (counter[nodeId] ?? 0) + 1 };
}

function merge(a: GCounter, b: GCounter): GCounter {
  const result: GCounter = { ...a };
  for (const [node, count] of Object.entries(b)) {
    result[node] = Math.max(result[node] ?? 0, count);
  }
  return result;
}

describe('GCounter snapshot', () => {
  it('matches expected state after concurrent increments', () => {
    let nodeA: GCounter = {};
    let nodeB: GCounter = {};
    nodeA = increment(increment(nodeA, 'A'), 'A');
    nodeB = increment(increment(increment(nodeB, 'B'), 'B'), 'B');
    expect(merge(nodeA, nodeB)).toMatchInlineSnapshot(`
      {
        "A": 2,
        "B": 3,
      }
    `);
  });

  it('merge is idempotent', () => {
    const a: GCounter = { A: 3, B: 1 };
    const b: GCounter = { A: 1, B: 4 };
    expect(merge(a, b)).toEqual(merge(merge(a, b), b));
  });
});
```
