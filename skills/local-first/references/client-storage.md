---
title: Client Storage
description: Client-side storage options for local-first web apps including IndexedDB, OPFS, SQLite WASM, and PGlite with capacity limits and performance tips
tags:
  [
    indexeddb,
    opfs,
    sqlite,
    pglite,
    wasm,
    storage,
    persistence,
    capacity,
    browser,
  ]
---

## Overview Table

| Feature         | IndexedDB           | OPFS                  | SQLite WASM        | PGlite                 |
| --------------- | ------------------- | --------------------- | ------------------ | ---------------------- |
| Capacity        | 50%+ of disk        | 50%+ of disk          | Depends on backend | Depends on backend     |
| Query language  | Cursor/index-based  | File system API       | Full SQL           | Full Postgres SQL      |
| Browser support | All modern browsers | Chrome, Edge, Firefox | All (via WASM)     | All (via WASM)         |
| Persistence     | Until evicted       | Until evicted         | IndexedDB or OPFS  | IndexedDB or OPFS      |
| Thread safety   | Multi-tab safe      | Sync API: Worker only | Depends on VFS     | Single-connection      |
| Bundle size     | 0 (built-in)        | 0 (built-in)          | ~500KB-1MB         | ~3-5MB                 |
| Best for        | Key-value, simple   | SQLite backend        | Complex queries    | Postgres compatibility |

## IndexedDB

Object store built into every modern browser. Stores structured data with indexes for fast lookups. No SQL — queries use cursors and key ranges.

### Basic CRUD Pattern

```ts
function openDB(name: string, version: number): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('todos')) {
        const store = db.createObjectStore('todos', { keyPath: 'id' });
        store.createIndex('completed', 'completed');
        store.createIndex('createdAt', 'createdAt');
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function insertTodo(db: IDBDatabase, todo: Todo): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('todos', 'readwrite');
    tx.objectStore('todos').put(todo);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function getTodos(db: IDBDatabase): Promise<Todo[]> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('todos', 'readonly');
    const request = tx.objectStore('todos').getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getTodosByIndex(
  db: IDBDatabase,
  completed: boolean,
): Promise<Todo[]> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('todos', 'readonly');
    const index = tx.objectStore('todos').index('completed');
    const request = index.getAll(IDBKeyRange.only(completed));
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function deleteTodo(db: IDBDatabase, id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('todos', 'readwrite');
    tx.objectStore('todos').delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
```

### Structured Clone Gotchas

IndexedDB uses the structured clone algorithm, not JSON serialization. Key differences:

```ts
// These types are supported (unlike JSON.stringify)
const supported = {
  date: new Date(),
  regex: /pattern/g,
  blob: new Blob(['data']),
  arrayBuffer: new ArrayBuffer(8),
  map: new Map([['key', 'value']]),
  set: new Set([1, 2, 3]),
};

// These types are NOT supported — will throw DataCloneError
const unsupported = {
  // functions: () => {},
  // symbols: Symbol('test'),
  // dom: document.body,
  // errors: new Error('test'),
};

// Classes lose their prototype — store plain objects
class Todo {
  constructor(
    public id: string,
    public title: string,
  ) {}
  format() {
    return `[${this.id}] ${this.title}`;
  }
}

const todo = new Todo('1', 'Test');
// After round-trip through IndexedDB, todo.format() is gone
// Store as plain object: { id: '1', title: 'Test' }
```

## OPFS (Origin Private File System)

File system API designed for high-performance binary storage. Primary use case: backing store for SQLite WASM. Provides synchronous access in Web Workers.

### Basic File Operations

```ts
async function writeFile(name: string, data: string): Promise<void> {
  const root = await navigator.storage.getDirectory();
  const fileHandle = await root.getFileHandle(name, { create: true });
  const writable = await fileHandle.createWritable();
  await writable.write(data);
  await writable.close();
}

async function readFile(name: string): Promise<string> {
  const root = await navigator.storage.getDirectory();
  const fileHandle = await root.getFileHandle(name);
  const file = await fileHandle.getFile();
  return file.text();
}

async function deleteFile(name: string): Promise<void> {
  const root = await navigator.storage.getDirectory();
  await root.removeEntry(name);
}

async function listFiles(): Promise<string[]> {
  const root = await navigator.storage.getDirectory();
  const names: string[] = [];
  for await (const [name] of root.entries()) {
    names.push(name);
  }
  return names;
}
```

