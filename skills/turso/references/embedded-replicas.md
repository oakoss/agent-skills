---
title: Embedded Replicas
description: Local-first embedded replicas with sync, offline mode, sync intervals, and read-your-writes consistency
tags: [embedded-replica, syncUrl, syncInterval, sync, offline, local-first]
---

# Embedded Replicas

Embedded replicas maintain a local SQLite copy of a remote Turso database. Reads happen locally with zero network latency. Writes go to the remote primary and sync back to the local replica.

## Basic Setup

```ts
import { createClient } from '@libsql/client';

const client = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});
```

Both `syncUrl` and `authToken` are required for embedded replicas.

## Manual Sync

Pull the latest changes from the remote database on demand:

```ts
await client.sync();

const result = await client.execute('SELECT * FROM users');
```

## Periodic Sync

Configure automatic background synchronization:

```ts
const client = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  syncInterval: 60,
});
```

The `syncInterval` value is in seconds. The client syncs in the background at this interval.

## Offline Mode

Enable offline mode to use the local replica without attempting remote connections:

```ts
const client = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  offline: true,
});
```

When `offline: true`, the client reads from and writes to the local database only. Call `client.sync()` explicitly when connectivity is restored.

## Read-Your-Writes Consistency

```ts
const client = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  readYourWrites: true,
});
```

With `readYourWrites: true`, the client automatically syncs after each write operation so subsequent reads reflect the latest state.

## Encrypted Embedded Replica

```ts
const client = createClient({
  url: 'file:replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  encryptionKey: process.env.DB_ENCRYPTION_KEY!,
});
```

## Server-Side Usage Pattern

Embedded replicas work well in long-running server processes (Node.js, Bun) where the local file persists between requests:

```ts
import { createClient } from '@libsql/client';

const db = createClient({
  url: 'file:/data/replica.db',
  syncUrl: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
  syncInterval: 30,
});

export async function getUsers() {
  const result = await db.execute('SELECT * FROM users');
  return result.rows;
}
```

## When to Use Embedded Replicas

| Scenario                     | Recommendation                 |
| ---------------------------- | ------------------------------ |
| Serverless functions         | Remote client (no local file)  |
| Long-running servers         | Embedded replica               |
| Edge workers with storage    | Embedded replica               |
| Edge workers without storage | Remote client                  |
| Local development            | Local file or embedded replica |
| Mobile/desktop apps          | Embedded replica               |
| CI/CD and testing            | In-memory or local file        |

## Sync Behavior

- **Initial sync**: Downloads the full database on first connection
- **Subsequent syncs**: Transfers only changed pages (incremental)
- **Write path**: Writes go to the remote primary; the local replica syncs afterward
- **Conflict handling**: The remote primary is authoritative; local writes that conflict are resolved server-side
