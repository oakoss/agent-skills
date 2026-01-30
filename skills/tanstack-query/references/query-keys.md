---
title: Query Keys
description: Object-based query keys, query key factories, query function context, and key organization patterns
tags:
  [queryKey, key-factory, query-function-context, object-keys, key-hierarchy]
---

# Query Keys

## Object-Based Keys

Use objects for named property access instead of positional array indices:

```tsx
// Array-based (positional - error prone)
const key = ['todos', 'list', status, sorting] as const;
const [, , statusParam, sortingParam] = key; // Easy to misalign

// Object-based (named - safer)
const key = ['todos', 'list', { status, sorting }] as const;
const [, , { status, sorting }] = key; // Self-documenting
```

## Query Function Context

Extract parameters from context instead of closures:

```tsx
import { type QueryFunctionContext } from '@tanstack/react-query';

const todoKeys = {
  list: (filters: { status: string }) => ['todos', 'list', filters] as const,
};

type TodoListKey = ReturnType<typeof todoKeys.list>;

async function fetchTodos({
  queryKey,
  signal,
}: QueryFunctionContext<TodoListKey>) {
  const [, , { status }] = queryKey; // Fully typed!
  const response = await fetch(`/api/todos?status=${status}`, { signal });
  return response.json();
}

useQuery({
  queryKey: todoKeys.list({ status: 'active' }),
  queryFn: fetchTodos,
});
```

Benefits: automatic abort signal handling, type-safe parameter extraction, no closure variables to track.

## Query Key Factory (TkDodo Pattern)

For granular cache invalidation, separate keys from options:

```tsx
export const postKeys = {
  all: ['posts'] as const,
  lists: () => [...postKeys.all, 'list'] as const,
  list: (filters: PostFilters) => [...postKeys.lists(), filters] as const,
  details: () => [...postKeys.all, 'detail'] as const,
  detail: (id: string) => [...postKeys.details(), id] as const,
};

export const postQueries = {
  list: (filters: PostFilters) =>
    queryOptions({
      queryKey: postKeys.list(filters),
      queryFn: () => fetchPosts(filters),
    }),
  detail: (id: string) =>
    queryOptions({
      queryKey: postKeys.detail(id),
      queryFn: () => fetchPost(id),
    }),
};

// Granular invalidation
queryClient.invalidateQueries({ queryKey: postKeys.all }); // All posts
queryClient.invalidateQueries({ queryKey: postKeys.lists() }); // All lists
queryClient.invalidateQueries({ queryKey: postKeys.detail('123') }); // One post
```

### Alternative: Centralized queryOptions Factory

Best for most use cases -- co-locates keys with query configuration:

```tsx
export const queries = {
  posts: {
    all: () =>
      queryOptions({
        queryKey: ['posts'],
        queryFn: getPosts,
      }),
    detail: (id: string) =>
      queryOptions({
        queryKey: ['posts', id],
        queryFn: () => getPost(id),
        staleTime: 1000 * 60 * 5,
      }),
  },
  users: {
    current: () =>
      queryOptions({
        queryKey: ['user', 'current'],
        queryFn: getCurrentUser,
        staleTime: 1000 * 60 * 10,
      }),
  },
} as const;

useQuery(queries.posts.detail('123'));
queryClient.invalidateQueries({ queryKey: queries.posts.all().queryKey });
```

**When to use each:**

- **Centralized factory:** Most applications, simpler mental model
- **Hierarchical key factory:** Complex invalidation needs, large-scale applications

### Key Colocation Principle

Keep query keys alongside their queries, not in a central file:

```sh
src/
├── features/
│   ├── posts/
│   │   ├── queries.ts      # postKeys + postQueries
│   │   └── components/
│   └── users/
│       ├── queries.ts      # userKeys + userQueries
│       └── components/
```

Modifying a query and its key happens together. Co-location reduces cognitive overhead.

### ESLint Rules (`@tanstack/eslint-plugin-query`)

- **exhaustive-deps** - Ensures query dependencies are properly included
- **stable-query-client** - QueryClient must remain stable across renders
- **no-rest-destructuring** - Prevents problematic rest destructuring
- **no-unstable-deps** - Flags unstable dependencies causing re-renders
- **infinite-query-property-order** - Validates property ordering
