---
name: tanstack-query
description: |
  TanStack Query v5 server state management for React. Covers query/mutation patterns, v4-to-v5 migration (object syntax, gcTime, isPending, keepPreviousData), optimistic updates via useMutationState, SSR/hydration with HydrationBoundary, infinite queries, offline/PWA support, error boundaries with throwOnError, and React 19 Suspense integration.

  Use when building data fetching, fixing migration errors, debugging hydration mismatches, implementing caching strategies, or configuring mutations.
---

# TanStack Query

## Overview

TanStack Query is an **async state manager**, not a data fetching library. You provide a `queryFn` that returns a Promise; React Query handles caching, deduplication, background updates, and stale data management.

**When to use:** Infinite scrolling, offline-first apps, auto-refetching on focus/reconnect, complex cache invalidation, React Native, hybrid server/client apps.

**When NOT to use:** Purely synchronous state (useState/Zustand), normalized GraphQL caching (Apollo/urql), server-components-only apps (native fetch), simple fetch-and-display (server components).

## Quick Reference

| Pattern           | API                                               | Key Points                        |
| ----------------- | ------------------------------------------------- | --------------------------------- |
| Basic query       | `useQuery({ queryKey, queryFn })`                 | Include params in queryKey        |
| Suspense query    | `useSuspenseQuery(options)`                       | No `enabled` option allowed       |
| Parallel queries  | `useQueries({ queries, combine })`                | Dynamic parallel fetching         |
| Dependent query   | `useQuery({ enabled: !!dep })`                    | Wait for prerequisite data        |
| Query options     | `queryOptions({ queryKey, queryFn })`             | Reusable, type-safe config        |
| Basic mutation    | `useMutation({ mutationFn, onSuccess })`          | Invalidate on success             |
| Optimistic update | `onMutate` → cancel → snapshot → set              | Rollback in `onError`             |
| Infinite query    | `useInfiniteQuery({ initialPageParam })`          | `initialPageParam` required in v5 |
| Prefetch          | `queryClient.prefetchQuery(options)`              | Preload on hover/intent           |
| Invalidation      | `queryClient.invalidateQueries({ queryKey })`     | Fuzzy-matches by default          |
| Cancellation      | `queryFn: ({ signal }) => fetch(url, { signal })` | Auto-cancel on key change         |
| Select transform  | `select: (data) => data.filter(...)`              | Structural sharing preserved      |

## v5 Migration Quick Reference

| v4 (Removed)                   | v5 (Use Instead)                           |
| ------------------------------ | ------------------------------------------ |
| `useQuery(key, fn, opts)`      | `useQuery({ queryKey, queryFn, ...opts })` |
| `cacheTime`                    | `gcTime`                                   |
| `isLoading` (no data)          | `isPending`                                |
| `keepPreviousData: true`       | `placeholderData: keepPreviousData`        |
| `onSuccess/onError` on queries | `useEffect` or mutation callbacks          |
| `useErrorBoundary`             | `throwOnError`                             |
| No `initialPageParam`          | `initialPageParam` required                |

## State Comparison

| State        | Meaning                                  |
| ------------ | ---------------------------------------- |
| `isPending`  | No data yet (first load or disabled)     |
| `isLoading`  | `isPending && isFetching` (first fetch)  |
| `isFetching` | Any fetch (including background refetch) |
| `isSuccess`  | Query succeeded, data available          |
| `isError`    | Query failed                             |

## Common Options

| Option                 | Default | Description                         |
| ---------------------- | ------- | ----------------------------------- |
| `staleTime`            | `0`     | Time until data is considered stale |
| `gcTime`               | 5 min   | Time to keep unused data in cache   |
| `retry`                | `3`     | Number of retry attempts            |
| `refetchOnWindowFocus` | `true`  | Refetch when window regains focus   |
| `enabled`              | `true`  | Whether query should execute        |

## Common Mistakes

| Mistake                                    | Correct Pattern                                           |
| ------------------------------------------ | --------------------------------------------------------- |
| Checking `isPending` before `data`         | Data-first: check `data` → `error` → `isPending`          |
| Copying server state to local useState     | Use data directly or derived state pattern                |
| Creating QueryClient in component          | Create once outside component or in useState              |
| Using `refetch()` for parameter changes    | Include params in queryKey, let it refetch automatically  |
| Same key for useQuery and useInfiniteQuery | Use distinct key segments (different cache structures)    |
| Inline select without memoization          | Extract to stable function or useCallback                 |
| Using `catch` without re-throwing          | Throw errors in queryFn (fetch doesn't reject on 4xx/5xx) |
| Manual generics on useQuery                | Type the queryFn return, let inference work               |
| Destructuring query for type narrowing     | Keep query object intact for proper narrowing             |

## Delegation

- **Query pattern discovery**: Use `Explore` agent
- **Cache strategy review**: Use `Task` agent
- **Code review**: Delegate to `code-reviewer` agent

## References

- [Basic patterns, architecture, and query variants](references/basic-patterns.md)
- [Query keys and factory patterns](references/query-keys.md)
- [Mutations, optimistic updates, and MutationCache](references/mutations.md)
- [Cache operations, staleTime vs gcTime, seeding](references/caching.md)
- [Data transformations and select patterns](references/data-transformations.md)
- [Error handling strategies](references/error-handling.md)
- [Infinite queries and pagination](references/infinite-queries.md)
- [Offline mode and persistence](references/offline-mode.md)
- [WebSocket integration](references/websocket-integration.md)
- [SSR and hydration patterns](references/ssr-hydration.md)
- [TypeScript patterns](references/typescript-patterns.md)
- [Testing with MSW and React Testing Library](references/testing.md)
- [Known v5 issues and workarounds](references/known-issues.md)
