---
title: Grid Virtualization
description: 2D grid virtualization with row and column virtualizers, dynamic cell sizing, and indexAttribute configuration
tags:
  [grid, row-virtualizer, column-virtualizer, 2D, indexAttribute, getTotalSize]
---

# Grid Virtualization

## Basic Grid with Two Virtualizers

Grids require two `useVirtualizer` instances -- one for rows (vertical) and one for columns (horizontal) -- sharing the same scroll element.

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualGrid({
  data,
  rowCount,
  columnCount,
}: {
  data: string[][];
  rowCount: number;
  columnCount: number;
}) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: columnCount,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150,
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '500px', width: '800px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: `${columnVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <React.Fragment key={virtualRow.key}>
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: `${virtualColumn.size}px`,
                  height: `${virtualRow.size}px`,
                  transform: `translateX(${virtualColumn.start}px) translateY(${virtualRow.start}px)`,
                }}
              >
                {data[virtualRow.index][virtualColumn.index]}
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

The inner container dimensions use both `rowVirtualizer.getTotalSize()` for height and `columnVirtualizer.getTotalSize()` for width. Each cell is positioned with both `translateX` and `translateY`.

## Grid with Variable Cell Sizes

```tsx
function VariableGrid({
  data,
  rowSizes,
  columnSizes,
}: {
  data: string[][];
  rowSizes: number[];
  columnSizes: number[];
}) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rowSizes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (i) => rowSizes[i],
    overscan: 5,
  });

  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: columnSizes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (i) => columnSizes[i],
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '500px', width: '800px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: `${columnVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <React.Fragment key={virtualRow.key}>
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: `${columnSizes[virtualColumn.index]}px`,
                  height: `${rowSizes[virtualRow.index]}px`,
                  transform: `translateX(${virtualColumn.start}px) translateY(${virtualRow.start}px)`,
                }}
              >
                {data[virtualRow.index][virtualColumn.index]}
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

When sizes are known ahead of time, pass them directly via `estimateSize`. This avoids the need for `measureElement` and prevents layout shifts.

## Dynamic Grid with measureElement

When cell sizes are determined by content, use `measureElement` with custom `indexAttribute` values to distinguish row and column indices.

```tsx
function DynamicGrid({ data }: { data: string[][] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    indexAttribute: 'data-row-index',
  });

  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: data[0].length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150,
    indexAttribute: 'data-column-index',
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '500px', width: '800px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: `${columnVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <React.Fragment key={virtualRow.key}>
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                data-row-index={virtualRow.index}
                data-column-index={virtualColumn.index}
                ref={(el) => {
                  rowVirtualizer.measureElement(el);
                  columnVirtualizer.measureElement(el);
                }}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: `${virtualColumn.size}px`,
                  height: `${virtualRow.size}px`,
                  transform: `translateX(${virtualColumn.start}px) translateY(${virtualRow.start}px)`,
                }}
              >
                {data[virtualRow.index][virtualColumn.index]}
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

The `indexAttribute` option tells each virtualizer which data attribute to read for index lookup. The default is `data-index`, but grids need separate attributes so each virtualizer reads the correct axis.

## Programmatic Scroll in Grids

```tsx
function scrollToCell(
  rowVirtualizer: Virtualizer<HTMLDivElement, Element>,
  columnVirtualizer: Virtualizer<HTMLDivElement, Element>,
  rowIndex: number,
  columnIndex: number,
) {
  rowVirtualizer.scrollToIndex(rowIndex, { align: 'start' });
  columnVirtualizer.scrollToIndex(columnIndex, { align: 'start' });
}
```

Call both virtualizers to scroll to a specific cell. The scroll operations happen on the same element and combine naturally.

## Grid with Fixed Header Row

```tsx
function GridWithHeader({
  headers,
  data,
}: {
  headers: string[];
  data: string[][];
}) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 5,
  });

  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: headers.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150,
    overscan: 3,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '500px', width: '100%', overflow: 'auto' }}
    >
      <div style={{ position: 'sticky', top: 0, zIndex: 1, display: 'flex' }}>
        {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
          <div
            key={virtualColumn.key}
            style={{
              width: `${virtualColumn.size}px`,
              flexShrink: 0,
              fontWeight: 'bold',
              borderBottom: '2px solid #ccc',
              padding: '8px',
            }}
          >
            {headers[virtualColumn.index]}
          </div>
        ))}
      </div>
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: `${columnVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <React.Fragment key={virtualRow.key}>
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: `${virtualColumn.size}px`,
                  height: `${virtualRow.size}px`,
                  transform: `translateX(${virtualColumn.start}px) translateY(${virtualRow.start}px)`,
                  padding: '8px',
                  borderBottom: '1px solid #eee',
                }}
              >
                {data[virtualRow.index][virtualColumn.index]}
              </div>
            ))}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

Use `position: sticky` for the header row so it stays visible while the virtualized body scrolls underneath.
