---
title: SSR and Streaming
description: Streaming SSR with Suspense boundaries, ensureQueryData vs prefetchQuery, static prerendering, ISR with cache-control, hybrid rendering strategies, and hydration safety
tags:
  [
    SSR,
    streaming,
    Suspense,
    ensureQueryData,
    prefetchQuery,
    prerender,
    ISR,
    cache-control,
    hydration,
    setHeaders,
  ]
---

# SSR and Streaming

## Streaming SSR with Suspense

```ts
export const Route = createFileRoute('/dashboard')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(userQueries.profile());
    queryClient.prefetchQuery(dashboardQueries.stats());
    queryClient.prefetchQuery(activityQueries.recent());
  },
  component: DashboardPage,
});

function DashboardPage() {
  const { data: user } = useSuspenseQuery(userQueries.profile());
  return (
    <div>
      <Header user={user} />
      <Suspense fallback={<StatsSkeleton />}>
        <DashboardStats />
      </Suspense>
      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```

- `ensureQueryData()` — blocks SSR until data is ready (above-the-fold content)
- `prefetchQuery()` — starts fetch but streams when ready (below-the-fold content)

## Static Prerendering

```ts
// vite.config.ts
export default defineConfig({
  server: {
    prerender: {
      routes: ['/', '/about', '/contact', '/pricing'],
      crawlLinks: true,
    },
  },
});
```

Dynamic route generation:

```ts
export default defineConfig({
  server: {
    prerender: {
      routes: async () => {
        const posts = await db.posts.findMany({
          where: { published: true },
          select: { slug: true },
        });
        return ['/', '/blog', ...posts.map((p) => `/blog/${p.slug}`)];
      },
    },
  },
});
```

## ISR with Cache-Control

Use the `headers` property on the route definition:

```ts
export const Route = createFileRoute('/blog/$slug')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.slug);
    return { post };
  },
  headers: () => ({
    'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
  }),
});
```

### Cache-Control Directives

| Directive                  | Meaning                            |
| -------------------------- | ---------------------------------- |
| `s-maxage=N`               | CDN cache duration (seconds)       |
| `max-age=N`                | Browser cache duration             |
| `stale-while-revalidate=N` | Serve stale while fetching fresh   |
| `private`                  | Don't cache on CDN (user-specific) |
| `no-store`                 | Never cache                        |

## Hybrid Static/Dynamic Strategy

```ts
// Static page (prerendered at build)
export const Route = createFileRoute('/products')({
  loader: async () => {
    const featured = await fetchFeaturedProducts();
    return { featured };
  },
});

// ISR page (cached 5 minutes)
export const Route = createFileRoute('/products/$productId')({
  loader: async ({ params }) => {
    const product = await fetchProduct(params.productId);
    if (!product) throw notFound();
    return { product };
  },
  headers: () => ({
    'Cache-Control': 'public, max-age=300, stale-while-revalidate=600',
  }),
});

// Always SSR (user-specific)
export const Route = createFileRoute('/cart')({
  loader: async ({ context }) => {
    const cart = await fetchUserCart(context.user.id);
    return { cart };
  },
  headers: () => ({
    'Cache-Control': 'private, no-store',
  }),
});
```

## Hydration Safety

Prevent mismatches by passing dynamic data from loaders:

```ts
export const Route = createFileRoute('/dashboard')({
  loader: async () => ({ generatedAt: Date.now() }),
  component: Dashboard,
});

function Dashboard() {
  const { generatedAt } = Route.useLoaderData();
  return <span>Generated at: {generatedAt}</span>;
}
```

| Mismatch Cause              | Solution                              |
| --------------------------- | ------------------------------------- |
| `Date.now()` / `new Date()` | Pass timestamp from loader            |
| `Math.random()`             | Generate on server, pass to client    |
| `window` / `document`       | Use `useEffect` or lazy loading       |
| User timezone               | Use UTC or client-only formatting     |
| Browser-specific APIs       | Check `typeof window !== 'undefined'` |
