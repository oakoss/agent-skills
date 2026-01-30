---
name: postgres-tuning
description: 'PostgreSQL 17/18+ performance tuning and optimization. Covers async I/O configuration, query plan forensics, index strategies, autovacuum tuning, and vector search optimization. Use when diagnosing slow queries, configuring async I/O, tuning autovacuum, optimizing vector indexes, or analyzing execution plans with EXPLAIN BUFFERS.'
---

# PostgreSQL Tuning

## Overview

Optimizes PostgreSQL 17/18+ performance across I/O, query execution, indexing, and maintenance. Covers the native AIO subsystem for throughput gains on modern storage, forensic query plan analysis with EXPLAIN BUFFERS, B-tree skip scans, UUIDv7 migration, and autovacuum tuning for high-churn tables.

**When to use:** Diagnosing slow queries, configuring async I/O, tuning shared_buffers and work_mem, optimizing indexes for write-heavy workloads, managing table bloat, pgvector HNSW tuning.

**When NOT to use:** Schema design (use a data modeling tool), application-level caching strategy, database selection decisions, ORM query generation.

## Quick Reference

| Pattern               | Configuration / Query                        | Key Points                                                     |
| --------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| Async I/O             | `io_method = worker` or `io_uring`           | 2-3x throughput on NVMe; must tune `io_workers`                |
| Forensic EXPLAIN      | `EXPLAIN (ANALYZE, BUFFERS, SETTINGS, WAL)`  | Target Shared Hit > 95%; watch for disk reads                  |
| UUIDv7 primary keys   | `DEFAULT uuid_generate_v7()`                 | 30% faster inserts; better cache locality than v4              |
| B-tree skip scan      | Composite index on `(a, b)`                  | PG 18 can skip leading column for trailing lookups             |
| Aggressive autovacuum | `autovacuum_vacuum_scale_factor = 0.01`      | Triggers at 1% row change instead of default 20%               |
| Shared buffers        | Start at 25% of RAM                          | Do not exceed 40% without benchmarking                         |
| work_mem tuning       | `SET work_mem = '64MB'` per session          | Prevents "External Merge Disk" spills to disk                  |
| BRIN index            | `CREATE INDEX USING brin(...)`               | 100x smaller than B-tree for time-series data                  |
| HNSW vector index     | `USING hnsw (col vector_cosine_ops)`         | Tune `m` and `ef_construction` for recall vs speed             |
| Checkpoint tuning     | `checkpoint_timeout = 30min`                 | Spread writes to avoid I/O storms                              |
| Bloat detection       | `SELECT n_dead_tup FROM pg_stat_user_tables` | Reindex concurrently if bloat > 30%                            |
| I/O monitoring        | `SELECT * FROM pg_stat_io`                   | Watch `evictions` (cache too small) and `extend` (fast growth) |

## Common Mistakes

| Mistake                                                      | Correct Pattern                                                                    |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Using SELECT \* in high-frequency queries                    | Select only needed columns to reduce I/O and improve cache hit ratios              |
| Ignoring sequential scans on tables over 10k rows            | Add targeted indexes on columns used in WHERE, ORDER BY, and JOIN clauses          |
| Using random UUIDv4 as primary key on high-write tables      | Migrate to UUIDv7 for sequential ordering, reducing B-tree page splits             |
| Setting shared_buffers above 40% of RAM without testing      | Start at 25% and benchmark; excessive allocation causes OS page cache contention   |
| Leaving autovacuum at default settings for high-churn tables | Tune autovacuum_vacuum_scale_factor to 0.01 for tables with frequent UPDATE/DELETE |
| Over-indexing columns rarely used in queries                 | Every extra index slows UPDATE/INSERT and prevents HOT (Heap Only Tuple) updates   |
| Ignoring "External Merge Disk" in query plans                | Increase work_mem for specific sessions; it indicates sort spills to disk          |

## Delegation

- **Discover slow queries and I/O bottlenecks**: Use `Explore` agent to analyze pg_stat_statements, pg_stat_io, and slow query logs
- **Execute query plan analysis and index optimization**: Use `Task` agent to run EXPLAIN ANALYZE, create indexes, and verify performance improvements
- **Design database scaling and partitioning strategy**: Use `Plan` agent to architect sharding, partitioning, and replication topology

## References

- [Async I/O configuration and storage tuning](references/aio-tuning.md)
- [Query plan analysis and operator forensics](references/query-plan-analysis.md)
- [Indexing strategies and bloat management](references/indexing-and-bloat.md)
