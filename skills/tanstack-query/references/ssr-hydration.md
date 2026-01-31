---
title: SSR and Hydration
description: Server-side rendering with prefetchQuery, HydrationBoundary, dehydrate, useSuspenseQuery, router integration, and React 19 Suspense patterns
tags:
  [
    SSR,
    hydration,
    prefetchQuery,
    dehydrate,
    HydrationBoundary,
    useSuspenseQuery,
    server-rendering,
    React-19,
    Suspense,
  ]
---

# SSR and Hydration

## Core Pattern

Create `QueryClient` per request on the server. Prefetch data, then wrap with `HydrationBoundary` to transfer cache to the client:

```tsx
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from '@tanstack/react-query';

async function ServerPage() {
  const queryClient = new QueryClient();
  await queryClient.prefetchQuery(todosQueryOptions);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Todos />
    </HydrationBoundary>
  );
}
```

Use `useSuspenseQuery` (not `useQuery`) on the client for SSR to avoid hydration mismatches from conditional `isLoading` rendering.

## QueryClient per Request

Never share a QueryClient across requests -- data leaks between users:

```tsx
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

function getQueryClient() {
  if (typeof window === 'undefined') {
    return makeQueryClient();
  }
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient();
  }
  return browserQueryClient;
}
```

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

## ensureQueryData vs prefetchQuery

| Method            | Behavior                            | Returns |
| ----------------- | ----------------------------------- | ------- |
| `prefetchQuery`   | Fetches, never throws, returns void | `void`  |
| `ensureQueryData` | Returns cached data OR fetches      | `TData` |
| `fetchQuery`      | Always fetches, throws on error     | `TData` |

```tsx
export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(postsOptions());
  },
});
```

## Await as a Control Lever

Control navigation behavior with selective awaiting:

```tsx
export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(postsOptions());

    context.queryClient.prefetchQuery(recommendationsOptions());
  },
});
```

Awaited queries block navigation until data loads. Non-awaited queries start fetching but allow immediate navigation with loading states via Suspense.

## React 19 Suspense Considerations

React 19 no longer pre-renders siblings when one suspends -- causes sequential waterfalls:

```tsx
<Suspense fallback={<Loading />}>
  <Posts />
  <Comments />
</Suspense>
```

`Posts` suspends first, then `Comments` waits for `Posts` to complete before starting its fetch.

**Solution 1:** Prefetch in loaders to avoid waterfalls:

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

**Solution 2:** Use `useSuspenseQueries` for parallel fetching within components:

```tsx
function Dashboard() {
  const [posts, comments] = useSuspenseQueries({
    queries: [
      { queryKey: ['posts'], queryFn: fetchPosts },
      { queryKey: ['comments'], queryFn: fetchComments },
    ],
  });
}
```

**Key principle:** Decouple data fetching from rendering. Initiate fetches in loaders, or use `useSuspenseQueries` for parallel fetching in components.

## Error Boundaries with Suspense

Combine `QueryErrorResetBoundary` with `react-error-boundary` for retry-able error states:

```tsx
import { QueryErrorResetBoundary } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ resetErrorBoundary }) => (
            <div>
              Something went wrong.
              <button onClick={resetErrorBoundary}>Retry</button>
            </div>
          )}
        >
          <Suspense fallback={<Loading />}>
            <Todos />
          </Suspense>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}

function Todos() {
  const { data } = useSuspenseQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });
  return <TodoList todos={data} />;
}
```

`throwOnError` defaults to throwing errors when there is no cached data to show. Queries with stale cached data render that data instead of throwing, even when a background refetch fails.

## Hydration Mismatch Prevention

Common causes and fixes:

| Cause                                   | Fix                                               |
| --------------------------------------- | ------------------------------------------------- |
| `useQuery` with conditional `isLoading` | Use `useSuspenseQuery` instead                    |
| Void prefetch with `fetchStatus` render | Await prefetch or avoid rendering on `isFetching` |
| Missing `staleTime` on server           | Set `staleTime > 0` to prevent immediate refetch  |
| Shared QueryClient across requests      | Create new QueryClient per server request         |

## Server-Side staleTime

Set `staleTime` on the server to prevent the client from immediately refetching data that was just fetched:

```tsx
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60,
      },
    },
  });
}
```

Without `staleTime`, data is immediately stale on the client, triggering a refetch right after hydration -- wasting the prefetch.