### Synchronous Access (Web Worker Only)

The synchronous access handle API is faster and required for SQLite's synchronous I/O model. Only available in Web Workers.

```ts
// worker.ts
async function syncFileAccess(): Promise<void> {
  const root = await navigator.storage.getDirectory();
  const fileHandle = await root.getFileHandle('database.sqlite3', {
    create: true,
  });

  const accessHandle = await fileHandle.createSyncAccessHandle();

  const encoder = new TextEncoder();
  const data = encoder.encode('binary data');

  accessHandle.write(data, { at: 0 });
  accessHandle.flush();

  const buffer = new ArrayBuffer(data.byteLength);
  accessHandle.read(buffer, { at: 0 });

  accessHandle.close();
}
```

## SQLite WASM

Full SQL database running in the browser via WebAssembly. Uses wa-sqlite or sql.js for the engine and OPFS or IndexedDB for persistence.

### Setup with wa-sqlite and OPFS

```ts
import * as SQLite from 'wa-sqlite';
import SQLiteESMFactory from 'wa-sqlite/dist/wa-sqlite-async.mjs';
import { OPFSCoopSyncVFS } from 'wa-sqlite/src/examples/OPFSCoopSyncVFS.js';

async function createDB(): Promise<{
  sqlite3: SQLiteAPI;
  db: number;
}> {
  const module = await SQLiteESMFactory();
  const sqlite3 = SQLite.Factory(module);

  const vfs = await OPFSCoopSyncVFS.create('app', module);
  sqlite3.vfs_register(vfs, true);

  const db = await sqlite3.open_v2('app.db');

  await sqlite3.exec(
    db,
    `
    CREATE TABLE IF NOT EXISTS todos (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      completed INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    )
  `,
  );

  return { sqlite3, db };
}
```

### Query Patterns

```ts
async function insertTodo(
  sqlite3: SQLiteAPI,
  db: number,
  todo: { id: string; title: string },
): Promise<void> {
  await sqlite3.exec(
    db,
    `
    INSERT INTO todos (id, title) VALUES ('${todo.id}', '${todo.title}')
  `,
  );
}

async function queryTodos(sqlite3: SQLiteAPI, db: number): Promise<Todo[]> {
  const todos: Todo[] = [];

  await sqlite3.exec(
    db,
    `SELECT * FROM todos WHERE completed = 0`,
    (row: string[], columns: string[]) => {
      const todo = {} as Record<string, string>;
      columns.forEach((col, i) => {
        todo[col] = row[i];
      });
      todos.push(todo as unknown as Todo);
    },
  );

  return todos;
}

// Use prepared statements for parameterized queries
async function queryByTitle(
  sqlite3: SQLiteAPI,
  db: number,
  search: string,
): Promise<Todo[]> {
  const todos: Todo[] = [];
  const str = sqlite3.str_new(
    db,
    `
    SELECT * FROM todos WHERE title LIKE ?
  `,
  );

  const prepared = await sqlite3.prepare_v2(db, sqlite3.str_value(str));
  if (prepared) {
    sqlite3.bind_text(prepared.stmt, 1, `%${search}%`);
    while ((await sqlite3.step(prepared.stmt)) === SQLite.SQLITE_ROW) {
      todos.push({
        id: sqlite3.column_text(prepared.stmt, 0),
        title: sqlite3.column_text(prepared.stmt, 1),
        completed: sqlite3.column_int(prepared.stmt, 2) === 1,
      } as Todo);
    }
    sqlite3.finalize(prepared.stmt);
  }

  sqlite3.str_finish(str);
  return todos;
}
```

## PGlite

Full Postgres database running in the browser via WASM. Supports Postgres SQL, extensions (pgvector, etc.), and full query compatibility.

