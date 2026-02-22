---
title: Common Patterns
description: Rate limiting, distributed locks, queues, session storage, pub/sub, streams, leaderboards, and counters with Valkey
tags:
  [
    rate-limiting,
    distributed-lock,
    queue,
    session,
    pub-sub,
    streams,
    leaderboard,
    counter,
    redlock,
  ]
---

## Rate Limiting

### Fixed Window

Simple counter per time window. Allows burst at window boundaries.

```ts
async function isRateLimited(
  userId: string,
  limit: number,
  windowSec: number,
): Promise<boolean> {
  const key = `rate:${userId}:${Math.floor(Date.now() / 1000 / windowSec)}`;
  const count = await valkey.incr(key);
  if (count === 1) await valkey.expire(key, windowSec);
  return count > limit;
}
```

### Sliding Window (Sorted Set)

More precise — no boundary burst. Uses sorted set with timestamps.

```ts
async function isRateLimited(
  userId: string,
  limit: number,
  windowMs: number,
): Promise<boolean> {
  const key = `rate:${userId}`;
  const now = Date.now();
  const windowStart = now - windowMs;

  const pipeline = valkey.pipeline();
  pipeline.zremrangebyscore(key, 0, windowStart);
  pipeline.zadd(key, now, `${now}:${Math.random()}`);
  pipeline.zcard(key);
  pipeline.expire(key, Math.ceil(windowMs / 1000));
  const results = await pipeline.exec();

  const count = results[2][1] as number;
  return count > limit;
}
```

## Distributed Locks

### Single-Instance Lock

```ts
async function acquireLock(
  resource: string,
  ttlMs: number,
): Promise<string | null> {
  const token = crypto.randomUUID();
  const result = await valkey.set(`lock:${resource}`, token, 'NX', 'PX', ttlMs);
  return result === 'OK' ? token : null;
}
```

### Safe Unlock (Lua Script)

Ensures only the lock holder can release:

```ts
const UNLOCK_SCRIPT = `
if redis.call("get", KEYS[1]) == ARGV[1] then
  return redis.call("del", KEYS[1])
else
  return 0
end
`;

async function releaseLock(resource: string, token: string): Promise<boolean> {
  const result = await valkey.eval(UNLOCK_SCRIPT, 1, `lock:${resource}`, token);
  return result === 1;
}
```

Valkey 9.0+ has `DELIFEQ` — delete if value equals, replacing the Lua script:

```bash
DELIFEQ lock:resource "token-value"
```

### Lock with Retry

```ts
async function withLock<T>(
  resource: string,
  ttlMs: number,
  fn: () => Promise<T>,
  retries = 3,
  retryDelayMs = 200,
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    const token = await acquireLock(resource, ttlMs);
    if (token) {
      try {
        return await fn();
      } finally {
        await releaseLock(resource, token);
      }
    }
    await new Promise((r) => setTimeout(r, retryDelayMs * (i + 1)));
  }
  throw new Error(`Failed to acquire lock on ${resource}`);
}
```

### Redlock (Multi-Instance)

For fault tolerance, acquire locks on N/2+1 out of N independent Valkey instances within a time budget. Use the `redlock` npm package for the algorithm implementation.

## Queues

### Simple Queue (List)

```ts
// Producer
await valkey.lpush(
  'queue:emails',
  JSON.stringify({ to: 'user@example.com', subject: 'Welcome' }),
);

// Consumer (blocking)
const [, message] = await valkey.brpop('queue:emails', 30); // 30s timeout
if (message) {
  const job = JSON.parse(message);
  await sendEmail(job);
}
```

### Reliable Queue (LMOVE)

Move to a processing list before handling. If the consumer crashes, the message is not lost.

```bash
LMOVE queue:emails queue:emails:processing RIGHT LEFT
# Process the message...
LREM queue:emails:processing 1 "message"
```

### Stream-Based Queue (Recommended)

Consumer groups provide at-least-once delivery, acknowledgment, and multiple consumers.

