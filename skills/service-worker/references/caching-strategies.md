---
title: Caching Strategies
description: Workbox v7.4 caching strategies, custom strategy creation, plugin lifecycle hooks, and workbox-precaching for app shell
tags:
  [
    CacheFirst,
    NetworkFirst,
    StaleWhileRevalidate,
    NetworkOnly,
    CacheOnly,
    precaching,
    workbox,
    plugin,
  ]
---

# Caching Strategies

## Workbox v7.4 Strategy Overview

Workbox strategies encapsulate cache-vs-network logic into reusable classes. Each strategy is registered against URL patterns via `registerRoute`:

```ts
import { registerRoute } from 'workbox-routing';
import { CacheFirst } from 'workbox-strategies';

registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images' }),
);
```

## Built-in Strategies

### CacheFirst

Serves from cache if available, falls back to network. Best for versioned static assets that do not change at a given URL:

```ts
import { CacheFirst } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';

registerRoute(
  ({ request }) =>
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font',
  new CacheFirst({
    cacheName: 'static-assets',
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 30 * 24 * 60 * 60,
      }),
    ],
  }),
);
```

### NetworkFirst

Tries network, falls back to cache on failure. Best for dynamic content that should be fresh but available offline:

```ts
import { NetworkFirst } from 'workbox-strategies';

registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-responses',
    networkTimeoutSeconds: 3,
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 5 * 60,
      }),
    ],
  }),
);
```

`networkTimeoutSeconds` sets how long to wait before falling back to cache. Omit for unlimited wait.

### StaleWhileRevalidate

Serves from cache immediately while fetching an update in the background. Best for resources where slight staleness is acceptable:

```ts
import { StaleWhileRevalidate } from 'workbox-strategies';

registerRoute(
  ({ url }) => url.pathname.startsWith('/content/'),
  new StaleWhileRevalidate({
    cacheName: 'content-cache',
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({ maxEntries: 50 }),
    ],
  }),
);
```

### NetworkOnly

Always goes to network. Use for non-cacheable requests like analytics pings or POST requests:

```ts
import { NetworkOnly } from 'workbox-strategies';

registerRoute(
  ({ url }) => url.pathname.startsWith('/analytics/'),
  new NetworkOnly(),
);
```

### CacheOnly

Only serves from cache, never hits network. Use for precached resources where a network fallback is unnecessary:

```ts
import { CacheOnly } from 'workbox-strategies';

registerRoute(
  ({ url }) => url.pathname === '/offline.html',
  new CacheOnly({ cacheName: 'precache' }),
);
```

## Strategy Selection Guide

| Content Type          | Strategy              | Reason                              |
| --------------------- | --------------------- | ----------------------------------- |
| App shell HTML        | Precache + CacheFirst | Versioned at build time             |
| Hashed JS/CSS bundles | CacheFirst            | URL changes on content change       |
| Google Fonts          | StaleWhileRevalidate  | Rarely change, staleness acceptable |
| API responses         | NetworkFirst          | Freshness matters, offline fallback |
| User avatars          | StaleWhileRevalidate  | Show fast, update in background     |
| Analytics             | NetworkOnly           | No value in caching                 |
| Offline fallback page | CacheOnly (precached) | Must be available without network   |

## Precaching with workbox-precaching

Precaching downloads and caches resources at install time. Workbox uses a manifest with revision hashes to manage updates:

```ts
import { precacheAndRoute } from 'workbox-precaching';

precacheAndRoute(self.__WB_MANIFEST);
```

`self.__WB_MANIFEST` is replaced at build time by workbox-build, workbox-webpack-plugin, or vite-plugin-pwa. The generated manifest looks like:

```json
[
  { "url": "/index.html", "revision": "abc123" },
  { "url": "/app.js", "revision": null },
  { "url": "/styles.css", "revision": null }
]
```

Files with content hashes in their filenames (e.g., `app.a1b2c3.js`) set `revision: null` because the URL itself changes on content change.

### Precache and Routing

`precacheAndRoute` automatically sets up a CacheFirst route for precached URLs. It handles revision parameter stripping and index.html redirects:

```ts
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';

cleanupOutdatedCaches();
precacheAndRoute(self.__WB_MANIFEST);
```

`cleanupOutdatedCaches` removes caches from previous Workbox versions.

## Plugin Lifecycle Hooks

Workbox plugins are objects implementing lifecycle callbacks. They run at specific points during request/response handling:

| Hook                       | When                              | Use Case                          |
| -------------------------- | --------------------------------- | --------------------------------- |
| `cacheWillUpdate`          | Before response enters cache      | Filter non-200 responses          |
| `cacheDidUpdate`           | After cache is updated            | Notify page of new content        |
| `cacheKeyWillBeUsed`       | Before cache key lookup           | Normalize URLs, strip params      |
| `cachedResponseWillBeUsed` | Before cached response is used    | Validate freshness, check headers |
| `requestWillFetch`         | Before network request            | Add auth headers                  |
| `fetchDidFail`             | After network request fails       | Log failures, queue for retry     |
| `fetchDidSucceed`          | After successful network response | Log response times                |
| `handlerWillStart`         | Before strategy starts            | Start timing                      |
| `handlerWillRespond`       | Before response is returned       | Modify response                   |
| `handlerDidRespond`        | After response is returned        | Log cache hit/miss                |
| `handlerDidComplete`       | After all work is done            | End timing, report metrics        |
| `handlerDidError`          | After all sources fail            | Return offline fallback           |

### Custom Plugin Example

```ts
const cacheNotificationPlugin = {
  cacheDidUpdate: async ({ cacheName, request, oldResponse, newResponse }) => {
    if (oldResponse) {
      const clients = await self.clients.matchAll();
      for (const client of clients) {
        client.postMessage({
          type: 'CACHE_UPDATED',
          url: request.url,
          cacheName,
        });
      }
    }
  },
};
```

## Custom Strategy

Extend the `Strategy` base class for custom logic:

```ts
import { Strategy, type StrategyHandler } from 'workbox-strategies';

class CacheFirstWithRefresh extends Strategy {
  async _handle(request: Request, handler: StrategyHandler): Promise<Response> {
    const cachedResponse = await handler.cacheMatch(request);

    const fetchPromise = handler.fetchAndCachePut(request).catch(() => {});

    return cachedResponse || (await handler.fetch(request));
  }
}
```

## Offline Fallback Pattern

Use the `handlerDidError` hook to serve a fallback page when both cache and network fail:

```ts
import { offlineFallback } from 'workbox-recipes';

offlineFallback({
  pageFallback: '/offline.html',
  imageFallback: '/fallback-image.svg',
  fontFallback: '/fallback-font.woff2',
});
```

Or manually with `setCatchHandler`:

```ts
import { setCatchHandler } from 'workbox-routing';

setCatchHandler(async ({ event }) => {
  if (event.request.destination === 'document') {
    return caches.match('/offline.html');
  }
  return Response.error();
});
```

## Cache Storage Considerations

- **Opaque responses** (cross-origin, no CORS) pad cache storage quota significantly (at least 7 MB each in Chrome)
- **Always set `maxEntries`** on expiration plugins to prevent unbounded cache growth
- **Use `CacheableResponsePlugin`** with `statuses: [0, 200]` to cache opaque responses intentionally
- **Storage quota** varies by browser: Chrome grants per-origin quota based on available disk space; check with `navigator.storage.estimate()`
