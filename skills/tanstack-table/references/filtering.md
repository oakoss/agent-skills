---
title: Filtering
description: Column filters, global filters, fuzzy matching with match-sorter-utils, faceted filters, and built-in filter functions
tags:
  [
    filter,
    columnFilters,
    globalFilter,
    fuzzy,
    faceted,
    match-sorter,
    includesString,
    getFilteredRowModel,
  ]
---

# Filtering

## Column Filter

```tsx
import { TextField } from '@oakoss/ui';

const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

const table = useReactTable({
  data,
  columns,
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  getCoreRowModel: getCoreRowModel(),
});

// Filter input for a specific column
<TextField
  label="Filter emails"
  value={(table.getColumn('email')?.getFilterValue() as string) ?? ''}
  onChange={(value) => table.getColumn('email')?.setFilterValue(value)}
/>;
```

## Global Filter

```tsx
const [globalFilter, setGlobalFilter] = useState('');

const table = useReactTable({
  data,
  columns,
  state: { globalFilter },
  onGlobalFilterChange: setGlobalFilter,
  getFilteredRowModel: getFilteredRowModel(),
  getCoreRowModel: getCoreRowModel(),
});

<TextField
  label="Search all columns"
  value={globalFilter}
  onChange={(value) => setGlobalFilter(value)}
/>;
```

## Built-in Filter Functions

| Function         | Description               |
| ---------------- | ------------------------- |
| `includesString` | Case-insensitive contains |
| `equalsString`   | Exact match               |
| `inNumberRange`  | Range `[min, max]`        |
| `arrIncludes`    | Array includes value      |
| `arrIncludesAll` | Array includes all        |

Set per-column:

```tsx
{
  accessorKey: 'status',
  filterFn: 'equalsString',
}
```

## Fuzzy Filtering

Uses `@tanstack/match-sorter-utils` for ranked fuzzy matching:

```tsx
import { rankItem, compareItems } from '@tanstack/match-sorter-utils';
import type { FilterFn, SortingFn } from '@tanstack/react-table';

// Extend table filter functions type
declare module '@tanstack/react-table' {
  interface FilterFns {
    fuzzy: FilterFn<unknown>;
  }
}

const fuzzyFilter: FilterFn<unknown> = (row, columnId, value, addMeta) => {
  const itemRank = rankItem(row.getValue(columnId), value);
  addMeta({ itemRank });
  return itemRank.passed;
};

// Optional: sort by fuzzy rank
const fuzzySort: SortingFn<unknown> = (rowA, rowB, columnId) => {
  let dir = 0;
  if (rowA.columnFiltersMeta[columnId]) {
    dir = compareItems(
      rowA.columnFiltersMeta[columnId]?.itemRank,
      rowB.columnFiltersMeta[columnId]?.itemRank,
    );
  }
  return dir === 0 ? sortingFns.alphanumeric(rowA, rowB, columnId) : dir;
};

const table = useReactTable({
  data,
  columns,
  filterFns: { fuzzy: fuzzyFilter },
  globalFilterFn: 'fuzzy',
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
});
```

## Client-Side Faceted Filters

Use faceted row models for local filter option counts:

```tsx
import {
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
} from '@tanstack/react-table';

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(),
  getFacetedUniqueValues: getFacetedUniqueValues(),
  getFacetedMinMaxValues: getFacetedMinMaxValues(),
});

// Get unique values for a column (for building filter dropdowns)
const uniqueValues = column.getFacetedUniqueValues(); // Map<value, count>

// Get min/max for a numeric column (for range filters)
const [min, max] = column.getFacetedMinMaxValues() ?? [0, 0];
```

## Server-Side Faceted Filters

Fetch distinct values from the server and use them as filter options:

```tsx
const getFilterOptions = createServerFn({ method: 'GET' }).handler(async () => {
  const [statuses, roles] = await Promise.all([
    db.selectDistinct({ status: users.status }).from(users),
    db.selectDistinct({ role: users.role }).from(users),
  ]);

  return {
    status: statuses.map((s) => s.status),
    role: roles.map((r) => r.role),
  };
});

function FilterToolbar({ table }: { table: Table<User> }) {
  const { data: options } = useQuery({
    queryKey: ['users', 'filter-options'],
    queryFn: getFilterOptions,
    staleTime: 1000 * 60 * 10,
  });

  return (
    <div className="flex gap-2">
      {options?.status && (
        <FacetedFilter
          column={table.getColumn('status')}
          title="Status"
          options={options.status.map((s) => ({ label: s, value: s }))}
        />
      )}
    </div>
  );
}
```

## Column Filters to Server Query

Convert TanStack Table filter state to server-side query parameters:

```tsx
function buildServerFilters(columnFilters: ColumnFiltersState) {
  const filters: Record<string, string | string[]> = {};

  for (const filter of columnFilters) {
    if (Array.isArray(filter.value)) {
      filters[filter.id] = filter.value;
    } else {
      filters[filter.id] = String(filter.value);
    }
  }

  return filters;
}
```

## Debounced Filter Input

Prevent excessive re-renders and API calls when typing:

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

## Enabling Filters on Columns

```tsx
const columns = [
  {
    accessorKey: 'name',
    header: 'Name',
    enableColumnFilter: true,
  },
  {
    accessorKey: 'id',
    header: 'ID',
    enableColumnFilter: false, // Disable filtering for this column
  },
];
```

## Server-Side Filtering

When using server-side filtering, set `manualFiltering: true` to prevent client-side filtering:

```tsx
const table = useReactTable({
  data: data?.data ?? [],
  columns,
  getCoreRowModel: getCoreRowModel(),
  manualFiltering: true,
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
});
```

Include filter state in query key so changes trigger refetch:

```tsx
const { data } = useQuery({
  queryKey: ['users', columnFilters],
  queryFn: () => fetchUsers({ filters: buildServerFilters(columnFilters) }),
});
```
