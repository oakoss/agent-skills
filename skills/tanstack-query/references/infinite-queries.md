---
title: Infinite Queries
description: Paginated data with useInfiniteQuery, infiniteQueryOptions, cursor-based pagination, intersection observer auto-loading, maxPages optimization, and select for page flattening
tags:
  [
    useInfiniteQuery,
    infiniteQueryOptions,
    pagination,
    cursor,
    getNextPageParam,
    maxPages,
    infinite-scroll,
  ]
---

# Infinite Queries

## Basic Setup with infiniteQueryOptions

```tsx
import { infiniteQueryOptions, useInfiniteQuery } from '@tanstack/react-query';

const todosInfiniteOptions = infiniteQueryOptions({
  queryKey: ['todos', 'infinite'],
  queryFn: ({ pageParam }) => fetchTodosPage(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
});

const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
  useInfiniteQuery(todosInfiniteOptions);
```

`infiniteQueryOptions` is the infinite-query equivalent of `queryOptions`. It provides type-safe, reusable configuration for `useInfiniteQuery`, `useSuspenseInfiniteQuery`, and `queryClient.prefetchInfiniteQuery`.

## Rendering Pages

```tsx
{
  data?.pages.map((page, i) => (
    <Fragment key={i}>
      {page.items.map((item) => (
        <ItemCard key={item.id} item={item} />
      ))}
    </Fragment>
  ));
}
```

## Flattening Pages with select

Transform the nested pages structure into a flat array:

```tsx
const { data } = useInfiniteQuery({
  queryKey: ['todos', 'infinite'],
  queryFn: ({ pageParam }) => fetchTodosPage(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  select: (data) => ({
    ...data,
    pages: data.pages.flatMap((page) => page.items),
  }),
});

// data.pages is now a flat array of items
```

## Memory Optimization with maxPages

`maxPages` limits how many pages are kept in cache. When the user scrolls forward past the limit, old pages are dropped. Requires `getPreviousPageParam` so dropped pages can be re-fetched when scrolling back (bi-directional pagination):

```tsx
useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam }) => fetchPosts(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage) => firstPage.prevCursor,
  maxPages: 3,
});
```

Without `maxPages`, infinite queries accumulate all fetched pages in memory and refetch all of them on invalidation. For long lists, this causes memory bloat and slow refetches.

## Intersection Observer Auto-Loading

```tsx
import { useInView } from 'react-intersection-observer';

function InfinitePostList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery(postsInfiniteOptions());

  const { ref, inView } = useInView({ threshold: 0 });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <>
      {data?.pages.map((page, i) => (
        <Fragment key={i}>
          {page.items.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </Fragment>
      ))}

      <div ref={ref} className="h-10">
        {isFetchingNextPage && <Spinner />}
      </div>
    </>
  );
}
```

## Bidirectional Infinite Scroll

For chat-style UIs where you load older messages upward and newer messages downward:

```tsx
const { data, fetchNextPage, fetchPreviousPage, hasPreviousPage, hasNextPage } =
  useInfiniteQuery({
    queryKey: ['messages', chatId],
    queryFn: ({ pageParam }) =>
      getMessages({
        chatId,
        cursor: pageParam.cursor,
        direction: pageParam.direction,
      }),
    initialPageParam: { cursor: undefined, direction: 'backward' as const },
    getNextPageParam: (lastPage) =>
      lastPage.nextCursor
        ? { cursor: lastPage.nextCursor, direction: 'forward' as const }
        : undefined,
    getPreviousPageParam: (firstPage) =>
      firstPage.prevCursor
        ? { cursor: firstPage.prevCursor, direction: 'backward' as const }
        : undefined,
  });
```

## Offset-Based Pagination

For traditional page-number pagination (not infinite scroll), use standard `useQuery` with `keepPreviousData`:

```tsx
import { keepPreviousData } from '@tanstack/react-query';

function postsPageOptions(page: number) {
  return queryOptions({
    queryKey: ['posts', 'paginated', { page }],
    queryFn: () => fetchPostsPage(page),
    placeholderData: keepPreviousData,
  });
}

function PaginatedPosts() {
  const [page, setPage] = useState(1);
  const { data, isPlaceholderData } = useQuery(postsPageOptions(page));

  return (
    <div className={isPlaceholderData ? 'opacity-50' : ''}>
      {data?.items.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
        Previous
      </button>
      <button
        disabled={isPlaceholderData || !data?.hasMore}
        onClick={() => setPage((p) => p + 1)}
      >
        Next
      </button>
    </div>
  );
}
```

`keepPreviousData` keeps the old page visible while the new page loads, preventing layout shift.

## Prefetching Next Page

Prefetch the next page while the user views the current one:

```tsx
const queryClient = useQueryClient();

useEffect(() => {
  if (!isPlaceholderData && data?.hasMore) {
    queryClient.prefetchQuery(postsPageOptions(page + 1));
  }
}, [data, isPlaceholderData, page, queryClient]);
```
