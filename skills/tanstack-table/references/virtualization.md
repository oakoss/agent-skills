---
title: Virtualization
description: Using TanStack Virtual with TanStack Table for large dataset rendering, performance optimization, and hidden container workarounds
tags:
  [
    virtual,
    virtualization,
    useVirtualizer,
    react-virtual,
    overscan,
    estimateSize,
    performance,
    profiler,
    memoization,
    large-dataset,
    1000-rows,
  ]
---

# Virtualization

## When to Virtualize

- Client-side tables with **1000+ rows**
- Scrolling feels slow or janky
- Browser runs out of memory
- Need to render 10k+ rows efficiently

For datasets > 10k rows, prefer server-side pagination over client-side virtualization.

## Setup

```bash
npm install @tanstack/react-virtual
```

## Basic Virtualized Table

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';
import { useReactTable, getCoreRowModel } from '@tanstack/react-table';
import { useRef } from 'react';

function VirtualizedTable({ data, columns }) {
  const containerRef = useRef<HTMLDivElement>(null);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const { rows } = table.getRowModel();

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 50, // Estimated row height in px
    overscan: 10, // Extra rows rendered above/below viewport
  });

  return (
    <div ref={containerRef} style={{ height: '600px', overflow: 'auto' }}>
      <table style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id}>
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext(),
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const row = rows[virtualRow.index];
            return (
              <tr
                key={row.id}
                style={{
                  position: 'absolute',
                  transform: `translateY(${virtualRow.start}px)`,
                  height: `${virtualRow.size}px`,
                  width: '100%',
                }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

## Hidden Container Warning (Tabs/Modals)

When virtualization is used inside tabbed content or modals that hide inactive content with `display: none`, the virtualizer continues performing layout calculations while hidden.

**Symptoms:**

- Infinite re-render loops (especially with 50k+ rows)
- Incorrect scroll position when tab becomes visible
- Empty table or reset scroll position

**Source:** [GitHub Issue #6109](https://github.com/TanStack/table/issues/6109)

**Solutions:**

```tsx
// Option 1: Disable virtualizer when container is hidden
const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => containerRef.current,
  estimateSize: () => 50,
  overscan: 10,
  enabled: containerRef.current?.getClientRects().length !== 0,
});

// Option 2: Conditionally render instead of hiding with CSS
{
  isVisible && <VirtualizedTable />;
}
```

## Performance Optimization Tips

### 1. Memoize Data and Columns

```tsx
// New array every render causes re-renders
const data = useMemo(() => [...rawData], [rawData]);
```

### 2. Use Fixed Column Sizes

```tsx
const columns = [
  { accessorKey: 'id', header: 'ID', size: 80 },
  { accessorKey: 'name', header: 'Name', size: 200 },
];
```

### 3. Memoize Heavy Cell Renderers

```tsx
const MemoizedCell = React.memo(ExpensiveComponent);

// In column definition
{
  accessorKey: 'data',
  cell: (info) => <MemoizedCell data={info.getValue()} />,
}
```

### 4. Enable Row Selection Carefully

Row selection adds overhead — only enable when needed:

```tsx
enableRowSelection: true, // Only if needed
```

### 5. Tune Overscan

Higher overscan values give smoother scrolling but render more rows:

```tsx
const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => containerRef.current,
  estimateSize: () => 50,
  overscan: 5, // Lower for better performance, higher for smoother scroll
});
```

## Memoization Strategy

Memoize at three levels to minimize re-renders:

```tsx
// Level 1: Stable data reference
const data = useMemo(() => apiResponse?.data ?? [], [apiResponse?.data]);

// Level 2: Stable column definitions (define outside component or useMemo)
const columns = useMemo<ColumnDef<User>[]>(
  () => [
    { accessorKey: 'name', header: 'Name', size: 200 },
    { accessorKey: 'email', header: 'Email', size: 250 },
  ],
  [],
);

// Level 3: Memoize expensive cell renderers
const StatusCell = memo(({ status }: { status: string }) => (
  <Badge variant={status === 'active' ? 'default' : 'secondary'}>
    {status}
  </Badge>
));
```

Columns defined inline without `useMemo` create new references every render, causing the entire table to re-render. This is the most common performance mistake.

## Measuring Performance

### React Profiler

Wrap the table to measure render cost:

```tsx
import { Profiler } from 'react';

function onRender(
  id: string,
  phase: string,
  actualDuration: number,
  baseDuration: number,
) {
  if (actualDuration > 16) {
    console.warn(
      `${id} ${phase}: ${actualDuration.toFixed(1)}ms (base: ${baseDuration.toFixed(1)}ms)`,
    );
  }
}

<Profiler id="VirtualTable" onRender={onRender}>
  <VirtualizedTable data={data} columns={columns} />
</Profiler>;
```

**Key metrics:**

- `actualDuration` > 16ms means the render takes longer than one frame (60fps)
- `baseDuration` shows the cost without memoization
- Compare both to see memoization effectiveness

### Performance Checklist

| Check                         | How to Verify                       | Target             |
| ----------------------------- | ----------------------------------- | ------------------ |
| Data reference stable         | React DevTools highlight updates    | No flash on scroll |
| Columns reference stable      | Log `useMemo` deps changes          | Zero after mount   |
| Cell renderers memoized       | Profiler `actualDuration`           | < 16ms per frame   |
| Overscan tuned                | Scroll smoothness vs DOM node count | 5-15 rows          |
| No DevTools during benchmarks | Close React DevTools extension      | Required           |
