---
title: Data Loading
description: Route loaders, TanStack Query integration with ensureQueryData, parallel loading with timeline visualization, streaming with prefetchQuery and defer, abort signals, and loader dependencies with loaderDeps
tags:
  [
    loader,
    data-loading,
    ensureQueryData,
    prefetchQuery,
    defer,
    streaming,
    parallel-loading,
    loaderDeps,
    useAwaited,
  ]
---

# Data Loading

## Route Loaders

Loaders execute before render, preventing loading waterfalls:

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => ({
    post: await fetchPost(params.postId),
  }),
  component: () => {
    const { post } = Route.useLoaderData();
    return <h1>{post.title}</h1>;
  },
});
```

## TanStack Query Integration

Use `ensureQueryData`, not `prefetchQuery`:

```ts
const postOpts = (id: string) =>
  queryOptions({
    queryKey: ['posts', id],
    queryFn: () => fetchPost(id),
  });

export const Route = createFileRoute('/posts/$postId')({
  loader: ({ context: { queryClient }, params }) =>
    queryClient.ensureQueryData(postOpts(params.postId)),
  component: () => {
    const { postId } = Route.useParams();
    const { data } = useSuspenseQuery(postOpts(postId));
    return <h1>{data.title}</h1>;
  },
});
```

## Parallel Loading

Nested routes load in parallel by default. Within a single loader, use `Promise.all`:

```ts
export const Route = createFileRoute('/dashboard')({
  beforeLoad: async () => {
    const [user, config] = await Promise.all([fetchUser(), fetchAppConfig()]);
    return { user, config };
  },
  loader: async ({ context: { queryClient } }) => {
    await Promise.all([
      queryClient.ensureQueryData(statsQueries.overview()),
      queryClient.ensureQueryData(activityQueries.recent()),
    ]);
  },
});
```

Parent and child loaders run simultaneously:

```ts
// routes/posts.tsx — runs in parallel with child
export const Route = createFileRoute('/posts')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(categoryQueries.all());
  },
});

// routes/posts/$postId.tsx — runs in parallel with parent
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    await Promise.all([
      queryClient.ensureQueryData(postQueries.detail(params.postId)),
      queryClient.ensureQueryData(commentQueries.forPost(params.postId)),
    ]);
  },
});
```

Loading timeline comparison:

```sh
Without parallelization:
|- beforeLoad (parent)  ========
|- loader (parent)              ========
|- beforeLoad (child)                   ====
|- loader (child)                           ========
|- Render                                           =

With parallelization:
|- beforeLoad (parent)  ========
|- beforeLoad (child)   ====
|- loader (parent)      ========
|- loader (child)       ============
|- Render                           =
```

Key rules: `beforeLoad` runs before `loader` (for auth, context setup). Parent context is available in child loaders only after `beforeLoad` completes.

## Streaming Non-Critical Data

Await critical data, prefetch the rest:

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    const post = await queryClient.ensureQueryData(
      postQueries.detail(params.postId),
    );

    queryClient.prefetchQuery(commentQueries.forPost(params.postId));
    queryClient.prefetchQuery(relatedQueries.forPost(params.postId));

    return { post };
  },
  component: PostPage,
});

function PostPage() {
  const { post } = Route.useLoaderData();
  const { postId } = Route.useParams();

  const { data: comments, isLoading } = useQuery(
    commentQueries.forPost(postId),
  );

  return (
    <article>
      <PostContent post={post} />
      {isLoading ? <CommentsSkeleton /> : <Comments data={comments} />}
    </article>
  );
}
```

## Deferred Data

Stream non-critical data after initial render by returning unawaited promises from loaders. Promises are handled automatically — `defer()` is no longer required. Consume deferred promises with the `<Await>` component or the `useAwaited` hook:

