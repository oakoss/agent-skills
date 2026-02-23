---
title: React Integration
description: Setting up @trpc/react-query, client hooks for queries and mutations, provider configuration, and SSR patterns
tags:
  [
    react,
    useQuery,
    useMutation,
    createTRPCReact,
    provider,
    httpBatchLink,
    QueryClient,
  ]
---

# React Integration

## Setup

### Create tRPC React Hooks

```ts
// src/utils/trpc.ts
import { createTRPCReact } from '@trpc/react-query';
import { type AppRouter } from '../server/routers/_app';

export const trpc = createTRPCReact<AppRouter>();
```

### Provider Configuration

```tsx
// src/app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useState } from 'react';
import { trpc } from '../utils/trpc';

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { staleTime: 30_000 },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

function getQueryClient() {
  if (typeof window === 'undefined') return makeQueryClient();
  return (browserQueryClient ??= makeQueryClient());
}

export function TRPCProvider({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient();
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: '/api/trpc',
        }),
      ],
    }),
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

## Query Hooks

```tsx
function UserList() {
  const { data, isPending, error } = trpc.user.list.useQuery();

  if (isPending) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Query with Input

```tsx
function UserProfile({ userId }: { userId: string }) {
  const { data } = trpc.user.byId.useQuery(userId);
  return data ? <h1>{data.name}</h1> : null;
}
```

### Conditional Queries

```tsx
function UserPosts({ userId }: { userId: string | undefined }) {
  const { data } = trpc.post.byUser.useQuery(userId!, {
    enabled: !!userId,
  });
  return data ? <PostList posts={data} /> : null;
}
```

### Suspense Queries

```tsx
function UserProfile({ userId }: { userId: string }) {
  const [data] = trpc.user.byId.useSuspenseQuery(userId);
  return <h1>{data.name}</h1>;
}
```

## Mutation Hooks

```tsx
function CreateUser() {
  const utils = trpc.useUtils();
  const mutation = trpc.user.create.useMutation({
    onSuccess() {
      utils.user.list.invalidate();
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        mutation.mutate({
          name: formData.get('name') as string,
          email: formData.get('email') as string,
        });
      }}
    >
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

## Optimistic Updates

```tsx
const utils = trpc.useUtils();

const mutation = trpc.todo.toggle.useMutation({
  async onMutate({ id, completed }) {
    await utils.todo.list.cancel();
    const previous = utils.todo.list.getData();
    utils.todo.list.setData(undefined, (old) =>
      old?.map((t) => (t.id === id ? { ...t, completed } : t)),
    );
    return { previous };
  },
  onError(_err, _vars, context) {
    if (context?.previous) {
      utils.todo.list.setData(undefined, context.previous);
    }
  },
  onSettled() {
    utils.todo.list.invalidate();
  },
});
```

## useUtils

`trpc.useUtils()` provides access to the query client scoped to tRPC:

```tsx
const utils = trpc.useUtils();

utils.user.list.invalidate();
utils.user.byId.prefetch('user-123');
utils.user.list.setData(undefined, newData);
utils.user.byId.getData('user-123');
```

## Streaming with httpBatchStreamLink

```tsx
const [trpcClient] = useState(() =>
  trpc.createClient({
    links: [
      httpBatchStreamLink({
        url: '/api/trpc',
      }),
    ],
  }),
);
```

Responses stream as individual procedures resolve, improving perceived performance for batched requests.

## Aborting Requests

tRPC React Query passes abort signals automatically. Requests cancel on component unmount or query key changes.

```tsx
const { data } = trpc.search.useQuery(searchTerm, {
  trpc: { abortOnUnmount: true },
});
```
