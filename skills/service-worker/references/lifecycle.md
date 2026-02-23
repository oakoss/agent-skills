---
title: Lifecycle
description: Service worker install, waiting, activate events, skipWaiting, clients.claim, update prompting with workbox-window, and registration patterns
tags:
  [
    install,
    activate,
    waiting,
    skipWaiting,
    clients.claim,
    workbox-window,
    register,
    update,
  ]
---

# Service Worker Lifecycle

## Lifecycle Phases

```text
Installing ──> Waiting ──> Activating ──> Activated (Functional)
    │              │            │
    │              │            └── Controls pages, receives fetch/push/sync events
    │              └── Old SW still controls pages; new SW waits
    └── Caching app shell; failure here aborts installation
```

A service worker progresses through install, wait, and activate before it can handle functional events (fetch, push, sync, message).

## Registration

Register in the window context after the page loads to avoid competing for network bandwidth during initial render:

```ts
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    });
    console.log('SW registered with scope:', registration.scope);
  });
}
```

Scope defaults to the directory containing the SW script. A SW at `/app/sw.js` controls `/app/*` by default. The `Service-Worker-Allowed` header can widen scope beyond the script directory.

## Install Event

The install event fires once per SW version. Use it to precache critical resources:

```ts
self.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(
    caches
      .open('app-shell-v1')
      .then((cache) =>
        cache.addAll(['/', '/index.html', '/styles.css', '/app.js']),
      ),
  );
});
```

If any resource in `cache.addAll` fails to fetch, the entire install aborts. Use `cache.add` individually for non-critical resources where partial success is acceptable.

## Waiting Phase

When a new SW installs while an existing SW controls pages, the new SW enters the waiting state. It remains waiting until all tabs controlled by the old SW are closed.

This prevents breaking in-flight pages that depend on the old SW's cached resources.

## skipWaiting and clients.claim

`skipWaiting` forces the waiting SW to become active immediately. `clients.claim` makes the newly active SW take control of existing pages without requiring a reload:

```ts
self.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(self.clients.claim());
});
```

**Use with caution.** Calling `skipWaiting` unconditionally means the new SW takes over pages that loaded with resources cached by the old SW. This can cause broken asset references if the new SW has a different precache manifest. The recommended approach is to prompt the user before activating.

## Activate Event

The activate event fires when the SW takes control. Use it to clean up old caches:

```ts
const CURRENT_CACHES = ['app-shell-v2', 'api-cache-v1'];

self.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((name) => !CURRENT_CACHES.includes(name))
            .map((name) => caches.delete(name)),
        ),
      ),
  );
});
```

## Update Detection with workbox-window

The `Workbox` class from `workbox-window` provides a clean API for detecting updates and prompting users in the page context:

```ts
import { Workbox } from 'workbox-window';

if ('serviceWorker' in navigator) {
  const wb = new Workbox('/sw.js');

  wb.addEventListener('waiting', () => {
    const shouldUpdate = confirm('New version available. Reload to update?');
    if (shouldUpdate) {
      wb.messageSkipWaiting();
      window.location.reload();
    }
  });

  wb.register();
}
```

Inside the service worker, listen for the skip waiting message:

```ts
self.addEventListener('message', (event: ExtendableMessageEvent) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
```

## Update Lifecycle Events

`workbox-window` exposes granular lifecycle events:

| Event               | When                                         | Use Case                             |
| ------------------- | -------------------------------------------- | ------------------------------------ |
| `installed`         | New SW installed (first time)                | Show "app ready for offline" message |
| `waiting`           | New SW installed, waiting for old to release | Show update prompt                   |
| `controlling`       | New SW took control of page                  | Safe to reload or update UI          |
| `activated`         | New SW activated                             | Clean up, log version                |
| `externalinstalled` | SW installed by another tab                  | Coordinate multi-tab updates         |
| `externalwaiting`   | SW from another tab is waiting               | Show update notification             |

## Checking for Updates Programmatically

```ts
const registration = await navigator.serviceWorker.ready;
await registration.update();
```

The browser also checks for updates automatically on navigation (if 24+ hours since last check) and on functional events like push/sync.

## Registration Patterns for Frameworks

### Vite with vite-plugin-pwa

```ts
import { registerSW } from 'virtual:pwa-register';

const updateSW = registerSW({
  onNeedRefresh() {
    const shouldUpdate = confirm('New content available. Reload?');
    if (shouldUpdate) {
      updateSW();
    }
  },
  onOfflineReady() {
    console.log('App ready for offline use');
  },
});
```

### Next.js with next-pwa (or Serwist)

Service worker registration is handled automatically by the plugin. Configure in `next.config.js`:

```ts
import withPWA from 'next-pwa';

export default withPWA({
  dest: 'public',
  register: true,
  skipWaiting: false,
})(nextConfig);
```

## Debugging Lifecycle Issues

Common debugging steps:

1. **Chrome DevTools** > Application > Service Workers shows lifecycle state
2. **"Update on reload"** checkbox forces install + activate on every navigation (dev only)
3. **"Bypass for network"** disables fetch handling without unregistering
4. `chrome://serviceworker-internals` shows all registered SWs across origins

## Unregistration

To remove a service worker entirely:

```ts
const registrations = await navigator.serviceWorker.getRegistrations();
await Promise.all(registrations.map((r) => r.unregister()));
```

Unregistration does not clear caches. Delete caches separately:

```ts
const cacheNames = await caches.keys();
await Promise.all(cacheNames.map((name) => caches.delete(name)));
```
