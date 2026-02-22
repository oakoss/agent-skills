---
title: Data Structures and Commands
description: Core Valkey data types with key commands — strings, hashes, lists, sets, sorted sets, streams, HyperLogLog, bitmaps, and geospatial indexes
tags:
  [
    strings,
    hashes,
    lists,
    sets,
    sorted-sets,
    streams,
    hyperloglog,
    bitmaps,
    geospatial,
  ]
---

## Strings

Binary-safe sequences up to 512 MB. The most basic type — used for caching, counters, and flags.

```bash
SET user:123:name "Alice" EX 3600       # Set with 1-hour TTL
GET user:123:name                        # Retrieve value
MSET k1 "v1" k2 "v2"                    # Set multiple atomically
MGET k1 k2                              # Get multiple
INCR page:views:home                    # Atomic increment (returns new value)
INCRBY user:credits:123 50              # Increment by amount
SETNX lock:resource "token"             # Set only if not exists
```

Key flags for `SET`:

| Flag              | Meaning                         |
| ----------------- | ------------------------------- |
| `EX seconds`      | TTL in seconds                  |
| `PX milliseconds` | TTL in milliseconds             |
| `NX`              | Only set if key does not exist  |
| `XX`              | Only set if key already exists  |
| `GET`             | Return old value before setting |

## Hashes

Field-value maps attached to a single key. Ideal for objects and structured data.

```bash
HSET user:123 name "Alice" email "alice@example.com" role "admin"
HGET user:123 name                       # Single field
HMGET user:123 name email                # Multiple fields
HGETALL user:123                         # All fields and values
HDEL user:123 role                       # Remove field
HINCRBY user:123 login_count 1           # Increment numeric field
HEXISTS user:123 email                   # Check field existence
HKEYS user:123                           # All field names
HLEN user:123                            # Field count
```

Valkey 9.0+ supports **hash field expiration** — expire individual fields without destroying the whole key:

```bash
HGETEX user:123 FIELDS 1 temp_token EX 300   # Get field, set 5-min TTL on it
```

## Lists

Ordered collections (insertion order). Implemented as linked lists — O(1) push/pop, O(N) index access.

```bash
RPUSH queue:emails "msg1" "msg2"         # Append to tail
LPUSH queue:emails "msg0"                # Prepend to head
RPOP queue:emails                        # Pop from tail
LPOP queue:emails                        # Pop from head
LRANGE queue:emails 0 -1                 # Get all elements
LLEN queue:emails                        # List length
BRPOP queue:emails 30                    # Blocking pop (30s timeout)
LMOVE src dest RIGHT LEFT                # Atomic move between lists
```

## Sets

Unordered collections of unique strings. O(1) membership check.

```bash
SADD tags:post:1 "typescript" "react" "testing"
SREM tags:post:1 "testing"              # Remove member
SISMEMBER tags:post:1 "react"           # Check membership (O(1))
SMEMBERS tags:post:1                     # All members
SCARD tags:post:1                        # Count
SINTER tags:post:1 tags:post:2          # Intersection
SUNION tags:post:1 tags:post:2          # Union
SDIFF tags:post:1 tags:post:2           # Difference
SRANDMEMBER tags:post:1 2               # 2 random members
```

## Sorted Sets

Unique strings ordered by floating-point score. O(log N) for most operations. The backbone of leaderboards, priority queues, and time-series indexes.

```bash
ZADD leaderboard 1500 "player:1" 1200 "player:2" 1800 "player:3"
ZREVRANGE leaderboard 0 9 WITHSCORES    # Top 10 (highest first)
ZRANGE leaderboard 0 9 WITHSCORES       # Bottom 10 (lowest first)
ZRANK leaderboard "player:1"            # Rank (0-based, ascending)
ZREVRANK leaderboard "player:1"         # Rank (0-based, descending)
ZSCORE leaderboard "player:1"           # Get score
ZINCRBY leaderboard 10 "player:1"       # Increment score
ZRANGEBYSCORE leaderboard 1000 2000     # Members in score range
ZREM leaderboard "player:2"             # Remove member
ZCARD leaderboard                        # Count
```

## Streams

Append-only log for event sourcing and message queuing. Persistent, replayable, with consumer groups.

```bash
# Produce
XADD events:orders * action "created" order_id "ord_123" total "4999"

# Consume (simple)
XREAD COUNT 10 BLOCK 5000 STREAMS events:orders 0
XRANGE events:orders - +                 # All entries
XLEN events:orders                       # Stream length

# Consumer groups (at-least-once delivery)
XGROUP CREATE events:orders workers $ MKSTREAM
XREADGROUP GROUP workers consumer1 COUNT 1 BLOCK 5000 STREAMS events:orders >
XACK events:orders workers 1234567890-0  # Acknowledge processing
XPENDING events:orders workers           # View unacknowledged
XTRIM events:orders MAXLEN ~ 10000       # Trim to ~10K entries
```

### Streams vs Pub/Sub

| Feature         | Pub/Sub                 | Streams                       |
| --------------- | ----------------------- | ----------------------------- |
| Persistence     | No                      | Yes                           |
| Replay          | No                      | Yes (`XRANGE`)                |
| Consumer groups | No                      | Yes (`XGROUP`)                |
| Acknowledgment  | No                      | Yes (`XACK`)                  |
| Delivery        | At-most-once            | At-most-once or at-least-once |
| Use case        | Real-time notifications | Event sourcing, task queues   |

## HyperLogLog

Probabilistic cardinality estimation using ~12 KB regardless of set size. 0.81% standard error.

```bash
PFADD unique:visitors:2025-02 "user:1" "user:2" "user:3"
PFCOUNT unique:visitors:2025-02          # Approximate unique count
PFMERGE unique:visitors:q1 unique:visitors:2025-01 unique:visitors:2025-02
```

Use for: unique visitor counts, distinct event tracking, cardinality where exact precision is not required.

## Bitmaps

Bit-level operations on strings. Memory-efficient for boolean flags across large ID spaces.

```bash
SETBIT feature:dark-mode 1001 1          # User 1001 enabled dark mode
GETBIT feature:dark-mode 1001            # Check flag
BITCOUNT feature:dark-mode               # Count enabled users
BITOP AND both:features feature:dark-mode feature:beta
BITPOS feature:dark-mode 1               # First user with flag set
```

Use for: feature flags, daily active user tracking, presence indicators.

## Geospatial

Store and query geographic coordinates using sorted sets internally.

```bash
GEOADD stores -122.4194 37.7749 "sf-downtown" -73.9857 40.7484 "nyc-midtown"
GEOPOS stores "sf-downtown"              # Get coordinates
GEODIST stores "sf-downtown" "nyc-midtown" km   # Distance
GEOSEARCH stores FROMLONLAT -122.4 37.8 BYRADIUS 10 km ASC COUNT 5
```

## Key Management

Commands that apply across all data types:

```bash
EXISTS key                               # Check existence (returns 0 or 1)
TYPE key                                 # Get data type
TTL key                                  # Remaining TTL in seconds (-1 = no TTL, -2 = expired)
EXPIRE key 3600                          # Set TTL
PERSIST key                              # Remove TTL
RENAME key newkey                        # Rename
UNLINK key                               # Async delete (non-blocking)
SCAN 0 MATCH "user:*" COUNT 100         # Iterate keys (cursor-based)
OBJECT ENCODING key                      # Internal encoding (ziplist, hashtable, etc.)
MEMORY USAGE key                         # Bytes used by key
```
