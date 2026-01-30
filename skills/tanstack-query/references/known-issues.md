---
title: Known Issues
description: Common v5 migration issues, breaking changes, SSR hydration bugs, and workarounds for TanStack Query pitfalls
tags:
  [v5-migration, breaking-changes, SSR, hydration, cacheTime, gcTime, isPending]
---

# Known v5 Issues and Workarounds

16 documented issues from v5 migration, SSR/hydration bugs, and common mistakes.

## Issue #1: Object Syntax Required

**Error**: `useQuery is not a function` or type errors
**Source**: [v5 Migration Guide](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#removed-overloads-in-favor-of-object-syntax)

v5 removed all function overloads, only object syntax works. Always use `useQuery({ queryKey, queryFn, ...options })`.

## Issue #2: Query Callbacks Removed

**Error**: Callbacks don't run, TypeScript errors
**Source**: [v5 Breaking Changes](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#callbacks-on-usequery-and-queryobserver-have-been-removed)

`onSuccess`, `onError`, `onSettled` removed from queries (still work in mutations). Use `useEffect` for side effects.

## Issue #3: Status Loading → Pending

**Error**: UI shows wrong loading state
**Source**: [v5 Migration](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#isloading-and-isfetching-flags)

`status: 'loading'` renamed to `status: 'pending'`. Use `isPending` for initial load, `isLoading` now means `isPending && isFetching`.

## Issue #4: cacheTime → gcTime

**Error**: `cacheTime is not a valid option`

Renamed to `gcTime` to better reflect "garbage collection time".

## Issue #5: useSuspenseQuery + enabled

**Error**: Type error, enabled option not available
**Source**: [GitHub Discussion #6206](https://github.com/TanStack/query/discussions/6206)

Suspense guarantees data is available, can't conditionally disable. Use conditional rendering instead.

## Issue #6: initialPageParam Required

**Error**: `initialPageParam is required` type error
**Source**: [v5 Migration](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#new-required-initialPageParam-option)

v5 requires explicit `initialPageParam` for infinite queries (v4 passed `undefined`).

## Issue #7: keepPreviousData Removed

**Error**: `keepPreviousData is not a valid option`

Replaced with `placeholderData: keepPreviousData` helper function.

## Issue #8: TypeScript Error Type Default

**Error**: Type errors with error handling

v5 defaults error type to `Error` (v4 used `unknown`). If throwing non-Error types, specify error type explicitly or always throw Error objects.

## Issue #9: Streaming Server Components Hydration Error

**Error**: `Hydration failed because the initial UI does not match what was rendered on the server`
**Source**: [GitHub Issue #9642](https://github.com/TanStack/query/issues/9642)
**Affects**: v5.82.0+ with streaming SSR (void prefetch pattern)

Race condition where `hydrate()` resolves synchronously but `query.fetch()` creates async retryer, causing isFetching/isStale mismatch.

**Workarounds:**

```tsx
// Option 1: Await prefetch instead of void
await streamingQueryClient.prefetchQuery({
  queryKey: ['data'],
  queryFn: getData,
});

// Option 2: Don't render based on fetchStatus with Suspense
const { data } = useSuspenseQuery({ queryKey: ['data'], queryFn: getData });
return <div>{data}</div>; // No conditional on isFetching
```

**Status**: Known issue, being investigated.

## Issue #10: useQuery Hydration Error with Prefetching

**Error**: Text content mismatch during hydration
**Source**: [GitHub Issue #9399](https://github.com/TanStack/query/issues/9399)
**Affects**: v5.x with server-side prefetching

`tryResolveSync` detects resolved promises in RSC payload and extracts data synchronously during hydration, bypassing normal pending state.

**Fix**: Use `useSuspenseQuery` instead of `useQuery` for SSR.

## Issue #11: refetchOnMount Not Respected for Errored Queries

**Error**: Queries refetch on mount despite `refetchOnMount: false`
**Source**: [GitHub Issue #10018](https://github.com/TanStack/query/issues/10018)
**Affects**: v5.90.16+

Errored queries with no data are always treated as stale (intentional to avoid permanently showing error states).

**Fix**: Use `retryOnMount: false` instead of (or in addition to) `refetchOnMount: false`.

## Issue #12: Mutation Callback Signature Breaking Change

**Error**: TypeScript errors in mutation callbacks
**Source**: [GitHub Issue #9660](https://github.com/TanStack/query/issues/9660)
**Affects**: v5.89.0+

`onMutateResult` parameter added between `variables` and `context`, changing callback signatures from 3 to 4 params.

```tsx
// v5.89.0+ signature
useMutation({
  mutationFn: addTodo,
  onError: (error, variables, onMutateResult, context) => { ... },
  onSuccess: (data, variables, onMutateResult, context) => { ... },
});
```

## Issue #13: Readonly Query Keys Break Partial Matching

**Source**: [GitHub Issue #9871](https://github.com/TanStack/query/issues/9871)
**Affects**: v5.90.8 only (fixed in v5.90.9)

Partial query matching broke TypeScript types for readonly query keys (`as const`). **Fix**: Upgrade to v5.90.9+.

## Issue #14: useMutationState Type Inference Lost

**Source**: [GitHub Issue #9825](https://github.com/TanStack/query/issues/9825)
**Affects**: All v5.x

Fuzzy mutation key matching prevents guaranteed type inference. `mutation.state.variables` typed as `unknown`.

**Fix**: Explicitly cast types in the `select` callback:

```tsx
const pendingTodos = useMutationState({
  filters: { mutationKey: ['addTodo'], status: 'pending' },
  select: (mutation) => mutation.state.variables as Todo,
});
```

## Issue #15: Query Cancellation in StrictMode with fetchQuery

**Source**: [GitHub Issue #9798](https://github.com/TanStack/query/issues/9798)
**Affects**: Development only (React StrictMode)

StrictMode double mount/unmount cancels queries when last observer unmounts, even if `fetchQuery()` is running. This is expected dev-only behavior, doesn't affect production.

## Issue #16: invalidateQueries Only Refetches Active Queries

**Source**: [GitHub Issue #9531](https://github.com/TanStack/query/issues/9531)
**Affects**: All v5.x

`invalidateQueries()` only refetches "active" queries (currently observed) by default.

**Fix**: Use `refetchType: 'all'` to force refetch of inactive queries:

```tsx
queryClient.invalidateQueries({
  queryKey: ['todos'],
  refetchType: 'all', // Refetch active AND inactive
});
```
