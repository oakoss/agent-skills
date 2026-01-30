---
title: Basic Patterns
description: QueryClient architecture, useQuery basics, dependent queries, parallel queries, and queryOptions factory pattern
tags:
  [
    useQuery,
    queryFn,
    queryKey,
    queryOptions,
    dependent-queries,
    parallel-queries,
    QueryClient,
  ]
---

# Basic Patterns

## Architecture Mental Model

```text
QueryClient
  └── QueryCache
        └── Query (one per unique queryKey)
              └── QueryObserver (one per useQuery call)
```

- **QueryClient**: Entry point. Created once, passed via `QueryClientProvider`.
- **QueryCache**: Stores all Query instances. One per QueryClient.
- **Query**: Holds data, error, state for a single queryKey. Shared across all observers.
- **QueryObserver**: Bridges a Query to a component. Multiple components can observe the same Query — they share cached data and deduplication.

When two components call `useQuery({ queryKey: ['todos'] })`, they create two QueryObservers pointing to the same Query. Only one network request fires.

## Basic Query

```tsx
const { data, isPending, isError, error } = useQuery({
  queryKey: ['todos'],
  queryFn: async () => {
    const res = await fetch('/api/todos');
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
  },
});
```

Data-first rendering pattern:

```tsx
if (data) return <TodoList todos={data} />;
if (isError) return <div>Error: {error.message}</div>;
return <Skeleton />;
```

## Dependent Queries

Query B waits for Query A via `enabled`:

```tsx
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});

const { data: posts } = useQuery({
  queryKey: ['users', userId, 'posts'],
  queryFn: () => fetchUserPosts(userId),
  enabled: !!user,
});
```

## Parallel Queries

### Static (known at render time)

Multiple `useQuery` calls in the same component run in parallel automatically:

```tsx
const users = useQuery({ queryKey: ['users'], queryFn: fetchUsers });
const projects = useQuery({ queryKey: ['projects'], queryFn: fetchProjects });
```

### Dynamic (variable number)

Use `useQueries` for dynamic parallel fetching:

```tsx
const results = useQueries({
  queries: userIds.map((id) => ({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
  })),
  combine: (results) => ({
    data: results.map((r) => r.data),
    pending: results.some((r) => r.isPending),
    error: results.find((r) => r.error)?.error,
  }),
});
```

### Parallel Suspense

`useSuspenseQueries` fetches in parallel without sequential waterfalls:

```tsx
const [posts, comments] = useSuspenseQueries({
  queries: [
    { queryKey: ['posts'], queryFn: fetchPosts },
    { queryKey: ['comments'], queryFn: fetchComments },
  ],
});
```

Individual `useSuspenseQuery` calls in the same component cause waterfalls in React 19. Use `useSuspenseQueries` or prefetch in loaders instead.

## Query Cancellation

Pass `signal` from the query function context to enable automatic cancellation when the queryKey changes or the component unmounts:

```tsx
useQuery({
  queryKey: ['todos', search],
  queryFn: async ({ signal }) => {
    const res = await fetch(`/api/todos?q=${search}`, { signal });
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
  },
});
```

Works with any API that accepts `AbortSignal` (fetch, axios with `signal` option, etc.).

## queryOptions Helper

Creates a reusable, type-safe query configuration object:

```tsx
import { queryOptions } from '@tanstack/react-query';

export const todosOptions = queryOptions({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  staleTime: 1000 * 60 * 5,
});

// Reuse everywhere with full type inference
useQuery(todosOptions);
useSuspenseQuery(todosOptions);
await queryClient.prefetchQuery(todosOptions);
await queryClient.ensureQueryData(todosOptions);
queryClient.invalidateQueries({ queryKey: todosOptions.queryKey });
```

## setQueryDefaults

Set default options for all queries matching a key prefix:

```tsx
queryClient.setQueryDefaults(['todos'], {
  staleTime: 1000 * 60 * 10,
  gcTime: 1000 * 60 * 60,
});
```

Useful for setting staleTime globally per entity type without repeating in every query. Options merge with individual query options (query-level takes precedence).

## Prefetching

Preload data before the user navigates:

```tsx
const queryClient = useQueryClient();

function TodoLink({ id }: { id: string }) {
  return (
    <Link
      to={`/todos/${id}`}
      onMouseEnter={() => {
        queryClient.prefetchQuery({
          queryKey: ['todos', id],
          queryFn: () => fetchTodo(id),
        });
      }}
    >
      View Todo
    </Link>
  );
}
```

`prefetchQuery` is a no-op if fresh data already exists in cache.
