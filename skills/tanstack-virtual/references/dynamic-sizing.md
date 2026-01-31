---
title: Dynamic Sizing
description: Dynamic item measurement with measureElement, variable height rows, auto-sizing content, and resize handling
tags:
  [
    measureElement,
    dynamic,
    variable-height,
    auto-size,
    resize,
    estimateSize,
    data-index,
  ]
---

# Dynamic Sizing

## measureElement for Auto-Sized Rows

When item heights depend on content, use `measureElement` as the ref callback to measure each item after rendering.

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function DynamicList({ sentences }: { sentences: string[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: sentences.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{
        height: '400px',
        overflow: 'auto',
        contain: 'strict',
      }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            transform: `translateY(${virtualizer.getVirtualItems()[0]?.start ?? 0}px)`,
          }}
        >
          {virtualizer.getVirtualItems().map((virtualRow) => (
            <div
              key={virtualRow.key}
              data-index={virtualRow.index}
              ref={virtualizer.measureElement}
            >
              <div style={{ padding: '10px 0' }}>
                {sentences[virtualRow.index]}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

Key requirements for `measureElement`:

- Set `data-index={virtualRow.index}` on the measured element
- Pass `virtualizer.measureElement` as the `ref` callback
- The element must be in the DOM when measured (no conditional rendering of the ref target)

This example uses a wrapper div pattern where items are positioned as a group using `translateY` of the first item's start offset, rather than positioning each item individually. Both patterns work.

## Overestimate for Smooth Scrolling

`estimateSize` provides the initial size before measurement. Setting it too low causes scroll jumping as items expand after measurement.

```tsx
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 100,
  overscan: 5,
});
```

Use the largest expected item size as the estimate. When items shrink after measurement, scrolling feels natural. When items grow after measurement, the scrollbar jumps.

## Variable Heights with Known Sizes

When sizes are known upfront (not from content measurement), pass them directly to `estimateSize`:

```tsx
const rowHeights = items.map((item) =>
  item.type === 'header' ? 60 : item.type === 'expanded' ? 120 : 40,
);

const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: (index) => rowHeights[index],
});
```

This is faster than `measureElement` because no DOM measurement is needed.

## Force Remeasure After Layout Changes

When external factors change item sizes (window resize, sidebar toggle, font loading), call `measure()` to invalidate cached measurements:

```tsx
function ResizableList({ items }: { items: string[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  React.useEffect(() => {
    const observer = new ResizeObserver(() => {
      virtualizer.measure();
    });

    if (parentRef.current) {
      observer.observe(parentRef.current);
    }

    return () => observer.disconnect();
  }, [virtualizer]);

  return (
    <div ref={parentRef} style={{ height: '100%', overflow: 'auto' }}>
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
            data-index={virtualItem.index}
            ref={virtualizer.measureElement}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Expandable Rows

When rows toggle between collapsed and expanded states, the virtualizer remeasures automatically through `measureElement`:

```tsx
function ExpandableList({
  items,
}: {
  items: { id: string; title: string; details: string }[];
}) {
  const parentRef = React.useRef<HTMLDivElement>(null);
  const [expandedIds, setExpandedIds] = React.useState<Set<string>>(new Set());

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    getItemKey: (index) => items[index].id,
  });

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = items[virtualItem.index];
          const isExpanded = expandedIds.has(item.id);

          return (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              ref={virtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <button onClick={() => toggleExpanded(item.id)}>
                {item.title}
              </button>
              {isExpanded ? <div>{item.details}</div> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

Using `getItemKey` with stable IDs ensures measurement caches persist correctly when items expand or collapse, avoiding size flickering during re-renders.

## Performance Tips for Dynamic Sizing

| Tip                                              | Why                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------- |
| Use `contain: strict` on scroll container        | Isolates layout recalculations to the container                             |
| Set `overflowAnchor: 'none'` on scroll container | Prevents browser scroll anchoring from conflicting with virtual positioning |
| Increase `overscan` for dynamic content          | Extra off-screen items prevent visible blank areas during fast scrolling    |
| Use `getItemKey` with stable IDs                 | Measurement cache survives list reorders                                    |
| Avoid measuring inside `useEffect`               | Let `measureElement` handle timing via ref callbacks                        |
