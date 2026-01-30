---
title: Cache Operations
description: Cache invalidation, staleTime vs gcTime, prefetching, setQueryData, and refetch behavior configuration
tags: [invalidation, staleTime, gcTime, prefetch, setQueryData, cache, refetch]
---

# Cache Operations

```tsx
const queryClient = useQueryClient();

// Invalidate
queryClient.invalidateQueries({ queryKey: ['posts'] });
queryClient.invalidateQueries({ queryKey: ['posts', '123'] });

// Invalidate with exact match
queryClient.invalidateQueries({ queryKey: ['posts'], exact: true });

// Control refetch behavior
queryClient.invalidateQueries({
  queryKey: ['posts'],
  refetchType: 'active', // 'active' | 'inactive' | 'all' | 'none'
});

// Set data directly
queryClient.setQueryData(['posts', '123'], newPost);

// Prefetch
await queryClient.prefetchQuery(postOptions('456'));
```

## staleTime vs gcTime

```tsx
// staleTime: How long data is considered "fresh"
// Fresh data won't trigger background refetch. Default: 0 (always stale)

// gcTime: How long unused data stays in cache
// After component unmounts, data stays for this duration. Default: 5 minutes

// Static data (rarely changes)
queryOptions({
  queryKey: ['categories'],
  queryFn: getCategories,
  staleTime: 1000 * 60 * 60, // Fresh for 1 hour
  gcTime: 1000 * 60 * 60 * 24, // Keep in cache for 24 hours
});

// Frequently updated data
queryOptions({
  queryKey: ['notifications'],
  queryFn: getNotifications,
  staleTime: 1000 * 30, // Fresh for 30 seconds
  refetchInterval: 1000 * 60, // Poll every minute
});
```

## Background Refetch Patterns

```tsx
queryOptions({
  queryKey: ['data'],
  queryFn: fetchData,
  refetchOnWindowFocus: true, // Default: true
  refetchOnReconnect: true, // Default: true
  refetchOnMount: true, // Default: true
  refetchInterval: 1000 * 60, // Polling interval
  refetchIntervalInBackground: false, // Only poll when focused
});

// Conditional polling
const { data } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => getJobStatus(jobId),
  refetchInterval: (query) => {
    return query.state.data?.status === 'completed' ? false : 1000;
  },
});
```

## placeholderData vs initialData

| Aspect           | placeholderData                    | initialData                |
| ---------------- | ---------------------------------- | -------------------------- |
| Level            | Observer (component)               | Cache (global)             |
| Persistence      | Never cached                       | Persisted to cache         |
| Refetch Behavior | Always triggers background refetch | Respects `staleTime`       |
| Error Handling   | Becomes `undefined` on failure     | Remains available on error |
| Flag             | `isPlaceholderData: true`          | No special flag            |

```tsx
// placeholderData - temporary "fake" data while real data loads
const { data, isPlaceholderData } = useQuery({
  queryKey: ['todo', id],
  queryFn: () => fetchTodo(id),
  placeholderData: { id, name: 'Loading...', completed: false },
});
<div className={isPlaceholderData ? 'opacity-50' : ''}>{data?.name}</div>;

// initialData - data "as good as fetched", persisted and respects staleness
useQuery({
  queryKey: ['todo', id],
  queryFn: () => fetchTodo(id),
  initialData: { id, name: 'Loading...', completed: false },
  staleTime: 1000 * 60, // Won't refetch for 1 minute!
});

// initialDataUpdatedAt - tell React Query when initial data was last updated
useQuery({
  queryKey: ['todo', id],
  queryFn: () => fetchTodo(id),
  initialData: cachedTodo,
  initialDataUpdatedAt: cachedTodo.lastUpdated,
  staleTime: 1000 * 60,
});
```

## Cache Seeding

**Pull approach** -- look up existing cache data for detail views:

```tsx
function useTodo(id: string) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ['todos', 'detail', id],
    queryFn: () => fetchTodo(id),
    initialData: () => {
      const todos = queryClient.getQueryData<Todo[]>(['todos', 'list']);
      return todos?.find((todo) => todo.id === id);
    },
    initialDataUpdatedAt: () => {
      return queryClient.getQueryState(['todos', 'list'])?.dataUpdatedAt;
    },
  });
}
```

**Push approach** -- populate detail caches when fetching lists:

```tsx
function useTodos() {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ['todos', 'list'],
    queryFn: async () => {
      const todos = await fetchTodos();
      for (const todo of todos) {
        queryClient.setQueryData(['todos', 'detail', todo.id], todo);
      }
      return todos;
    },
  });
}
```