```ts
// Create consumer group (once)
await valkey.xgroup('CREATE', 'stream:tasks', 'workers', '$', 'MKSTREAM');

// Producer
await valkey.xadd(
  'stream:tasks',
  '*',
  'type',
  'process',
  'payload',
  JSON.stringify(data),
);

// Consumer
const entries = await valkey.xreadgroup(
  'GROUP',
  'workers',
  'consumer1',
  'COUNT',
  1,
  'BLOCK',
  5000,
  'STREAMS',
  'stream:tasks',
  '>',
);

if (entries) {
  const [, messages] = entries[0];
  for (const [id, fields] of messages) {
    await processTask(fields);
    await valkey.xack('stream:tasks', 'workers', id);
  }
}
```

## Session Storage

### Hash-Based Sessions

```ts
async function createSession(
  sessionId: string,
  data: Record<string, string>,
): Promise<void> {
  const key = `session:${sessionId}`;
  await valkey.hset(key, data);
  await valkey.expire(key, 1800); // 30 minutes
}

async function getSession(
  sessionId: string,
): Promise<Record<string, string> | null> {
  const key = `session:${sessionId}`;
  const data = await valkey.hgetall(key);
  if (Object.keys(data).length === 0) return null;

  // Sliding expiration
  await valkey.expire(key, 1800);
  return data;
}

async function destroySession(sessionId: string): Promise<void> {
  await valkey.unlink(`session:${sessionId}`);
}
```

### String-Based Sessions (JSON)

Simpler but cannot update individual fields without read-modify-write:

```ts
await valkey.set(`session:${id}`, JSON.stringify(sessionData), 'EX', 1800);
const session = JSON.parse(await valkey.get(`session:${id}`));
```

Hash-based is preferred when individual fields are read or updated independently.

## Pub/Sub

Fire-and-forget messaging. Messages are NOT persisted — if no subscriber is listening, the message is lost.

```ts
// Subscriber
const sub = valkey.duplicate(); // Dedicated connection for subscriptions
await sub.subscribe('notifications:user:123');

sub.on('message', (channel, message) => {
  const event = JSON.parse(message);
  handleNotification(event);
});

// Publisher (from any connection)
await valkey.publish(
  'notifications:user:123',
  JSON.stringify({ type: 'new_message', from: 'Alice' }),
);
```

### Pattern Subscriptions

```ts
await sub.psubscribe('notifications:*');

sub.on('pmessage', (pattern, channel, message) => {
  // pattern = 'notifications:*'
  // channel = 'notifications:user:123'
});
```

Use Pub/Sub for: real-time notifications, cache invalidation broadcasts, live dashboards.
Use Streams instead when: you need message persistence, replay, or at-least-once delivery.

## Leaderboards

Sorted sets provide O(log N) rank operations — ideal for leaderboards at any scale.

```ts
// Add or update score
await valkey.zadd('leaderboard:weekly', score, `player:${userId}`);

// Increment score
await valkey.zincrby('leaderboard:weekly', pointsEarned, `player:${userId}`);

// Top 10 with scores
const top10 = await valkey.zrevrange('leaderboard:weekly', 0, 9, 'WITHSCORES');

// Player rank (0-based)
const rank = await valkey.zrevrank('leaderboard:weekly', `player:${userId}`);

// Players in score range
const tier = await valkey.zrangebyscore(
  'leaderboard:weekly',
  1000,
  2000,
  'WITHSCORES',
);
```

## Counters

Atomic increment/decrement operations. No race conditions.

```ts
// Page views
await valkey.incr('page:views:home');

// Credits
await valkey.incrby(`user:credits:${userId}`, 50);

// Hash field counters
await valkey.hincrby('stats:daily', 'signups', 1);
await valkey.hincrby('stats:daily', 'api_calls', 1);

// Decrement
await valkey.decrby(`user:credits:${userId}`, 10);
```

## Pipelining

Send multiple commands without waiting for individual responses. Reduces round-trip overhead.

```ts
const pipeline = valkey.pipeline();
pipeline.set('key1', 'val1', 'EX', 3600);
pipeline.set('key2', 'val2', 'EX', 3600);
pipeline.get('key3');
pipeline.incr('counter');

const results = await pipeline.exec();
// results = [[null, 'OK'], [null, 'OK'], [null, 'val3'], [null, 42]]
```

Pipeline in batches of ~1,000-10,000 commands to balance throughput and memory.
