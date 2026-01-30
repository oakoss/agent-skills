---
title: Indexing Strategies and Bloat Management
description: B-tree, BRIN, HNSW, and GIN index patterns, autovacuum tuning, HOT updates, bloat detection, and UUIDv7 migration
tags: [indexes, brin, hnsw, autovacuum, bloat, uuidv7]
---

# Indexing Strategies and Bloat Management

Effective indexing reduces query latency. Bloat management prevents performance degradation from dead tuples accumulating in tables and indexes.

## Index Type Selection

| Index Type | Best For                               | Size                     | Trade-off                     |
| ---------- | -------------------------------------- | ------------------------ | ----------------------------- |
| B-tree     | Equality and range queries             | Medium                   | General purpose, default      |
| BRIN       | Time-series, physically sorted data    | 100x smaller than B-tree | Only works on correlated data |
| GIN        | JSONB fields, full-text search, arrays | Large                    | Slower writes                 |
| HNSW       | Vector similarity (pgvector)           | Large                    | Tune accuracy vs speed        |
| Partial    | Filtered subsets                       | Small                    | Only covers matching rows     |
| Covering   | Queries needing specific columns       | Medium-Large             | Avoids table lookups          |

## B-tree Patterns

### Standard Index

```sql
CREATE INDEX CONCURRENTLY idx_orders_status
ON orders (status);
```

### Composite Index

Column order matters. Place the most selective column first:

```sql
CREATE INDEX CONCURRENTLY idx_orders_tenant_status
ON orders (tenant_id, status);
```

This index serves queries filtering on `tenant_id` alone, or `tenant_id` AND `status`, but not `status` alone (pre-PG18).

### Partial Index

Index only the rows you query:

```sql
CREATE INDEX CONCURRENTLY idx_orders_active
ON orders (created_at)
WHERE status = 'active';
```

Much smaller than a full index. Only covers queries with `WHERE status = 'active'`.

### Covering Index (INCLUDE)

Eliminate table lookups by including extra columns in the index:

```sql
CREATE INDEX CONCURRENTLY idx_orders_status_covering
ON orders (status)
INCLUDE (customer_id, total);
```

Queries selecting only `customer_id` and `total` with a `status` filter can be served entirely from the index.

## BRIN Index (Time-Series)

Block Range Index stores min/max values per block range. Ideal for append-only, physically ordered data:

```sql
CREATE INDEX idx_logs_timestamp
ON logs USING brin (created_at);
```

**100x smaller** than an equivalent B-tree. Only effective when physical row order correlates with the indexed column.

## HNSW Vector Index (pgvector)

For semantic search and AI embeddings:

```sql
CREATE INDEX idx_embeddings_vector
ON embeddings USING hnsw (embedding_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 128);
```

| Parameter         | Effect                                                            | Default |
| ----------------- | ----------------------------------------------------------------- | ------- |
| `m`               | Connections per node (higher = better recall, more memory)        | 16      |
| `ef_construction` | Build-time search breadth (higher = better quality, slower build) | 64      |

Increase both values if recall is too low. Decrease if index build time is excessive.

## UUIDv7 Migration

Random UUIDv4 primary keys cause B-tree page splits because new values are randomly distributed. UUIDv7 is time-ordered, providing sequential inserts.

```sql
CREATE TABLE transactions (
  id uuid DEFAULT uuid_generate_v7() PRIMARY KEY,
  amount numeric NOT NULL,
  created_at timestamptz DEFAULT now()
);
```

**Benefits:** 30% faster insertions, better cache locality, reduced index fragmentation. The time component also enables rough time-based ordering without a separate timestamp column.

## Autovacuum Tuning

Autovacuum reclaims space from dead tuples (rows deleted or updated). Default settings trigger after 20% of the table changes.

### Aggressive Settings for High-Churn Tables

```sql
ALTER TABLE high_churn_orders SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_vacuum_cost_limit = 1000,
  autovacuum_analyze_scale_factor = 0.005
);
```

| Parameter              | Default   | Aggressive   | Effect                                  |
| ---------------------- | --------- | ------------ | --------------------------------------- |
| `vacuum_scale_factor`  | 0.2 (20%) | 0.01 (1%)    | Triggers vacuum after 1% rows change    |
| `vacuum_cost_limit`    | 200       | 1000         | Allows vacuum to do more work per cycle |
| `analyze_scale_factor` | 0.1 (10%) | 0.005 (0.5%) | Updates statistics more frequently      |

### Global Settings

```ini
# postgresql.conf
autovacuum_max_workers = 6
autovacuum_naptime = '30s'
autovacuum_vacuum_cost_delay = '2ms'
```

## HOT (Heap Only Tuple) Updates

HOT updates avoid creating new index entries when an UPDATE does not modify any indexed column. They are a significant performance win.

**Optimization rule:** Only index columns you actually filter, sort, or join on. Every extra index:

- Slows INSERT and UPDATE operations
- Prevents HOT updates for modifications to indexed columns
- Consumes additional disk space and shared_buffers

## Bloat Detection

Find tables with the most dead tuples:

```sql
SELECT
  schemaname,
  relname,
  n_live_tup,
  n_dead_tup,
  round(n_dead_tup::numeric / nullif(n_live_tup, 0) * 100, 2) AS dead_pct,
  last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 20;
```

**Action thresholds:**

| Dead Tuple % | Action                                         |
| ------------ | ---------------------------------------------- |
| < 5%         | Normal, no action                              |
| 5-20%        | Tune autovacuum settings for this table        |
| 20-30%       | Run manual `VACUUM VERBOSE tablename`          |
| > 30%        | Consider `REINDEX CONCURRENTLY` or `pg_repack` |

### Reclaiming Space

```sql
-- Standard vacuum (reclaims space within table, non-blocking)
VACUUM VERBOSE orders;

-- Full vacuum (rewrites entire table, requires exclusive lock)
VACUUM FULL orders;

-- Reindex without locking (preferred)
REINDEX INDEX CONCURRENTLY idx_orders_status;

-- pg_repack (no locking, requires extension)
-- pg_repack --table=orders --no-order
```

Prefer `REINDEX CONCURRENTLY` over `VACUUM FULL` in production because it does not require an exclusive lock.

## GIN Index for JSONB

```sql
CREATE INDEX idx_metadata_gin
ON products USING gin (metadata);

SELECT * FROM products
WHERE metadata @> '{"category": "electronics"}';
```

GIN indexes support containment (`@>`), existence (`?`), and key-path operators on JSONB columns.
