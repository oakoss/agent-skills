---
title: Loader Data Flow Patterns
description: ensureQueryData in loaders, parallel loading, critical vs non-critical data, search-param-dependent loaders, and useSuspenseQuery
tags:
  [
    loaders,
    ensureQueryData,
    useSuspenseQuery,
    parallel,
    prefetch,
    queryOptions,
    loaderDeps,
    validateSearch,
  ]
---

# Loader Data Flow Patterns

## Define Reusable Query Options

```tsx
// lib/queries/posts.ts
import { queryOptions } from '@tanstack/react-query';

export const postQueries = {
  all: () =>
    queryOptions({
      queryKey: ['posts'],
      queryFn: fetchPosts,
      staleTime: 5 * 60 * 1000,
    }),
  detail: (id: string) =>
    queryOptions({
      queryKey: ['posts', id],
      queryFn: () => fetchPost(id),
      staleTime: 5 * 60 * 1000,
    }),
  comments: (postId: string) =>
    queryOptions({
      queryKey: ['posts', postId, 'comments'],
      queryFn: () => fetchComments(postId),
    }),
};
```

## Basic Loader + Component Pattern

Prefetch in loaders, consume with `useSuspenseQuery`:

```tsx
// routes/posts.tsx
export const Route = createFileRoute('/posts')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(postQueries.all());
  },
  component: PostsPage,
});

function PostsPage() {
  const { data: posts } = useSuspenseQuery(postQueries.all());
  return <PostList posts={posts} />;
}
```

## Parallel Data Loading

```tsx
export const Route = createFileRoute('/dashboard')({
  loader: async ({ context: { queryClient } }) => {
    await Promise.all([
      queryClient.ensureQueryData(statsQueries.overview()),
      queryClient.ensureQueryData(activityQueries.recent()),
      queryClient.ensureQueryData(userQueries.current()),
    ]);
  },
  component: DashboardPage,
});

function DashboardPage() {
  const { data: stats } = useSuspenseQuery(statsQueries.overview());
  const { data: activity } = useSuspenseQuery(activityQueries.recent());
  const { data: user } = useSuspenseQuery(userQueries.current());
  return <Dashboard stats={stats} activity={activity} user={user} />;
}
```

## Critical vs Non-Critical Data

```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    // Critical - await it
    await queryClient.ensureQueryData(postQueries.detail(params.postId));
    // Non-critical - prefetch but don't block
    queryClient.prefetchQuery(postQueries.comments(params.postId));
  },
  component: PostPage,
});

function PostPage() {
  const { postId } = Route.useParams();
  const { data: post } = useSuspenseQuery(postQueries.detail(postId));
  const { data: comments, isLoading } = useQuery(postQueries.comments(postId));

  return (
    <article>
      <PostContent post={post} />
      {isLoading ? <CommentsSkeleton /> : <Comments data={comments} />}
    </article>
  );
}
```

## Search-Param-Dependent Loaders

Use `loaderDeps` to re-run loaders when search params change:

```tsx
import { createFileRoute } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { useSuspenseQuery } from '@tanstack/react-query';
import { z } from 'zod';

const searchSchema = z.object({
  page: z.number().default(1),
  size: z.number().default(10),
  sort: z.enum(['name', 'email', 'createdAt']).default('createdAt'),
  filter: z.string().optional(),
});

export const Route = createFileRoute('/admin/users')({
  validateSearch: zodValidator(searchSchema),
  loaderDeps: ({ search }) => search,
  loader: async ({ context: { queryClient }, deps }) => {
    await queryClient.ensureQueryData(userQueries.list(deps));
  },
  component: UsersPage,
});

function UsersPage() {
  const search = Route.useSearch();
  const { data } = useSuspenseQuery(userQueries.list(search));
  return <UserTable data={data} />;
}
```

`loaderDeps` declares which values the loader depends on. When those values change (search params update), the loader re-runs. Without `loaderDeps`, the loader only runs on initial navigation.

## Data Flow Summary

```text
Navigation Starts
       |
Router matches route
       |
loader() executes
       |
ensureQueryData() checks cache
       |
Fresh cache? -> Return cached     Stale/missing? -> Fetch and cache
       |                                    |
Route renders                         Route renders
       |                                    |
useSuspenseQuery returns data     useSuspenseQuery returns data
```

## Key Points

- `ensureQueryData` respects `staleTime` -- won't refetch fresh data
- `useSuspenseQuery` throws promise to Suspense if data missing
- Loaders enable preloading on link hover via `defaultPreload: 'intent'`
- Use `useQuery` (not `useSuspenseQuery`) for non-critical data that can load after render
- Query invalidation and background updates still work normally
