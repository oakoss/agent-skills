---
title: Local-First Patterns
description: Integration with sync engines, data caching in IndexedDB vs Cache API, OPFS patterns, storage quota management, and Navigation Preload
tags:
  [
    local-first,
    sync-engine,
    IndexedDB,
    Cache-API,
    OPFS,
    storage-quota,
    Navigation-Preload,
    Electric,
  ]
---

# Local-First Patterns

## Separation of Concerns

In a local-first architecture with a sync engine, the service worker and the sync engine have distinct responsibilities:

| Responsibility        | Service Worker                    | Sync Engine (e.g., Electric)       |
| --------------------- | --------------------------------- | ---------------------------------- |
| App shell caching     | Yes -- precache HTML/JS/CSS       | No                                 |
| Static asset caching  | Yes -- images, fonts, icons       | No                                 |
| API response caching  | Selective (non-synced endpoints)  | No                                 |
| Application data sync | No                                | Yes -- handles reads, writes, sync |
| Offline data access   | No (data lives in sync engine DB) | Yes -- local DB is source of truth |
| Background sync       | Queues for non-synced mutations   | Handles its own sync protocol      |
| Push notifications    | Yes -- shows notifications        | May trigger via server events      |

The key principle: let the sync engine handle all application data. The service worker handles everything else -- the app shell, static assets, and browser APIs like push and background sync.

## App Shell Strategy with Sync Engine

Precache the app shell so the application loads instantly, then the sync engine handles data:

```ts
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute, NavigationRoute } from 'workbox-routing';
import { NetworkFirst } from 'workbox-strategies';

precacheAndRoute(self.__WB_MANIFEST);

const navigationHandler = new NetworkFirst({
  cacheName: 'navigations',
  networkTimeoutSeconds: 3,
});

registerRoute(new NavigationRoute(navigationHandler));
```

Do not cache API endpoints that the sync engine manages. The sync engine maintains its own local database and handles replication independently.

## IndexedDB vs Cache API

These two storage mechanisms serve different purposes:

| Feature          | IndexedDB                           | Cache API                     |
| ---------------- | ----------------------------------- | ----------------------------- |
| Data model       | Structured key-value / object store | Request-Response pairs        |
| Query capability | Indexes, key ranges, cursors        | URL matching only             |
| Best for         | Application data, offline queues    | HTTP responses, static assets |
| Access from SW   | Yes                                 | Yes                           |
| Transactions     | Yes (read/write)                    | No                            |
| Size limit       | Large (quota-managed)               | Large (quota-managed)         |

### When to Use Each

- **Cache API**: HTTP responses, precached assets, API response caching, offline fallback pages
- **IndexedDB**: Application state, offline mutation queues, sync engine storage, user preferences, structured data

Sync engines typically use IndexedDB (or OPFS) as their backing store. The service worker uses the Cache API for asset caching.

## OPFS in Service Workers

The Origin Private File System (OPFS) provides fast file-based storage. However, service workers have a critical limitation:

- `createSyncAccessHandle()` is **not available** in service workers (dedicated workers only)
- Service workers can only use the **async** OPFS API

```ts
async function writeToOPFS(filename: string, data: string): Promise<void> {
  const root = await navigator.storage.getDirectory();
  const fileHandle = await root.getFileHandle(filename, { create: true });
  const writable = await fileHandle.createWritable();
  await writable.write(data);
  await writable.close();
}

async function readFromOPFS(filename: string): Promise<string> {
  const root = await navigator.storage.getDirectory();
  const fileHandle = await root.getFileHandle(filename);
  const file = await fileHandle.getFile();
  return file.text();
}
```

The async API is significantly slower than the sync access handle. For performance-critical storage in service workers, IndexedDB is generally a better choice.

### OPFS Use Cases in Service Workers

- Storing large binary assets (images, WASM modules) that do not fit well in Cache API
- Temporary file staging for Background Fetch downloads
- Log files for debugging service worker behavior

## Storage Quota Management

All storage APIs (Cache API, IndexedDB, OPFS) share a single origin quota:

