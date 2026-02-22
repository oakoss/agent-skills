---
title: Observability and Monitoring
description: Health checks, sync metrics, Prometheus integration, alerting patterns, stalled sync detection, and production monitoring for ElectricSQL deployments
tags:
  [
    monitoring,
    observability,
    health-check,
    prometheus,
    grafana,
    metrics,
    alerting,
    sync-latency,
    replication-lag,
    debugging,
  ]
---

## Health Monitoring

Electric exposes a health endpoint for liveness checks.

```bash
curl http://localhost:3000/v1/health
```

Response returns `200 OK` when Electric is connected to Postgres and ready to serve shapes.

### Kubernetes Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: electric
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: electric
          image: electricsql/electric:latest
          ports:
            - containerPort: 3000
            - containerPort: 9090
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: electric-secrets
                  key: database-url
            - name: ELECTRIC_PROMETHEUS_PORT
              value: '9090'
          livenessProbe:
            httpGet:
              path: /v1/health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 15
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /v1/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: '256Mi'
              cpu: '250m'
            limits:
              memory: '1Gi'
              cpu: '1000m'
```

### Docker Compose Health Check

```yaml
services:
  electric:
    image: electricsql/electric:latest
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/app
      ELECTRIC_PROMETHEUS_PORT: 9090
    ports:
      - '3000:3000'
      - '9090:9090'
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/v1/health']
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    depends_on:
      db:
        condition: service_healthy
```

## Client-Side Observability

### Tracking Sync Freshness

```ts
import { ShapeStream } from '@electric-sql/client';

type SyncMetrics = {
  lastSyncedAt: number | null;
  initialSyncDurationMs: number | null;
  reconnectionCount: number;
  totalRowsSynced: number;
};

function createMonitoredStream<T extends Record<string, unknown>>(
  url: string,
  table: string,
  where?: string,
): { stream: ShapeStream<T>; getMetrics: () => SyncMetrics } {
  const metrics: SyncMetrics = {
    lastSyncedAt: null,
    initialSyncDurationMs: null,
    reconnectionCount: 0,
    totalRowsSynced: 0,
  };

  const startTime = Date.now();
  let initialSyncComplete = false;

  const params: Record<string, string> = { table };
  if (where) params.where = where;

  const stream = new ShapeStream<T>({ url, params });

  stream.subscribe((messages) => {
    for (const msg of messages) {
      if ('key' in msg) {
        metrics.totalRowsSynced++;
      }

      if ('headers' in msg && msg.headers?.control === 'up-to-date') {
        metrics.lastSyncedAt = Date.now();
        if (!initialSyncComplete) {
          metrics.initialSyncDurationMs = Date.now() - startTime;
          initialSyncComplete = true;
        }
      }
    }
  });

  return { stream, getMetrics: () => ({ ...metrics }) };
}
```

### Detecting Stale Shapes

```ts
function monitorStaleness(
  getMetrics: () => SyncMetrics,
  thresholdMs: number,
  onStale: (staleDurationMs: number) => void,
): () => void {
  const intervalId = setInterval(() => {
    const metrics = getMetrics();
    if (metrics.lastSyncedAt === null) return;

    const staleDuration = Date.now() - metrics.lastSyncedAt;
    if (staleDuration > thresholdMs) {
      onStale(staleDuration);
    }
  }, 5000);

  return () => clearInterval(intervalId);
}

const STALE_THRESHOLD_MS = 30_000;

const cleanup = monitorStaleness(
  getMetrics,
  STALE_THRESHOLD_MS,
  (staleDuration) => {
    console.warn(`Shape stale for ${Math.round(staleDuration / 1000)}s`);
    reportToTelemetry('shape_stale', { staleDuration });
  },
);
```

### Reporting to Analytics

```ts
type TelemetryEvent = {
  event: string;
  properties: Record<string, unknown>;
  timestamp: number;
};

function reportToTelemetry(
  event: string,
  properties: Record<string, unknown>,
): void {
  const payload: TelemetryEvent = {
    event,
    properties,
    timestamp: Date.now(),
  };

  navigator.sendBeacon('/api/telemetry', JSON.stringify(payload));
}

function reportSyncMetrics(getMetrics: () => SyncMetrics): void {
  const metrics = getMetrics();
  reportToTelemetry('sync_metrics', {
    initialSyncDurationMs: metrics.initialSyncDurationMs,
    reconnectionCount: metrics.reconnectionCount,
    totalRowsSynced: metrics.totalRowsSynced,
    lastSyncedAt: metrics.lastSyncedAt,
  });
}
```

## Prometheus Integration

Enable Prometheus metrics by setting the `ELECTRIC_PROMETHEUS_PORT` environment variable.

```bash
ELECTRIC_PROMETHEUS_PORT=9090
```

### Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: electric
    scrape_interval: 15s
    static_configs:
      - targets: ['electric:9090']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'electric_.*'
        action: keep
```

### Key Metrics

| Metric                           | Type    | Description                          |
| -------------------------------- | ------- | ------------------------------------ |
| `electric_shapes_active`         | Gauge   | Number of active shapes being served |
| `electric_connections_active`    | Gauge   | Number of active client connections  |
| `electric_replication_lag_bytes` | Gauge   | Replication slot lag in bytes        |
| `electric_rows_streamed_total`   | Counter | Total rows streamed to clients       |
| `electric_shape_creation_total`  | Counter | Total shapes created                 |

