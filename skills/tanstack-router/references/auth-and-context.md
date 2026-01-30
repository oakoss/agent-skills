---
title: Auth and Context
description: Authentication with beforeLoad, route context and dependency injection, pathless layout routes, context inheritance, and error/not-found handling
tags:
  [
    auth,
    beforeLoad,
    redirect,
    context,
    dependency-injection,
    pathless-layout,
    error-handling,
  ]
---

# Auth and Context

## Authentication with beforeLoad

```ts
export const Route = createFileRoute('/(authenticated)')({
  beforeLoad: async ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login', search: { redirect: location.href } });
    }
    return {
      user: context.auth.user,
      permissions: context.auth.user.permissions,
    };
  },
});

// Child routes receive the extended context automatically
export const Route = createFileRoute('/(authenticated)/admin')({
  beforeLoad: async ({ context }) => {
    if (!context.permissions.includes('admin')) {
      throw redirect({ to: '/unauthorized' });
    }
  },
});
```

## Route Context and Dependency Injection

Define context at root, extend in `beforeLoad`, consume in loaders and components:

```ts
type RouterContext = {
  queryClient: QueryClient;
  auth: { getSession: () => Promise<Session | null> };
};

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

const router = createRouter({
  routeTree,
  context: {
    queryClient,
    auth: { getSession: () => auth.api.getSession({ headers: getHeaders() }) },
  },
});
```

## Context Inheritance

Three things flow automatically through nested routes:

| Inheritance   | Source                     | Example                                       |
| ------------- | -------------------------- | --------------------------------------------- |
| Path params   | Parent routes              | `postId: string` from parent flows to child   |
| Search params | Global + route-specific    | `debug: boolean` at root merges with route    |
| Route context | `beforeLoad` return values | `{ user, permissions }` flows to all children |

Types compose from the entire parent hierarchy automatically.

| Context                                 | Loader Data                  |
| --------------------------------------- | ---------------------------- |
| Available in beforeLoad, loader, render | Only available in component  |
| Set at router creation or beforeLoad    | Returned from loader         |
| Flows down to all children              | Specific to route            |
| Good for services, clients, auth        | Good for route-specific data |

## Pathless Layout Routes

Group routes by concern with shared layout and context:

```sh
routes/
├── _app.tsx           # Layout + auth guard for authenticated routes
├── _app/
│   ├── dashboard.tsx  # /dashboard
│   ├── settings.tsx   # /settings
│   └── profile.tsx    # /profile
├── _public.tsx        # Layout for public routes
└── _public/
    ├── login.tsx      # /login
    └── register.tsx   # /register
```

## Error and Not-Found Handling

```ts
import { notFound } from '@tanstack/react-router';

export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.postId);
    if (!post) throw notFound();
    return { post };
  },
  notFoundComponent: () => <div>Post not found</div>,
  errorComponent: ({ error, reset }) => (
    <div>
      <p>Error: {error?.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  ),
});
```

Not-found errors bubble up the route tree. Use `notFound({ data })` to pass context to the 404 component.
