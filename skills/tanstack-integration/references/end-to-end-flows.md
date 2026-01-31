---
title: End-to-End Flows
description: Complete patterns for form submission with cache update, infinite scroll, paginated tables with URL state, auth-protected routes, and error handling
tags:
  [
    form-flow,
    infinite-scroll,
    paginated-table,
    auth,
    protected-routes,
    error-handling,
    intersection-observer,
    useMutation,
    useInfiniteQuery,
    validateSearch,
    loaderDeps,
  ]
---

# End-to-End Flows

## Form Submission Flow (Form -> Server -> Query Cache)

Complete pattern: user fills form, submits via mutation, cache updates, UI reflects new data.

```tsx
import { useForm } from '@tanstack/react-form';
import { zodValidator } from '@tanstack/zod-form-adapter';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { z } from 'zod';

const postSchema = z.object({
  title: z.string().min(1),
  body: z.string().min(10),
  categoryId: z.string(),
});

type CreatePostInput = z.infer<typeof postSchema>;

function CreatePostPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const createMutation = useMutation({
    mutationFn: (data: CreatePostInput) =>
      fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }).then((res) => res.json()),
    onSuccess: (newPost) => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      queryClient.setQueryData(['posts', newPost.id], newPost);
      navigate({ to: '/posts/$postId', params: { postId: newPost.id } });
    },
  });

  const form = useForm({
    defaultValues: {
      title: '',
      body: '',
      categoryId: '',
    } satisfies CreatePostInput,
    validatorAdapter: zodValidator(),
    validators: { onChange: postSchema },
    onSubmit: async ({ value }) => {
      await createMutation.mutateAsync(value);
    },
  });

  // Render form with form.Field for each input,
  // form.Subscribe for canSubmit/isSubmitting state,
  // and createMutation.isError for server error display.
  // See form-query-integration reference for full field patterns.
}
```

## Infinite List with Intersection Observer

Paginated data with automatic loading on scroll using `useInfiniteQuery` and the Intersection Observer API.

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';
import { useRef, useEffect, useCallback } from 'react';

interface Page<T> {
  items: T[];
  nextCursor: string | null;
}

function fetchPosts(cursor?: string): Promise<Page<Post>> {
  const params = new URLSearchParams({ limit: '20' });
  if (cursor) params.set('cursor', cursor);
  return fetch(`/api/posts?${params}`).then((res) => res.json());
}

function InfinitePostList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status } =
    useInfiniteQuery({
      queryKey: ['posts', 'infinite'],
      queryFn: ({ pageParam }) => fetchPosts(pageParam),
      initialPageParam: undefined as string | undefined,
      getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    });

  const observerTarget = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = observerTarget.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { rootMargin: '200px' },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  if (status === 'pending') return <PostListSkeleton />;
  if (status === 'error') return <ErrorMessage />;

  const allPosts = data.pages.flatMap((page) => page.items);

  return (
    <div>
      {allPosts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      <div ref={observerTarget} aria-hidden="true" />
      {isFetchingNextPage && <LoadingSpinner />}
    </div>
  );
}
```

## Auth-Protected Route Flow

Authentication check in the root loader gates access to protected routes.

### Auth Query Options

```tsx
import { queryOptions } from '@tanstack/react-query';

export const authQueryOptions = queryOptions({
  queryKey: ['auth', 'session'],
  queryFn: async () => {
    const res = await fetch('/api/auth/session');
    if (!res.ok) return null;
    return res.json() as Promise<{ id: string; role: string }>;
  },
  staleTime: 5 * 60 * 1000,
  retry: false,
});
```

### Root Route with Auth Context

```tsx
import {
  createRootRouteWithContext,
  Outlet,
  redirect,
} from '@tanstack/react-router';
import { type QueryClient } from '@tanstack/react-query';

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  beforeLoad: async ({ context: { queryClient } }) => {
    const user = await queryClient.ensureQueryData(authQueryOptions);
    return { user };
  },
  component: () => <Outlet />,
});
```

### Protected Layout Route

```tsx
import { createFileRoute, redirect, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_protected')({
  beforeLoad: async ({ context }) => {
    if (!context.user) {
      throw redirect({ to: '/login', search: { redirect: location.pathname } });
    }
  },
  component: () => (
    <div className="authenticated-layout">
      <Sidebar />
      <main>
        <Outlet />
      </main>
    </div>
  ),
});
```

Protected child routes access the user via `Route.useRouteContext()` and use the standard loader + `useSuspenseQuery` pattern for data.

### Login Page with Redirect

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';

const loginSearchSchema = z.object({
  redirect: z.string().optional(),
});

export const Route = createFileRoute('/login')({
  validateSearch: loginSearchSchema,
  component: LoginPage,
});

function LoginPage() {
  const { redirect: redirectTo } = Route.useSearch();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: (credentials: { email: string; password: string }) =>
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      }).then((res) => {
        if (!res.ok) throw new Error('Invalid credentials');
        return res.json();
      }),
    onSuccess: (user) => {
      queryClient.setQueryData(['auth', 'session'], user);
      navigate({ to: redirectTo ?? '/dashboard' });
    },
  });

  // Form renders inputs, error display, and submit button
  // using loginMutation.mutate(), .isError, .isPending
}
```

