---
title: Error Handling
description: Error state checking, error boundaries with throwOnError, global error callbacks, and retry configuration
tags: [error, throwOnError, error-boundary, retry, onError, global-handler]
---

# Error Handling

## Three Strategies

**1. Direct Error State Checking:**

```tsx
const { data, isError, error } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

if (isError) return <div>Error: {error.message}</div>;
```

Limitation: replaces entire component with error UI, even during background refetch failures when stale data is available.

**2. Error Boundaries with throwOnError:**

```tsx
// Boolean: throw all errors
useQuery({ queryKey: ['todos'], queryFn: fetchTodos, throwOnError: true });

// Function: selective error throwing
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  throwOnError: (error) => error.response?.status >= 500,
});
```

Use for critical data where the component cannot render without it.

**3. Global QueryCache Callbacks (Recommended for background errors):**

```tsx
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      // Only show toast for background refetches (stale data exists)
      if (query.state.data !== undefined) {
        toast.error(`Background update failed: ${error.message}`);
      }
    },
  }),
});
```

Triggers once per failed request, not per Observer.

## Data-First Error Pattern

Always check for data before showing error UI:

```tsx
function TodoList() {
  const { data, isError, error, isFetching } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });

  if (data) {
    return (
      <>
        <ul>
          {data.map((todo) => (
            <li key={todo.id}>{todo.name}</li>
          ))}
        </ul>
        {isError && <Banner>Update failed - showing cached data</Banner>}
        {isFetching && <Spinner />}
      </>
    );
  }

  if (isError) return <div>Error: {error.message}</div>;
  return <Skeleton />;
}
```

## fetch API Error Handling

The native `fetch` API does NOT reject on 4xx/5xx status codes. You must throw manually:

```tsx
const fetchTodos = async (): Promise<Todo[]> => {
  const response = await fetch('/api/todos');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
};
```

Common mistake -- using `catch` without re-throwing returns a successful Promise with `undefined`, which React Query treats as success.

## Retry Configuration

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  retry: 3, // Default
  retry: false, // Disable retries
  retry: (failureCount, error) => {
    if (error.response?.status === 404) return false;
    return failureCount < 3;
  },
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
});
```

## Global Mutation Error Handling

```tsx
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onError: (error, variables, context, mutation) => {
      if (mutation.options.onError) return; // Let local handler take precedence
      toast.error(`Operation failed: ${error.message}`);
    },
  }),
});
```
