---
title: v7 to v8 Migration
description: Migration guide from React Table v7 to TanStack Table v8 covering package names, hooks, column definitions, rendering, sorting, and pagination
tags:
  [
    migration,
    v7,
    v8,
    react-table,
    useTable,
    useReactTable,
    Header,
    accessor,
    accessorKey,
    upgrade,
  ]
---

# v7 to v8 Migration

Claude's training data may reference React Table v7. This project uses **TanStack Table v8**.

## Package Name Change

```bash
# v7 (old)
npm install react-table

# v8 (new)
npm install @tanstack/react-table
```

## Hook Changes

```tsx
// v7: useTable with plugin hooks
import { useTable, useSortBy, usePagination } from 'react-table';

const { getTableProps, getTableBodyProps, rows } = useTable(
  { columns, data },
  useSortBy,
  usePagination,
);

// v8: useReactTable with row model functions
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
} from '@tanstack/react-table';

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
});
```

## Column Definitions

```tsx
// v7 columns
const columns = [
  { Header: 'Name', accessor: 'name' },
  { Header: 'Age', accessor: 'age' },
];

// v8 columns (lowercase `header`, `accessorKey`)
const columns: ColumnDef<Person>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'age', header: 'Age' },
];

// v8 with column helper (type-safe)
import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper<Person>();
const columns = [
  columnHelper.accessor('name', {
    header: 'Name',
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor('age', {
    header: 'Age',
  }),
];
```

## Rendering

```tsx
// v7: Spread props pattern
<table {...getTableProps()}>
  <tbody {...getTableBodyProps()}>
    {rows.map((row) => (
      <tr {...row.getRowProps()}>
        {row.cells.map((cell) => (
          <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
        ))}
      </tr>
    ))}
  </tbody>
</table>;

// v8: Direct JSX with flexRender
import { flexRender } from '@tanstack/react-table';

<table>
  <tbody>
    {table.getRowModel().rows.map((row) => (
      <tr key={row.id}>
        {row.getVisibleCells().map((cell) => (
          <td key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>;
```

## Sorting State

```tsx
// v7
const { setSortBy } = useTable(/* ... */);

// v8: Controlled state
const [sorting, setSorting] = useState<SortingState>([]);

const table = useReactTable({
  state: { sorting },
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
});
```

## Pagination

```tsx
// v7
const { pageIndex, pageSize, gotoPage } = useTable(/* ... */);

// v8: Controlled state
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 10,
});

const table = useReactTable({
  state: { pagination },
  onPaginationChange: setPagination,
  getPaginationRowModel: getPaginationRowModel(),
});

// Navigation
table.setPageIndex(0);
table.nextPage();
table.previousPage();
```

## Quick Fix Reference

| v7 (old)                  | v8 (new)                                                    |
| ------------------------- | ----------------------------------------------------------- |
| `npm install react-table` | `npm install @tanstack/react-table`                         |
| `useTable`                | `useReactTable`                                             |
| `Header: 'Name'`          | `header: 'Name'` (lowercase)                                |
| `accessor: 'name'`        | `accessorKey: 'name'` or `columnHelper.accessor('name')`    |
| `getTableProps()`         | Direct JSX (no spread props needed)                         |
| `row.cells`               | `row.getVisibleCells()`                                     |
| `cell.render('Cell')`     | `flexRender(cell.column.columnDef.cell, cell.getContext())` |
| `useSortBy` plugin        | `getSortedRowModel()` row model                             |
| `usePagination` plugin    | `getPaginationRowModel()` row model                         |
| `setSortBy`               | `onSortingChange` + `useState`                              |
| `gotoPage`                | `table.setPageIndex(n)`                                     |

## Key Conceptual Changes

1. **Plugin hooks → Row models**: v7 used plugin hooks (`useSortBy`, `usePagination`) passed as arguments. v8 uses row model functions (`getSortedRowModel()`, `getPaginationRowModel()`) in the table options.

2. **Spread props → Direct JSX**: v7 required spreading table/body/row/cell props. v8 uses direct JSX with keys.

3. **Uncontrolled → Controlled state**: v7 managed state internally. v8 uses explicit controlled state via `state` + `on*Change` handlers for full state ownership.

4. **`flexRender`**: New utility for rendering dynamic cell/header content. Required for both static strings and React components.
