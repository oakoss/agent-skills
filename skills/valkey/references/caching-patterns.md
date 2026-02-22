---
title: Caching Patterns
description: Cache-aside, write-through, TTL strategies, eviction policies, client-side caching, and cache invalidation patterns for Valkey
tags:
  [
    cache-aside,
    write-through,
    ttl,
    eviction,
    lru,
    lfu,
    invalidation,
    client-side-caching,
  ]
---

## Cache-Aside (Lazy Loading)

The application checks the cache first. On miss, reads from the database, then populates the cache. Most common pattern.

```ts
async function getUser(id: string): Promise<User> {
  const cached = await valkey.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUnique({ where: { id } });
  if (user) {
    await valkey.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);
  }
  return user;
}
```

**Pros**: Only caches what is actually requested. Cache failures do not break reads.
**Cons**: Cache miss adds latency (DB read + cache write). Data can go stale.

## Write-Through

Write to both cache and database on every write. Cache is always current.

```ts
async function updateUser(id: string, data: Partial<User>): Promise<User> {
  const user = await db.user.update({ where: { id }, data });
  await valkey.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);
  return user;
}
```

**Pros**: Cache always reflects latest writes. No stale data for known keys.
**Cons**: Write latency increases. Caches data that may never be read.

## Write-Behind (Write-Back)

Write to cache immediately, flush to database asynchronously. Higher throughput but risk of data loss on crash.

Best implemented with Streams as a write buffer:

```ts
async function updateCounter(id: string, amount: number): Promise<void> {
  await valkey.incrby(`counter:${id}`, amount);
  await valkey.xadd('flush:counters', '*', 'id', id, 'amount', String(amount));
}
```

A background worker consumes the stream and persists to the database in batches.

## TTL Strategies

| Strategy        | Command                          | Use Case                                    |
| --------------- | -------------------------------- | ------------------------------------------- |
| Fixed TTL       | `SET key val EX 3600`            | General caching                             |
| Sliding TTL     | `EXPIRE key 1800` on each access | Session storage                             |
| Staggered TTL   | `EX (base + random(0, spread))`  | Prevent thundering herd                     |
| Short TTL       | `EX 60`                          | Frequently changing data                    |
| Long safety net | `EX 86400`                       | Rarely changes but should eventually expire |

### Thundering Herd Prevention

When many keys expire at the same time, all cache misses hit the database simultaneously:

```ts
function ttlWithJitter(baseTtl: number, jitterPercent = 10): number {
  const jitter = Math.floor(Math.random() * baseTtl * (jitterPercent / 100));
  return baseTtl + jitter;
}

await valkey.set(key, value, 'EX', ttlWithJitter(3600));
```

### Stale-While-Revalidate

Serve stale data immediately, refresh in the background:

```ts
async function getWithSWR(
  key: string,
  fetchFn: () => Promise<string>,
): Promise<string> {
  const ttl = await valkey.ttl(key);
  const value = await valkey.get(key);

  if (value && ttl < 300) {
    // Less than 5 minutes left — refresh in background
    fetchFn().then((fresh) => valkey.set(key, fresh, 'EX', 3600));
  }

  if (value) return value;

  const fresh = await fetchFn();
  await valkey.set(key, fresh, 'EX', 3600);
  return fresh;
}
```

## Eviction Policies

Set with `maxmemory` and `maxmemory-policy` in configuration.

| Policy            | Scope         | Algorithm                         |
| ----------------- | ------------- | --------------------------------- |
| `noeviction`      | N/A           | Returns error on writes when full |
| `allkeys-lru`     | All keys      | Least Recently Used               |
| `allkeys-lfu`     | All keys      | Least Frequently Used             |
| `allkeys-random`  | All keys      | Random eviction                   |
| `volatile-lru`    | Keys with TTL | LRU among expiring keys           |
| `volatile-lfu`    | Keys with TTL | LFU among expiring keys           |
| `volatile-random` | Keys with TTL | Random among expiring keys        |
| `volatile-ttl`    | Keys with TTL | Shortest remaining TTL first      |

### Choosing a Policy

- **`allkeys-lru`** — best default for most workloads (power-law access patterns)
- **`allkeys-lfu`** — when frequency matters more than recency (popular items stay cached)
- **`volatile-ttl`** — when TTL hints are set intentionally and should drive eviction
- **`noeviction`** — when data loss is unacceptable (session store, queues)

### Tuning

```text
maxmemory 256mb
maxmemory-policy allkeys-lru
maxmemory-samples 10          # Higher = closer to true LRU (default 5)

# LFU tuning (only relevant with *-lfu policies)
lfu-log-factor 10             # Higher = more hits needed to saturate counter
lfu-decay-time 1              # Minutes before counter halves
```

Monitor eviction with `INFO stats` — check `evicted_keys`.

## Client-Side Caching

Server-assisted caching where Valkey pushes invalidation messages when cached keys change.

### Tracking Mode (Default)

Server tracks which keys each client reads. When a key changes, the server sends an invalidation to clients that cached it.

```bash
CLIENT TRACKING ON REDIRECT 42    # 42 = client ID for invalidation channel
```

### Broadcasting Mode

Clients subscribe to key prefixes. Less server memory but more invalidation messages.

```bash
CLIENT TRACKING ON BCAST PREFIX user: PREFIX product:
```

### OPTIN Mode

Clients explicitly opt-in per key:

```bash
CLIENT CACHING YES
GET user:123                       # Server tracks this key for this client
```

### NOLOOP

Prevents receiving invalidation for keys you modified yourself:

```bash
CLIENT TRACKING ON NOLOOP
```

## Cache Invalidation

| Method                 | Command                                 | Use Case                   |
| ---------------------- | --------------------------------------- | -------------------------- |
| TTL-based              | `EXPIRE key ttl`                        | Natural expiration         |
| Active delete          | `DEL key` or `UNLINK key`               | On write/update            |
| Pattern delete         | `SCAN` + `UNLINK`                       | Invalidate by prefix       |
| Keyspace notifications | `CONFIG SET notify-keyspace-events KEA` | React to key changes       |
| Client tracking        | `CLIENT TRACKING ON`                    | Server-pushed invalidation |

### Pattern Invalidation with SCAN

Never use `KEYS` in production. Use `SCAN` for safe iteration:

```ts
async function invalidatePattern(pattern: string): Promise<number> {
  let cursor = '0';
  let deleted = 0;

  do {
    const [next, keys] = await valkey.scan(
      cursor,
      'MATCH',
      pattern,
      'COUNT',
      100,
    );
    cursor = next;
    if (keys.length > 0) {
      deleted += await valkey.unlink(...keys);
    }
  } while (cursor !== '0');

  return deleted;
}

await invalidatePattern('user:123:*');
```

## Memory Monitoring

```bash
INFO memory                              # Memory usage summary
MEMORY USAGE key                         # Bytes for a specific key
MEMORY DOCTOR                            # Diagnostic suggestions
DBSIZE                                   # Total key count
INFO keyspace                            # Keys per database with TTL stats
```
