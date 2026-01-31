---
title: SSR and Hydration
description: Server-side rendering with prefetchQuery, HydrationBoundary, dehydrate, useSuspenseQuery, and router integration
tags:
  [
    SSR,
    hydration,
    prefetchQuery,
    dehydrate,
    HydrationBoundary,
    useSuspenseQuery,
    server-rendering,
  ]
---

# SSR and Hydration

Create `QueryClient` per request. Prefetch on server, wrap with `HydrationBoundary`:

```tsx
const queryClient = new QueryClient();
await queryClient.prefetchQuery(todosQueryOptions);

<HydrationBoundary state={dehydrate(queryClient)}>
  <Todos />
</HydrationBoundary>;
```

Use `useSuspenseQuery` (not `useQuery`) for SSR to avoid hydration mismatches from conditional `isLoading` rendering.

## Router Integration: Cache-First Resolution

Return cached data immediately, only fetch if cache is empty:

```tsx
export const Route = createFileRoute('/posts/$id')({
  loader: async ({ context, params }) => {
    const { queryClient } = context;
    const options = postOptions(params.id);

    return (
      queryClient.getQueryData(options.queryKey) ??
      (await queryClient.fetchQuery(options))
    );
  },
});
```

## Await as a Control Lever

Control navigation behavior:

```tsx
export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    // WITH await: Block navigation until data loads
    await context.queryClient.ensureQueryData(postsOptions());

    // WITHOUT await: Navigate immediately, show loading state
    context.queryClient.prefetchQuery(recommendationsOptions());
  },
});
```

## React 19 Suspense Considerations

React 19 no longer pre-renders siblings when one suspends -- causes sequential waterfalls:

```tsx
// These fetch sequentially in React 19 (waterfall)
<Suspense fallback={<Loading />}>
  <Posts /> {/* Suspends first */}
  <Comments /> {/* Waits for Posts to complete */}
</Suspense>
```

**Solution:** Prefetch in loaders to avoid waterfalls:

```tsx
export const Route = createFileRoute('/dashboard')({
  loader: async ({ context: { queryClient } }) => {
    await Promise.all([
      queryClient.prefetchQuery(postsOptions()),
      queryClient.prefetchQuery(commentsOptions()),
    ]);
  },
});

function Dashboard() {
  const posts = useSuspenseQuery(postsOptions());
  const comments = useSuspenseQuery(commentsOptions());
}
```

**Alternative:** Use `useSuspenseQueries` for parallel fetching within components:

```tsx
function Dashboard() {
  const [posts, comments] = useSuspenseQueries({
    queries: [
      { queryKey: ['posts'], queryFn: fetchPosts },
      { queryKey: ['comments'], queryFn: fetchComments },
    ],
  });
  // Both fetch in parallel, no waterfall
}
```

**Key principle:** Decouple data fetching from rendering. Initiate fetches in loaders, or use `useSuspenseQueries` for parallel fetching in components.
