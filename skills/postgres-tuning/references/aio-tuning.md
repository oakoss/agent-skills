---
title: Async I/O Configuration and Storage Tuning
description: PostgreSQL 18 AIO configuration, io_method selection, shared buffer tuning, pg_stat_io monitoring, and checkpoint optimization
tags: [aio, io-method, io-uring, shared-buffers, checkpoints, pg-stat-io, nvme]
---

# Async I/O Configuration and Storage Tuning

PostgreSQL 18 introduces native Asynchronous I/O (AIO), enabling pipelined I/O requests that deliver 2-3x throughput gains on NVMe storage.

## AIO Configuration

### io_method Selection

Choose the I/O method based on your operating system and deployment:

```ini
# postgresql.conf

# Option 1: Worker processes (all platforms)
io_method = worker
io_workers = 4

# Option 2: io_uring (Linux only, highest performance)
io_method = io_uring
```

| Method     | Platform                    | Performance | Requirements           |
| ---------- | --------------------------- | ----------- | ---------------------- |
| `worker`   | All (Linux, macOS, Windows) | Good        | None                   |
| `io_uring` | Linux only                  | Best        | Kernel 5.10+, liburing |

**Worker tuning:** Set `io_workers` to match the number of NVMe queue pairs. For cloud instances, start with 4 and increase based on `pg_stat_io` monitoring.

### AIO Queue Depth

```ini
max_async_ios = 1024
```

Controls the depth of the AIO request queue. Higher values allow more concurrent I/O operations. Start at 1024 for NVMe storage; reduce to 256 for spinning disks.

## Shared Buffer Tuning

`shared_buffers` is the in-memory cache for frequently accessed data pages.

### Baseline Configuration

```ini
# Start here for most workloads
shared_buffers = '4GB'  # 25% of 16GB system RAM
```

### Sizing Guidelines

| System RAM | shared_buffers | Workload                  |
| ---------- | -------------- | ------------------------- |
| 8 GB       | 2 GB           | Small OLTP                |
| 16 GB      | 4 GB           | Standard OLTP             |
| 64 GB      | 16 GB          | Large OLTP                |
| 256 GB     | 64-100 GB      | Data warehouse (with AIO) |

**AIO impact:** With AIO enabled, read-heavy workloads can benefit from larger shared_buffers (up to 40-50% of RAM) because AIO reduces the CPU cost of cache misses. Benchmark before increasing beyond 40%.

### Cache Hit Ratio Monitoring

```sql
SELECT
  sum(heap_blks_hit) AS hits,
  sum(heap_blks_read) AS reads,
  round(
    sum(heap_blks_hit)::numeric /
    nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100,
    2
  ) AS hit_ratio
FROM pg_statio_user_tables;
```

**Target:** > 99% hit ratio. If below 95%, increase `shared_buffers` or investigate which tables are causing cache misses.

## pg_stat_io Monitoring

This view provides granular I/O analysis:

```sql
SELECT backend_type, io_object, io_context, reads, writes, extends
FROM pg_stat_io
WHERE reads > 0 OR writes > 0
ORDER BY reads + writes DESC;
```

**Key metrics:**

| Metric      | Meaning                  | Action if High                           |
| ----------- | ------------------------ | ---------------------------------------- |
| `reads`     | Pages read from disk     | Increase shared_buffers or add indexes   |
| `writes`    | Pages written to disk    | Tune checkpoint settings                 |
| `extends`   | Table growth operations  | Check fill factor, consider partitioning |
| `evictions` | Pages removed from cache | shared_buffers too small                 |

## Checkpoint Tuning

Checkpoints flush dirty pages to disk. Poorly tuned checkpoints cause latency spikes ("I/O storms").

```ini
# postgresql.conf
checkpoint_timeout = 30min
max_wal_size = 16GB
checkpoint_completion_target = 0.9
```

| Parameter                      | Purpose                                     | Recommended |
| ------------------------------ | ------------------------------------------- | ----------- |
| `checkpoint_timeout`           | Time between checkpoints                    | 15-30 min   |
| `max_wal_size`                 | WAL size before forced checkpoint           | 8-16 GB     |
| `checkpoint_completion_target` | Spread writes over this fraction of timeout | 0.9         |

**Goal:** Spread checkpoint writes evenly over 90% of the timeout window, avoiding sudden I/O bursts.

### Monitoring Checkpoints

```sql
SELECT
  checkpoints_timed,
  checkpoints_req,
  checkpoint_write_time,
  checkpoint_sync_time
FROM pg_stat_bgwriter;
```

If `checkpoints_req` (forced checkpoints) is high relative to `checkpoints_timed`, increase `max_wal_size`.

## WAL Configuration

```ini
# Write-Ahead Log
wal_level = replica
wal_compression = zstd
wal_buffers = '64MB'
```

`wal_compression = zstd` reduces WAL I/O by 50-70% for write-heavy workloads.

## Full Configuration Template

```ini
# postgresql.conf - Performance Template (16GB RAM, NVMe)
shared_buffers = '4GB'
effective_cache_size = '12GB'
work_mem = '16MB'
maintenance_work_mem = '512MB'
io_method = worker
io_workers = 4
max_async_ios = 1024
checkpoint_timeout = '30min'
max_wal_size = '16GB'
checkpoint_completion_target = 0.9
wal_compression = zstd
wal_buffers = '64MB'
random_page_cost = 1.1
effective_io_concurrency = 200
```

Adjust `random_page_cost` to 1.1 for SSDs (default 4.0 is for spinning disks). Set `effective_io_concurrency` to 200 for NVMe.