```tsx
export const Route = createFileRoute('/dashboard')({
  loader: async () => {
    const user = await fetchUser();
    return {
      user,
      stats: fetchStats(),
      activity: fetchActivity(),
    };
  },
  component: () => {
    const { user, stats, activity } = Route.useLoaderData();
    return (
      <div>
        <h1>Welcome, {user.name}</h1>
        <Suspense fallback={<StatsSkeleton />}>
          <Await promise={stats}>
            {(data) => <StatsDisplay data={data} />}
          </Await>
        </Suspense>
        <Suspense fallback={<ActivitySkeleton />}>
          <Await promise={activity}>
            {(data) => <ActivityFeed data={data} />}
          </Await>
        </Suspense>
      </div>
    );
  },
});
```

### `useAwaited` Hook

Hook-based alternative to `<Await>` — suspends until the deferred promise resolves:

```tsx
import { useAwaited } from '@tanstack/react-router';

function StatsPanel() {
  const { stats } = Route.useLoaderData();
  const data = useAwaited({ promise: stats });
  return <StatsDisplay data={data} />;
}
```

## Loader Cause and Preload

Loaders receive `cause` and `preload` to distinguish navigation types:

| `cause`     | Description                          |
| ----------- | ------------------------------------ |
| `'preload'` | Triggered by link hover/focus        |
| `'enter'`   | Initial navigation to route          |
| `'stay'`    | Route re-entered (search/dep change) |

Use `preload` to conditionally load less data during prefetching:

```ts
loader: async ({ preload, context: { queryClient } }) => {
  if (preload) {
    await queryClient.prefetchQuery(postListOptions);
    return;
  }
  const [posts, stats] = await Promise.all([
    queryClient.ensureQueryData(postListOptions),
    queryClient.ensureQueryData(statsOptions),
  ]);
  return { posts, stats };
};
```

## Abort Signal

Cancel in-flight requests on navigation:

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, abortController }) => {
    const response = await fetch(`/api/posts/${params.postId}`, {
      signal: abortController.signal,
    });
    if (!response.ok) {
      if (response.status === 404) throw notFound();
      throw new Error('Failed to fetch post');
    }
    return response.json();
  },
});
```

## Loader Dependencies

Declare which search params the loader depends on so it only re-runs when those change:

```ts
export const Route = createFileRoute('/posts')({
  validateSearch: z.object({ page: z.number().default(1) }),
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: async ({ deps }) => fetchPosts({ page: deps.page }),
});
```

### Preventing Unnecessary Re-Fetches

Without `loaderDeps`, the loader re-runs on every search param change. With `loaderDeps`, it only re-runs when the returned value changes (compared via structural sharing):

```ts
export const Route = createFileRoute('/products')({
  validateSearch: z.object({
    page: z.number().default(1),
    sort: z.enum(['name', 'price']).default('name'),
    highlight: z.string().optional(),
  }),
  loaderDeps: ({ search }) => ({
    page: search.page,
    sort: search.sort,
  }),
  loader: async ({ deps }) => fetchProducts(deps),
});
```

Changing `highlight` (cosmetic param) does not re-run the loader. Only `page` and `sort` trigger re-fetches. Return only the values the loader actually uses.

When using TanStack Query, `loaderDeps` and `queryKey` serve complementary roles: `loaderDeps` controls when the loader re-runs, and `queryKey` controls Query's cache identity. Keep them aligned:

```ts
const productOpts = (deps: { page: number; sort: string }) =>
  queryOptions({
    queryKey: ['products', deps],
    queryFn: () => fetchProducts(deps),
  });

export const Route = createFileRoute('/products')({
  loaderDeps: ({ search }) => ({ page: search.page, sort: search.sort }),
  loader: ({ deps, context: { queryClient } }) =>
    queryClient.ensureQueryData(productOpts(deps)),
});
```

## Automatic Suspense

Every route wraps in `<Suspense>` and `<ErrorBoundary>` automatically. Route components only need happy-path rendering:

```ts
function PostPage() {
  const { data } = useSuspenseQuery(postOptions(postId));
  //      ^? Post (guaranteed, never undefined)
  return <h1>{data.title}</h1>;
}
```
