---
title: Infinite Scroll
description: Infinite scroll patterns combining TanStack Virtual with TanStack Query, scroll detection, loading indicators, and bidirectional scrolling
tags:
  [
    infinite-scroll,
    useInfiniteQuery,
    intersection-observer,
    fetchNextPage,
    loading,
    bidirectional,
  ]
---

# Infinite Scroll

## Basic Infinite Scroll with TanStack Query

Combine `useInfiniteQuery` for data fetching with `useVirtualizer` for rendering. Detect when the user scrolls near the end and fetch the next page.

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';

interface Page {
  items: { id: string; name: string }[];
  nextCursor: string | null;
}

function InfiniteList() {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ['items'],
      queryFn: ({ pageParam }): Promise<Page> =>
        fetch(`/api/items?cursor=${pageParam}`).then((r) => r.json()),
      initialPageParam: '',
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    });

  const allItems = data?.pages.flatMap((page) => page.items) ?? [];

  const virtualizer = useVirtualizer({
    count: hasNextPage ? allItems.length + 1 : allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  React.useEffect(() => {
    const lastItem = virtualItems[virtualItems.length - 1];
    if (!lastItem) return;

    if (
      lastItem.index >= allItems.length - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage();
    }
  }, [
    virtualItems,
    allItems.length,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  ]);

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualItems.map((virtualItem) => {
          const isLoaderRow = virtualItem.index > allItems.length - 1;

          return (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              {isLoaderRow
                ? hasNextPage
                  ? 'Loading more...'
                  : 'Nothing more to load'
                : allItems[virtualItem.index].name}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

The count includes an extra item (`allItems.length + 1`) when more pages exist. This loader row triggers `fetchNextPage` when it becomes visible.

## Intersection Observer Approach

Use `IntersectionObserver` instead of checking virtual item indices for more precise scroll detection.

```tsx
function InfiniteListWithObserver() {
  const parentRef = React.useRef<HTMLDivElement>(null);
  const loadMoreRef = React.useRef<HTMLDivElement>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ['items'],
      queryFn: ({ pageParam }): Promise<Page> =>
        fetch(`/api/items?cursor=${pageParam}`).then((r) => r.json()),
      initialPageParam: '',
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    });

  const allItems = data?.pages.flatMap((page) => page.items) ?? [];

  const virtualizer = useVirtualizer({
    count: allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  React.useEffect(() => {
    const el = loadMoreRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { rootMargin: '200px' },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {allItems[virtualItem.index].name}
          </div>
        ))}
      </div>
      <div ref={loadMoreRef}>{isFetchingNextPage ? 'Loading...' : null}</div>
    </div>
  );
}
```

The `rootMargin: '200px'` triggers fetching before the sentinel element is visible, creating a smoother experience.

## Bidirectional Infinite Scroll

Load pages in both directions by combining `fetchNextPage` and `fetchPreviousPage`.

```tsx
function BidirectionalList() {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const {
    data,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage,
    hasPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
  } = useInfiniteQuery({
    queryKey: ['timeline'],
    queryFn: ({ pageParam }): Promise<Page> =>
      fetch(
        `/api/timeline?cursor=${pageParam.cursor}&direction=${pageParam.direction}`,
      ).then((r) => r.json()),
    initialPageParam: { cursor: '', direction: 'forward' as const },
    getNextPageParam: (lastPage) =>
      lastPage.nextCursor
        ? { cursor: lastPage.nextCursor, direction: 'forward' as const }
        : undefined,
    getPreviousPageParam: (firstPage) =>
      firstPage.previousCursor
        ? { cursor: firstPage.previousCursor, direction: 'backward' as const }
        : undefined,
  });

  const allItems = data?.pages.flatMap((page) => page.items) ?? [];

  const virtualizer = useVirtualizer({
    count: allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  React.useEffect(() => {
    if (!virtualItems.length) return;

    const firstItem = virtualItems[0];
    const lastItem = virtualItems[virtualItems.length - 1];

    if (firstItem.index <= 1 && hasPreviousPage && !isFetchingPreviousPage) {
      fetchPreviousPage();
    }

    if (
      lastItem.index >= allItems.length - 2 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage();
    }
  }, [
    virtualItems,
    allItems.length,
    hasNextPage,
    hasPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
    fetchNextPage,
    fetchPreviousPage,
  ]);

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      {isFetchingPreviousPage ? <div>Loading previous...</div> : null}
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualItems.map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {allItems[virtualItem.index].name}
          </div>
        ))}
      </div>
      {isFetchingNextPage ? <div>Loading more...</div> : null}
    </div>
  );
}
```

## Loading States

| State                    | Display                         |
| ------------------------ | ------------------------------- |
| `isFetchingNextPage`     | Spinner or skeleton at bottom   |
| `isFetchingPreviousPage` | Spinner or skeleton at top      |
| `!hasNextPage`           | "End of list" message           |
| `isLoading` (initial)    | Full-page skeleton or spinner   |
| `isError`                | Error message with retry button |

## Performance Considerations

| Concern                              | Solution                                                        |
| ------------------------------------ | --------------------------------------------------------------- |
| Flattening pages on every render     | Memoize `allItems` with `useMemo`                               |
| Too many DOM nodes from loaded pages | Virtual count grows with data; only visible items are rendered  |
| Memory from accumulated pages        | Use `maxPages` option on `useInfiniteQuery` to cap stored pages |
| Scroll position jumps on prepend     | Use `scrollMargin` or maintain scroll position manually         |
