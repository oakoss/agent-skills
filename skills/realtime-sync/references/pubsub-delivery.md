---
title: Pub/Sub Messaging and Guaranteed Delivery
description: Sequence tracking, transactional outbox pattern, rewind recovery, presence management, and channel multiplexing
tags: [pubsub, sequence-ids, outbox, cdc, presence, ably, guaranteed-delivery]
---

# Pub/Sub Messaging and Guaranteed Delivery

Pub/sub infrastructure provides the orchestration layer between transport and application state. Guaranteed delivery requires sequence tracking, transactional consistency, and reconnection recovery.

## Sequence Tracking

Every message published to a channel carries a sequence ID. This enables detection of gaps (missed messages) and ordering guarantees.

### Rewind on Reconnect

When a client reconnects after a network interruption, use the rewind parameter to fetch missed messages:

```ts
const channel = ably.channels.get('orders', {
  params: { rewind: '1m' },
});

channel.subscribe('update', (msg) => {
  applyUpdate(msg.data);
});
```

The `rewind: '1m'` parameter requests the last minute of message history, filling any gaps from the disconnection period.

### Sequence Validation

On the client, track the last received sequence and detect gaps:

```ts
let lastSequence = 0;

function onMessage(msg: { sequence: number; data: unknown }) {
  if (msg.sequence > lastSequence + 1) {
    requestRewind(lastSequence + 1, msg.sequence - 1);
  }
  lastSequence = msg.sequence;
  applyUpdate(msg.data);
}
```

## Transactional Outbox Pattern

Ensures database state and real-time notifications never drift. The outbox guarantees that a message is only published if the database transaction succeeds.

### Database Schema

```sql
CREATE TABLE realtime_outbox (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  channel text NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  sequence_id uuid DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now(),
  published_at timestamptz
);
```

### Transaction Pattern

Write the business data and outbox entry in a single transaction:

```sql
BEGIN;
  UPDATE orders SET status = 'shipped' WHERE id = 456;

  INSERT INTO realtime_outbox (channel, event_type, payload)
  VALUES (
    'order_updates',
    'status_changed',
    '{"order_id": 456, "status": "shipped"}'::jsonb
  );
COMMIT;
```

### CDC Worker

A background process (Change Data Capture) reads unpublished outbox entries and pushes them to the real-time channel:

```ts
async function processOutbox() {
  const pending = await db.query(
    'SELECT * FROM realtime_outbox WHERE published_at IS NULL ORDER BY id LIMIT 100',
  );

  for (const entry of pending.rows) {
    await channel.publish(entry.event_type, entry.payload);
    await db.query(
      'UPDATE realtime_outbox SET published_at = now() WHERE id = $1',
      [entry.id],
    );
  }
}
```

Poll this function on a short interval (100-500ms) or trigger it via a database notification (LISTEN/NOTIFY).

## Presence Management

Track which users are currently active in a channel:

```ts
const channel = ably.channels.get('document-123');

await channel.presence.enter({ cursor: { x: 0, y: 0 } });

channel.presence.subscribe('enter', (member) => {
  addUserCursor(member.clientId, member.data.cursor);
});

channel.presence.subscribe('leave', (member) => {
  removeUserCursor(member.clientId);
});
```

### Zombie Prevention

Presence relies on heartbeats. When a client crashes without sending a "leave" message, it becomes a zombie presence entry.

**Epidemic broadcast protocol:** Peers periodically exchange presence state. If a peer reports a user absent that another peer still shows as present, the conflict resolves by removing the stale entry.

**Heartbeat tuning:** Mobile devices need longer heartbeat intervals to conserve battery. Desktop clients can use shorter intervals for faster detection:

| Platform       | Heartbeat Interval |
| -------------- | ------------------ |
| Desktop        | 15 seconds         |
| Mobile         | 30-60 seconds      |
| Background tab | 60-120 seconds     |

## Channel Multiplexing

Ably SDKs multiplex all channel traffic over a single transport connection. Subscribe to multiple channels without extra connections:

```ts
const orders = ably.channels.get('orders');
const notifications = ably.channels.get('notifications');
const presence = ably.channels.get('presence');

orders.subscribe('update', (msg) => handleOrder(msg.data));
notifications.subscribe('alert', (msg) => handleNotification(msg.data));
presence.subscribe('enter', (msg) => handlePresenceEvent(msg.data));
```

All subscriptions share one WebSocket connection, reducing overhead on mobile devices.

## Quality Checklist

| Check                                              | Target                 |
| -------------------------------------------------- | ---------------------- |
| Auto-reconnect enabled                             | Yes                    |
| Rewind on reconnect                                | Last 1-5 minutes       |
| Presence heartbeat tuned per platform              | See table above        |
| Rejected/Suspended states handled with UI feedback | Banner or toast        |
| Outbox worker polling interval                     | 100-500ms              |
| Sequence validation on client                      | Gap detection + rewind |
