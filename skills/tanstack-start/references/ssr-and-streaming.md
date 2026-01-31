---
title: SSR and Streaming
description: Streaming SSR with Suspense boundaries, ensureQueryData vs prefetchQuery, static prerendering, ISR with cache-control, hybrid rendering strategies, error boundaries, and hydration safety
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
    headers,
    ErrorBoundary,
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

- `ensureQueryData()` -- blocks SSR until data is ready (above-the-fold content)
- `prefetchQuery()` -- starts fetch but streams when ready (below-the-fold content)

## Error Boundaries with Streaming

Each streamed section can handle its own errors independently:

```tsx
function DashboardPage() {
  return (
    <div>
      <Header />
      <ErrorBoundary fallback={<StatsError />}>
        <Suspense fallback={<StatsSkeleton />}>
          <DashboardStats />
        </Suspense>
      </ErrorBoundary>
      <ErrorBoundary fallback={<ActivityError />}>
        <Suspense fallback={<ActivitySkeleton />}>
          <RecentActivity />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}
```

## Progressive Enhancement

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    await queryClient.ensureQueryData(postQueries.detail(params.postId));
    queryClient.prefetchQuery(commentQueries.forPost(params.postId));
    queryClient.prefetchQuery(postQueries.related(params.postId));
  },
  component: PostPage,
});

function PostPage() {
  const { postId } = Route.useParams();
  const { data: post } = useSuspenseQuery(postQueries.detail(postId));

  return (
    <article>
      <PostHeader post={post} />
      <PostContent content={post.content} />
      <Suspense fallback={<CommentsSkeleton />}>
        <CommentsSection postId={postId} />
      </Suspense>
      <Suspense fallback={<RelatedSkeleton />}>
        <RelatedPosts postId={postId} />
      </Suspense>
    </article>
  );
}
```

## Fallback Content Strategies

Design fallbacks that match the final content structure to minimize layout shift:

```tsx
function CommentsSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="border rounded-lg p-4">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
          <div className="h-3 bg-gray-200 rounded w-full mb-1" />
          <div className="h-3 bg-gray-200 rounded w-5/6" />
        </div>
      ))}
    </div>
  );
}

function StatsCard({ stat }: { stat?: { label: string; value: number } }) {
  if (!stat) {
    return (
      <div className="border rounded-lg p-6">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4" />
        <div className="h-10 bg-gray-200 rounded w-3/4" />
      </div>
    );
  }

  return (
    <div className="border rounded-lg p-6">
      <h3 className="text-lg font-medium mb-2">{stat.label}</h3>
      <p className="text-3xl font-bold">{stat.value.toLocaleString()}</p>
    </div>
  );
}
```

## Nested Suspense for Granular Streaming

```tsx
function DashboardPage() {
  const { data: user } = useSuspenseQuery(userQueries.profile());

  return (
    <div>
      <Header user={user} />
      <div className="grid grid-cols-3 gap-4">
        <Suspense fallback={<StatsCard />}>
          <StatsCard1 />
        </Suspense>
        <Suspense fallback={<StatsCard />}>
          <StatsCard2 />
        </Suspense>
        <Suspense fallback={<StatsCard />}>
          <StatsCard3 />
        </Suspense>
      </div>
      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```

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

For client-only features, use lazy loading or `useEffect`:

```tsx
import { lazy, Suspense } from 'react';

const ClientOnlyMap = lazy(() => import('./Map'));

function LocationPage() {
  return (
    <Suspense fallback={<MapPlaceholder />}>
      <ClientOnlyMap />
    </Suspense>
  );
}
```

| Mismatch Cause              | Solution                              |
| --------------------------- | ------------------------------------- |
| `Date.now()` / `new Date()` | Pass timestamp from loader            |
| `Math.random()`             | Generate on server, pass to client    |
| `window` / `document`       | Use `useEffect` or lazy loading       |
| User timezone               | Use UTC or client-only formatting     |
| Browser-specific APIs       | Check `typeof window !== 'undefined'` |
| Extension-injected content  | Use `suppressHydrationWarning`        |
