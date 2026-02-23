---
title: Background Sync
description: Background Sync API, workbox-background-sync plugin and Queue class, cross-browser fallbacks, IndexedDB write queue, idempotency keys
tags:
  [
    background-sync,
    workbox-background-sync,
    Queue,
    IndexedDB,
    idempotency,
    offline,
    fallback,
  ]
---

# Background Sync

## Browser Support

The Background Sync API is supported in Chrome and Edge only (~80% global support). Firefox and Safari do not support it. Any implementation must include a fallback strategy for cross-browser compatibility.

## How Background Sync Works

```text
Page sends request ──> SW intercepts ──> Network fails
    │
    └── Request queued in IndexedDB
          │
          └── Browser fires "sync" event when connectivity returns
                │
                └── SW replays queued requests
```

The browser controls when the sync event fires. It uses exponential backoff and may coalesce multiple sync registrations.

## Workbox Background Sync Plugin

The simplest approach uses `BackgroundSyncPlugin` as a plugin on a strategy. It automatically queues failed requests and replays them:

```ts
import { registerRoute } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';
import { BackgroundSyncPlugin } from 'workbox-background-sync';

const bgSyncPlugin = new BackgroundSyncPlugin('api-queue', {
  maxRetentionTime: 24 * 60,
  onSync: async ({ queue }) => {
    let entry;
    while ((entry = await queue.shiftRequest())) {
      try {
        await fetch(entry.request);
      } catch (error) {
        await queue.unshiftRequest(entry);
        throw error;
      }
    }
  },
});

registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkOnly({ plugins: [bgSyncPlugin] }),
  'POST',
);
```

`maxRetentionTime` is in minutes. Requests older than this are discarded on the next sync.

## Queue Class for Fine-Grained Control

The `Queue` class provides direct control over the request queue:

```ts
import { Queue } from 'workbox-background-sync';

const queue = new Queue('mutations', {
  maxRetentionTime: 7 * 24 * 60,
  onSync: async ({ queue }) => {
    let entry;
    while ((entry = await queue.shiftRequest())) {
      try {
        await fetch(entry.request);
      } catch (error) {
        await queue.unshiftRequest(entry);
        throw error;
      }
    }
  },
});

self.addEventListener('fetch', (event: FetchEvent) => {
  if (
    event.request.method === 'POST' &&
    event.request.url.includes('/api/mutations')
  ) {
    const bgSyncLogic = async () => {
      try {
        return await fetch(event.request.clone());
      } catch (error) {
        await queue.pushRequest({ request: event.request });
        return new Response(JSON.stringify({ queued: true }), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    };
    event.respondWith(bgSyncLogic());
  }
});
```

## Queue API Methods

| Method                        | Description                                   |
| ----------------------------- | --------------------------------------------- |
| `pushRequest({ request })`    | Add request to end of queue                   |
| `unshiftRequest({ request })` | Add request to front of queue (for retry)     |
| `shiftRequest()`              | Remove and return first request               |
| `popRequest()`                | Remove and return last request                |
| `getAll()`                    | Return all queued requests (without removing) |
| `size()`                      | Return number of queued requests              |

## Idempotency Keys

Background sync may replay requests that the server already received (if the original response was lost). Always include idempotency keys:

```ts
self.addEventListener('fetch', (event: FetchEvent) => {
  if (event.request.method === 'POST' && event.request.url.includes('/api/')) {
    const clonedRequest = event.request.clone();

    const addIdempotencyKey = async () => {
      const body = await clonedRequest.json();
      if (!body.idempotencyKey) {
        body.idempotencyKey = crypto.randomUUID();
      }
      return new Request(event.request.url, {
        method: 'POST',
        headers: event.request.headers,
        body: JSON.stringify(body),
      });
    };

    event.respondWith(addIdempotencyKey().then((request) => fetch(request)));
  }
});
```

The server must check the idempotency key and return the cached response for duplicate requests.

## Cross-Browser Fallback Pattern

For Firefox and Safari, implement an IndexedDB-based write queue with online/offline detection:

```ts
import { openDB, type IDBPDatabase } from 'idb';

interface QueuedMutation {
  id: string;
  url: string;
  method: string;
  body: string;
  headers: Record<string, string>;
  timestamp: number;
  idempotencyKey: string;
}

async function getDB(): Promise<IDBPDatabase> {
  return openDB('offline-queue', 1, {
    upgrade(db) {
      db.createObjectStore('mutations', { keyPath: 'id' });
    },
  });
}

async function queueMutation(
  mutation: Omit<QueuedMutation, 'id' | 'timestamp'>,
): Promise<void> {
  const db = await getDB();
  await db.put('mutations', {
    ...mutation,
    id: crypto.randomUUID(),
    timestamp: Date.now(),
  });
}

async function flushQueue(): Promise<void> {
  const db = await getDB();
  const mutations = await db.getAll('mutations');

  for (const mutation of mutations) {
    try {
      await fetch(mutation.url, {
        method: mutation.method,
        headers: {
          ...mutation.headers,
          'Idempotency-Key': mutation.idempotencyKey,
        },
        body: mutation.body,
      });
      await db.delete('mutations', mutation.id);
    } catch {
      break;
    }
  }
}

window.addEventListener('online', flushQueue);

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && navigator.onLine) {
    flushQueue();
  }
});
```

## Hybrid Approach

Combine Background Sync API (when available) with the IndexedDB fallback:

```ts
async function submitMutation(url: string, body: string): Promise<Response> {
  try {
    return await fetch(url, { method: 'POST', body });
  } catch {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      await queueInServiceWorker(url, body);
    } else {
      await queueMutation({
        url,
        method: 'POST',
        body,
        headers: { 'Content-Type': 'application/json' },
        idempotencyKey: crypto.randomUUID(),
      });
    }
    return new Response(JSON.stringify({ queued: true }), {
      status: 202,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
```

## Periodic Background Sync

Periodic Background Sync runs at intervals, but it is Chromium-only and requires the app to be installed as a PWA:

```ts
const registration = await navigator.serviceWorker.ready;

const status = await navigator.permissions.query({
  name: 'periodic-background-sync' as PermissionName,
});

if (status.state === 'granted') {
  await registration.periodicSync.register('content-sync', {
    minInterval: 24 * 60 * 60 * 1000,
  });
}
```

In the service worker:

```ts
self.addEventListener('periodicsync', (event: Event) => {
  const syncEvent = event as ExtendableEvent & { tag: string };
  if (syncEvent.tag === 'content-sync') {
    syncEvent.waitUntil(syncContent());
  }
});
```

The browser determines actual interval based on site engagement score. `minInterval` is a hint, not a guarantee.

## Testing Background Sync

Chrome DevTools > Application > Service Workers has a "Sync" button to trigger sync events manually. Use the "Offline" checkbox in the Network panel to simulate connectivity loss.

For automated testing:

```ts
// In SW test harness
const syncEvent = new ExtendableEvent('sync');
Object.defineProperty(syncEvent, 'tag', { value: 'api-queue' });
self.dispatchEvent(syncEvent);
```
