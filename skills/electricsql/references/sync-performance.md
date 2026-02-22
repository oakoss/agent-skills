---
title: Sync Performance
description: Performance optimization for ElectricSQL sync including initial sync tuning, progressive loading, memory management, bandwidth optimization, caching, and benchmarking
tags:
  [
    performance,
    sync,
    initial-sync,
    progressive-loading,
    pagination,
    checkpoint,
    memory,
    bandwidth,
    cache,
    benchmark,
    columns,
    where-clause,
    web-worker,
    batch,
    SSE,
  ]
---

## Initial Sync Optimization

### Measuring First-Sync Time

```ts
import { ShapeStream } from '@electric-sql/client';

function measureInitialSync(
  url: string,
  params: Record<string, string>,
): Promise<{
  durationMs: number;
  rowCount: number;
  bytesReceived: number;
}> {
  return new Promise((resolve) => {
    const start = performance.now();
    let rowCount = 0;
    let bytesReceived = 0;

    const stream = new ShapeStream({ url, params });

    stream.subscribe((messages) => {
      for (const msg of messages) {
        if (msg.headers.operation) {
          rowCount++;
          bytesReceived += JSON.stringify(msg.value).length;
        }
        if (msg.headers.control === 'up-to-date') {
          resolve({
            durationMs: Math.round(performance.now() - start),
            rowCount,
            bytesReceived,
          });
        }
      }
    });
  });
}

const stats = await measureInitialSync('http://localhost:3000/v1/shape', {
  table: 'orders',
});

console.log(`Initial sync: ${stats.rowCount} rows in ${stats.durationMs}ms`);
console.log(
  `Throughput: ${Math.round(stats.rowCount / (stats.durationMs / 1000))} rows/sec`,
);
console.log(`Transfer: ${(stats.bytesReceived / 1024).toFixed(1)} KB`);
```

### Column Selection to Reduce Payload

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'orders',
    columns: 'id,status,total,created_at',
  },
});
```

| Approach      | Columns Synced | Typical Payload Reduction |
| ------------- | -------------- | ------------------------- |
| All columns   | `*`            | Baseline                  |
| List view     | 4-6 columns    | 40-60%                    |
| Summary/count | 2-3 columns    | 70-80%                    |

### Where Clauses to Limit Rows

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'orders',
    where: "status IN ('pending','processing') AND created_at > '2025-01-01'",
  },
});
```

### Changes-Only Mode

Skip the full initial snapshot when local state already exists from a previous session:

```ts
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'orders' },
  offset: 'now',
});
```

## Progressive Loading Strategy

### Small Initial Dataset with Background Sync

```ts
import { Shape, ShapeStream } from '@electric-sql/client';

type Order = {
  id: string;
  status: string;
  total: number;
  created_at: string;
};

function createProgressiveLoader(url: string) {
  let isFullySynced = false;

  const recentStream = new ShapeStream<Order>({
    url,
    params: {
      table: 'orders',
      where: "created_at > NOW() - INTERVAL '7 days'",
      columns: 'id,status,total,created_at',
    },
  });

  const recentShape = new Shape(recentStream);

  recentShape.subscribe(() => {
    if (!isFullySynced) {
      startBackgroundSync();
    }
  });

  function startBackgroundSync() {
    const fullStream = new ShapeStream<Order>({
      url,
      params: {
        table: 'orders',
        columns: 'id,status,total,created_at',
      },
    });

    const fullShape = new Shape(fullStream);

    fullShape.subscribe((data) => {
      if (data.size > 0) {
        isFullySynced = true;
      }
    });
  }

  return {
    recentShape,
    get isFullySynced() {
      return isFullySynced;
    },
  };
}
```

### UI with Loading Indicator

