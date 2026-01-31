---
title: Storage
description: KV key-value store, D1 SQLite database, R2 object storage, and Durable Objects storage APIs
tags:
  [
    kv,
    d1,
    r2,
    durable-objects,
    storage,
    database,
    sqlite,
    object-storage,
    bindings,
  ]
---

# Storage

## KV (Key-Value Store)

Eventually consistent, global key-value storage optimized for high-read, low-write workloads. Max value size is 25 MiB. Max key size is 512 bytes.

### Basic Operations

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    await env.MY_KV.put('user:123', JSON.stringify({ name: 'Alice' }));

    const value = await env.MY_KV.get('user:123');

    const json = await env.MY_KV.get<{ name: string }>('user:123', {
      type: 'json',
    });

    await env.MY_KV.delete('user:123');

    return Response.json({ value, json });
  },
};
```

### KV with Metadata and Expiration

```ts
await env.MY_KV.put('session:abc', JSON.stringify(sessionData), {
  expirationTtl: 3600,
  metadata: { userId: '123', role: 'admin' },
});

const { value, metadata } = await env.MY_KV.getWithMetadata<
  string,
  { userId: string; role: string }
>('session:abc');
```

### Listing Keys

```ts
async function listAllKeys(
  kv: KVNamespace,
  prefix?: string,
): Promise<string[]> {
  const keys: string[] = [];
  let cursor: string | undefined;

  do {
    const result = await kv.list({ prefix, cursor });
    keys.push(...result.keys.map((k) => k.name));
    cursor = result.list_complete ? undefined : result.cursor;
  } while (cursor);

  return keys;
}
```

### Wrangler Configuration

```toml
[[kv_namespaces]]
binding = "MY_KV"
id = "abc123def456"
preview_id = "preview_abc123"
```

## D1 (SQLite Database)

Server-side SQLite database with prepared statements. Strongly consistent within a region. Use `.prepare().bind()` for all queries to prevent SQL injection.

### Basic Queries

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const allUsers = await env.DB.prepare('SELECT * FROM users').all();

    const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?')
      .bind(1)
      .first();

    await env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)')
      .bind('Alice', 'alice@example.com')
      .run();

    return Response.json({ users: allUsers.results, user });
  },
};
```

### Batch Queries (Atomic Transactions)

All statements execute in a single transaction. If any statement fails, the entire batch is rolled back.

```ts
const results = await env.DB.batch([
  env.DB.prepare('INSERT INTO orders (user_id, total) VALUES (?, ?)').bind(
    1,
    99.99,
  ),
  env.DB.prepare(
    'UPDATE users SET order_count = order_count + 1 WHERE id = ?',
  ).bind(1),
  env.DB.prepare('INSERT INTO audit_log (action, user_id) VALUES (?, ?)').bind(
    'order_created',
    1,
  ),
]);
```

### Query Result Shape

```ts
const result = await env.DB.prepare('SELECT * FROM users').all();
```

The `result` object contains:

```ts
interface D1Result<T> {
  results: T[];
  success: boolean;
  meta: {
    duration: number;
    rows_read: number;
    rows_written: number;
    last_row_id: number;
    changed_db: boolean;
    changes: number;
    size_after: number;
  };
}
```

### Schema Migrations

Create and apply migrations with the Wrangler CLI:

```bash
wrangler d1 migrations create my-db create-users-table
wrangler d1 migrations apply my-db
wrangler d1 migrations apply my-db --remote
```

### Wrangler Configuration

```toml
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "abc123-def456-ghi789"
```

## R2 (Object Storage)

S3-compatible object storage with zero egress fees. Max object size is 5 TiB (multipart). Single PUT max is 5 GiB.

### Basic Operations

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    await env.BUCKET.put('images/photo.png', request.body, {
      httpMetadata: { contentType: 'image/png' },
      customMetadata: { uploadedBy: 'user-123' },
    });

    const object = await env.BUCKET.get('images/photo.png');
    if (!object) {
      return new Response('Not Found', { status: 404 });
    }

    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set('ETag', object.httpEtag);

    return new Response(object.body, { headers });
  },
};
```

### Listing Objects

```ts
const listed = await env.BUCKET.list({
  prefix: 'images/',
  limit: 100,
  cursor: undefined,
});

