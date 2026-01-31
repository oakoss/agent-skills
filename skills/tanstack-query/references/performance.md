---
title: Performance Optimization
description: Render optimizations with notifyOnChangeProps, structural sharing mechanics, select memoization strategies
tags:
  [
    notifyOnChangeProps,
    structural-sharing,
    render-optimization,
    select,
    memoization,
    performance,
  ]
---

# Performance Optimization

## Tracked Properties (Default Behavior)

TanStack Query tracks which properties you access and only re-renders when those properties change. This happens automatically:

```tsx
function TodoCount() {
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });

  return <div>Total: {data?.length ?? 0}</div>;
}
```

This component only accesses `data`, so it won't re-render when `isFetching` or `isStale` change. Background refetches happen silently without triggering re-renders.

## notifyOnChangeProps

Override automatic tracking to explicitly control which properties trigger re-renders:

```tsx
const { data, error } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  notifyOnChangeProps: ['data', 'error'],
});
```

Now the component only re-renders when `data` or `error` change. Changes to `isPending`, `isFetching`, `isStale`, etc. are ignored.

### Opt-Out of Tracking

Set `notifyOnChangeProps: 'all'` to disable smart tracking and re-render on any change:

```tsx
const query = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  notifyOnChangeProps: 'all',
});
```

Useful when spreading the entire query object or debugging tracking issues.

### Destructuring vs Spreading

```tsx
const { data, error, isPending } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

const query = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});
```

First example tracks `data`, `error`, `isPending`. Second example tracks nothing unless you access properties. If you spread `{...query}`, use `notifyOnChangeProps: 'all'` to ensure correct behavior.

## Structural Sharing

TanStack Query preserves referential equality for unchanged data. When a background refetch returns identical JSON, existing references remain stable:

```tsx
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

// If server returns same JSON, `data` reference doesn't change
// useMemo/useCallback dependencies stay stable
const completedCount = useMemo(
  () => data?.filter((t) => t.completed).length ?? 0,
  [data],
);
```

### How It Works

React Query deeply compares new data with cached data. Unchanged objects/arrays keep their old reference:

```tsx
// Initial fetch
const v1 = [{ id: 1, title: 'Task 1' }];

// Background refetch returns same data
const v2 = [{ id: 1, title: 'Task 1' }];

// React Query detects structural equality
// Returns v1 reference, not v2
```

### Limitations

Only works with JSON-compatible data (objects, arrays, primitives). Non-serializable values (Functions, Dates, Maps, Sets) always trigger new references.

### Custom Structural Sharing

Provide your own comparison function for non-JSON data:

```tsx
useQuery({
  queryKey: ['data'],
  queryFn: fetchDataWithDates,
  structuralSharing: (oldData, newData) => {
    if (!oldData) return newData;
    if (isEqual(oldData, newData)) return oldData;
    return newData;
  },
});
```

### Disable Structural Sharing

For large responses where deep comparison is expensive:

```tsx
useQuery({
  queryKey: ['large-dataset'],
  queryFn: fetchLargeDataset,
  structuralSharing: false,
});
```

## select with Memoization

The `select` option transforms data before it reaches your component. Structural sharing applies to the transformed result:

```tsx
const selectUppercaseTodos = (data: Todo[]) =>
  data.map((todo) => todo.name.toUpperCase());

function TodoList() {
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    select: selectUppercaseTodos,
  });
}
```

Extracting to a stable function reference prevents re-running the transformation on every render.

### Inline select (Anti-pattern)

```tsx
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data) => data.map((todo) => todo.name.toUpperCase()),
});
```

This inline arrow function creates a new reference on every render, forcing the selector to re-run even when data hasn't changed.

### useCallback for Dynamic Selectors

When the selector depends on props or state:

```tsx
function FilteredTodos({ status }: { status: string }) {
  const selectFiltered = useCallback(
    (data: Todo[]) => data.filter((t) => t.status === status),
    [status],
  );

  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    select: selectFiltered,
  });
}
```

### Structural Sharing on select Results

React Query applies structural sharing to the output of `select`:

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data) => data.filter((todo) => todo.completed),
});
```

If background refetch returns the same list of completed todos, the filtered array reference stays stable even though a new selector function ran.

## Global Configuration

Set defaults for all queries:

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      notifyOnChangeProps: ['data', 'error'],
      structuralSharing: true,
    },
  },
});
```

Query-level options override global defaults.

## When to Optimize

| Scenario                         | Recommendation                       |
| -------------------------------- | ------------------------------------ |
| Component re-renders too often   | Check tracked properties, use select |
| Large dataset causing slow deep  | Disable structural sharing           |
| Expensive transformation         | Use select with stable function      |
| Spreading query object           | Set notifyOnChangeProps: 'all'       |
| Non-JSON data (Dates, custom)    | Custom structuralSharing function    |
| Selector depends on props        | Use useCallback                      |
| Simple component, few properties | Default tracking is sufficient       |
