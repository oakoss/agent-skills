---
title: Docker and Deployment
description: Docker Compose setup, persistence configuration, replication, Sentinel, Cluster mode, security, client libraries, and migration from Redis
tags:
  [
    docker,
    compose,
    persistence,
    replication,
    sentinel,
    cluster,
    security,
    migration,
    ioredis,
    iovalkey,
  ]
---

## Docker Compose

### Development Setup

```yaml
services:
  valkey:
    image: valkey/valkey:8.1-alpine
    ports:
      - '6379:6379'
    volumes:
      - valkey-data:/data
    command: valkey-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ['CMD', 'valkey-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

volumes:
  valkey-data:
```

### Production Setup

```yaml
services:
  valkey:
    image: valkey/valkey:8.1-alpine
    ports:
      - '6379:6379'
    volumes:
      - valkey-data:/data
    command: >
      valkey-server
      --appendonly yes
      --appendfsync everysec
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
      --requirepass ${VALKEY_PASSWORD}
      --bind 0.0.0.0
      --protected-mode yes
      --save 900 1
      --save 300 10
      --save 60 10000
    healthcheck:
      test: ['CMD', 'valkey-cli', '-a', '${VALKEY_PASSWORD}', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1280m
    restart: unless-stopped

volumes:
  valkey-data:
```

### With Application Service

```yaml
services:
  app:
    build: .
    environment:
      VALKEY_URL: valkey://valkey:6379
    depends_on:
      valkey:
        condition: service_healthy

  valkey:
    image: valkey/valkey:8.1-alpine
    volumes:
      - valkey-data:/data
    command: valkey-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ['CMD', 'valkey-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  valkey-data:
```

### Valkey Bundle (With Modules)

Includes JSON, Bloom, and Search modules:

```yaml
services:
  valkey:
    image: valkey/valkey-bundle:latest
    ports:
      - '6379:6379'
    volumes:
      - valkey-data:/data
```

## Persistence

### RDB (Point-in-Time Snapshots)

```text
save 900 1         # Snapshot if 1+ keys changed in 900 seconds
save 300 10        # Snapshot if 10+ keys changed in 300 seconds
save 60 10000      # Snapshot if 10000+ keys changed in 60 seconds
dbfilename dump.rdb
dir /data
```

Good for backups. Some data loss on crash (up to the last snapshot interval).

### AOF (Append-Only File)

```text
appendonly yes
appendfsync everysec       # Options: always, everysec, no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

| `appendfsync` | Durability          | Performance            |
| ------------- | ------------------- | ---------------------- |
| `always`      | No data loss        | Slowest                |
| `everysec`    | Up to 1 second loss | Balanced (recommended) |
| `no`          | OS-dependent        | Fastest                |

### RDB + AOF (Recommended)

Enable both. On restart, AOF is used for recovery (more complete). RDB provides efficient backups.

## Replication

Asynchronous primary-replica replication for read scaling and high availability.

```text
# On replica (valkey.conf)
replicaof primary-host 6379
replica-read-only yes
```

Docker Compose with replication:

```yaml
services:
  valkey-primary:
    image: valkey/valkey:8.1-alpine
    command: valkey-server --appendonly yes
    volumes:
      - primary-data:/data

  valkey-replica:
    image: valkey/valkey:8.1-alpine
    command: valkey-server --replicaof valkey-primary 6379 --replica-read-only yes
    depends_on:
      - valkey-primary

volumes:
  primary-data:
```

## Sentinel (High Availability)

Automatic failover for primary-replica deployments. Run 3+ Sentinel instances for quorum.

```text
# sentinel.conf
sentinel monitor myvalkey valkey-primary 6379 2    # 2 = quorum
sentinel down-after-milliseconds myvalkey 5000
sentinel failover-timeout myvalkey 60000
sentinel parallel-syncs myvalkey 1
```

Clients connect to Sentinel to discover the current primary:

```ts
import Valkey from 'iovalkey';

