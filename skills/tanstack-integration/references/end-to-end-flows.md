---
title: End-to-End Flows
description: Complete patterns for form submission with cache update, infinite scroll with intersection observer, and auth-protected routes
tags:
  [
    form-flow,
    infinite-scroll,
    auth,
    protected-routes,
    intersection-observer,
    useMutation,
    useInfiniteQuery,
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

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
    >
      <form.Field name="title">
        {(field) => (
          <div>
            <label htmlFor={field.name}>Title</label>
            <input
              id={field.name}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
            />
            {field.state.meta.isTouched &&
              field.state.meta.errors.length > 0 && (
                <span className="error">{field.state.meta.errors[0]}</span>
              )}
          </div>
        )}
      </form.Field>

      <form.Field name="body">
        {(field) => (
          <div>
            <label htmlFor={field.name}>Body</label>
            <textarea
              id={field.name}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
            />
          </div>
        )}
      </form.Field>

      {createMutation.isError && (
        <div className="error">{createMutation.error.message}</div>
      )}

      <form.Subscribe
        selector={(state) => [state.canSubmit, state.isSubmitting]}
      >
        {([canSubmit, isSubmitting]) => (
          <button type="submit" disabled={!canSubmit || isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Post'}
          </button>
        )}
      </form.Subscribe>
    </form>
  );
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

  const handleIntersect = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      if (entries[0]?.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage],
  );

  useEffect(() => {
    const element = observerTarget.current;
    if (!element) return;

    const observer = new IntersectionObserver(handleIntersect, {
      rootMargin: '200px',
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [handleIntersect]);

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

### Protected Page Consuming Auth

```tsx
import { createFileRoute } from '@tanstack/react-router';
import { useSuspenseQuery } from '@tanstack/react-query';

export const Route = createFileRoute('/_protected/dashboard')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(dashboardQueries.overview());
  },
  component: DashboardPage,
});

function DashboardPage() {
  const { user } = Route.useRouteContext();
  const { data: dashboard } = useSuspenseQuery(dashboardQueries.overview());

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <DashboardContent data={dashboard} />
    </div>
  );
}
```

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

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        loginMutation.mutate({
          email: formData.get('email') as string,
          password: formData.get('password') as string,
        });
      }}
    >
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      {loginMutation.isError && (
        <div className="error">{loginMutation.error.message}</div>
      )}
      <button type="submit" disabled={loginMutation.isPending}>
        {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
}
```

## Flow Summary

| Flow            | Key Libraries                 | Pattern                                                       |
| --------------- | ----------------------------- | ------------------------------------------------------------- |
| Form submission | Form + Query + Router         | `useForm` -> `useMutation` -> `invalidateQueries` -> navigate |
| Infinite scroll | Query + Intersection Observer | `useInfiniteQuery` -> observer triggers `fetchNextPage`       |
| Auth protection | Router + Query                | `beforeLoad` checks session -> `redirect` if unauthenticated  |
