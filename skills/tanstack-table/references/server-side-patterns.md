---
title: Server-Side Patterns
description: Server-side pagination, filtering, and sorting with TanStack Query integration, URL sync, keepPreviousData, and combined patterns
tags:
  [
    server-side,
    manualPagination,
    manualSorting,
    manualFiltering,
    pageCount,
    queryKey,
    query-key-factory,
    keepPreviousData,
    placeholderData,
    optimistic,
    prefetch,
    URL,
    searchParams,
  ]
---

# Server-Side Patterns

## When to Use Server-Side

| Condition                 | Client-Side | Server-Side |
| ------------------------- | ----------- | ----------- |
| Dataset < 1000 rows       | Yes         | Optional    |
| Dataset > 1000 rows       | No          | Yes         |
| Data changes frequently   | No          | Yes         |
| Need real-time DB queries | No          | Yes         |
| No backend API            | Yes         | No          |

## Pattern 1: Server-Side Pagination

### Backend API

```tsx
export async function onRequestGet({
  request,
  env,
}: {
  request: Request;
  env: Env;
}) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get('page')) || 0;
  const pageSize = Number(url.searchParams.get('pageSize')) || 20;
  const offset = page * pageSize;

  const { results } = await env.DB.prepare(
    'SELECT * FROM users LIMIT ? OFFSET ?',
  )
    .bind(pageSize, offset)
    .all();

  const { total } = await env.DB.prepare(
    'SELECT COUNT(*) as total FROM users',
  ).first<{ total: number }>();

  return Response.json({
    data: results,
    pagination: {
      page,
      pageSize,
      total: total ?? 0,
      pageCount: Math.ceil((total ?? 0) / pageSize),
    },
  });
}
```

### Frontend

```tsx
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 20,
});

const { data } = useQuery({
  queryKey: ['users', pagination.pageIndex, pagination.pageSize],
  queryFn: async () => {
    const response = await fetch(
      `/api/users?page=${pagination.pageIndex}&pageSize=${pagination.pageSize}`,
    );
    return response.json();
  },
});

const table = useReactTable({
  data: data?.data ?? [],
  columns,
  getCoreRowModel: getCoreRowModel(),
  manualPagination: true,
  pageCount: data?.pagination.pageCount ?? 0,
  state: { pagination },
  onPaginationChange: setPagination,
});
```

## Pattern 2: Combined Pagination + Sorting + Filtering

```tsx
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 20,
});
const [sorting, setSorting] = useState<SortingState>([]);
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

const search =
  (columnFilters.find((f) => f.id === 'search')?.value as string) || '';

const { data, isPlaceholderData } = useQuery({
  queryKey: ['users', pagination, sorting, search],
  queryFn: async () => {
    const params = new URLSearchParams({
      page: pagination.pageIndex.toString(),
      pageSize: pagination.pageSize.toString(),
    });

    if (sorting.length > 0) {
      params.append('sortBy', sorting[0].id);
      params.append('sortOrder', sorting[0].desc ? 'desc' : 'asc');
    }

    if (search) {
      params.append('search', search);
    }

    const response = await fetch(`/api/users?${params}`);
    return response.json();
  },
  placeholderData: (previousData) => previousData,
});

const table = useReactTable({
  data: data?.data ?? [],
  columns,
  getCoreRowModel: getCoreRowModel(),
  manualPagination: true,
  manualSorting: true,
  manualFiltering: true,
  pageCount: data?.pagination.pageCount ?? 0,
  state: { pagination, sorting, columnFilters },
  onPaginationChange: setPagination,
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
});
```

## Query Key Factory

Structure query keys hierarchically so invalidation works at any level:

```tsx
const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (pagination: PaginationState, sorting: SortingState, filter: string) =>
    [...userKeys.lists(), pagination, sorting, filter] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};
```

Then use in queries and invalidation:

```tsx
const { data } = useQuery({
  queryKey: userKeys.list(pagination, sorting, search),
  queryFn: () => fetchUsers(pagination, sorting, search),
  placeholderData: keepPreviousData,
});

const deleteMutation = useMutation({
  mutationFn: deleteUser,
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: userKeys.lists() });
  },
});
```

## Query Options Factory

Extract query configuration into a reusable factory function:

```tsx
import { queryOptions, keepPreviousData } from '@tanstack/react-query';

function usersQueryOptions(
  pagination: PaginationState,
  sorting: SortingState,
  filter: string,
) {
  return queryOptions({
    queryKey: userKeys.list(pagination, sorting, filter),
    queryFn: () =>
      getUsers({
        data: {
          page: pagination.pageIndex + 1,
          pageSize: pagination.pageSize,
          sortBy: sorting[0]?.id,
          sortOrder: sorting[0]?.desc ? 'desc' : 'asc',
          filter,
        },
      }),
    placeholderData: keepPreviousData,
  });
}
```

## URL Search Params Sync

Sync table state with URL for shareable, bookmarkable links:

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';