### Basic Setup

```ts
import { PGlite } from '@electric-sql/pglite';

const pg = new PGlite('idb://my-app');

await pg.exec(`
  CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'
  )
`);
```

### Query Patterns

```ts
async function insertTodo(title: string): Promise<Todo> {
  const result = await pg.query<Todo>(
    'INSERT INTO todos (title) VALUES ($1) RETURNING *',
    [title],
  );
  return result.rows[0];
}

async function getTodos(): Promise<Todo[]> {
  const result = await pg.query<Todo>(
    'SELECT * FROM todos WHERE completed = false ORDER BY created_at DESC',
  );
  return result.rows;
}

async function searchTodos(search: string): Promise<Todo[]> {
  const result = await pg.query<Todo>(
    "SELECT * FROM todos WHERE title ILIKE '%' || $1 || '%'",
    [search],
  );
  return result.rows;
}

async function updateMetadata(
  id: string,
  metadata: Record<string, unknown>,
): Promise<void> {
  await pg.query('UPDATE todos SET metadata = metadata || $1 WHERE id = $2', [
    JSON.stringify(metadata),
    id,
  ]);
}
```

### With Extensions

```ts
import { PGlite } from '@electric-sql/pglite';
import { vector } from '@electric-sql/pglite/vector';

const pg = new PGlite({
  dataDir: 'idb://my-app',
  extensions: { vector },
});

await pg.exec('CREATE EXTENSION IF NOT EXISTS vector');

await pg.exec(`
  CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(384)
  )
`);

// Similarity search
const results = await pg.query(
  `SELECT id, content, embedding <=> $1 AS distance
   FROM documents
   ORDER BY distance
   LIMIT 5`,
  [JSON.stringify(queryEmbedding)],
);
```

## Selection Guide

| If you need...                       | Use              |
| ------------------------------------ | ---------------- |
| Simple key-value storage, no SQL     | IndexedDB        |
| High-performance binary file storage | OPFS             |
| SQL queries on the client            | SQLite WASM      |
| Postgres SQL compatibility           | PGlite           |
| Smallest bundle size                 | IndexedDB (0 KB) |
| Complex joins and aggregations       | SQLite or PGlite |
| Extension support (pgvector, etc.)   | PGlite           |
| Backing store for sync engines       | OPFS + SQLite    |

**Decision flow:**

1. **Need SQL?** If no, IndexedDB is sufficient. If yes, continue.
2. **Need Postgres compatibility?** If yes, PGlite. If standard SQL is fine, SQLite WASM.
3. **Bundle size constrained?** PGlite is 3-5MB. SQLite WASM is ~500KB-1MB. IndexedDB is 0.
4. **Using a sync engine?** Check what the engine requires — PowerSync needs SQLite, ElectricSQL works with any.

## Capacity and Limits

Browser storage quotas vary. Most browsers allow up to 50-80% of available disk space for a single origin.

```ts
async function checkStorageQuota(): Promise<{
  usage: number;
  quota: number;
  percentUsed: number;
}> {
  const estimate = await navigator.storage.estimate();
  return {
    usage: estimate.usage ?? 0,
    quota: estimate.quota ?? 0,
    percentUsed: ((estimate.usage ?? 0) / (estimate.quota ?? 1)) * 100,
  };
}
```

### Persistent Storage

By default, browsers can evict storage under pressure (low disk space). Request persistent storage to prevent eviction:

```ts
async function requestPersistence(): Promise<boolean> {
  if (navigator.storage?.persist) {
    const granted = await navigator.storage.persist();
    console.log(`Persistent storage: ${granted ? 'granted' : 'denied'}`);
    return granted;
  }
  return false;
}
```

Chrome auto-grants persistence for installed PWAs and sites with high engagement. Firefox prompts the user. Safari has limited support.

### Eviction Order

When storage pressure occurs and persistence is not granted:

1. Cache API entries (least recently used first)
2. IndexedDB databases (least recently used origin first)
3. OPFS files (same origin-based eviction)

## Performance Tips

