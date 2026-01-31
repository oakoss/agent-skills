---
title: Known Issues
description: 15 documented TanStack Table issues with symptoms, causes, sources, and solutions including infinite re-renders, React Compiler incompatibility, column filtering, and row selection bugs
tags:
  [
    bugs,
    issues,
    errors,
    re-render,
    compiler,
    selection,
    pagination,
    pinning,
    filtering,
    DevTools,
    TypeScript,
    getValue,
    workaround,
    debugging,
  ]
---

# Known Issues

## Issue 1: Infinite Re-Renders

- **Symptom:** Browser freezes, "Maximum update depth exceeded" error
- **Cause:** `data` or `columns` references change on every render
- **Fix:** Memoize with `useMemo` or define outside component

```tsx
// BAD: New array every render
const data = [{ id: 1 }];

// GOOD: Stable reference
const data = useMemo(() => [{ id: 1 }], []);
// OR: Define outside the component
```

## Issue 2: Query + Table State Mismatch

- **Symptom:** Changing page doesn't fetch new data, stale data displayed
- **Cause:** Query key missing table state (pagination, filters, sorting)
- **Fix:** Include ALL state in query key

```tsx
// BAD
queryKey: ['users']; // Static!

// GOOD
queryKey: ['users', pagination, sorting, filters];
```

## Issue 3: Server-Side Features Not Working

- **Symptom:** Pagination/filtering/sorting happens client-side instead of server-side
- **Cause:** Missing `manual*` flags
- **Fix:** Set all three flags + provide `pageCount`

```tsx
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  manualPagination: true,
  manualFiltering: true,
  manualSorting: true,
  pageCount: serverPageCount,
});
```

## Issue 4: TypeScript "Cannot Find Module"

- **Symptom:** Import error for `createColumnHelper` or other exports
- **Fix:** Import from `@tanstack/react-table`, not `@tanstack/table-core`

```tsx
// BAD
import { createColumnHelper } from '@tanstack/table-core';

// GOOD
import { createColumnHelper } from '@tanstack/react-table';
```

## Issue 5: Sorting Not Working Server-Side

- **Symptom:** Clicking sort headers doesn't update data
- **Cause:** Sorting state not included in query key or API params
- **Fix:** Include `sorting` in query key, add sort params to API, set `manualSorting: true` + `onSortingChange`

## Issue 6: Poor Performance (1000+ Rows)

- **Symptom:** Table slow or laggy with large datasets
- **Fix:** Use TanStack Virtual for client-side rendering or implement server-side pagination
- **Tip:** Close React DevTools during benchmarks (see Issue 11)

## Issue 7: React Compiler Incompatibility (React 19+)

