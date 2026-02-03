---
title: Caching Coordination
description: Single-source caching with Query, disabling Router cache, cache comparison, and coordinated configuration
tags:
  [
    caching,
    defaultPreloadStaleTime,
    staleTime,
    gcTime,
    dual-cache,
    coordination,
  ]
---

# Caching Coordination

## The Dual Caching Problem

When using TanStack Router with TanStack Query, both have their own cache. Running them simultaneously leads to confusion about which cache is authoritative and potentially different data in each.

```tsx
// Bad: Both Router and Query caching active
const router = createRouter({
  routeTree,
  context: { queryClient },
  // defaultPreloadStaleTime uses Router's default cache
});

// Good: Disable Router cache, let Query be single source
const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreloadStaleTime: 0,
});
```

## Cache Comparison

| Feature             | Router Cache      | Query Cache          |
| ------------------- | ----------------- | -------------------- |
| Invalidation        | Manual/time-based | Query keys, patterns |
| Background refetch  | No                | Yes                  |
| Optimistic updates  | No                | Yes                  |
| Mutations           | No built-in       | Full support         |
| DevTools            | Limited           | Rich debugging       |
| Cross-route sharing | Full              | Full                 |

## Coordinated Caching Configuration

```tsx
export function getRouter() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // Fresh for 1 minute
        gcTime: 10 * 60 * 1000, // Cache for 10 minutes
        refetchOnWindowFocus: true,
        retry: 1,
      },
    },
  });

  const router = createRouter({
    routeTree,
    context: { queryClient },
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0, // Router defers to Query
    scrollRestoration: true,
    defaultStructuralSharing: true,
  });

  setupRouterSsrQueryIntegration({
    router,
    queryClient,
  });

  return router;
}
```

## Preloading Still Works

```tsx
export function getRouter() {
  const queryClient = new QueryClient();

  const router = createRouter({
    routeTree,
    context: { queryClient },
    defaultPreload: 'intent', // Preload on hover
    defaultPreloadStaleTime: 0, // Query decides if data is stale
  });

  setupRouterSsrQueryIntegration({ router, queryClient });

  return router;
}

// When user hovers a Link:
// 1. Router triggers preload
// 2. Loader runs ensureQueryData
// 3. Query checks its cache - fresh? skip fetch. stale? refetch.
// 4. User clicks - data already in Query cache
```

## Mutation Invalidation with Single Cache

```tsx
const createPost = useMutation({
  mutationFn: submitPost,
  onSuccess: () => {
    // Invalidate Query cache - the single source
    queryClient.invalidateQueries({ queryKey: ['posts'] });

    // Router automatically uses updated cache on next navigation
    navigate({ to: '/posts' });
  },
});
```

## Single Source of Truth Rules

1. **Query owns the cache.** Never store server data in Zustand, Context, or component state alongside Query. If you need derived data, use `select` in the query hook.
2. **Disable Router cache.** Set `defaultPreloadStaleTime: 0` so Router always defers to Query for freshness decisions.
3. **One query key per entity.** Avoid duplicating the same data under different query keys. Use query key factories to keep keys consistent.
4. **Invalidate, don't manually set.** After mutations, prefer `invalidateQueries` over `setQueryData` unless you need instant optimistic feedback.

```tsx
const postKeys = {
  all: ['posts'] as const,
  lists: () => [...postKeys.all, 'list'] as const,
  list: (filters: PostFilters) => [...postKeys.lists(), filters] as const,
  details: () => [...postKeys.all, 'detail'] as const,
  detail: (id: string) => [...postKeys.details(), id] as const,
};

const updatePost = useMutation({
  mutationFn: (data: UpdatePostInput) => api.updatePost(data.id, data),
  onSuccess: (_result, variables) => {
    queryClient.invalidateQueries({ queryKey: postKeys.detail(variables.id) });
    queryClient.invalidateQueries({ queryKey: postKeys.lists() });
  },
});
```

## Key Points

- `defaultPreloadStaleTime: 0` means "always ask Query"
- Query's `staleTime`/`gcTime` controls caching behavior
- Preloading still works -- just uses Query's cache
- Mutations, optimistic updates, invalidation all work normally
- DevTools show the single authoritative cache state
- Use `setupRouterSsrQueryIntegration` for SSR hydration