**Batch writes in transactions.** Individual writes are expensive; batch them.

```ts
// Slow: each insert is its own transaction
for (const todo of todos) {
  await insertTodo(db, todo);
}

// Fast: batch all inserts in one transaction
async function batchInsert(db: IDBDatabase, todos: Todo[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('todos', 'readwrite');
    const store = tx.objectStore('todos');
    for (const todo of todos) {
      store.put(todo);
    }
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
```

**Avoid reading large blobs on the main thread.** Move heavy I/O to a Web Worker.

```ts
// main.ts
const worker = new Worker(new URL('./db-worker.ts', import.meta.url), {
  type: 'module',
});

worker.postMessage({ type: 'query', sql: 'SELECT * FROM large_table' });

worker.onmessage = (event) => {
  const { rows } = event.data;
  renderTable(rows);
};
```

**Use indexes for frequent queries.** Without indexes, IndexedDB scans every record.

## Storage Quota Management

### StorageManager API

```ts
async function getStorageInfo(): Promise<{
  usage: number;
  quota: number;
  percentUsed: number;
  persisted: boolean;
}> {
  const estimate = await navigator.storage.estimate();
  const persisted = (await navigator.storage.persisted?.()) ?? false;

  return {
    usage: estimate.usage ?? 0,
    quota: estimate.quota ?? 0,
    percentUsed: ((estimate.usage ?? 0) / (estimate.quota ?? 1)) * 100,
    persisted,
  };
}

async function requestPersistentStorage(): Promise<boolean> {
  if (!navigator.storage?.persist) return false;
  return navigator.storage.persist();
}
```

### Browser-Specific Limits

| Browser | Quota                       | Eviction Behavior                                 |
| ------- | --------------------------- | ------------------------------------------------- |
| Chrome  | 60% of total disk space     | LRU by origin, entire origin evicted at once      |
| Firefox | 10% of disk or 10 GiB max   | LRU by origin, entire origin evicted at once      |
| Safari  | 60% of disk, 1 GiB soft cap | 7-day ITP cap: evicts after 7 days no interaction |

Safari's Intelligent Tracking Prevention (ITP) proactively evicts all storage for origins that haven't been interacted with in 7 days. This applies to IndexedDB, OPFS, Cache API, and localStorage. PWAs added to the home screen are exempt.

### QuotaExceededError Handling

```ts
async function safeWrite(
  db: IDBDatabase,
  storeName: string,
  data: unknown,
): Promise<boolean> {
  try {
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      tx.objectStore(storeName).put(data);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
    return true;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'QuotaExceededError') {
      await evictOldData(db, storeName);
      return safeWrite(db, storeName, data);
    }
    throw error;
  }
}
```

### Eviction Strategies

Browsers evict entire origins at once based on LRU (least recently used). Within your application, implement your own eviction to stay under quota.

```ts
async function evictOldData(
  db: IDBDatabase,
  storeName: string,
  maxAge = 30 * 24 * 60 * 60 * 1000,
): Promise<number> {
  const cutoff = Date.now() - maxAge;
  let evicted = 0;

  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    const index = store.index('createdAt');
    const range = IDBKeyRange.upperBound(new Date(cutoff).toISOString());
    const request = index.openCursor(range);

    request.onsuccess = () => {
      const cursor = request.result;
      if (cursor) {
        cursor.delete();
        evicted++;
        cursor.continue();
      }
    };

    tx.oncomplete = () => resolve(evicted);
    tx.onerror = () => reject(tx.error);
  });
}
```

**Use indexes for frequent queries.** Without indexes, IndexedDB scans every record.

```ts
// Create indexes during upgrade
request.onupgradeneeded = () => {
  const store = db.createObjectStore('todos', { keyPath: 'id' });
  store.createIndex('by_project', 'projectId');
  store.createIndex('by_status', ['completed', 'createdAt']);
};

// Query using the compound index
const index = store.index('by_status');
const range = IDBKeyRange.bound([false, ''], [false, '\uffff']);
const request = index.openCursor(range, 'prev');
```
