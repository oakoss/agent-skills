---
title: Type Safety
description: Router type registration, from parameter for type narrowing, strict false for shared components, route-specific helpers, getRouteApi, and type utilities
tags:
  [
    type-safety,
    Register,
    getRouteApi,
    TypeScript,
    inference,
    route-types,
    type-narrowing,
  ]
---

# Type Safety

## Register Router Type (CRITICAL)

Without registration, `useNavigate`, `useParams`, `useSearch`, and `<Link>` have no type inference:

```ts
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
```

## Use `from` for Type Narrowing (CRITICAL)

```ts
const params = useParams({ from: '/posts/$postId' });
// params: { postId: string }
```

Within route files, use route-specific helpers:

```ts
const { postId } = Route.useParams();
const data = Route.useLoaderData();
```

In code-split components, use `getRouteApi`:

```ts
const postRoute = getRouteApi('/posts/$postId');
const params = postRoute.useParams();
const data = postRoute.useLoaderData();
```

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

Only use `strict: false` in truly generic cross-route components.

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