for (const object of listed.objects) {
  console.log(`${object.key} - ${object.size} bytes`);
}

if (listed.truncated) {
  const nextPage = await env.BUCKET.list({
    prefix: 'images/',
    cursor: listed.cursor,
  });
}
```

### Deleting Objects

```ts
await env.BUCKET.delete('images/photo.png');

await env.BUCKET.delete(['images/a.png', 'images/b.png', 'images/c.png']);
```

### Conditional Operations

```ts
const object = await env.BUCKET.get('data.json', {
  onlyIf: {
    etagMatches: request.headers.get('If-None-Match') ?? undefined,
  },
});

if (object && !('body' in object)) {
  return new Response(null, { status: 304 });
}
```

### Multipart Upload

```ts
const multipart = await env.BUCKET.createMultipartUpload('large-file.zip', {
  httpMetadata: { contentType: 'application/zip' },
});

const part1 = await multipart.uploadPart(1, chunk1);
const part2 = await multipart.uploadPart(2, chunk2);

const finalObject = await multipart.complete([part1, part2]);
```

### Wrangler Configuration

```toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"
preview_bucket_name = "my-bucket-preview"
```

## Durable Objects

Single-instance stateful objects for coordination, counters, WebSockets, and rate limiting. Each instance runs in one location and provides strong consistency.

### SQLite Storage (Recommended)

```ts
import { DurableObject } from 'cloudflare:workers';

export class ChatRoom extends DurableObject<Env> {
  sql = this.ctx.storage.sql;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      )
    `);
  }

  async addMessage(author: string, content: string): Promise<void> {
    this.sql.exec(
      'INSERT INTO messages (author, content) VALUES (?, ?)',
      author,
      content,
    );
  }

  async getMessages(limit = 50): Promise<unknown[]> {
    return this.sql
      .exec('SELECT * FROM messages ORDER BY id DESC LIMIT ?', limit)
      .toArray();
  }
}
```

### KV Storage (Legacy)

```ts
import { DurableObject } from 'cloudflare:workers';

export class Counter extends DurableObject<Env> {
  async increment(): Promise<number> {
    const value = (await this.ctx.storage.get<number>('count')) ?? 0;
    const newValue = value + 1;
    await this.ctx.storage.put('count', newValue);
    return newValue;
  }

  async getCount(): Promise<number> {
    return (await this.ctx.storage.get<number>('count')) ?? 0;
  }
}
```

### WebSocket Hibernation

```ts
import { DurableObject } from 'cloudflare:workers';

export class WebSocketRoom extends DurableObject<Env> {
  async fetch(request: Request): Promise<Response> {
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);

    this.ctx.acceptWebSocket(server);

    return new Response(null, { status: 101, webSocket: client });
  }

  webSocketMessage(ws: WebSocket, message: string | ArrayBuffer): void {
    this.ctx.getWebSockets().forEach((socket) => {
      if (socket !== ws) {
        socket.send(
          typeof message === 'string' ? message : new Uint8Array(message),
        );
      }
    });
  }

  webSocketClose(ws: WebSocket): void {
    ws.close();
  }
}
```

### Wrangler Configuration

```toml
[durable_objects]
bindings = [
  { name = "CHAT_ROOM", class_name = "ChatRoom" },
  { name = "COUNTER", class_name = "Counter" },
]

[[migrations]]
tag = "v1"
new_sqlite_classes = ["ChatRoom"]
new_classes = ["Counter"]
```

### Alarms

Schedule a single timer per Durable Object instance:

```ts
import { DurableObject } from 'cloudflare:workers';

export class Scheduler extends DurableObject<Env> {
  async scheduleTask(delayMs: number): Promise<void> {
    await this.ctx.storage.setAlarm(Date.now() + delayMs);
  }

  async alarm(): Promise<void> {
    await this.performScheduledWork();
  }
}
```
