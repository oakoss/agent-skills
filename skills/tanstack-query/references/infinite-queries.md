---
title: Infinite Queries
description: Paginated data with useInfiniteQuery, cursor-based pagination, intersection observer auto-loading, and maxPages optimization
tags:
  [
    useInfiniteQuery,
    pagination,
    cursor,
    getNextPageParam,
    maxPages,
    infinite-scroll,
  ]
---

# Infinite Queries

```tsx
import { infiniteQueryOptions, useInfiniteQuery } from '@tanstack/react-query';

const todosInfiniteOptions = infiniteQueryOptions({
  queryKey: ['todos', 'infinite'],
  queryFn: ({ pageParam }) => fetchTodosPage(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
});

useInfiniteQuery(todosInfiniteOptions);
```

Memory optimization with `maxPages` limits how many pages are kept in cache. When the user scrolls forward past the limit, old pages are dropped. Requires `getPreviousPageParam` so dropped pages can be re-fetched when scrolling back (bi-directional pagination):

```tsx
useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam }) => fetchPosts(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage) => firstPage.prevCursor,
  maxPages: 3, // Only keep 3 pages in memory at a time
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

      {/* Sentinel element */}
      <div ref={ref} className="h-10">
        {isFetchingNextPage && <Spinner />}
      </div>
    </>
  );
}
```

## Bidirectional Infinite Scroll

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

```tsx
import { keepPreviousData } from '@tanstack/react-query';

function postsPageOptions(page: number) {
  return queryOptions({
    queryKey: ['posts', 'paginated', { page }],
    queryFn: () => fetchPostsPage(page),
    placeholderData: keepPreviousData, // Keep old data while fetching new page
  });
}
```