- **Symptom:** Table doesn't re-render when data changes (with React Compiler enabled)
- **Source:** [GitHub Issue #5567](https://github.com/TanStack/table/issues/5567)
- **Cause:** React Compiler's automatic memoization conflicts with table core instance
- **Fix:** Add `'use no memo'` directive at top of components using `useReactTable`

```tsx
'use no memo';

function TableComponent() {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  // Now works correctly with React Compiler
}
```

This also affects column visibility and row selection. Full fix coming in v9.

## Issue 8: Server-Side Pagination Row Selection Bug

- **Symptom:** `toggleAllRowsSelected(false)` only deselects current page, not all pages
- **Source:** [GitHub Issue #5929](https://github.com/TanStack/table/issues/5929)
- **Cause:** Selection state persists across pages (intentional), but header checkbox state is calculated incorrectly
- **Fix:** Manually clear selection state

```tsx
const toggleAllRows = (value: boolean) => {
  if (!value) {
    table.setRowSelection({}); // Clear entire selection object
  } else {
    table.toggleAllRowsSelected(true);
  }
};
```

## Issue 9: Client-Side onPaginationChange Returns Wrong pageIndex

- **Symptom:** `onPaginationChange` always returns `pageIndex: 0`
- **Source:** [GitHub Issue #5970](https://github.com/TanStack/table/issues/5970)
- **Cause:** Client-side pagination mode has state tracking bug (works correctly in manual mode)
- **Fix:** Use manual pagination

```tsx
const table = useReactTable({
  data,
  columns,
  manualPagination: true,
  pageCount: Math.ceil(data.length / pagination.pageSize),
  state: { pagination },
  onPaginationChange: setPagination,
});
```

## Issue 10: Row Selection Not Cleaned Up When Data Removed

- **Symptom:** Selected rows that no longer exist remain in selection state
- **Source:** [GitHub Issue #5850](https://github.com/TanStack/table/issues/5850)
- **Cause:** Intentional for server-side pagination (rows disappear from page but stay selected)
- **Fix:** Manually clean up selection when removing data

```tsx
const removeRow = (idToRemove: string) => {
  setData(data.filter((row) => row.id !== idToRemove));

  const { rowSelection } = table.getState();
  if (rowSelection[idToRemove]) {
    table.setRowSelection((old) => {
      const filtered = Object.entries(old).filter(([id]) => id !== idToRemove);
      return Object.fromEntries(filtered);
    });
  }
};

// OR: Clear all selection
table.resetRowSelection(true);
```

## Issue 11: Performance Degradation with React DevTools

- **Symptom:** Table performance significantly degrades with React DevTools open
- **Cause:** DevTools inspects table instance and row models on every render (500+ rows)
- **Fix:** Close React DevTools during performance testing. Not a production issue.

## Issue 12: TypeScript getValue() Type with Grouped Columns

- **Symptom:** `getValue()` returns `unknown` instead of accessor's type inside `columnHelper.group()`
- **Source:** [GitHub Issue #5860](https://github.com/TanStack/table/issues/5860)
- **Fix:** Type assertion or `renderValue()`

```tsx
// Option 1: Type assertion
cell: (info) => {
  const value = info.getValue() as string;
  return value.toUpperCase();
};

// Option 2: renderValue() (better type inference)
cell: (info) => {
  const value = info.renderValue();
  return typeof value === 'string' ? value.toUpperCase() : value;
};
```

## Issue 13: Column Filter Not Resetting Page

- **Symptom:** Changing a column filter shows empty results or wrong page
- **Cause:** `pageIndex` stays at current value when filters narrow the result set
- **Fix:** Reset `pageIndex` to 0 when filters change

```tsx
const handleFilterChange = (updater: Updater<ColumnFiltersState>) => {
  setColumnFilters(updater);
  setPagination((prev) => ({ ...prev, pageIndex: 0 }));
};
```

## Issue 14: Row Selection State Uses String Keys

- **Symptom:** `rowSelection` state keys don't match your data IDs
- **Cause:** TanStack Table uses row index as key by default, not your data's ID field
- **Fix:** Set `getRowId` to use your data's unique identifier

```tsx
const table = useReactTable({
  data,
  columns,
  getRowId: (row) => row.id,
  enableRowSelection: true,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
});
```

Without `getRowId`, selection breaks across page changes because indices shift.

## Issue 15: Column Filter Value Type Mismatch

- **Symptom:** `column.setFilterValue()` doesn't filter correctly, or filter clears unexpectedly
- **Cause:** Filter value type doesn't match what the filter function expects
- **Fix:** Match value types between `setFilterValue` and `filterFn`

```tsx
// For range filters, pass a tuple
column.setFilterValue([min, max]);

// For select filters, pass the exact value type
column.setFilterValue('active'); // string, not { label: 'Active', value: 'active' }

// To clear a filter, pass undefined (not null or empty string)
column.setFilterValue(undefined);
```

## Debugging Tips

### Diagnosing Re-Render Loops

```tsx
// Log what's causing re-renders
useEffect(() => {
  console.log('data ref changed');
}, [data]);

useEffect(() => {
  console.log('columns ref changed');
}, [columns]);

useEffect(() => {
  console.log('table state changed', table.getState());
});
```

If `data ref changed` fires repeatedly, data is not memoized.

### Verifying Query Key Sync

```tsx
const queryKey = ['users', pagination, sorting, filters];
console.log('queryKey:', JSON.stringify(queryKey));
```

Check the Network tab to confirm each state change triggers exactly one API call. Multiple calls indicate unstable references in the query key.

### State Handler Debugging

```tsx
onPaginationChange: (updater) => {
  const next =
    typeof updater === 'function' ? updater(pagination) : updater;
  console.log('pagination:', pagination, '->', next);
  setPagination(next);
},
```

### Common Debugging Checklist

| Symptom                       | First Check                            | Likely Cause                             |
| ----------------------------- | -------------------------------------- | ---------------------------------------- |
| Table doesn't update          | React DevTools: check for re-renders   | React Compiler + missing `'use no memo'` |
| Filter shows wrong results    | Log `columnFilters` state              | Value type mismatch or stale state       |
| Selection lost on page change | Check `getRowId` config                | Missing `getRowId`, using index keys     |
| API called multiple times     | Network tab: count requests per action | Unstable query key references            |
| Empty table after filter      | Log `pageIndex` on filter change       | Page not reset to 0                      |
| Sort not applying server-side | Log query key after sort click         | `sorting` not in query key               |