const searchSchema = z.object({
  page: z.number().default(1),
  size: z.number().default(10),
  sort: z.string().optional(),
  order: z.enum(['asc', 'desc']).optional(),
  q: z.string().optional(),
});

export const Route = createFileRoute('/users')({
  validateSearch: zodValidator(searchSchema),
  loaderDeps: ({ search }) => search,
  loader: async ({ context, deps }) => {
    await context.queryClient.ensureQueryData(
      usersQueryOptions(
        { pageIndex: deps.page - 1, pageSize: deps.size },
        deps.sort ? [{ id: deps.sort, desc: deps.order === 'desc' }] : [],
        deps.q ?? '',
      ),
    );
  },
});

function UsersPage() {
  const search = Route.useSearch();
  const navigate = useNavigate();

  const pagination = { pageIndex: search.page - 1, pageSize: search.size };
  const sorting = search.sort
    ? [{ id: search.sort, desc: search.order === 'desc' }]
    : [];

  const handlePaginationChange = (updater: Updater<PaginationState>) => {
    const next = typeof updater === 'function' ? updater(pagination) : updater;
    navigate({
      search: (prev) => ({
        ...prev,
        page: next.pageIndex + 1,
        size: next.pageSize,
      }),
    });
  };

  const handleSortingChange = (updater: Updater<SortingState>) => {
    const next = typeof updater === 'function' ? updater(sorting) : updater;
    navigate({
      search: (prev) => ({
        ...prev,
        sort: next[0]?.id,
        order: next[0]?.desc ? 'desc' : 'asc',
      }),
    });
  };

  // Use these handlers in useReactTable onPaginationChange/onSortingChange
}
```

## Optimistic Updates for Mutations

```tsx
const queryClient = useQueryClient();

const deleteMutation = useMutation({
  mutationFn: (id: string) => fetch(`/api/users/${id}`, { method: 'DELETE' }),
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: ['users'] });
    const previous = queryClient.getQueryData([
      'users',
      pagination,
      sorting,
      search,
    ]);

    queryClient.setQueryData(
      ['users', pagination, sorting, search],
      (old: any) => ({
        ...old,
        data: old.data.filter((user: User) => user.id !== id),
      }),
    );

    return { previous };
  },
  onError: (_err, _id, context) => {
    queryClient.setQueryData(
      ['users', pagination, sorting, search],
      context?.previous,
    );
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

## Optimistic Inline Edit

```tsx
const editMutation = useMutation({
  mutationFn: (updated: User) =>
    fetch(`/api/users/${updated.id}`, {
      method: 'PATCH',
      body: JSON.stringify(updated),
    }),
  onMutate: async (updated) => {
    const queryKey = userKeys.list(pagination, sorting, search);
    await queryClient.cancelQueries({ queryKey });
    const previous = queryClient.getQueryData(queryKey);

    queryClient.setQueryData(queryKey, (old: UsersResponse) => ({
      ...old,
      data: old.data.map((user) =>
        user.id === updated.id ? { ...user, ...updated } : user,
      ),
    }));

    return { previous, queryKey };
  },
  onError: (_err, _updated, context) => {
    if (context) {
      queryClient.setQueryData(context.queryKey, context.previous);
    }
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: userKeys.lists() });
  },
});
```

## Reset Page on Filter Change

When filters change, reset to the first page to avoid empty results:

```tsx
const handleFilterChange = (updater: Updater<ColumnFiltersState>) => {
  setColumnFilters(updater);
  setPagination((prev) => ({ ...prev, pageIndex: 0 }));
};

const table = useReactTable({
  // ...
  onColumnFiltersChange: handleFilterChange,
});
```

Alternatively, use `autoResetPageIndex` for client-side tables to automatically reset to page 0 when sorting or filtering changes:

```tsx
const table = useReactTable({
  data,
  columns,
  autoResetPageIndex: true, // Reset page on sort/filter change (default: true)
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
});
```

Set `autoResetPageIndex: false` to preserve the current page when data changes.

## Prefetching Next Page

```tsx
const queryClient = useQueryClient();

useEffect(() => {
  if (pagination.pageIndex < (data?.pageCount ?? 0) - 1) {
    queryClient.prefetchQuery({
      queryKey: ['users', pagination.pageIndex + 1],
      queryFn: () => fetchUsers(pagination.pageIndex + 1),
    });
  }
}, [pagination.pageIndex, data?.pageCount, queryClient]);
```

## Backend: Sort Column Validation

Always validate sort columns to prevent SQL injection:

```tsx
const allowedColumns = ['id', 'name', 'email', 'created_at'];
const allowedOrders = ['asc', 'desc'];

if (!allowedColumns.includes(sortBy) || !allowedOrders.includes(sortOrder)) {
  return Response.json({ error: 'Invalid sort parameters' }, { status: 400 });
}
```

## Performance Tips

1. **Add database indexes** for sorted/filtered columns
2. **Use `placeholderData`** to show old data while fetching
3. **Debounce search inputs** to reduce API calls; **use cursor-based pagination** for >100k rows