const valkey = new Valkey({
  sentinels: [
    { host: 'sentinel-1', port: 26379 },
    { host: 'sentinel-2', port: 26379 },
    { host: 'sentinel-3', port: 26379 },
  ],
  name: 'myvalkey',
});
```

## Cluster Mode

Data partitioned across nodes using 16,384 hash slots. Horizontal scaling.

```text
# valkey.conf (each node)
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
```

Client connection:

```ts
import Valkey from 'iovalkey';

const cluster = new Valkey.Cluster([
  { host: 'node-1', port: 6379 },
  { host: 'node-2', port: 6379 },
  { host: 'node-3', port: 6379 },
]);
```

Valkey 9.0 improvements: atomic slot migration, numbered databases in cluster mode, scaling to 2,000+ nodes.

## Security

### Authentication

```text
# Single password (legacy)
requirepass your_strong_password

# ACL (recommended)
user default off
user appuser on >password ~app:* +@read +@write -@admin
user readonly on >readpass ~* +@read
```

### TLS

```text
tls-port 6380
tls-cert-file /path/to/valkey.crt
tls-key-file /path/to/valkey.key
tls-ca-cert-file /path/to/ca.crt
tls-auth-clients yes
```

### Hardening Checklist

- Set `requirepass` or configure ACLs
- Bind to specific interfaces: `bind 127.0.0.1`
- Enable `protected-mode yes` when no auth is set
- Disable dangerous commands via ACLs or `rename-command FLUSHALL ""`
- Run as unprivileged user (default in Docker image)
- Never expose port 6379 directly to the internet

## Client Libraries

### Node.js / TypeScript Options

| Package                | Description                                        | Recommendation                      |
| ---------------------- | -------------------------------------------------- | ----------------------------------- |
| `ioredis`              | Popular Redis client, works with Valkey unchanged  | Existing projects                   |
| `iovalkey`             | Official Valkey fork of ioredis, identical API     | New projects (official maintenance) |
| `redis` (node-redis)   | Official Redis client, works with Valkey unchanged | If already using                    |
| `@valkey/valkey-glide` | Rust-core client with Node.js bindings             | Maximum performance                 |

### Connection Example (iovalkey / ioredis)

```ts
import Valkey from 'iovalkey';

const valkey = new Valkey({
  host: 'localhost',
  port: 6379,
  password: process.env.VALKEY_PASSWORD,
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    return Math.min(times * 50, 2000);
  },
});

valkey.on('error', (err) => console.error('Valkey connection error:', err));
valkey.on('connect', () => console.log('Connected to Valkey'));
```

### Connection URL

```ts
const valkey = new Valkey('redis://user:password@host:6379/0');
```

The `redis://` scheme works — Valkey is protocol-compatible.

## Migration from Redis

### What Changes

| Aspect       | Redis                        | Valkey                         |
| ------------ | ---------------------------- | ------------------------------ |
| Binary       | `redis-server` / `redis-cli` | `valkey-server` / `valkey-cli` |
| Config file  | `redis.conf`                 | `valkey.conf`                  |
| License      | RSALv2 / SSPLv1              | BSD 3-Clause                   |
| Docker image | `redis`                      | `valkey/valkey`                |

### What Stays the Same

- All commands and data structures
- Wire protocol (RESP2 / RESP3)
- RDB and AOF file formats (through Redis 7.2)
- Client libraries (no code changes needed)
- Cluster, Sentinel, and replication protocols
- Lua scripting and module API
- Default port (6379)

### Migration Steps

**Minimal downtime (replication):**

1. Start Valkey instance
2. Configure Valkey as replica of Redis: `replicaof redis-host 6379`
3. Wait for sync to complete: `INFO replication` shows `master_link_status:up`
4. Stop writes to Redis
5. Promote Valkey: `replicaof no one`
6. Update application connection strings
7. Resume writes

**Zero downtime (DNS swap):**

1. Run Valkey as replica until caught up
2. Promote Valkey to primary
3. Update DNS or load balancer to point to Valkey
4. Decommission Redis

**Physical (requires downtime):**

1. Stop Redis
2. Copy RDB file to Valkey data directory
3. Start Valkey

Redis CE 7.4+ data files are NOT compatible with Valkey. Migrate from 7.4+ using replication or export/import.
