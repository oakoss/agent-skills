---
title: Use Cache Patterns
description: Preventing data drift with the Next.js use cache directive, React 19 use() hook for deterministic hydration, and server-to-client data bridges
tags:
  [
    use-cache,
    data-drift,
    deterministic-hydration,
    use-hook,
    nextjs,
    server-components,
  ]
---

# Use Cache Patterns

Data drift occurs when data fetched on the server changes by the time the client hydrates. The Next.js `'use cache'` directive and React 19 `use()` hook work together to eliminate this class of hydration errors.

## The Problem: Data Drift

Without caching, the server renders with data at time T1, but the client hydrates at time T2 when the data may have changed. This causes hydration mismatches even though the code is correct.

**Common drift sources:**

- Real-time data (stock prices, counters, notifications)
- Time-dependent formatting (relative timestamps like "2 minutes ago")
- Session-dependent content (user name, avatar loaded asynchronously)
- A/B test variants resolved at different times

## Next.js use cache Directive

The `'use cache'` directive caches the return value of async functions and components. The cached result is embedded in the server-rendered payload, ensuring the client uses the exact same data.

### Enabling use cache

```ts
// next.config.ts
const nextConfig = {
  experimental: {
    cacheComponents: true,
  },
};

export default nextConfig;
```

### Caching a Data Fetcher

```tsx
async function getProductData(id: string) {
  'use cache';
  const product = await db.product.findUnique({ where: { id } });
  return product;
}
```

Arguments automatically become part of the cache key, so different inputs produce separate cache entries.

### Cache Variants

| Directive              | Storage              | Use Case                                       |
| ---------------------- | -------------------- | ---------------------------------------------- |
| `'use cache'`          | In-memory (server)   | Default; fast for typical data                 |
| `'use cache: remote'`  | External cache store | Durable caching across deployments             |
| `'use cache: private'` | Browser memory only  | Personalized data with `cookies()`/`headers()` |

### Controlling Cache Lifetime

```tsx
import { cacheLife } from 'next/cache';

async function getProductData(id: string) {
  'use cache';
  cacheLife('hours');
  return await db.product.findUnique({ where: { id } });
}
```

Built-in profiles: `'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, `'max'`.

### Cache Revalidation

```tsx
import { cacheTag } from 'next/cache';
import { revalidateTag } from 'next/cache';

async function getProductData(id: string) {
  'use cache';
  cacheTag(`product-${id}`);
  return await db.product.findUnique({ where: { id } });
}

// In a mutation or webhook handler
async function updateProduct(id: string) {
  'use server';
  await db.product.update({ where: { id }, data: { ... } });
  revalidateTag(`product-${id}`);
}
```

## React 19 use() Hook

The `use()` API reads the value of a Promise or context. Unlike other hooks, `use()` can be called inside conditionals and loops.

### Server-to-Client Data Bridge

Pass a Promise from a Server Component to a Client Component. The client resolves it via `use()` without re-fetching.

```tsx
// Server Component
import { Suspense } from 'react';
import { getProductData } from './data';
import { ProductDetail } from './ProductDetail';

export default function ProductPage({ params }: { params: { id: string } }) {
  const dataPromise = getProductData(params.id);

  return (
    <Suspense fallback={<ProductSkeleton />}>
      <ProductDetail dataPromise={dataPromise} />
    </Suspense>
  );
}
```

```tsx
// Client Component
'use client';

import { use } from 'react';

export function ProductDetail({
  dataPromise,
}: {
  dataPromise: Promise<Product>;
}) {
  const product = use(dataPromise);

  return (
    <article>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <span>{formatPrice(product.price)}</span>
    </article>
  );
}
```

**Why this prevents hydration mismatches:** The Promise created on the server is serialized into the HTML payload. The client `use()` call resolves the same data, producing identical output.

### use() vs useEffect + useState

```tsx
// LEGACY: Double-fetch pattern (causes hydration mismatch)
function LegacyProduct({ id }: { id: string }) {
  const [data, setData] = useState<Product | null>(null);

  useEffect(() => {
    fetchProduct(id).then(setData);
  }, [id]);

  if (!data) return <Skeleton />;
  return <ProductView product={data} />;
}

// MODERN: Deterministic bridge via use() (zero mismatch)
function ModernProduct({ dataPromise }: { dataPromise: Promise<Product> }) {
  const data = use(dataPromise);
  return <ProductView product={data} />;
}
```

### Error Handling with use()

`use()` cannot be called in a try-catch block. Use Error Boundaries or Promise `.catch()`:

```tsx
// Option 1: Error Boundary
import { ErrorBoundary } from 'react-error-boundary';

function ProductPage({ dataPromise }: { dataPromise: Promise<Product> }) {
  return (
    <ErrorBoundary fallback={<ProductError />}>
      <Suspense fallback={<ProductSkeleton />}>
        <ProductDetail dataPromise={dataPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}

// Option 2: Promise .catch() for fallback value
function ProductDetail({ dataPromise }: { dataPromise: Promise<Product> }) {
  const safePromise = dataPromise.catch(() => DEFAULT_PRODUCT);
  const product = use(safePromise);
  return <ProductView product={product} />;
}
```

### Limitations of use() with Promises

- Promises created inside Client Components are not yet supported (only via frameworks or Suspense-compatible libraries)
- Pass Promises from Server Components to Client Components for the intended pattern
- `use()` integrates with Suspense; the parent must have a Suspense boundary

## Complete Hydration-Safe Pattern

Combining `'use cache'`, `use()`, and `Suspense` for a fully resilient component:

```tsx
// data.ts (Server)
async function getDashboardData(userId: string) {
  'use cache';
  cacheTag(`dashboard-${userId}`);
  return {
    userName: await fetchName(userId),
    stats: await fetchStats(userId),
  };
}

// DashboardPage.tsx (Server Component)
import { Suspense } from 'react';

export default function DashboardPage({ userId }: { userId: string }) {
  const dataPromise = getDashboardData(userId);

  return (
    <section>
      <h2>Dashboard</h2>
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardContent dataPromise={dataPromise} />
      </Suspense>
    </section>
  );
}

// DashboardContent.tsx (Client Component)
('use client');

import { use } from 'react';

export function DashboardContent({
  dataPromise,
}: {
  dataPromise: Promise<DashboardData>;
}) {
  const data = use(dataPromise);

  return (
    <div>
      <span>Welcome back, {data.userName}</span>
      <StatsGrid stats={data.stats} />
    </div>
  );
}
```

## Cache Payload Considerations

- **Audit payload size** to ensure cached data does not bloat the initial HTML document
- **Cache only fields** needed for the initial render, not entire database rows
- **Set appropriate TTL** based on data freshness requirements via `cacheLife`
- **Use `cacheTag`** for on-demand revalidation when data changes

## Troubleshooting

| Issue                           | Likely Cause                         | Corrective Action                                 |
| ------------------------------- | ------------------------------------ | ------------------------------------------------- |
| Data still mismatches           | `'use cache'` not applied to fetcher | Verify the directive is inside the async function |
| Large initial HTML payload      | Too much data cached                 | Cache only fields needed for initial render       |
| Stale data after mutation       | No revalidation configured           | Use `cacheTag` and `revalidateTag`                |
| `use()` throws during hydration | Promise rejected on server           | Add Error Boundary around the consuming component |
| `use()` suspends indefinitely   | No Suspense boundary above           | Wrap in `<Suspense fallback={...}>`               |
