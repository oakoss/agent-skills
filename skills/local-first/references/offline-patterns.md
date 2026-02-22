---
title: Offline Patterns
description: Offline resilience patterns including network detection, write queues, retry strategies, and sync status UI for local-first web apps
tags:
  [
    offline,
    queue,
    retry,
    sync,
    indexeddb,
    background-sync,
    reconnection,
    idempotency,
    service-worker,
  ]
---

## Network Detection

`navigator.onLine` only detects whether the device has a network interface -- it does not verify actual internet connectivity. A machine connected to a router with no upstream link reports `true`.

### Fetch Probe for Real Detection

```ts
async function checkConnectivity(url = '/api/health'): Promise<boolean> {
  try {
    const response = await fetch(url, {
      method: 'HEAD',
      cache: 'no-store',
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
```

### Online/Offline Event Listeners

```ts
type ConnectionStatus = 'online' | 'offline' | 'checking';

function createConnectionMonitor(
  onStatusChange: (status: ConnectionStatus) => void,
) {
  let currentStatus: ConnectionStatus = navigator.onLine ? 'online' : 'offline';

  async function verify() {
    onStatusChange('checking');
    const isOnline = await checkConnectivity();
    currentStatus = isOnline ? 'online' : 'offline';
    onStatusChange(currentStatus);
  }

  window.addEventListener('online', verify);
  window.addEventListener('offline', () => {
    currentStatus = 'offline';
    onStatusChange('offline');
  });

  return { getStatus: () => currentStatus };
}
```

### Exponential Backoff Reconnection

```ts
function createReconnector(onReconnect: () => void) {
  let attempt = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;

  async function tryReconnect() {
    const isOnline = await checkConnectivity();
    if (isOnline) {
      attempt = 0;
      onReconnect();
      return;
    }
    attempt++;
    const base = Math.min(1000 * 2 ** attempt, 30000);
    timer = setTimeout(tryReconnect, base + Math.random() * base * 0.5);
  }

  return {
    start: () => tryReconnect(),
    stop: () => {
      if (timer) clearTimeout(timer);
    },
  };
}
```

## Write Queue Architecture

### Queue Entry Structure

```ts
type QueueEntry = {
  id: string;
  operation: 'create' | 'update' | 'delete';
  table: string;
  payload: Record<string, unknown>;
  idempotencyKey: string;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  status: 'pending' | 'in-flight' | 'failed' | 'dead';
};
```

### IndexedDB Persistence Layer

```ts
const QUEUE_DB = 'write-queue';
const QUEUE_STORE = 'operations';
const DEAD_LETTER_STORE = 'dead-letters';

function openQueueDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(QUEUE_DB, 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(QUEUE_STORE)) {
        const store = db.createObjectStore(QUEUE_STORE, { keyPath: 'id' });
        store.createIndex('status', 'status');
        store.createIndex('timestamp', 'timestamp');
      }
      if (!db.objectStoreNames.contains(DEAD_LETTER_STORE)) {
        db.createObjectStore(DEAD_LETTER_STORE, { keyPath: 'id' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function enqueue(
  entry: Omit<QueueEntry, 'id' | 'timestamp' | 'retryCount' | 'status'>,
): Promise<string> {
  const db = await openQueueDB();
  const id = crypto.randomUUID();
  const record: QueueEntry = {
    ...entry,
    id,
    timestamp: Date.now(),
    retryCount: 0,
    status: 'pending',
  };
  return new Promise((resolve, reject) => {
    const tx = db.transaction(QUEUE_STORE, 'readwrite');
    tx.objectStore(QUEUE_STORE).put(record);
    tx.oncomplete = () => resolve(id);
    tx.onerror = () => reject(tx.error);
  });
}

async function getPendingEntries(): Promise<QueueEntry[]> {
  const db = await openQueueDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(QUEUE_STORE, 'readonly');
    const request = tx.objectStore(QUEUE_STORE).index('timestamp').getAll();
    request.onsuccess = () => {
      resolve(
        (request.result as QueueEntry[]).filter(
          (e) => e.status === 'pending' || e.status === 'failed',
        ),
      );
    };
    request.onerror = () => reject(request.error);
  });
}

async function updateEntry(entry: QueueEntry): Promise<void> {
  const db = await openQueueDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(QUEUE_STORE, 'readwrite');
    tx.objectStore(QUEUE_STORE).put(entry);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function moveToDeadLetter(entry: QueueEntry): Promise<void> {
  const db = await openQueueDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction([QUEUE_STORE, DEAD_LETTER_STORE], 'readwrite');
    tx.objectStore(DEAD_LETTER_STORE).put({
      ...entry,
      status: 'dead',
      movedAt: Date.now(),
    });
    tx.objectStore(QUEUE_STORE).delete(entry.id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function removeEntry(id: string): Promise<void> {
  const db = await openQueueDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(QUEUE_STORE, 'readwrite');
    tx.objectStore(QUEUE_STORE).delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
```

## Queue Processing

### Draining the Queue on Reconnection

```ts
type DrainResult = { succeeded: number; failed: number; deadLettered: number };

async function drainQueue(
  sendFn: (entry: QueueEntry) => Promise<Response>,
): Promise<DrainResult> {
  const entries = await getPendingEntries();
  const result: DrainResult = { succeeded: 0, failed: 0, deadLettered: 0 };

  for (const entry of entries) {
    await updateEntry({ ...entry, status: 'in-flight' });
    try {
      const response = await sendFn(entry);
      if (response.ok) {
        await removeEntry(entry.id);
        result.succeeded++;
        continue;
      }
      // 4xx = permanent failure, do not retry
      if (response.status >= 400 && response.status < 500) {
        await moveToDeadLetter(entry);
        result.deadLettered++;
        continue;
      }
      throw new Error(`Server error: ${response.status}`);
    } catch {
      entry.retryCount++;
      if (entry.retryCount >= entry.maxRetries) {
        await moveToDeadLetter(entry);
        result.deadLettered++;
      } else {
        await updateEntry({ ...entry, status: 'failed' });
        result.failed++;
      }
    }
  }
  return result;
}
```