```tsx
import { useShape } from '@electric-sql/react';

type Order = { id: string; status: string; total: number; created_at: string };

function OrderList() {
  const recent = useShape<Order>({
    url: 'http://localhost:3000/v1/shape',
    params: {
      table: 'orders',
      where: "created_at > NOW() - INTERVAL '7 days'",
      columns: 'id,status,total,created_at',
    },
  });

  const full = useShape<Order>({
    url: 'http://localhost:3000/v1/shape',
    params: {
      table: 'orders',
      columns: 'id,status,total,created_at',
    },
  });

  const data = full.isLoading ? recent.data : full.data;
  const showingPartial = full.isLoading && !recent.isLoading;

  if (recent.isLoading) return <div>Loading orders...</div>;

  return (
    <div>
      {showingPartial ? (
        <p>Showing recent orders. Loading full history...</p>
      ) : null}
      <ul>
        {data.map((order) => (
          <li key={order.id}>
            {order.status} - ${order.total}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Large Dataset Handling

### Multiple Shapes for Pagination

```ts
import { Shape, ShapeStream } from '@electric-sql/client';

function createPagedShapes<T extends Record<string, unknown>>(
  url: string,
  table: string,
  pageSize: number,
  totalPages: number,
): Array<Shape<T>> {
  return Array.from({ length: totalPages }, (_, i) => {
    const stream = new ShapeStream<T>({
      url,
      params: {
        table,
        where: `row_number >= ${i * pageSize} AND row_number < ${(i + 1) * pageSize}`,
      },
    });
    return new Shape(stream);
  });
}
```

### Splitting by Partition Key

```ts
const statusShapes = {
  active: new ShapeStream({
    url: 'http://localhost:3000/v1/shape',
    params: { table: 'orders', where: "status = 'active'" },
  }),
  completed: new ShapeStream({
    url: 'http://localhost:3000/v1/shape',
    params: { table: 'orders', where: "status = 'completed'" },
  }),
  archived: new ShapeStream({
    url: 'http://localhost:3000/v1/shape',
    params: { table: 'orders', where: "status = 'archived'" },
  }),
};
```

## Checkpoint Resumption

Electric handles reconnection using offset-based resumption. Store the last offset to avoid re-fetching everything on restart.

```ts
import { ShapeStream } from '@electric-sql/client';

function createResumableStream(
  url: string,
  params: Record<string, string>,
  storageKey: string,
) {
  const stored = localStorage.getItem(storageKey);
  const checkpoint = stored ? JSON.parse(stored) : null;

  const streamParams: Record<string, string> = { ...params };

  const stream = new ShapeStream({
    url,
    params: streamParams,
    offset: checkpoint?.offset,
    handle: checkpoint?.handle,
  });

  stream.subscribe((messages) => {
    for (const msg of messages) {
      if (msg.headers.control === 'up-to-date' && msg.offset) {
        localStorage.setItem(
          storageKey,
          JSON.stringify({ offset: msg.offset, handle: stream.handle }),
        );
      }
    }
  });

  return stream;
}

const stream = createResumableStream(
  'http://localhost:3000/v1/shape',
  { table: 'orders' },
  'orders-checkpoint',
);
```

## Memory Management

### Garbage Collecting Stale Shape Data

```ts
import { Shape, ShapeStream } from '@electric-sql/client';

class ManagedShapePool {
  private shapes = new Map<
    string,
    {
      shape: Shape<Record<string, unknown>>;
      stream: ShapeStream;
      lastAccess: number;
    }
  >();

  get<T extends Record<string, unknown>>(
    key: string,
    url: string,
    params: Record<string, string>,
  ): Shape<T> {
    const existing = this.shapes.get(key);
    if (existing) {
      existing.lastAccess = Date.now();
      return existing.shape as Shape<T>;
    }

    const stream = new ShapeStream<T>({ url, params });
    const shape = new Shape(stream);

    this.shapes.set(key, {
      shape: shape as Shape<Record<string, unknown>>,
      stream,
      lastAccess: Date.now(),
    });
    return shape;
  }

  cleanup(maxAgeMs: number): void {
    const now = Date.now();
    for (const [key, entry] of this.shapes) {
      if (now - entry.lastAccess > maxAgeMs) {
        this.shapes.delete(key);
      }
    }
  }
}

const pool = new ManagedShapePool();

setInterval(() => {
  pool.cleanup(5 * 60 * 1000);
}, 60 * 1000);
```

### Web Worker Offloading

```ts
const workerCode = `
  self.onmessage = async (event) => {
    const { url, params } = event.data;
    const query = new URLSearchParams(params).toString();
    const response = await fetch(url + '/v1/shape?' + query + '&offset=-1');
    const messages = await response.json();

    const rows = messages
      .filter(m => m.headers?.operation === 'insert')
      .map(m => m.value);

    self.postMessage({ rows, count: rows.length });
  };
`;

