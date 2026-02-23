---
title: Static Routing
description: Service Worker Static Routing API, event.addRoutes() in install event, conditions, sources, and ServiceWorkerAutoPreload
tags:
  [
    static-routing,
    addRoutes,
    urlPattern,
    fetch-event,
    race,
    network,
    ServiceWorkerAutoPreload,
  ]
---

# Static Routing

## Overview

The Service Worker Static Routing API (Chrome 123+) lets service workers declare routing rules at install time. The browser evaluates these rules before starting the service worker, bypassing the fetch event handler entirely for matched routes. This eliminates service worker startup latency for known routing decisions.

## Browser Support

- **Chrome 123+**: Full support
- **Edge 123+**: Full support (Chromium-based)
- **Firefox**: Not supported
- **Safari**: Not supported

Feature-detect before using:

```ts
self.addEventListener('install', (event: ExtendableEvent) => {
  if ('addRoutes' in event) {
    (event as ExtendableEvent & { addRoutes: Function }).addRoutes([
      /* rules */
    ]);
  }
});
```

## Basic Usage

Declare routes in the install event using `event.addRoutes()`:

```ts
self.addEventListener('install', (event: ExtendableEvent) => {
  const installEvent = event as ExtendableEvent & {
    addRoutes: (routes: StaticRoute[]) => void;
  };

  if ('addRoutes' in installEvent) {
    installEvent.addRoutes([
      {
        condition: {
          urlPattern: new URLPattern({ pathname: '/api/*' }),
        },
        source: 'network',
      },
      {
        condition: {
          urlPattern: new URLPattern({ pathname: '/static/*' }),
        },
        source: 'cache',
      },
    ]);
  }
});
```

## Conditions

Conditions determine which requests match a rule:

### urlPattern

Uses the URLPattern API to match request URLs:

```ts
{
  condition: {
    urlPattern: new URLPattern({ pathname: '/images/*' }),
  },
  source: 'network',
}
```

URLPattern supports wildcards, named groups, and regex:

```ts
new URLPattern({ pathname: '/users/:id' });
new URLPattern({ pathname: '/docs/:category/:slug' });
new URLPattern({ pathname: '/*.{png,jpg,webp}' });
```

String shorthand is also accepted:

```ts
{
  condition: { urlPattern: '/api/*' },
  source: 'network',
}
```

### requestMethod

Filter by HTTP method:

```ts
{
  condition: {
    urlPattern: new URLPattern({ pathname: '/api/*' }),
    requestMethod: 'GET',
  },
  source: 'network',
}
```

### runningStatus

Match based on whether the service worker is already running:

```ts
{
  condition: {
    urlPattern: new URLPattern({ pathname: '/*' }),
    runningStatus: 'not-running',
  },
  source: 'network',
}
```

| Value         | Meaning                                  |
| ------------- | ---------------------------------------- |
| `running`     | SW is already started                    |
| `not-running` | SW would need to start to handle request |

This is useful for bypassing the fetch handler only when the SW is cold, avoiding startup cost.

## Sources

Sources determine how matched requests are handled:

### network

Bypass the service worker entirely and go straight to the network:

```ts
{
  condition: { urlPattern: '/api/*' },
  source: 'network',
}
```

Best for: API calls that should never be intercepted, analytics endpoints, real-time data.

### cache

Serve directly from a named cache without waking the service worker:

```ts
{
  condition: {
    urlPattern: new URLPattern({ pathname: '/shell/*' }),
  },
  source: {
    type: 'cache',
    cacheName: 'app-shell-v1',
  },
}
```

Best for: Precached app shell resources, static assets with known cache names.

### fetch-event

Fall through to the service worker's fetch event handler (default behavior):

```ts
{
  condition: { urlPattern: '/dynamic/*' },
  source: 'fetch-event',
}
```

Explicitly opting into fetch handler processing. This is the default when no static route matches, so this source is primarily useful for clarity or overriding other rules.

### race-network-and-fetch-handler

Race the network request against the service worker's fetch handler. Whichever responds first wins:

```ts
{
  condition: {
    urlPattern: new URLPattern({ pathname: '/' }),
    runningStatus: 'not-running',
  },
  source: 'race-network-and-fetch-handler',
}
```

Best for: Navigation requests when the SW is cold. The network request starts immediately while the SW boots up. If the network is fast, the response arrives before the SW is ready. If the SW is faster (e.g., cache hit), it wins the race.

## Practical Configuration

A complete static routing setup for a typical PWA:

```ts
self.addEventListener('install', (event: ExtendableEvent) => {
  const installEvent = event as ExtendableEvent & {
    addRoutes: (routes: StaticRoute[]) => void;
  };

  if (!('addRoutes' in installEvent)) {
    return;
  }

  installEvent.addRoutes([
    {
      condition: {
        urlPattern: new URLPattern({ pathname: '/api/*' }),
        requestMethod: 'GET',
        runningStatus: 'not-running',
      },
      source: 'network',
    },
    {
      condition: {
        urlPattern: new URLPattern({ pathname: '/' }),
        runningStatus: 'not-running',
      },
      source: 'race-network-and-fetch-handler',
    },
    {
      condition: {
        urlPattern: new URLPattern({ pathname: '/analytics/*' }),
      },
      source: 'network',
    },
    {
      condition: {
        urlPattern: new URLPattern({ pathname: '/static/*' }),
      },
      source: {
        type: 'cache',
        cacheName: 'static-assets',
      },
    },
  ]);
});
```

## Rule Evaluation Order

Rules are evaluated in declaration order. The first matching rule wins. Place more specific rules before general ones:

```ts
installEvent.addRoutes([
  // Specific: analytics always bypasses SW
  { condition: { urlPattern: '/api/analytics/*' }, source: 'network' },

  // General: other API calls go through fetch handler
  { condition: { urlPattern: '/api/*' }, source: 'fetch-event' },
]);
```

## ServiceWorkerAutoPreload

ServiceWorkerAutoPreload is a Chrome feature that automatically starts a preload request in parallel with service worker startup for navigation requests. It requires no code changes -- the browser handles it automatically.

When enabled, the fetch event handler receives the preloaded response via `event.preloadResponse`:

```ts
self.addEventListener('fetch', (event: FetchEvent) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        const preloadResponse = await event.preloadResponse;
        if (preloadResponse) {
          return preloadResponse;
        }
        const cachedResponse = await caches.match(event.request);
        return cachedResponse || fetch(event.request);
      })(),
    );
  }
});
```

ServiceWorkerAutoPreload differs from manual Navigation Preload (`navigationPreload.enable()`) in that it requires zero configuration. However, manually enabling Navigation Preload remains necessary for broader browser support (Firefox 99+, Safari 15.4+).

## Static Routing vs Navigation Preload

| Feature           | Static Routing              | Navigation Preload                    |
| ----------------- | --------------------------- | ------------------------------------- |
| Browser support   | Chrome 123+                 | Chrome 59+, Firefox 99+, Safari 15.4+ |
| Configuration     | Install event rules         | Activate event enable                 |
| SW startup        | Can bypass entirely         | Runs in parallel                      |
| Response handling | No fetch event for bypassed | Fetch event receives preload          |
| Flexibility       | URL patterns, methods       | Navigation requests only              |

Use static routing for known routes that never need fetch handler logic. Use Navigation Preload for navigations that need SW processing but benefit from parallel network requests.
