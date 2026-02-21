---
title: Connection Pooling, Partitioning, and Query Patterns
description: PgBouncer configuration, Supavisor, declarative partitioning, cursor pagination, queue processing with FOR UPDATE SKIP LOCKED, fillfactor, and NULLS NOT DISTINCT
tags:
  [
    pgbouncer,
    supavisor,
    partitioning,
    pg_partman,
    cursor-pagination,
    keyset,
    skip-locked,
    fillfactor,
    nulls-not-distinct,
  ]
---

# Connection Pooling, Partitioning, and Query Patterns

PostgreSQL holds one OS process per connection. Without pooling, high connection counts waste memory and create scheduling overhead. Partitioning keeps large tables manageable. The query patterns in this file cover pagination, queue processing, and update performance.

## Connection Pooling

### Why Pooling Matters

Each PostgreSQL backend consumes ~5-10 MB of RAM and involves process forking overhead. Without pooling:

- 500 concurrent app connections = 500 backend processes
- Serverless functions spike connections on cold starts
- Connection storms during deployments exhaust `max_connections`

**Rule of thumb:** Set `max_connections = 100 * CPU_cores` in PostgreSQL. Route all application traffic through a pooler targeting 3-5 connections per CPU core to the database.

### PgBouncer

PgBouncer is the standard lightweight connection pooler for PostgreSQL.

#### Transaction Mode (Recommended for Most Apps)

A client holds a server connection only for the duration of a transaction. The connection returns to the pool between transactions.

```ini
; pgbouncer.ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
server_idle_timeout = 600
```

| Parameter           | Recommended   | Effect                                               |
| ------------------- | ------------- | ---------------------------------------------------- |
| `pool_mode`         | `transaction` | Release connection after each transaction            |
| `max_client_conn`   | 500-5000      | Total clients PgBouncer accepts                      |
| `default_pool_size` | 10-50         | Server connections per database+user pair            |
| `min_pool_size`     | 5             | Keeps warm connections to reduce first-query latency |
| `reserve_pool_size` | 5             | Extra connections for bursts                         |

#### Session Mode

A client holds a server connection for its entire session lifetime. Use only when the application requires session-level features (`SET`, temp tables, advisory locks, `LISTEN`/`NOTIFY`).

```ini
pool_mode = session
```

**Transaction mode does not support:** `SET` outside a transaction, temporary tables, advisory locks held across statements, `LISTEN`/`NOTIFY`. Switch to session mode for these, or use `SET LOCAL` inside transactions.

#### Pool Size Formula

```text
pool_size = (max_db_connections * 0.8) / num_pgbouncer_instances
```

Reserve 20% of `max_connections` for direct admin access, monitoring, and migrations.

#### Monitoring PgBouncer

```sql
-- Connect to the pgbouncer admin database
SHOW POOLS;
SHOW CLIENTS;
SHOW STATS;
```

Watch `cl_waiting` in `SHOW POOLS` — clients waiting for a connection. Non-zero values indicate the pool is undersized or the database is saturated.

### Supavisor

Supavisor is a cloud-native, multi-tenant pooler built by Supabase. It runs in Elixir and supports the same transaction/session/statement modes as PgBouncer but adds:

- Per-tenant isolation without separate processes
- Integrated metrics and observability
- Horizontal scaling across multiple nodes

Use Supavisor when running a multi-tenant SaaS with many databases, or when deploying on Supabase. PgBouncer remains the standard for single-database deployments.

### When to Use Pooling

| Scenario                          | Recommendation                          |
| --------------------------------- | --------------------------------------- |
| Serverless (Lambda, Edge, Vercel) | Always — cold starts spike connections  |
| Long-running app servers          | Recommended when > 50 app instances     |
| Single-process application        | Optional — built-in pool may suffice    |
| `LISTEN`/`NOTIFY` consumers       | Session mode or direct connection       |
| Background workers                | Direct connection, long-lived processes |

---

## Declarative Partitioning

Partitioning splits a large table into smaller physical tables (partitions) while presenting a single logical table to queries. The planner prunes irrelevant partitions from query plans.

### Range Partitioning by Date

The most common partitioning strategy for time-series data such as events, logs, and orders.

```sql
CREATE TABLE events (
  id bigint GENERATED ALWAYS AS IDENTITY,
  occurred_at timestamptz NOT NULL,
  event_type text NOT NULL,
  payload jsonb
) PARTITION BY RANGE (occurred_at);

CREATE TABLE events_2024_q1 PARTITION OF events
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE events_2024_q2 PARTITION OF events
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE events_2024_q3 PARTITION OF events
  FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE events_2024_q4 PARTITION OF events
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

CREATE TABLE events_default PARTITION OF events DEFAULT;
```

