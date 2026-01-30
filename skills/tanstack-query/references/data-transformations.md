---
title: Data Transformations
description: Four approaches to transforming query data: backend, queryFn, render-level useMemo, and the select option
tags: [select, useMemo, transform, queryFn, data-mapping, memoization]
---

# Data Transformations

Four approaches ranked by recommendation:

## 1. Backend Transformation (Ideal)

Have your backend return exactly what the frontend needs. No frontend transformation overhead, but may not be feasible with public APIs or shared backends.

## 2. In the queryFn

Transform immediately after fetching, before caching:

```tsx
const fetchTodos = async (): Promise<string[]> => {
  const response = await fetch('/api/todos');
  const data = await response.json();
  return data.map((todo: Todo) => todo.name.toUpperCase());
};

useQuery({ queryKey: ['todos'], queryFn: fetchTodos });
```

Runs on every fetch; transformed structure obscures original data in cache.

## 3. In the Render Function (useMemo)

```tsx
function useTodosQuery() {
  const queryInfo = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });

  return {
    ...queryInfo,
    data: useMemo(
      () => queryInfo.data?.map((todo) => todo.name.toUpperCase()),
      [queryInfo.data],
    ),
  };
}
```

Original data preserved in cache, but transformation runs on component re-renders.

## 4. Using select (Recommended)

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data) => data.map((todo) => todo.name.toUpperCase()),
});
```

Structural sharing preserves referential identity. Components only re-render when selected data changes. Original data preserved in cache. Inline functions run every render -- requires memoization for expensive transforms.

## select Memoization Strategies

**Extract to stable function:**

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

**useCallback for prop-dependent selectors:**

```tsx
const selectFiltered = useCallback(
  (data: Todo[]) => data.filter((todo) => todo.status === status),
  [status],
);

useQuery({ queryKey: ['todos'], queryFn: fetchTodos, select: selectFiltered });
```

## Type-Safe Selector Abstractions

Create reusable query options that accept custom selectors:

```tsx
function postOptions<TData = Post>(id: string, select?: (data: Post) => TData) {
  return queryOptions({
    queryKey: ['posts', id],
    queryFn: () => fetchPost(id),
    select,
  });
}

useQuery(postOptions('123')); // data: Post | undefined
useQuery(postOptions('123', (data) => data.title)); // data: string | undefined
```

## When to Use Each Approach

| Scenario                              | Recommended Approach        |
| ------------------------------------- | --------------------------- |
| Simple display transformation         | `select` option             |
| Expensive computation                 | `select` with memoization   |
| Need original data elsewhere          | `select` (preserves cache)  |
| Transformation for multiple consumers | `queryFn` transformation    |
| Backend control available             | Backend transformation      |
| Depends on component props            | `select` with `useCallback` |
