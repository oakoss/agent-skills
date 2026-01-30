---
title: Column Definitions
description: Column definition patterns including accessors, helpers, custom headers/cells, sorting, filtering, pagination, visibility, and row selection
tags:
  [
    columns,
    accessorKey,
    accessorFn,
    columnHelper,
    header,
    cell,
    flexRender,
    visibility,
    selection,
    pagination,
    sorting,
    filtering,
  ]
---

# Column Definitions

## Basic Column Types

```tsx
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from '@tanstack/react-table';

const columns: ColumnDef<Person>[] = [
  // Simple accessor
  { accessorKey: 'email', header: 'Email' },

  // Computed value (requires id)
  {
    accessorFn: (row) => `${row.first} ${row.last}`,
    id: 'fullName',
    header: 'Name',
  },

  // Custom cell rendering
  {
    accessorKey: 'amount',
    header: () => <div className="text-right">Amount</div>,
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('amount'));
      const formatted = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(amount);
      return <div className="text-right font-medium">{formatted}</div>;
    },
  },

  // Actions column (display-only, no accessor)
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => <ActionMenu item={row.original} />,
  },
];
```

## Type-Safe Column Helper

```tsx
import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper<Person>();

const columns = [
  columnHelper.accessor('name', { header: 'Name' }),
  columnHelper.accessor((row) => `${row.first} ${row.last}`, {
    id: 'fullName',
    header: 'Full Name',
  }),
  columnHelper.display({
    id: 'actions',
    cell: ({ row }) => <ActionMenu row={row} />,
  }),
];
```

## Custom Header with Sorting

```tsx
{
  accessorKey: 'email',
  header: ({ column }) => (
    <Button
      variant="ghost"
      onPress={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      Email
      {column.getIsSorted() === 'asc' && <ChevronUp className="ml-2 size-4" />}
      {column.getIsSorted() === 'desc' && <ChevronDown className="ml-2 size-4" />}
      {!column.getIsSorted() && <ChevronsUpDown className="ml-2 size-4" />}
    </Button>
  ),
}
```

## Select All Column

```tsx
{
  id: 'select',
  header: ({ table }) => (
    <Checkbox
      isSelected={table.getIsAllPageRowsSelected()}
      isIndeterminate={table.getIsSomePageRowsSelected()}
      onChange={(isSelected) => table.toggleAllPageRowsSelected(isSelected)}
      aria-label="Select all"
    />
  ),
  cell: ({ row }) => (
    <Checkbox
      isSelected={row.getIsSelected()}
      onChange={(isSelected) => row.toggleSelected(isSelected)}
      aria-label="Select row"
    />
  ),
  enableSorting: false,
  enableHiding: false,
}
```

## State Management Pattern

```tsx
const [sorting, setSorting] = useState<SortingState>([]);
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

const table = useReactTable({
  data,
  columns,
  state: { sorting, columnFilters, columnVisibility, rowSelection },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onColumnVisibilityChange: setColumnVisibility,
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
});
```

## Column Visibility Toggle

```tsx
<MenuTrigger>
  <Button variant="outline">Columns</Button>
  <Popover>
    <Menu>
      {table
        .getAllColumns()
        .filter((col) => col.getCanHide())
        .map((column) => (
          <MenuItem key={column.id} onAction={() => column.toggleVisibility()}>
            {column.getIsVisible() ? '✓ ' : '  '}
            {column.id}
          </MenuItem>
        ))}
    </Menu>
  </Popover>
</MenuTrigger>
```

## Pagination Controls

```tsx
const table = useReactTable({
  // ...
  getPaginationRowModel: getPaginationRowModel(),
});

// Navigation
<Button onPress={() => table.previousPage()} isDisabled={!table.getCanPreviousPage()}>
  Previous
</Button>
<Button onPress={() => table.nextPage()} isDisabled={!table.getCanNextPage()}>
  Next
</Button>

// Page info
<span>
  Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
</span>

// Page size selector
<Select
  label="Rows per page"
  selectedKey={String(table.getState().pagination.pageSize)}
  onSelectionChange={(key) => table.setPageSize(Number(key))}
>
  {[10, 20, 50].map((size) => (
    <SelectItem key={size} id={String(size)}>{size}</SelectItem>
  ))}
</Select>
```

## Pagination Methods

| Method                 | Description            |
| ---------------------- | ---------------------- |
| `nextPage()`           | Next page              |
| `previousPage()`       | Previous page          |
| `setPageIndex(n)`      | Go to page (0-indexed) |
| `setPageSize(n)`       | Set rows per page      |
| `getPageCount()`       | Total pages            |
| `getCanNextPage()`     | Can go forward         |
| `getCanPreviousPage()` | Can go back            |

## Rendering with flexRender

Always use `flexRender()` for both static and dynamic column content:

```tsx
<table>
  <thead>
    {table.getHeaderGroups().map((headerGroup) => (
      <tr key={headerGroup.id}>
        {headerGroup.headers.map((header) => (
          <th key={header.id}>
            {flexRender(header.column.columnDef.header, header.getContext())}
          </th>
        ))}
      </tr>
    ))}
  </thead>
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
</table>
```