## Paginated Table with URL State

Server-side pagination with search params as the source of truth for table state.

### Route with Validated Search Params

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { useSuspenseQuery } from '@tanstack/react-query';
import { z } from 'zod';

const searchSchema = z.object({
  page: z.number().default(1),
  size: z.number().default(10),
  sort: z.enum(['name', 'email', 'createdAt']).default('createdAt'),
  search: z.string().optional(),
});

type SearchParams = z.infer<typeof searchSchema>;

export const Route = createFileRoute('/_protected/admin/users')({
  validateSearch: zodValidator(searchSchema),
  loaderDeps: ({ search }) => search,
  loader: async ({ context: { queryClient }, deps }) => {
    await queryClient.ensureQueryData(userQueries.list(deps));
  },
  component: UsersPage,
});
```

### Component with URL-Synced Table State

```tsx
function UsersPage() {
  const search = Route.useSearch();
  const navigate = useNavigate();
  const { data } = useSuspenseQuery(userQueries.list(search));

  const handlePaginationChange = (pagination: {
    pageIndex: number;
    pageSize: number;
  }) => {
    navigate({
      search: (prev: SearchParams) => ({
        ...prev,
        page: pagination.pageIndex + 1,
        size: pagination.pageSize,
      }),
    });
  };

  const handleSearchChange = (value: string) => {
    navigate({
      search: (prev: SearchParams) => ({
        ...prev,
        search: value || undefined,
        page: 1,
      }),
    });
  };

  return (
    <div>
      <input
        defaultValue={search.search}
        onChange={(e) => handleSearchChange(e.target.value)}
        placeholder="Search users..."
      />
      <UserTable
        data={data.items}
        pageCount={data.meta.totalPages}
        pagination={{
          pageIndex: search.page - 1,
          pageSize: search.size,
        }}
        onPaginationChange={handlePaginationChange}
      />
    </div>
  );
}
```

Key pattern: reset `page` to 1 when filters change. The URL is the single source of truth for table state -- back/forward navigation restores exact table position.

## Error Handling Flow

Structured errors with route-level boundaries and server function error patterns.

### Route Error Components

```tsx
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_protected/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    await queryClient.ensureQueryData(postQueries.detail(params.postId));
  },
  component: PostPage,
  errorComponent: ({ error, reset }) => (
    <div>
      <p>{error.message}</p>
      <button onClick={reset}>Try Again</button>
    </div>
  ),
  notFoundComponent: () => <p>Post not found</p>,
});
```

### Server Function Error Handling

```tsx
const mutation = useMutation({
  mutationFn: (values: CreatePostInput) => createPost({ data: values }),
  onSuccess: (result) => {
    if ('error' in result) {
      switch (result.code) {
        case 'AUTH_REQUIRED':
          navigate({ to: '/login' });
          break;
        case 'VALIDATION_ERROR':
          form.setErrorMap({ onServer: result.error });
          break;
        default:
          toast.error(result.error);
      }
      return;
    }
    queryClient.invalidateQueries({ queryKey: ['posts'] });
    navigate({ to: '/posts' });
  },
});
```

Server functions return structured `{ error, code }` objects rather than throwing. Always check the result shape in `onSuccess` instead of relying on `onError`.

## Flow Summary

| Flow            | Key Libraries                 | Pattern                                                       |
| --------------- | ----------------------------- | ------------------------------------------------------------- |
| Form submission | Form + Query + Router         | `useForm` -> `useMutation` -> `invalidateQueries` -> navigate |
| Infinite scroll | Query + Intersection Observer | `useInfiniteQuery` -> observer triggers `fetchNextPage`       |
| Paginated table | Table + Query + Router        | `validateSearch` -> `loaderDeps` -> navigate on state change  |
| Auth protection | Router + Query                | `beforeLoad` checks session -> `redirect` if unauthenticated  |
| Error handling  | Router + Server Functions     | `errorComponent` on routes, structured errors from server     |