function syncInWorker(
  url: string,
  params: Record<string, string>,
): Promise<{ rows: Record<string, unknown>[]; count: number }> {
  return new Promise((resolve) => {
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    const worker = new Worker(URL.createObjectURL(blob));

    worker.onmessage = (event) => {
      resolve(event.data);
      worker.terminate();
    };

    worker.postMessage({ url, params });
  });
}
```

## Bandwidth Optimization

### Full vs Default Replica Mode

| Mode      | Update Message Contains     | Transfer Size | Use Case                       |
| --------- | --------------------------- | ------------- | ------------------------------ |
| `default` | Only changed columns        | Smaller       | Most applications              |
| `full`    | All columns on every change | Larger        | When full row needed on update |

```ts
const defaultStream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'orders' },
});

const fullStream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'orders', replica: 'full' },
});
```

## Measuring Sync Performance

### Comprehensive Sync Monitor

```ts
type SyncMetrics = {
  initialSyncMs: number;
  rowCount: number;
  bytesReceived: number;
  rowsPerSecond: number;
  avgMessageSize: number;
  lastSyncedAt: Date | null;
  updatesReceived: number;
};

class SyncMonitor {
  private metrics: SyncMetrics = {
    initialSyncMs: 0,
    rowCount: 0,
    bytesReceived: 0,
    rowsPerSecond: 0,
    avgMessageSize: 0,
    lastSyncedAt: null,
    updatesReceived: 0,
  };
  private startTime = performance.now();
  private initialSyncComplete = false;

  onMessage(
    messages: Array<{ headers: Record<string, string>; value?: unknown }>,
  ): void {
    for (const msg of messages) {
      if (msg.headers.operation) {
        this.metrics.rowCount++;
        const size = JSON.stringify(msg.value).length;
        this.metrics.bytesReceived += size;

        if (this.initialSyncComplete) {
          this.metrics.updatesReceived++;
        }
      }

      if (msg.headers.control === 'up-to-date') {
        if (!this.initialSyncComplete) {
          this.metrics.initialSyncMs = Math.round(
            performance.now() - this.startTime,
          );
          this.initialSyncComplete = true;
        }
        this.metrics.lastSyncedAt = new Date();
      }
    }

    this.metrics.rowsPerSecond = Math.round(
      this.metrics.rowCount / ((performance.now() - this.startTime) / 1000),
    );
    this.metrics.avgMessageSize =
      this.metrics.rowCount > 0
        ? Math.round(this.metrics.bytesReceived / this.metrics.rowCount)
        : 0;
  }

  getMetrics(): SyncMetrics {
    return { ...this.metrics };
  }

  report(): string {
    const m = this.metrics;
    return [
      `Initial sync: ${m.initialSyncMs}ms`,
      `Rows: ${m.rowCount}`,
      `Transfer: ${(m.bytesReceived / 1024).toFixed(1)} KB`,
      `Throughput: ${m.rowsPerSecond} rows/sec`,
      `Avg message: ${m.avgMessageSize} bytes`,
      `Live updates: ${m.updatesReceived}`,
      `Last sync: ${m.lastSyncedAt?.toISOString() ?? 'never'}`,
    ].join('\n');
  }
}

const monitor = new SyncMonitor();
const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'orders' },
});

stream.subscribe((messages) => {
  monitor.onMessage(
    messages as Array<{ headers: Record<string, string>; value?: unknown }>,
  );
});
```

## Batch Processing

### Debouncing UI Updates During Bulk Sync

```ts
function createBatchedSubscriber<T>(
  onBatch: (rows: Map<string, T>) => void,
  debounceMs = 16,
): (
  messages: Array<{ headers: Record<string, string>; key?: string; value?: T }>,
) => void {
  const buffer = new Map<string, T>();
  let frameId: number | null = null;

  return (messages) => {
    for (const msg of messages) {
      if (
        msg.headers.operation === 'insert' ||
        msg.headers.operation === 'update'
      ) {
        buffer.set(msg.key!, msg.value!);
      }
      if (msg.headers.operation === 'delete') {
        buffer.delete(msg.key!);
      }
    }

    if (frameId !== null) cancelAnimationFrame(frameId);

    frameId = requestAnimationFrame(() => {
      onBatch(new Map(buffer));
      frameId = null;
    });
  };
}

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: { table: 'orders' },
});

