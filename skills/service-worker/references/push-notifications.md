---
title: Push Notifications
description: Push API with VAPID keys, pushManager.subscribe, service worker push event handler, notificationclick, and offline-first integration
tags:
  [
    push,
    notifications,
    VAPID,
    pushManager,
    subscribe,
    notificationclick,
    offline,
  ]
---

# Push Notifications

## Browser Support

The Push API has ~96% browser support, including Safari 16.4+ (with differences). Safari requires the app to be added to the home screen for push to work on iOS.

## Architecture

```text
App Server ──> Push Service (FCM/APNs/Mozilla) ──> Browser ──> Service Worker
                                                                     │
                                                          push event fires
                                                                     │
                                                          show notification
```

The push flow involves three parties: the application server, the browser's push service, and the service worker. VAPID keys authenticate the application server to the push service.

## VAPID Key Generation

Generate a VAPID key pair once and store securely:

```bash
npx web-push generate-vapid-keys
```

Or programmatically:

```ts
import webPush from 'web-push';

const vapidKeys = webPush.generateVAPIDKeys();
// Store vapidKeys.publicKey and vapidKeys.privateKey securely
```

## Subscription Flow

### Request Permission and Subscribe (Client)

```ts
async function subscribeToPush(): Promise<PushSubscription | null> {
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    return null;
  }

  const registration = await navigator.serviceWorker.ready;

  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  });

  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription),
  });

  return subscription;
}

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
```

`userVisibleOnly: true` is required -- browsers mandate that push messages result in a visible notification.

### Check Existing Subscription

```ts
async function getExistingSubscription(): Promise<PushSubscription | null> {
  const registration = await navigator.serviceWorker.ready;
  return registration.pushManager.getSubscription();
}
```

### Unsubscribe

```ts
async function unsubscribe(): Promise<void> {
  const subscription = await getExistingSubscription();
  if (subscription) {
    await subscription.unsubscribe();
    await fetch('/api/push/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: subscription.endpoint }),
    });
  }
}
```

## Sending Push Messages (Server)

```ts
import webPush from 'web-push';

webPush.setVapidDetails(
  'mailto:admin@example.com',
  process.env.VAPID_PUBLIC_KEY!,
  process.env.VAPID_PRIVATE_KEY!,
);

async function sendPush(
  subscription: webPush.PushSubscription,
  payload: { title: string; body: string; url?: string; tag?: string },
): Promise<void> {
  try {
    await webPush.sendNotification(subscription, JSON.stringify(payload), {
      TTL: 60 * 60,
      urgency: 'normal',
    });
  } catch (error: unknown) {
    if (error instanceof webPush.WebPushError && error.statusCode === 410) {
      await removeSubscription(subscription.endpoint);
    }
    throw error;
  }
}
```

`TTL` (Time To Live) in seconds determines how long the push service stores the message if the device is offline. A `410 Gone` response means the subscription expired and should be removed.

## Service Worker Push Event Handler

```ts
self.addEventListener('push', (event: PushEvent) => {
  const data = event.data?.json() ?? {
    title: 'Notification',
    body: 'New update available',
  };

  const options: NotificationOptions = {
    body: data.body,
    icon: '/icons/notification-192.png',
    badge: '/icons/badge-72.png',
    tag: data.tag ?? 'default',
    renotify: Boolean(data.tag),
    data: { url: data.url ?? '/' },
    actions: data.actions ?? [],
    vibrate: [200, 100, 200],
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});
```

### Notification Options

| Option               | Type                   | Description                                    |
| -------------------- | ---------------------- | ---------------------------------------------- |
| `body`               | `string`               | Notification body text                         |
| `icon`               | `string`               | Large icon URL                                 |
| `badge`              | `string`               | Small monochrome icon (Android)                |
| `image`              | `string`               | Large image displayed in notification          |
| `tag`                | `string`               | Groups notifications; same tag replaces        |
| `renotify`           | `boolean`              | Alert again when replacing tagged notification |
| `data`               | `any`                  | Custom data passed to notificationclick        |
| `actions`            | `NotificationAction[]` | Up to 2 action buttons                         |
| `silent`             | `boolean`              | Suppress sound/vibration                       |
| `vibrate`            | `number[]`             | Vibration pattern in ms                        |
| `requireInteraction` | `boolean`              | Keep notification visible until dismissed      |

## Handling Notification Clicks

```ts
self.addEventListener('notificationclick', (event: NotificationEvent) => {
  event.notification.close();

  const targetUrl = event.notification.data?.url ?? '/';
  const action = event.action;

  if (action === 'view') {
    event.waitUntil(openOrFocusWindow(targetUrl));
  } else if (action === 'dismiss') {
    return;
  } else {
    event.waitUntil(openOrFocusWindow(targetUrl));
  }
});

async function openOrFocusWindow(url: string): Promise<WindowClient | null> {
  const clients = await self.clients.matchAll({
    type: 'window',
    includeUncontrolled: true,
  });

  for (const client of clients) {
    if (new URL(client.url).pathname === url && 'focus' in client) {
      return client.focus();
    }
  }

  return self.clients.openWindow(url);
}
```

## Notification Actions

```ts
const options: NotificationOptions = {
  body: 'You have a new message from Alice',
  actions: [
    { action: 'view', title: 'View', icon: '/icons/view.png' },
    { action: 'dismiss', title: 'Dismiss', icon: '/icons/dismiss.png' },
  ],
  data: { url: '/messages/123' },
};
```

Action support is limited to two buttons on most platforms. Chrome on Android supports actions; desktop Chrome and Safari show the notification without action buttons.

## Offline-First Push Integration

When a push arrives while the device is offline or has stale data, pre-sync relevant data before showing the notification:

```ts
self.addEventListener('push', (event: PushEvent) => {
  const data = event.data?.json();

  event.waitUntil(
    (async () => {
      if (data.prefetch) {
        const cache = await caches.open('push-prefetch');
        await Promise.allSettled(
          data.prefetch.map((url: string) =>
            fetch(url)
              .then((response) => cache.put(url, response))
              .catch(() => {}),
          ),
        );
      }

      await self.registration.showNotification(data.title, {
        body: data.body,
        data: { url: data.url },
      });
    })(),
  );
});
```

This ensures that when the user taps the notification and opens the app, the relevant data is already cached.

## Permission Best Practices

- Never request permission on page load; ask after user interaction that indicates intent
- Explain what notifications will be used for before requesting permission
- Provide an in-app toggle to manage subscription independent of browser settings
- Handle the `denied` state gracefully; once denied, the permission prompt cannot be shown again (user must change it in browser settings)

```ts
function canRequestPermission(): boolean {
  return 'Notification' in window && Notification.permission === 'default';
}
```

## Safari-Specific Considerations

- Push requires the app to be added to the home screen on iOS (16.4+)
- Safari on macOS supports push in normal browsing (16.1+)
- Safari does not support notification actions (action buttons)
- Safari does not support the `image` notification option
- Badge icons are not supported on Safari