## Alerting Patterns

### Prometheus Alerting Rules

```yaml
groups:
  - name: electric_alerts
    rules:
      - alert: ElectricDown
        expr: up{job="electric"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: 'Electric instance is down'

      - alert: HighReplicationLag
        expr: electric_replication_lag_bytes > 104857600
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'Replication lag exceeds 100MB'
          description: 'WAL lag is {{ $value | humanize1024 }}B'

      - alert: ConnectionSpike
        expr: |
          electric_connections_active
            > 2 * avg_over_time(electric_connections_active[1h])
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'Connection count spike detected'

      - alert: NoActiveShapes
        expr: electric_shapes_active == 0
        for: 10m
        labels:
          severity: info
        annotations:
          summary: 'No active shapes for 10 minutes'

      - alert: HighShapeCreationRate
        expr: rate(electric_shape_creation_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'Shapes being created at unusually high rate'
```

## Stalled Sync Detection

### Server-Side: Replication Slot Monitoring

```sql
SELECT
  slot_name,
  active,
  pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size,
  pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots
WHERE slot_name LIKE 'electric_%';
```

### WAL Retention Check

```sql
SELECT
  slot_name,
  wal_status,
  safe_wal_size,
  pg_size_pretty(
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)
  ) AS unconfirmed_lag
FROM pg_replication_slots
WHERE slot_name LIKE 'electric_%'
  AND wal_status != 'reserved';
```

### Automated Lag Monitoring Script

```bash
#!/usr/bin/env bash
set -euo pipefail

THRESHOLD_BYTES=${LAG_THRESHOLD:-104857600}
DATABASE_URL=${DATABASE_URL:?DATABASE_URL required}

lag_bytes=$(psql "$DATABASE_URL" -t -A -c "
  SELECT COALESCE(
    MAX(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)),
    0
  )
  FROM pg_replication_slots
  WHERE slot_name LIKE 'electric_%';
")

if [ "$lag_bytes" -gt "$THRESHOLD_BYTES" ]; then
  echo "ALERT: Replication lag is ${lag_bytes} bytes (threshold: ${THRESHOLD_BYTES})"
  exit 1
fi

echo "OK: Replication lag is ${lag_bytes} bytes"
```

## Debugging Sync Issues

### Common Failure Modes

| Failure                       | Symptoms                                          | Resolution                                                           |
| ----------------------------- | ------------------------------------------------- | -------------------------------------------------------------------- |
| Replication slot deleted      | Electric fails to start, logs show slot errors    | Restart Electric to recreate the slot                                |
| WAL retention exceeded        | Postgres disk fills up, `wal_status` shows `lost` | Increase `max_slot_wal_keep_size`, restart Electric                  |
| Schema change breaking shapes | Clients receive error responses, shapes restart   | Clients reconnect automatically; clear stale client caches if needed |
| Connection pool exhaustion    | Intermittent 503 errors from Electric             | Increase `ELECTRIC_DB_POOL_SIZE`, check for connection leaks         |
| Postgres max connections      | Electric cannot connect to Postgres               | Increase `max_connections` in Postgres or use PgBouncer              |

### Diagnostic Checklist

```sql
-- 1. Check replication slots
SELECT slot_name, active, wal_status,
  pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
FROM pg_replication_slots;

-- 2. Check active replication connections
SELECT pid, application_name, state, sent_lsn, write_lsn, flush_lsn, replay_lsn
FROM pg_stat_replication;

-- 3. Check Postgres connection count
SELECT count(*) AS total_connections,
  count(*) FILTER (WHERE application_name LIKE 'electric%') AS electric_connections
FROM pg_stat_activity;

-- 4. Check WAL generation rate
SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')) AS total_wal;
```

## Log Levels

Configure with `ELECTRIC_LOG_LEVEL`:

| Level     | Shows                                 | Use Case                     |
| --------- | ------------------------------------- | ---------------------------- |
| `error`   | Errors only                           | Production (quiet)           |
| `warning` | Errors + warnings                     | Production (recommended)     |
| `info`    | Startup, connections, shape lifecycle | Staging                      |
| `debug`   | Detailed internal operations          | Development, troubleshooting |

```yaml
services:
  electric:
    environment:
      ELECTRIC_LOG_LEVEL: warning
```

## Production Monitoring Checklist

| What to Monitor       | How                                      | Alert Threshold             |
| --------------------- | ---------------------------------------- | --------------------------- |
| Electric health       | `GET /v1/health`                         | Down for > 2 minutes        |
| Replication lag       | `pg_replication_slots` query             | > 100MB or growing steadily |
| Active connections    | Prometheus `electric_connections_active` | > 2x normal baseline        |
| Active shapes         | Prometheus `electric_shapes_active`      | Sudden drop to 0            |
| Postgres connections  | `pg_stat_activity` count                 | > 80% of `max_connections`  |
| Disk usage            | OS-level monitoring                      | > 80% capacity              |
| WAL disk usage        | `pg_wal_lsn_diff`                        | > 1GB unconfirmed           |
| Client sync freshness | Client-side `lastSyncedAt`               | Stale > 30 seconds          |
| Shape error rate      | Proxy access logs                        | > 1% error responses        |
| Memory usage          | Container metrics                        | > 80% of limit              |
