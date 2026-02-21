---
title: Mutations
description: Mutation patterns with useMutation, optimistic updates, cache invalidation, useMutationState, serial scope, and rollback strategies
tags:
  [
    useMutation,
    optimistic-update,
    invalidation,
    mutateAsync,
    onMutate,
    rollback,
    useMutationState,
    scope,
  ]
---

# Mutations

## Basic Mutation

```tsx
const mutation = useMutation({
  mutationFn: async (newPost: { title: string; body: string }) => {
    const res = await fetch('/api/posts', {
      method: 'POST',
      body: JSON.stringify(newPost),
    });
    if (!res.ok) throw new Error('Failed to create post');
    return res.json();
  },
  onSuccess: async (_data, _variables, _onMutateResult, context) => {
    await context.client.invalidateQueries({ queryKey: ['posts'] });
  },
});

mutation.mutate(data);
```

## mutate vs mutateAsync

| Method          | Error Handling      | Return Value     | Use Case                  |
| --------------- | ------------------- | ---------------- | ------------------------- |
| `mutate()`      | Handles internally  | `void`           | Most cases, use callbacks |
| `mutateAsync()` | Must catch manually | `Promise<TData>` | Need to await result      |

Prefer `mutate()` with callbacks for cleaner code:

```tsx
mutation.mutate(data, {
  onSuccess: (result) => navigate(`/posts/${result.id}`),
});

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
  onSuccess: (_data, _variables, _onMutateResult, context) => {
    context.client.invalidateQueries({ queryKey: ['posts'] });
  },
});

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
  onSuccess: (_data, _variables, _onMutateResult, context) => {
    return context.client.invalidateQueries({ queryKey: ['posts'] });
  },
});
```

Without `return`, `mutation.isPending` becomes false immediately after the mutation succeeds but before queries refetch.

## Optimistic Updates with Rollback

```tsx
const updatePost = useMutation({
  mutationFn: (data: { id: string; title: string }) => updatePostFn(data),
  onMutate: async (newData, context) => {
    await context.client.cancelQueries({ queryKey: ['posts', newData.id] });
    const previousPost = context.client.getQueryData(['posts', newData.id]);

    context.client.setQueryData(['posts', newData.id], (old) => ({
      ...old,
      ...newData,
    }));

    return { previousPost };
  },
  onError: (_error, variables, onMutateResult, context) => {
    if (onMutateResult?.previousPost) {
      context.client.setQueryData(
        ['posts', variables.id],
        onMutateResult.previousPost,
      );
    }
  },
  onSettled: (_data, _error, variables, _onMutateResult, context) => {
    context.client.invalidateQueries({ queryKey: ['posts', variables.id] });
  },
});
```

## Simplified Optimistic Updates via useMutationState

No cache manipulation or rollback needed -- render pending mutations directly:

```tsx
function OptimisticTodoList() {
  const { data: todos } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });

  const addTodo = useMutation({
    mutationKey: ['addTodo'],
    mutationFn: (newTodo: CreateTodoInput) => api.addTodo(newTodo),
    onSettled: (_data, _error, _variables, _onMutateResult, context) => {
      context.client.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  const pendingTodos = useMutationState<CreateTodoInput>({
    filters: { mutationKey: ['addTodo'], status: 'pending' },
    select: (mutation) => mutation.state.variables,
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

`useMutationState` returns a snapshot array that updates when matching mutations change. Requires `mutationKey` on the `useMutation` call to enable filtering.

## Concurrent Optimistic Updates

Handle rapid mutations with `isMutating()`:

```tsx
const updateTodo = useMutation({
  mutationFn: updateTodoFn,
  onMutate: async (newData, context) => {
    await context.client.cancelQueries({ queryKey: ['todos', newData.id] });
    const previous = context.client.getQueryData(['todos', newData.id]);
    context.client.setQueryData(['todos', newData.id], newData);
    return { previous };
  },
  onError: (_error, variables, onMutateResult, context) => {
    context.client.setQueryData(
      ['todos', variables.id],
      onMutateResult?.previous,
    );
  },
  onSettled: (_data, _error, variables, _onMutateResult, context) => {
    if (context.client.isMutating({ mutationKey: ['todos'] }) === 1) {
      context.client.invalidateQueries({
        queryKey: ['todos', variables.id],
      });
    }
  },
});
```

Using `isMutating()` ensures only the final mutation triggers invalidation, preventing flickering UI from intermediate refetches.

## Serial Mutations with scope

Run mutations with the same scope ID in serial (FIFO queue):

```tsx
const uploadFile = useMutation({
  mutationFn: uploadFileFn,
  scope: { id: 'file-upload' },
});
```

All mutations sharing `scope: { id: 'file-upload' }` execute one at a time. Useful for ordered operations like sequential file uploads or dependent API calls.

## Automatic Invalidation via MutationCache

Global mutation error/success handling:

```tsx
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
    onError: (error, _variables, _context, mutation) => {
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

## Global Loading Indicator

```tsx
import { useMutationState } from '@tanstack/react-query';

function GlobalSavingIndicator() {
  const pendingCount = useMutationState({
    filters: { status: 'pending' },
    select: (mutation) => mutation.state.status,
  }).length;

  if (pendingCount === 0) return null;
  return <div>Saving {pendingCount} items...</div>;
}
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

export const Route = createFileRoute('/posts')({
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(postsOptions());
  },
});
```
