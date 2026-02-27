---
title: Column and Row Pinning
description: Pin columns to left/right edges and rows to top/bottom during scrolling, with group column pinning workaround
tags:
  [
    pin,
    pinning,
    column,
    row,
    sticky,
    left,
    right,
    top,
    bottom,
    enableColumnPinning,
    enableRowPinning,
  ]
---

# Column and Row Pinning

## Column Pinning Setup

```tsx
import { useReactTable, getCoreRowModel } from '@tanstack/react-table';

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  enableColumnPinning: true,
  enableRowPinning: true,
  initialState: {
    columnPinning: {
      left: ['select', 'name'],
      right: ['actions'],
    },
  },
});
```

## Rendering Pinned Columns

Use CSS `position: sticky` on pinned cells within a single `<table>`:

```tsx
import { type Column, type Header, type Cell } from '@tanstack/react-table';

function getCommonPinningStyles<T>(column: Column<T>): React.CSSProperties {
  const isPinned = column.getIsPinned();
  return {
    left: isPinned === 'left' ? `${column.getStart('left')}px` : undefined,
    right: isPinned === 'right' ? `${column.getAfter('right')}px` : undefined,
    position: isPinned ? 'sticky' : 'relative',
    width: column.getSize(),
    zIndex: isPinned ? 1 : 0,
  };
}

function PinnedTable({ table }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  style={getCommonPinningStyles(header.column)}
                  className="bg-background"
                >
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
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  style={getCommonPinningStyles(cell.column)}
                  className="bg-background"
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Programmatic Pinning

```tsx
column.pin('left'); // Pin column to left
column.pin('right'); // Pin column to right
column.pin(false); // Unpin column

row.pin('top'); // Pin row to top
row.pin('bottom'); // Pin row to bottom
row.pin(false); // Unpin row
```

## Column Pinning with Column Groups (Known Bug)

Pinning parent group columns (created with `columnHelper.group()`) causes incorrect positioning and duplicated headers. `column.getStart('left')` returns wrong values for group headers.

**Source:** [GitHub Issue #5397](https://github.com/TanStack/table/issues/5397)

**Workaround:** Pin individual columns within the group, not the group itself:

```tsx
// Check if a column is pinnable (no parent group)
const isPinnable = (column: Column<unknown>) => !column.parent;

// Pin individual columns, not the group
table.getColumn('firstName')?.pin('left');
table.getColumn('lastName')?.pin('left');
// Don't pin the parent group column
```

## Row Pinning

```tsx
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  enableRowPinning: true,
});

// Pin specific rows
row.pin('top');
row.pin('bottom');

// Get pinned rows for rendering
const topPinnedRows = table.getTopRows();
const centerRows = table.getCenterRows();
const bottomPinnedRows = table.getBottomRows();
```
