---
title: Data Fetching
description: TanStack Query for client-side fetching with caching and mutations, Server Components for server-side data, and cache revalidation patterns
tags:
  [
    data-fetching,
    tanstack-query,
    server-components,
    revalidation,
    cache,
    react-query,
  ]
---

# Data Fetching

## Decision Tree

| Scenario                            | Approach                                              |
| ----------------------------------- | ----------------------------------------------------- |
| Static or semi-static data          | Server Component with `fetch`                         |
| User-specific server data           | Server Component (reads cookies/headers)              |
| Interactive list with filters       | Server Component initial + TanStack Query client-side |
| Real-time or frequently polled data | TanStack Query with `refetchInterval`                 |
| Mutations (create, update, delete)  | Server Actions or TanStack Query `useMutation`        |
| Infinite scroll / pagination        | TanStack Query `useInfiniteQuery`                     |

## Server Component Data Fetching

Server Components can fetch data directly using `async`/`await`. No client-side JavaScript is shipped for the data-fetching logic.

```tsx
// app/products/page.tsx
import { Suspense } from 'react';

export default function ProductsPage() {
  return (
    <div>
      <h1>Products</h1>
      <Suspense fallback={<ProductsSkeleton />}>
        <ProductList />
      </Suspense>
    </div>
  );
}

async function ProductList() {
  const products = await db.select().from(productsTable);

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### Parallel Data Fetching

```tsx
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const [stats, recentOrders, topProducts] = await Promise.all([
    fetchStats(),
    fetchRecentOrders(),
    fetchTopProducts(),
  ]);

  return (
    <div>
      <StatsGrid stats={stats} />
      <RecentOrders orders={recentOrders} />
      <TopProducts products={topProducts} />
    </div>
  );
}
```

## TanStack Query (Client-Side)

Use TanStack Query when you need client-side caching, background refetching, optimistic updates, or interactive data management.

### Provider Setup

```tsx
// providers/query-provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            gcTime: 5 * 60 * 1000,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

### Queries

```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then((r) => r.json()),
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <Skeleton className="h-32" />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### Dependent Queries

```tsx
function UserPosts({ userId }: { userId: string }) {
  const { data: user } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetchUser(userId),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts', { authorId: user?.id }],
    queryFn: () => fetchPostsByAuthor(user!.id),
    enabled: !!user,
  });

  return posts ? <PostList posts={posts} /> : <Skeleton />;
}
```

### Mutations with Invalidation

```tsx
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreatePostForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: { title: string; body: string }) =>
      fetch('/api/posts', {
        method: 'POST',
        body: JSON.stringify(data),
      }).then((r) => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        mutation.mutate({
          title: formData.get('title') as string,
          body: formData.get('body') as string,
        });
      }}
    >
      <input name="title" required />
      <textarea name="body" required />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create Post'}
      </button>
      {mutation.isError ? (
        <p className="text-destructive">{mutation.error.message}</p>
      ) : null}
    </form>
  );
}
```

### Optimistic Updates

```tsx
const mutation = useMutation({
  mutationFn: toggleLike,
  onMutate: async (postId: string) => {
    await queryClient.cancelQueries({ queryKey: ['posts', postId] });
    const previous = queryClient.getQueryData<Post>(['posts', postId]);

    queryClient.setQueryData<Post>(['posts', postId], (old) =>
      old
        ? {
            ...old,
            liked: !old.liked,
            likeCount: old.liked ? old.likeCount - 1 : old.likeCount + 1,
          }
        : old,
    );

    return { previous };
  },
  onError: (_err, postId, context) => {
    queryClient.setQueryData(['posts', postId], context?.previous);
  },
  onSettled: (_data, _err, postId) => {
    queryClient.invalidateQueries({ queryKey: ['posts', postId] });
  },
});
```

## Cache Revalidation (Server Actions)

After mutations via Server Actions, revalidate the Next.js cache to reflect changes.

```tsx
// app/posts/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { revalidateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  await db.insert(posts).values({
    title: formData.get('title') as string,
    body: formData.get('body') as string,
  });

  revalidatePath('/posts');
}

export async function updatePost(id: string, formData: FormData) {
  await db
    .update(posts)
    .set({ title: formData.get('title') as string })
    .where(eq(posts.id, id));

  revalidateTag(`post-${id}`);
  revalidatePath('/posts');
}
```

### Tag-Based Revalidation

```tsx
// app/posts/[id]/page.tsx
export default async function PostPage({ params }: { params: { id: string } }) {
  const post = await fetch(`${API_URL}/posts/${params.id}`, {
    next: { tags: [`post-${params.id}`] },
  }).then((r) => r.json());

  return <PostContent post={post} />;
}
```

## API Client Pattern

Centralize API calls with a typed client to avoid scattered `fetch` calls.

```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '/api';

async function apiClient<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export const api = {
  users: {
    list: () => apiClient<User[]>('/users'),
    get: (id: string) => apiClient<User>(`/users/${id}`),
    create: (data: CreateUser) =>
      apiClient<User>('/users', { method: 'POST', body: JSON.stringify(data) }),
  },
  posts: {
    list: () => apiClient<Post[]>('/posts'),
    get: (id: string) => apiClient<Post>(`/posts/${id}`),
  },
};
```