### Idempotency Keys

```ts
function sendToServer(entry: QueueEntry): Promise<Response> {
  return fetch(`/api/${entry.table}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': entry.idempotencyKey,
    },
    body: JSON.stringify({
      operation: entry.operation,
      payload: entry.payload,
    }),
  });
}
```

## Retry Strategies

| Strategy            | Detail                                                    |
| ------------------- | --------------------------------------------------------- |
| Exponential backoff | `min(1000 * 2^attempt, 60000)` with 30% jitter            |
| Max retries         | Cap at 5-10 attempts, then dead-letter                    |
| Dead letter queue   | Store permanently failed ops for manual inspection/retry  |
| User notification   | Surface dead-lettered items so the user can decide action |

### Dead Letter Queue Retry

```ts
async function retryDeadLetter(id: string): Promise<void> {
  const db = await openQueueDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction([QUEUE_STORE, DEAD_LETTER_STORE], 'readwrite');
    const getReq = tx.objectStore(DEAD_LETTER_STORE).get(id);
    getReq.onsuccess = () => {
      const entry = getReq.result;
      if (!entry) return;
      tx.objectStore(QUEUE_STORE).put({
        ...entry,
        status: 'pending',
        retryCount: 0,
      });
      tx.objectStore(DEAD_LETTER_STORE).delete(id);
    };
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
```

## Persistence Across Restarts

```ts
async function resumeQueueOnStartup(
  sendFn: (entry: QueueEntry) => Promise<Response>,
  onStatusChange: (status: ConnectionStatus) => void,
) {
  const pending = await getPendingEntries();
  for (const entry of pending.filter((e) => e.status === 'in-flight')) {
    await updateEntry({ ...entry, status: 'pending' });
  }
  if (pending.length === 0) return;

  if (await checkConnectivity()) {
    onStatusChange('online');
    await drainQueue(sendFn);
  } else {
    onStatusChange('offline');
    createReconnector(async () => {
      onStatusChange('online');
      await drainQueue(sendFn);
    }).start();
  }
}
```

## UI Feedback

### Sync Status Indicator

```tsx
type SyncStatus = 'synced' | 'syncing' | 'offline' | 'error';

function SyncIndicator({ status }: { status: SyncStatus }) {
  const config: Record<SyncStatus, { label: string; color: string }> = {
    synced: { label: 'All changes saved', color: 'green' },
    syncing: { label: 'Syncing...', color: 'blue' },
    offline: { label: 'Offline — changes saved locally', color: 'yellow' },
    error: { label: 'Sync error — will retry', color: 'red' },
  };
  const { label, color } = config[status];
  return (
    <div role="status" aria-live="polite" style={{ color }}>
      {label}
    </div>
  );
}
```

### Stale Data Warning

```tsx
function StaleDataBanner({ lastSyncedAt }: { lastSyncedAt: number | null }) {
  if (!lastSyncedAt) {
    return (
      <div role="alert">
        Data has never been synced. Connect to the internet to load latest data.
      </div>
    );
  }
  const staleMinutes = Math.floor((Date.now() - lastSyncedAt) / 60000);
  if (staleMinutes < 5) return null;
  return (
    <div role="alert">
      Data last synced {staleMinutes} minutes ago. Some information may be
      outdated.
    </div>
  );
}
```

## Background Sync API

Service Worker background sync defers operations until the browser has connectivity. The browser decides when to fire the sync event -- the page does not need to be open.

```ts
async function registerBackgroundSync(tag: string): Promise<void> {
  const registration = await navigator.serviceWorker.ready;
  await registration.sync.register(tag);
}
```

```ts
self.addEventListener('sync', (event: SyncEvent) => {
  if (event.tag === 'drain-write-queue') {
    event.waitUntil(drainQueue(sendToServer));
  }
});
```

| Constraint           | Detail                                                 |
| -------------------- | ------------------------------------------------------ |
| Browser support      | Chrome, Edge only -- no Firefox or Safari              |
| Requires SW          | Must have an active Service Worker registration        |
| No guaranteed timing | Browser batches sync events, may delay                 |
| One-shot             | Each tag fires once -- re-register for continuous sync |
| Payload via IDB      | Cannot pass data to sync event, must read from storage |

## Offline-First Read Patterns

### Cache-First with Freshness Indicator

```ts
type CachedResult<T> = {
  data: T;
  source: 'cache' | 'network';
  cachedAt: number;
  isStale: boolean;
};

async function cacheFirstFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  staleAfterMs = 300000,
): Promise<CachedResult<T>> {
  const cached = await getFromCache<T>(key);

  if (cached && !navigator.onLine) {
    return {
      data: cached.data,
      source: 'cache',
      cachedAt: cached.timestamp,
      isStale: true,
    };
  }

  try {
    const fresh = await fetcher();
    await writeToCache(key, fresh);
    return {
      data: fresh,
      source: 'network',
      cachedAt: Date.now(),
      isStale: false,
    };
  } catch {
    if (cached) {
      return {
        data: cached.data,
        source: 'cache',
        cachedAt: cached.timestamp,
        isStale: Date.now() - cached.timestamp > staleAfterMs,
      };
    }
    throw new Error('No cached data available and network request failed');
  }
}
```