stream.subscribe(
  createBatchedSubscriber<Record<string, unknown>>((rows) => {
    console.log(`Batch update: ${rows.size} rows`);
  }),
);
```

## Caching

### Electric Cache Headers

Electric sets HTTP cache headers on shape responses to enable CDN and browser caching.

| Environment Variable       | Default | Description                            |
| -------------------------- | ------- | -------------------------------------- |
| `ELECTRIC_CACHE_MAX_AGE`   | 5       | Seconds a response is considered fresh |
| `ELECTRIC_CACHE_STALE_AGE` | 300     | Seconds a stale response can be served |

### CDN Configuration

```yaml
services:
  electric:
    image: electricsql/electric:latest
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/app
      ELECTRIC_CACHE_MAX_AGE: 10
      ELECTRIC_CACHE_STALE_AGE: 600
```

Place a CDN (CloudFront, Cloudflare, Fastly) in front of Electric. Shape responses include `Cache-Control` and `ETag` headers that CDNs respect automatically. Initial sync requests (`offset=-1`) are cached, reducing load on Electric for repeated requests from different clients.

```text
Client → CDN → Electric → Postgres
         ↑
    Cached initial sync responses
    served without hitting Electric
```

### Client-Side Cache Warm-Up

```ts
async function warmCache(
  url: string,
  shapes: Array<Record<string, string>>,
): Promise<void> {
  await Promise.all(
    shapes.map(async (params) => {
      const query = new URLSearchParams(params).toString();
      await fetch(`${url}/v1/shape?${query}&offset=-1`);
    }),
  );
}

await warmCache('http://localhost:3000', [
  { table: 'orders', where: "status = 'active'" },
  { table: 'products', columns: 'id,name,price' },
  { table: 'users', columns: 'id,name,email' },
]);
```

## Benchmarking Reference

Expected sync times vary based on row size, column count, network conditions, and whether responses are cached. These are rough baselines for a typical application with 5-10 columns per row on a low-latency connection.

| Row Count | Avg Row Size | Expected Initial Sync | Recommendation                        |
| --------- | ------------ | --------------------- | ------------------------------------- |
| 100       | 200 bytes    | < 100ms               | Single shape, no optimization needed  |
| 1,000     | 200 bytes    | 100-300ms             | Column selection recommended          |
| 10,000    | 200 bytes    | 500ms-2s              | Column selection + where clause       |
| 100,000   | 200 bytes    | 3-15s                 | Progressive loading, split shapes     |
| 100,000+  | 200 bytes    | 10s+                  | Pagination, Web Worker, cache warm-up |

### Quick Benchmark Utility

```ts
async function benchmarkShape(
  url: string,
  params: Record<string, string>,
  runs = 3,
): Promise<{ avgMs: number; minMs: number; maxMs: number; rows: number }> {
  const times: number[] = [];
  let rows = 0;

  for (let i = 0; i < runs; i++) {
    const start = performance.now();
    let count = 0;

    await new Promise<void>((resolve) => {
      const stream = new ShapeStream({ url, params });
      stream.subscribe((messages) => {
        for (const msg of messages) {
          if (msg.headers.operation) count++;
          if (msg.headers.control === 'up-to-date') resolve();
        }
      });
    });

    times.push(Math.round(performance.now() - start));
    rows = count;
  }

  return {
    avgMs: Math.round(times.reduce((a, b) => a + b, 0) / times.length),
    minMs: Math.min(...times),
    maxMs: Math.max(...times),
    rows,
  };
}

const result = await benchmarkShape('http://localhost:3000/v1/shape', {
  table: 'orders',
  columns: 'id,status,total,created_at',
});

console.log(
  `${result.rows} rows | avg: ${result.avgMs}ms | min: ${result.minMs}ms | max: ${result.maxMs}ms`,
);
```