Always include a `DEFAULT` partition to catch rows that fall outside defined ranges.

### Partition Pruning

The planner eliminates partitions that cannot contain matching rows based on the `WHERE` clause. Pruning only works when the partition key is present in the filter.

```sql
-- Pruning works: planner scans only events_2024_q1
EXPLAIN SELECT * FROM events
WHERE occurred_at BETWEEN '2024-01-01' AND '2024-03-31';

-- Pruning does NOT work: no filter on occurred_at
EXPLAIN SELECT * FROM events
WHERE event_type = 'signup';
```

Look for `Partitions selected` in the `EXPLAIN` output to confirm pruning is active.

```sql
-- Enable partition pruning (default on)
SET enable_partition_pruning = on;
```

### List Partitioning

Partition by a discrete column such as region, tenant, or status.

```sql
CREATE TABLE orders (
  id bigint GENERATED ALWAYS AS IDENTITY,
  region text NOT NULL,
  amount numeric NOT NULL
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders
  FOR VALUES IN ('us-east', 'us-west');

CREATE TABLE orders_eu PARTITION OF orders
  FOR VALUES IN ('eu-west', 'eu-central');

CREATE TABLE orders_default PARTITION OF orders DEFAULT;
```

### Indexes on Partitioned Tables

Indexes created on the parent table are automatically created on all existing and future partitions.

```sql
-- Index propagates to all partitions
CREATE INDEX CONCURRENTLY idx_events_occurred_at
ON events (occurred_at);
```

### pg_partman for Automation

Manually creating partitions is error-prone. `pg_partman` automates partition creation and maintenance.

```sql
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
  p_parent_table   => 'public.events',
  p_control        => 'occurred_at',
  p_interval       => 'monthly',
  p_premake        => 3
);
```

`p_premake = 3` creates 3 future partitions in advance, preventing gaps. Run the maintenance function on a cron schedule:

```sql
SELECT partman.run_maintenance_proc();
```

Schedule via `pg_cron` or an external scheduler. Without regular maintenance, new partitions are not created automatically.

### Partition Anti-Patterns

| Anti-Pattern                                | Problem                                                         |
| ------------------------------------------- | --------------------------------------------------------------- |
| Too many partitions (> 1000)                | Planning overhead increases; `pg_dump` and schema ops slow down |
| Too few large partitions                    | No pruning benefit; equivalent to an unpartitioned table        |
| Partitioning small tables (< 1 GB)          | Adds complexity with no measurable benefit                      |
| Forgetting the DEFAULT partition            | Rows outside range bounds cause insert errors                   |
| Filtering on non-partition key              | No pruning; all partitions scanned regardless of query filter   |
| Foreign keys referencing partitioned tables | Not supported in all PostgreSQL versions; check compatibility   |

---

## Practical Query Patterns

### Cursor-Based (Keyset) Pagination

`OFFSET` pagination degrades as page numbers grow because the database must scan and discard all preceding rows. Keyset pagination uses a stable cursor based on the last seen row.

#### OFFSET Pagination (Avoid for Deep Pages)

```sql
-- Scans and discards 10,000 rows on every call at page 200
SELECT id, created_at, title
FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 50 OFFSET 10000;
```

#### Keyset Pagination

