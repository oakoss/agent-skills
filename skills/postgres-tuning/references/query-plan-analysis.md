---
title: Query Plan Analysis and Operator Forensics
description: EXPLAIN ANALYZE interpretation, identifying slow operators, B-tree skip scans, work_mem tuning, and pg_stat_statements usage
tags: [explain, analyze, buffers, seq-scan, work-mem, skip-scan]
---

# Query Plan Analysis and Operator Forensics

Optimizing queries without analyzing execution plans is guesswork. Use `EXPLAIN ANALYZE` with full context flags to identify bottlenecks.

## The Standard EXPLAIN Call

```sql
-- PG18: BUFFERS is auto-included with ANALYZE
EXPLAIN (ANALYZE, VERBOSE, SETTINGS)
SELECT o.id, o.status, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending'
ORDER BY o.created_at DESC
LIMIT 50;

-- Pre-PG18: explicitly include BUFFERS
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS)
SELECT o.id, o.status, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending'
ORDER BY o.created_at DESC
LIMIT 50;
```

### Key Metrics to Audit

| Metric                           | Meaning                             | Target                          |
| -------------------------------- | ----------------------------------- | ------------------------------- |
| Shared Hit                       | Pages found in shared_buffers (RAM) | > 95% of total reads            |
| Shared Read                      | Pages read from disk                | As low as possible              |
| Local Hit/Read                   | Pages in temporary storage          | 0 (indicates work_mem overflow) |
| Sort Method: external merge Disk | Sort spilled to disk                | Never in OLTP                   |
| Rows Removed by Filter           | Rows read but discarded             | Indicates missing index         |

## Identifying Slow Operators

### Sequential Scan (Seq Scan)

Reads the entire table row by row. Acceptable for small tables (<1000 rows) or when reading most of the table.

**Problem indicator:** Seq Scan on a table with >10,000 rows in a WHERE clause.

**Fix:** Add an index on the filtered column:

```sql
CREATE INDEX CONCURRENTLY idx_orders_status
ON orders (status);
```

### Nested Loop

Scans Table B for every row in Table A. Efficient when Table A returns few rows and Table B has an index on the join key.

**Problem indicator:** Nested Loop with high row counts on both sides.

**Fix:** Ensure Table B has an index on the join column:

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id
ON orders (customer_id);
```

### Hash Join

Builds a hash table from one side and probes it with the other. Good for large joins but memory-intensive.

**Problem indicator:** `Batches: 2` or higher in the plan means the hash table spilled to disk.

**Fix:** Increase `work_mem` for the session:

```sql
SET work_mem = '128MB';
```

### Merge Join

Sorts both sides and merges. Efficient when both inputs are already sorted or have matching indexes.

## B-tree Skip Scans (PostgreSQL 18)

PostgreSQL 18 can skip irrelevant parts of a composite index's leading column, using repeated targeted index searches for each distinct value in the prefix.

**Scenario:** Index on `(tenant_id, status)`, query filters only on `status`:

```sql
SELECT * FROM orders WHERE status = 'pending';
```

| PostgreSQL Version | Behavior                                                   |
| ------------------ | ---------------------------------------------------------- |
| Pre-18             | Cannot use the index (needs `tenant_id` prefix)            |
| 18+                | Skips through `tenant_id` values to find matching `status` |

**When skip scan works best:**

- Low cardinality (few distinct values) in the skipped prefix column
- Equality conditions on the trailing column (not ranges or inequalities)
- Narrow result sets and covering indexes (Index-Only Scans)

**When skip scan does NOT help:**

- High-cardinality prefix columns (millions of distinct values create too many probes)
- Range predicates (`>`, `<`, `BETWEEN`) on trailing columns -- equality only
- Large result sets where sequential or bitmap scans are more efficient

This can reduce the number of indexes needed, lowering storage costs and improving write performance. The planner enables skip scan automatically based on table statistics.

## work_mem Tuning

`work_mem` controls memory available for sort and hash operations per query operator.

```sql
-- Check current setting
SHOW work_mem;

-- Increase for a specific session
SET work_mem = '64MB';

-- Increase for a specific query
SET LOCAL work_mem = '256MB';
SELECT ... ORDER BY complex_expression;
RESET work_mem;
```

**Caution:** `work_mem` is allocated per operator, not per query. A query with 5 sort/hash operations uses up to 5x the `work_mem` value. Set high values only for specific sessions, not globally.

### Detecting work_mem Issues

Look for these in EXPLAIN output:

```text
Sort Method: external merge  Disk: 45MB
```

This means the sort exceeded work_mem and spilled to disk. Increase work_mem to at least the reported disk size.

## pg_stat_statements

The most important extension for identifying slow query patterns:

```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find the top 10 slowest queries by total time
SELECT
  queryid,
  calls,
  round(total_exec_time::numeric, 2) AS total_ms,
  round(mean_exec_time::numeric, 2) AS mean_ms,
  round((shared_blks_hit::numeric /
    nullif(shared_blks_hit + shared_blks_read, 0)) * 100, 2) AS cache_hit_pct,
  query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

**Review cadence:** Check weekly for new slow queries. Focus on queries with high `total_exec_time` (most cumulative impact) rather than high `mean_exec_time` (single worst case).

## Plan Analysis Workflow

1. **Identify** the slow query from `pg_stat_statements`
2. **Run** `EXPLAIN (ANALYZE, BUFFERS, SETTINGS)` on it
3. **Find** the most expensive node (highest actual time)
4. **Check** buffer hits vs reads (cache efficiency)
5. **Look** for Seq Scans on large tables, disk sorts, and high "Rows Removed"
6. **Fix** with targeted indexes, work_mem increases, or query rewrites
7. **Verify** by re-running EXPLAIN and comparing costs
