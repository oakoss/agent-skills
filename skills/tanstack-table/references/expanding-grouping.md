---
title: Row Expanding and Grouping
description: Row expanding for nested/tree data and detail rows, row grouping with aggregation functions, and performance considerations
tags:
  [
    expanding,
    grouping,
    subRows,
    getExpandedRowModel,
    getGroupedRowModel,
    aggregationFn,
    tree,
    nested,
    detail,
  ]
---

# Row Expanding and Grouping

## Row Expanding (Nested Data)

### Setup

```tsx
import {
  useReactTable,
  getCoreRowModel,
  getExpandedRowModel,
} from '@tanstack/react-table';

// Data with nested children
const data = [
  {
    id: 1,
    name: 'Parent Row',
    subRows: [
      { id: 2, name: 'Child Row 1' },
      { id: 3, name: 'Child Row 2' },
    ],
  },
];

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  getSubRows: (row) => row.subRows, // Tell table where children are
});
```

### Rendering with Expand Button

```tsx
function ExpandableTable({ table }) {
  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr key={row.id}>
          <td>
            {row.getCanExpand() && (
              <button onClick={row.getToggleExpandedHandler()}>
                {row.getIsExpanded() ? '▼' : '▶'}
              </button>
            )}
          </td>
          {row.getVisibleCells().map((cell) => (
            <td key={cell.id} style={{ paddingLeft: `${row.depth * 20}px` }}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}
```

### Programmatic Control

```tsx
table.toggleAllRowsExpanded(); // Expand/collapse all
row.toggleExpanded(); // Toggle single row
table.getIsAllRowsExpanded(); // Check if all expanded
row.getCanExpand(); // Check if row has children
row.getIsExpanded(); // Check if row is expanded
```

## Detail Rows

For showing custom content (not nested data) when a row is expanded:

```tsx
function TableWithDetails({ table, columns }) {
  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <Fragment key={row.id}>
          <tr>
            <td>
              <button onClick={row.getToggleExpandedHandler()}>
                {row.getIsExpanded() ? '▼' : '▶'}
              </button>
            </td>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
          {row.getIsExpanded() && (
            <tr>
              <td colSpan={columns.length + 1}>
                <div className="p-4 bg-muted">
                  Custom detail content for {row.original.name}
                </div>
              </td>
            </tr>
          )}
        </Fragment>
      ))}
    </tbody>
  );
}
```

## Row Grouping

### Setup

```tsx
import {
  useReactTable,
  getCoreRowModel,
  getGroupedRowModel,
  getExpandedRowModel,
} from '@tanstack/react-table';

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getGroupedRowModel: getGroupedRowModel(),
  getExpandedRowModel: getExpandedRowModel(), // Groups are expandable
  initialState: {
    grouping: ['status'], // Group by 'status' column
  },
});
```

### Column with Aggregation

```tsx
const columns = [
  {
    accessorKey: 'status',
    header: 'Status',
  },
  {
    accessorKey: 'amount',
    header: 'Amount',
    aggregationFn: 'sum',
    aggregatedCell: ({ getValue }) => `Total: ${getValue()}`,
  },
];
```

### Built-in Aggregation Functions

`sum`, `min`, `max`, `extent`, `mean`, `median`, `unique`, `uniqueCount`, `count`

### Rendering Grouped Rows

```tsx
function GroupedTable({ table }) {
  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr key={row.id}>
          {row.getVisibleCells().map((cell) => (
            <td key={cell.id}>
              {cell.getIsGrouped() ? (
                // Group header — show expand toggle + count
                <button onClick={row.getToggleExpandedHandler()}>
                  {row.getIsExpanded() ? '▼' : '▶'}{' '}
                  {flexRender(cell.column.columnDef.cell, cell.getContext())} (
                  {row.subRows.length})
                </button>
              ) : cell.getIsAggregated() ? (
                // Aggregated value
                flexRender(
                  cell.column.columnDef.aggregatedCell ??
                    cell.column.columnDef.cell,
                  cell.getContext(),
                )
              ) : cell.getIsPlaceholder() ? null : (
                // Regular cell
                flexRender(cell.column.columnDef.cell, cell.getContext())
              )}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}
```

## Performance Warning: Grouping at Scale

Grouping causes significant performance degradation on medium-to-large datasets. With grouping enabled, render times can increase from <1 second to 30-40 seconds on 50k rows due to excessive memory usage in `createRow` calculations.

**Source:** [Blog Post (JP Camara)](https://jpcamara.com/2023/03/07/making-tanstack-table.html) | [GitHub Issue #5926](https://github.com/TanStack/table/issues/5926)

**Mitigations:**

```tsx
// 1. Disable grouping for large datasets
const shouldEnableGrouping = data.length < 10000;

// 2. Use server-side grouping instead
const table = useReactTable({
  manualGrouping: true,
  // Server returns pre-grouped data
});

// 3. Paginate to limit rows per page
// 4. Memoize row components
const MemoizedRow = React.memo(TableRow);
```
