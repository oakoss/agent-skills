---
title: List Virtualization
description: Vertical and horizontal list virtualization with useVirtualizer, estimateSize, overscan, scrollToIndex, and useWindowVirtualizer
tags:
  [
    useVirtualizer,
    useWindowVirtualizer,
    vertical,
    horizontal,
    estimateSize,
    overscan,
    scrollToIndex,
    getVirtualItems,
  ]
---

# List Virtualization

## Basic Vertical List

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: string[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
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
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

The three-layer DOM structure is required:

1. **Scroll container** (`parentRef`) -- fixed height, `overflow: auto`
2. **Inner container** -- height set to `getTotalSize()`, `position: relative`
3. **Virtual items** -- absolute positioned, translated to `virtualItem.start`

## Horizontal List

```tsx
function HorizontalList({ items }: { items: string[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    horizontal: true,
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ width: '600px', overflow: 'auto' }}>
      <div
        style={{
          width: `${virtualizer.getTotalSize()}px`,
          height: '100%',
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
              height: '100%',
              width: `${virtualItem.size}px`,
              transform: `translateX(${virtualItem.start}px)`,
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

For horizontal lists, swap height for width in the inner container and use `translateX` instead of `translateY`.

## Window Scroller

`useWindowVirtualizer` uses the browser window as the scroll container instead of a specific element.

```tsx
import { useWindowVirtualizer } from '@tanstack/react-virtual';

function WindowVirtualList({ items }: { items: string[] }) {
  const virtualizer = useWindowVirtualizer({
    count: items.length,
    estimateSize: () => 45,
    overscan: 5,
  });

  return (
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
          {items[virtualItem.index]}
        </div>
      ))}
    </div>
  );
}
```

No `getScrollElement` is needed -- the hook attaches to the window automatically.

## Scroll to Index

```tsx
function ScrollableList({ items }: { items: string[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
  });

  return (
    <div>
      <button onClick={() => virtualizer.scrollToIndex(0)}>Top</button>
      <button onClick={() => virtualizer.scrollToIndex(items.length - 1)}>
        Bottom
      </button>
      <button
        onClick={() =>
          virtualizer.scrollToIndex(Math.floor(items.length / 2), {
            align: 'center',
            behavior: 'smooth',
          })
        }
      >
        Middle
      </button>
      <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
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
              {items[virtualItem.index]}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

The `align` option controls where the target item appears: `'start'`, `'center'`, `'end'`, or `'auto'` (default, scrolls minimum distance).

## Stable Item Keys

When items can be reordered or the list changes, provide stable keys for measurement caching:

```tsx
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 35,
  getItemKey: (index) => items[index].id,
});
```

## Virtualizer Options Reference

| Option             | Type                         | Default    | Description                           |
| ------------------ | ---------------------------- | ---------- | ------------------------------------- |
| `count`            | `number`                     | required   | Total number of items                 |
| `getScrollElement` | `() => Element \| null`      | required   | Returns the scrollable container      |
| `estimateSize`     | `(index: number) => number`  | required   | Estimated item size in pixels         |
| `overscan`         | `number`                     | `1`        | Extra items rendered outside viewport |
| `horizontal`       | `boolean`                    | `false`    | Enable horizontal orientation         |
| `paddingStart`     | `number`                     | `0`        | Padding before first item             |
| `paddingEnd`       | `number`                     | `0`        | Padding after last item               |
| `gap`              | `number`                     | `0`        | Space between items                   |
| `lanes`            | `number`                     | `1`        | Multi-column lane count               |
| `enabled`          | `boolean`                    | `true`     | Enable or disable the virtualizer     |
| `isRtl`            | `boolean`                    | `false`    | Right-to-left layout                  |
| `getItemKey`       | `(index: number) => Key`     | `(i) => i` | Stable key for each item              |
| `rangeExtractor`   | `(range: Range) => number[]` | built-in   | Customize which indices to render     |
| `scrollMargin`     | `number`                     | `0`        | Margin for scroll positioning         |
| `initialOffset`    | `number`                     | `0`        | Starting scroll position              |

## VirtualItem Properties

| Property | Type     | Description                       |
| -------- | -------- | --------------------------------- |
| `key`    | `Key`    | Unique key for React rendering    |
| `index`  | `number` | Index in the original list        |
| `start`  | `number` | Pixel offset from container start |
| `end`    | `number` | Pixel offset of item end          |
| `size`   | `number` | Measured or estimated item size   |
| `lane`   | `number` | Lane index for multi-lane layouts |
