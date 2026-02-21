---
title: Type Safety
description: Router type registration, from parameter for type narrowing, strict false for shared components, getRouteApi for code-split files, route-specific helpers, and type utilities for extracting route types
tags:
  [
    type-safety,
    Register,
    getRouteApi,
    TypeScript,
    inference,
    route-types,
    type-narrowing,
    NavigateOptions,
  ]
---

# Type Safety

## Register Router Type (CRITICAL)

Without registration, `useNavigate`, `useParams`, `useSearch`, and `<Link>` have no type inference:

```ts
import { createRouter } from '@tanstack/react-router';
import { routeTree } from './routeTree.gen';

const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
```

After registration, `<Link to="/invalid" />` produces a TypeScript error and `to` autocompletes all valid routes.

## Use `from` for Type Narrowing (CRITICAL)

```ts
const params = useParams({ from: '/posts/$postId' });
// params: { postId: string }

const search = useSearch({ from: '/search' });
// search: { query: string; page: number }
```

Without `from`, hooks return a union of all possible params/search across all routes.

## Route-Specific Helpers

Within route files, use `Route.useX()` methods for automatic type narrowing:

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => fetchPost(params.postId),
  component: PostPage,
});

function PostPage() {
  const { postId } = Route.useParams();
  const data = Route.useLoaderData();
  const search = Route.useSearch();
}
```

## `Route.fullPath` for Type Narrowing

`Route.fullPath` provides the full path string for use with hooks in non-route files:

```ts
const params = useParams({ from: Route.fullPath });
```

This is equivalent to passing the string literal but keeps it co-located with the route definition.

## getRouteApi for Code-Split Components

In code-split (`.lazy.tsx`) files that don't have access to the `Route` export:

```ts
import { getRouteApi } from '@tanstack/react-router';

const postRoute = getRouteApi('/posts/$postId');

function PostPage() {
  const params = postRoute.useParams();
  const data = postRoute.useLoaderData();
  const search = postRoute.useSearch();
}
```

`getRouteApi` is a zero-cost abstraction that provides the same type-safe hooks as `Route.useX()`.

## `strict: false` for Shared Components

When a component is used across multiple routes and doesn't know which route it's in:

```ts
function Breadcrumbs() {
  const params = useParams({ strict: false });
  //    ^? { postId?: string, userId?: string, ... }

  const search = useSearch({ strict: false });
  //    ^? Partial<FullSearchSchema>

  return <nav>{/* Build breadcrumbs from available params */}</nav>;
}
```

Only use `strict: false` in truly generic cross-route components. Note: parsed param types may not be correct after navigation (see Known Issues #10).

## Type Route Context

```ts
interface RouterContext {
  queryClient: QueryClient;
  auth: { user: User | null; isAuthenticated: boolean };
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});
```

Context types compose from the entire parent hierarchy. Child routes automatically inherit typed context from parent `beforeLoad` return values.

## NavigateOptions Type Safety

The `NavigateOptions` type is less strict than `useNavigate()` about enforcing required params. Prefer the hook's return type:

```ts
const navigate = useNavigate();

navigate({
  to: '/posts/$postId',
  params: { postId: '123' },
});

// NavigateOptions doesn't enforce params — avoid using it directly as a type
```

## Type Utilities

Extract route types programmatically:

```ts
import type {
  RouteIds,
  RegisteredRouter,
  ParseRoute,
} from '@tanstack/react-router';

type AllRouteIds = RouteIds<RegisteredRouter['routeTree']>;

type PostParams = ParseRoute<
  RegisteredRouter['routeTree'],
  '/posts/$postId'
>['params'];
```
