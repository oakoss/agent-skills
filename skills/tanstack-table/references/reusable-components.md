---
title: Reusable Components
description: Reusable table UI components including skeletons, loading overlays, column headers, pagination, debounced input, and full-feature DataTable
tags:
  [
    components,
    skeleton,
    loading,
    overlay,
    header,
    pagination,
    DataTable,
    debounced,
    reusable,
  ]
---

# Reusable Components

## Table Skeleton

```tsx
function TableSkeleton({
  rows = 10,
  columns = 5,
}: {
  rows?: number;
  columns?: number;
}) {
  return (
    <div className="rounded-md border">
      <table className="w-full">
        <thead>
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i} className="border p-2">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="border p-2">
                  <div className="h-4 w-full bg-muted animate-pulse rounded" />
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

## Loading Overlay

Show over the table while fetching new data (e.g., page change):

```tsx
function LoadingOverlay() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
      <Spinner className="size-8" />
    </div>
  );
}
```

## DataTableColumnHeader

Sortable column header with sort direction indicators and a visibility toggle menu:

```tsx
import type { Column } from '@tanstack/react-table';

type DataTableColumnHeaderProps<TData, TValue> = {
  column: Column<TData, TValue>;
  title: string;
};

export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
}: DataTableColumnHeaderProps<TData, TValue>) {
  if (!column.getCanSort()) return <div>{title}</div>;

  return (
    <MenuTrigger>
      <Button variant="ghost" size="sm" className="-ml-3 h-8">
        <span>{title}</span>
        {column.getIsSorted() === 'desc' ? (
          <ArrowDown className="ml-2 size-4" />
        ) : column.getIsSorted() === 'asc' ? (
          <ArrowUp className="ml-2 size-4" />
        ) : (
          <ChevronsUpDown className="ml-2 size-4" />
        )}
      </Button>
      <Popover>
        <Menu>
          <MenuItem onAction={() => column.toggleSorting(false)}>
            <ArrowUp className="mr-2 size-3.5" /> Asc
          </MenuItem>
          <MenuItem onAction={() => column.toggleSorting(true)}>
            <ArrowDown className="mr-2 size-3.5" /> Desc
          </MenuItem>
          <MenuItem onAction={() => column.toggleVisibility(false)}>
            <EyeOff className="mr-2 size-3.5" /> Hide
          </MenuItem>
        </Menu>
      </Popover>
    </MenuTrigger>
  );
}
```

## DataTablePagination

Full pagination controls with row count, page size selector, and navigation:

```tsx
import type { Table } from '@tanstack/react-table';

export function DataTablePagination<TData>({ table }: { table: Table<TData> }) {
  return (
    <div className="flex items-center justify-between px-2">
      <div className="text-muted-foreground text-sm">
        {table.getFilteredSelectedRowModel().rows.length} of{' '}
        {table.getFilteredRowModel().rows.length} selected
      </div>
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <p className="text-sm">Rows per page</p>
          <Select
            aria-label="Rows per page"
            selectedKey={String(table.getState().pagination.pageSize)}
            onSelectionChange={(key) => table.setPageSize(Number(key))}
          >
            {[10, 20, 30, 50].map((size) => (
              <SelectItem key={size} id={String(size)}>
                {size}
              </SelectItem>
            ))}
          </Select>
        </div>
        <div className="text-sm">
          Page {table.getState().pagination.pageIndex + 1} of{' '}
          {table.getPageCount()}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onPress={() => table.firstPage()}
            isDisabled={!table.getCanPreviousPage()}
          >
            First
          </Button>
          <Button
            variant="outline"
            size="sm"
            onPress={() => table.previousPage()}
            isDisabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onPress={() => table.nextPage()}
            isDisabled={!table.getCanNextPage()}
          >
            Next
          </Button>
          <Button
            variant="outline"
            size="sm"
            onPress={() => table.lastPage()}
            isDisabled={!table.getCanNextPage()}
          >
            Last
          </Button>
        </div>
      </div>
    </div>
  );
}
```

## DebouncedInput

Debounced text input for filter/search fields:

```tsx
function DebouncedInput({
  value: initialValue,
  onChange,
  debounce = 300,
  label,
  ...props
}: {
  value: string;
  onChange: (value: string) => void;
  debounce?: number;
  label: string;
}) {
  const [value, setValue] = useState(initialValue);

  useEffect(() => setValue(initialValue), [initialValue]);

  useEffect(() => {
    const timeout = setTimeout(() => onChange(value), debounce);
    return () => clearTimeout(timeout);
  }, [value, debounce, onChange]);

  return (
    <TextField
      {...props}
      label={label}
      value={value}
      onChange={(v) => setValue(v)}
    />
  );
}
```

## Full-Feature DataTable

Complete table with sorting, filtering, visibility, selection, pagination, and empty state:

```tsx
function DataTable<TData>({
  data,
  columns,
}: {
  data: TData[];
  columns: ColumnDef<TData>[];
}) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [globalFilter, setGlobalFilter] = useState('');

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 py-4">
        <TextField
          label="Search"
          value={globalFilter}
          onChange={(value) => setGlobalFilter(value)}
          className="max-w-sm"
        />
      </div>
      <div className="rounded-md border">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className="border p-2 text-left">
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
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <tr key={row.id} data-state={row.getIsSelected() && 'selected'}>
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="border p-2">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="h-24 text-center">
                  No results.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <DataTablePagination table={table} />
    </div>
  );
}
```

## Important Notes

- All table components must be client components (`'use client'`)
- Use `flexRender()` for both static and dynamic content
- Access original row data via `row.original`
- Only import row models you actually use
- Each table is unique — avoid over-abstracting into a single generic wrapper
