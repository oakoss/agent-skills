---
title: Mutations
description: Mutation patterns with useMutation, optimistic updates, cache invalidation, mutate vs mutateAsync, and rollback strategies
tags:
  [
    useMutation,
    optimistic-update,
    invalidation,
    mutateAsync,
    onMutate,
    rollback,
    onSettled,
  ]
---

# Mutations

## Basic Mutation

```tsx
const queryClient = useQueryClient();

const mutation = useMutation({
  mutationFn: async (newPost: { title: string; body: string }) => {
    const res = await fetch('/api/posts', {
      method: 'POST',
      body: JSON.stringify(newPost),
    });
    return res.json();
  },
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
});

mutation.mutate(data);
// Or: await mutation.mutateAsync(data);
```

## mutate vs mutateAsync

| Method          | Error Handling      | Return Value     | Use Case                  |
| --------------- | ------------------- | ---------------- | ------------------------- |
| `mutate()`      | Handles internally  | `void`           | Most cases, use callbacks |
| `mutateAsync()` | Must catch manually | `Promise<TData>` | Need to await result      |

Prefer `mutate()` with callbacks for cleaner code:

```tsx
// mutate - errors handled internally
mutation.mutate(data, {
  onSuccess: (result) => navigate(`/posts/${result.id}`),
});

// mutateAsync - must handle errors yourself
try {
  const result = await mutation.mutateAsync(data);
  navigate(`/posts/${result.id}`);
} catch (error) {
  toast.error(error.message);
}
```

## Single Argument Limitation

Mutations accept only ONE variable argument. Use objects for multiple values:

```tsx
// BAD: Multiple arguments (won't work)
mutation.mutate(id, title, body);

// GOOD: Single object argument
mutation.mutate({ id, title, body });
```

## Callback Execution Order

1. `useMutation.onMutate`
2. `useMutation.onSuccess/onError`
3. `useMutation.onSettled`
4. `mutate.onSuccess/onError`
5. `mutate.onSettled`

If component unmounts, `mutate()` callbacks may not fire. Place critical logic (like invalidation) in `useMutation()` callbacks:

```tsx
const updatePost = useMutation({
  mutationFn: updatePostFn,
  // Query-related logic here (always runs)
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
});

// UI-specific logic in mutate() (may not run if unmounted)
updatePost.mutate(data, {
  onSuccess: () => {
    toast.success('Post updated!');
    navigate('/posts');
  },
});
```

## Returning Promises from Callbacks

Return `invalidateQueries` to maintain loading state during refetch:

```tsx
const mutation = useMutation({
  mutationFn: createPost,
  onSuccess: () => {
    // Without return: mutation.isPending becomes false immediately
    // With return: mutation.isPending stays true until refetch completes
    return queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
});
```

## Optimistic Updates with Rollback

```tsx
const updatePost = useMutation({
  mutationFn: (data: { id: string; title: string }) => updatePostFn(data),
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['posts', newData.id] });
    const previousPost = queryClient.getQueryData(['posts', newData.id]);

    queryClient.setQueryData(['posts', newData.id], (old) => ({
      ...old,
      ...newData,
    }));

    return { previousPost };
  },
  onError: (error, variables, context) => {
    if (context?.previousPost) {
      queryClient.setQueryData(['posts', variables.id], context.previousPost);
    }
  },
  onSettled: (data, error, variables) => {
    queryClient.invalidateQueries({ queryKey: ['posts', variables.id] });
  },
});
```

## Optimistic Add to List

```tsx
const addPost = useMutation({
  mutationFn: createPostFn,
  onMutate: async (newPost) => {
    await queryClient.cancelQueries({ queryKey: ['posts'] });
    const previousPosts = queryClient.getQueryData(['posts']);

    const optimisticPost = {
      ...newPost,
      id: `temp-${Date.now()}`,
      createdAt: new Date(),
    };
    queryClient.setQueryData(['posts'], (old: Post[]) => [
      optimisticPost,
      ...old,
    ]);

    return { previousPosts };
  },
  onError: (error, variables, context) => {
    queryClient.setQueryData(['posts'], context?.previousPosts);
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
});
```

## Concurrent Optimistic Updates

Handle rapid mutations with `isMutating()`:

```tsx
const updateTodo = useMutation({
  mutationFn: updateTodoFn,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['todos', newData.id] });
    const previous = queryClient.getQueryData(['todos', newData.id]);
    queryClient.setQueryData(['todos', newData.id], newData);
    return { previous };
  },
  onError: (_error, variables, context) => {
    queryClient.setQueryData(['todos', variables.id], context?.previous);
  },
  onSettled: (_data, _error, variables) => {
    // Only invalidate when this is the last pending mutation
    if (queryClient.isMutating({ mutationKey: ['todos'] }) === 1) {
      queryClient.invalidateQueries({ queryKey: ['todos', variables.id] });
    }
  },
});
```

Multiple rapid mutations can cause flickering UI as each invalidation triggers refetch. Using `isMutating()` ensures only the final mutation triggers invalidation.

## Automatic Invalidation via MutationCache

Global mutation error/success handling:

```tsx
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
    onError: (error, variables, context, mutation) => {
      if (!mutation.options.onError) {
        toast.error(`Operation failed: ${error.message}`);
      }
    },
  }),
});
```

## Meta-Based Invalidation Tagging

Specify which queries to invalidate per mutation:

```tsx
const updateLabel = useMutation({
  mutationFn: updateLabelFn,
  meta: {
    invalidates: [['issues'], ['labels']],
  },
});

// In MutationCache
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: async (_data, _variables, _context, mutation) => {
      const invalidates = mutation.meta?.invalidates as string[][] | undefined;
      if (invalidates) {
        for (const queryKey of invalidates) {
          await queryClient.invalidateQueries({ queryKey });
        }
      }
    },
  }),
});
```

## useMutationState for Cross-Component Tracking

Track mutation state from any component without prop drilling:

```tsx
import { useMutationState } from '@tanstack/react-query';

function GlobalLoadingIndicator() {
  const pendingCount = useMutationState({
    filters: { status: 'pending' },
    select: (mutation) => mutation.state.status,
  }).length;

  if (pendingCount === 0) return null;
  return <Spinner />;
}
```

Show optimistic items from a sibling component:

```tsx
function OptimisticTodoList() {
  const { data: todos } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });

  const pendingTodos = useMutationState({
    filters: { mutationKey: ['addTodo'], status: 'pending' },
    select: (mutation) => mutation.state.variables as CreateTodoInput,
  });

  return (
    <ul>
      {todos?.map((todo) => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
      {pendingTodos.map((todo, i) => (
        <TodoItem key={`pending-${i}`} todo={todo} isPending />
      ))}
    </ul>
  );
}
```

`useMutationState` returns a snapshot array that updates when matching mutations change. Combine with `mutationKey` on `useMutation` to enable filtering:

```tsx
const addTodo = useMutation({
  mutationKey: ['addTodo'],
  mutationFn: createTodoFn,
});
```

## Query with Server Functions

```tsx
import { createServerFn } from '@tanstack/react-start';

const getPosts = createServerFn({ method: 'GET' }).handler(async () => {
  return await db.query.posts.findMany();
});

function postsOptions() {
  return queryOptions({
    queryKey: ['posts'],
    queryFn: () => getPosts(),
  });
}

// Prefetch in loader
export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(postsOptions());
  },
});
```