```sql
-- First page: no cursor
SELECT id, created_at, title
FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 50;

-- Subsequent pages: use last row values as cursor
SELECT id, created_at, title
FROM posts
WHERE (created_at, id) < ('2024-03-15 10:00:00', 98765)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

The composite `WHERE` clause skips directly to the next page without scanning preceding rows.

**Required index** for efficient keyset pagination:

```sql
CREATE INDEX CONCURRENTLY idx_posts_cursor
ON posts (created_at DESC, id DESC);
```

#### TypeScript Application Pattern

```ts
async function getPostsPage(cursor?: { createdAt: Date; id: number }) {
  const rows = await db.query<Post>(
    cursor
      ? `SELECT id, created_at, title
         FROM posts
         WHERE (created_at, id) < ($1, $2)
         ORDER BY created_at DESC, id DESC
         LIMIT 50`
      : `SELECT id, created_at, title
         FROM posts
         ORDER BY created_at DESC, id DESC
         LIMIT 50`,
    cursor ? [cursor.createdAt, cursor.id] : [],
  );

  const nextCursor =
    rows.length === 50
      ? {
          createdAt: rows[rows.length - 1].created_at,
          id: rows[rows.length - 1].id,
        }
      : null;

  return { rows, nextCursor };
}
```

**Trade-offs:**

| Aspect             | OFFSET Pagination        | Keyset Pagination          |
| ------------------ | ------------------------ | -------------------------- |
| Deep pages         | O(N) — gets slower       | O(log N) — constant cost   |
| Jump to page N     | Supported                | Not supported              |
| Consistent results | No — inserts shift pages | Yes — stable cursor        |
| Index required     | Optional                 | Required (on sort columns) |

### Queue Processing with FOR UPDATE SKIP LOCKED

`FOR UPDATE SKIP LOCKED` enables multiple workers to claim jobs from a shared queue without contention. Rows locked by one worker are silently skipped by others instead of blocking.

```sql
-- Worker claims the next available job
WITH claimed AS (
  SELECT id, payload, attempts
  FROM job_queue
  WHERE status = 'pending'
    AND run_at <= now()
  ORDER BY run_at ASC
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
UPDATE job_queue
SET status = 'processing',
    started_at = now()
FROM claimed
WHERE job_queue.id = claimed.id
RETURNING job_queue.id, job_queue.payload;
```

Each worker locks exactly one row. Other workers skip that row and move to the next without waiting for a lock.

**Required index** to avoid a full table scan:

```sql
CREATE INDEX CONCURRENTLY idx_job_queue_status_run_at
ON job_queue (status, run_at)
WHERE status = 'pending';
```

#### TypeScript Worker Pattern

```ts
async function claimNextJob(db: DatabaseClient) {
  const result = await db.query<{ id: number; payload: unknown }>(`
    WITH claimed AS (
      SELECT id, payload
      FROM job_queue
      WHERE status = 'pending'
        AND run_at <= now()
      ORDER BY run_at ASC
      LIMIT 1
      FOR UPDATE SKIP LOCKED
    )
    UPDATE job_queue
    SET status = 'processing', started_at = now()
    FROM claimed
    WHERE job_queue.id = claimed.id
    RETURNING job_queue.id, job_queue.payload
  `);

  return result.rows[0] ?? null;
}
```

**Requirements:** Must run inside an explicit transaction. The lock is held until the transaction commits or rolls back.

### fillfactor for HOT Updates

By default, PostgreSQL fills data pages to 100% (`fillfactor = 100`). When a row is updated, a new row version is written to the next available page, requiring an index entry update. Setting `fillfactor` below 100 leaves free space on each page, allowing HOT (Heap Only Tuple) updates to write the new row version on the same page without touching indexes.

```sql
-- Create table with fillfactor
CREATE TABLE sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  last_seen timestamptz NOT NULL,
  metadata jsonb
) WITH (fillfactor = 70);

-- Apply to an existing table
ALTER TABLE sessions SET (fillfactor = 70);

-- Reclaim space and apply the setting (requires brief lock)
VACUUM sessions;
```

| fillfactor | Free Space per Page | When to Use                                      |
| ---------- | ------------------- | ------------------------------------------------ |
| 100        | 0%                  | Append-only tables, rarely updated               |
| 70-80      | 20-30%              | Frequently updated rows (sessions, counters)     |
| 50         | 50%                 | Extremely hot rows updated many times per second |

**Verify HOT updates are happening:**

```sql
SELECT relname, n_tup_hot_upd, n_tup_upd,
  round(n_tup_hot_upd::numeric / nullif(n_tup_upd, 0) * 100, 1) AS hot_pct
FROM pg_stat_user_tables
WHERE relname = 'sessions';
```

A `hot_pct` below 50% on a frequently updated table suggests removing unnecessary indexes or lowering `fillfactor`.

### NULLS NOT DISTINCT (PostgreSQL 15+)

Standard SQL treats `NULL` as distinct from every other value, including other `NULL`s. A unique index on a nullable column allows multiple rows with `NULL` in that column. `NULLS NOT DISTINCT` changes this — `NULL` is treated as a regular value for uniqueness purposes.

```sql
-- PG15+: Only one row with NULL allowed in email
CREATE UNIQUE INDEX idx_users_email_unique
ON users (email) NULLS NOT DISTINCT;

-- Table-level constraint
ALTER TABLE users
ADD CONSTRAINT uq_users_email UNIQUE NULLS NOT DISTINCT (email);
```

**Composite unique constraint example** — useful for soft-delete patterns where `deleted_at` is nullable:

```sql
-- Allow multiple deleted rows with the same username, but only one active row
CREATE UNIQUE INDEX idx_users_username_active
ON users (username, deleted_at) NULLS NOT DISTINCT;
```

Without `NULLS NOT DISTINCT`, the index allows unlimited rows where `deleted_at IS NULL` and `username = 'alice'` — the opposite of the intended constraint.

**Pre-PostgreSQL 15 workaround:**

```sql
-- Partial unique index covers only the non-deleted (active) case
CREATE UNIQUE INDEX idx_users_username_active
ON users (username)
WHERE deleted_at IS NULL;
```

This is still the correct approach for multi-column uniqueness involving null semantics on older versions.
