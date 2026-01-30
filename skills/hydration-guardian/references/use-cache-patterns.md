---
title: Use Cache Patterns
description: Preventing data drift with the @use cache directive and React use() hook for deterministic hydration in Next.js
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

Data drift occurs when the data fetched on the server changes by the time the client tries to hydrate (a stock price update, a new comment appearing, a counter incrementing). The `@use cache` directive eliminates this class of hydration errors.

## The Problem: Data Drift

Without caching, the server renders with data at time T1, but the client hydrates at time T2 when the data may have changed. This causes hydration mismatches even though the code is correct.

**Common drift sources:**

- Real-time data (stock prices, counters, notifications)
- Time-dependent formatting (relative timestamps like "2 minutes ago")
- Session-dependent content (user name, avatar that loads asynchronously)
- A/B test variants resolved at different times

## The Solution: @use cache Directive

Next.js `@use cache` caches a specific data-fetching promise and shares its exact result between server and client during the hydration window.

```tsx
'use server';

async function getStableProductData(id: string) {
  'use cache';
  const product = await db.product.findUnique({ where: { id } });
  return product;
}
```

The cached result is embedded in the server-rendered HTML payload, so the client uses the exact same data without re-fetching.

## Consuming with the use() Hook

```tsx
import { Suspense, use } from 'react';
import { getStableProductData } from './data-actions';

export default function ProductPage({ id }: { id: string }) {
  const dataPromise = getStableProductData(id);

  return (
    <Suspense fallback={<ProductSkeleton />}>
      <ProductDetail dataPromise={dataPromise} />
    </Suspense>
  );
}

function ProductDetail({ dataPromise }: { dataPromise: Promise<Product> }) {
  const data = use(dataPromise);

  return (
    <article>
      <h1>{data.name}</h1>
      <p>{data.description}</p>
      <span>{formatPrice(data.price)}</span>
    </article>
  );
}
```

## Complete Hydration-Safe Component

Combining `@use cache`, `use()`, `Suspense`, and `Pausable` for a fully resilient component:

```tsx
import { Pausable, Suspense, use } from 'react';

async function getHydrationData(userId: string) {
  'use cache';
  return {
    timestamp: Date.now(),
    userName: await fetchName(userId),
  };
}

export default function ResilientWidget({ userId }: { userId: string }) {
  const dataPromise = getHydrationData(userId);

  return (
    <section>
      <h2>User Dashboard</h2>
      <Suspense fallback={<Skeleton />}>
        <DashboardContent dataPromise={dataPromise} />
      </Suspense>
    </section>
  );
}

function DashboardContent({
  dataPromise,
}: {
  dataPromise: Promise<DashboardData>;
}) {
  const data = use(dataPromise);

  return (
    <Pausable fallback={<div>Initializing locale...</div>}>
      <div>
        <span>Welcome back, {data.userName}</span>
        <span>{getLocalizedTime(data.timestamp)}</span>
      </div>
    </Pausable>
  );
}
```

## Benefits

| Benefit                   | Description                                                           |
| ------------------------- | --------------------------------------------------------------------- |
| Zero data drift           | Client guaranteed to see exactly what the server rendered             |
| No double fetch           | Client uses payload embedded in HTML; no re-fetch needed              |
| Automatic synchronization | Next.js handles cache re-validation seamlessly when cache expires     |
| Reduced API load          | Eliminates "hydration fetch" pattern, reducing API calls by up to 40% |

## use() vs useEffect + useState

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

// MODERN: Deterministic bridge (zero mismatch)
function ModernProduct({ dataPromise }: { dataPromise: Promise<Product> }) {
  const data = use(dataPromise);
  return <ProductView product={data} />;
}
```

The `use()` hook consumes the exact promise result from the server, ensuring the client renders identical content.

## Cache Payload Considerations

- **Audit payload size** to ensure cached data does not bloat the initial HTML document
- **Prefer** `@use cache` for data rendered in the initial viewport
- **Avoid** caching large datasets; cache only the fields needed for the initial render
- **Set appropriate TTL** based on data freshness requirements

## Troubleshooting

| Issue                           | Likely Cause                         | Corrective Action                                 |
| ------------------------------- | ------------------------------------ | ------------------------------------------------- |
| Data still mismatches           | `'use cache'` not applied to fetcher | Verify the directive is inside the async function |
| Large initial HTML payload      | Too much data cached                 | Cache only fields needed for initial render       |
| Stale data after cache expiry   | No re-validation configured          | Configure cache TTL and re-validation strategy    |
| `use()` throws during hydration | Promise rejected on server           | Add error boundary around the consuming component |