```ts
async function checkStorageQuota(): Promise<{
  usage: number;
  quota: number;
  percentUsed: number;
}> {
  const estimate = await navigator.storage.estimate();
  const usage = estimate.usage ?? 0;
  const quota = estimate.quota ?? 0;
  return {
    usage,
    quota,
    percentUsed: quota > 0 ? (usage / quota) * 100 : 0,
  };
}
```

### Requesting Persistent Storage

By default, the browser can evict storage under pressure. Request persistent storage to protect critical data:

```ts
async function requestPersistentStorage(): Promise<boolean> {
  if (navigator.storage && navigator.storage.persist) {
    return navigator.storage.persist();
  }
  return false;
}
```

Chrome auto-grants persistent storage for installed PWAs and sites with high engagement. Firefox prompts the user. Safari grants it for home screen apps.

### Storage Eviction Strategy

When quota is running low, prioritize what to keep:

```ts
async function evictLowPriorityCaches(): Promise<void> {
  const { usage, quota } = await checkStorageQuota();

  if (quota > 0 && usage / quota > 0.8) {
    const lowPriorityCaches = ['api-responses', 'images', 'content-cache'];
    for (const cacheName of lowPriorityCaches) {
      await caches.delete(cacheName);
    }
  }
}
```

Never evict the precache or the sync engine's IndexedDB database. Prioritize evicting runtime caches for API responses and images.

## Navigation Preload

Navigation Preload starts a network request for navigation in parallel with service worker startup, reducing latency:

```ts
self.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(
    (async () => {
      if (self.registration.navigationPreload) {
        await self.registration.navigationPreload.enable();
      }
    })(),
  );
});

self.addEventListener('fetch', (event: FetchEvent) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        const cachedResponse = await caches.match('/app-shell.html');

        const preloadResponse = await event.preloadResponse;
        if (preloadResponse) {
          return preloadResponse;
        }

        return cachedResponse ?? fetch(event.request);
      })(),
    );
  }
});
```

### Browser Support

| Browser | Version | Notes        |
| ------- | ------- | ------------ |
| Chrome  | 59+     | Full support |
| Edge    | 18+     | Full support |
| Firefox | 99+     | Full support |
| Safari  | 15.4+   | Full support |

### Navigation Preload with App Shell

For local-first apps that always serve a cached app shell, Navigation Preload is less critical because the shell is served from cache instantly. However, it is valuable when the app shell is served network-first (e.g., for server-rendered content):

```ts
self.addEventListener('fetch', (event: FetchEvent) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          const preloadResponse = await event.preloadResponse;
          if (preloadResponse) {
            const cache = await caches.open('navigations');
            await cache.put(event.request, preloadResponse.clone());
            return preloadResponse;
          }
          return await fetch(event.request);
        } catch {
          return (await caches.match('/offline.html'))!;
        }
      })(),
    );
  }
});
```

## Background Fetch for Large Downloads

Background Fetch (Chrome 74+, experimental) handles large downloads that may outlive the service worker:

```ts
async function startBackgroundDownload(
  urls: string[],
  title: string,
): Promise<void> {
  const registration = await navigator.serviceWorker.ready;
  await registration.backgroundFetch.fetch('large-download', urls, {
    title,
    icons: [
      { src: '/icons/download.png', sizes: '192x192', type: 'image/png' },
    ],
    downloadTotal: 50 * 1024 * 1024,
  });
}
```

In the service worker:

```ts
self.addEventListener('backgroundfetchsuccess', (event: Event) => {
  const bgFetchEvent = event as BackgroundFetchEvent & {
    registration: BackgroundFetchRegistration;
    updateUI: (options: { title: string }) => Promise<void>;
  };
  bgFetchEvent.waitUntil(
    (async () => {
      const cache = await caches.open('downloads');
      const records = await bgFetchEvent.registration.matchAll();
      for (const record of records) {
        const response = await record.responseReady;
        await cache.put(record.request, response);
      }
      await bgFetchEvent.updateUI({ title: 'Download complete' });
    })(),
  );
});
```

Background Fetch is useful for large media files, datasets, or WASM modules that cannot be reliably downloaded in a single fetch handler execution.
