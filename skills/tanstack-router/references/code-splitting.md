---
title: Code Splitting
description: Lazy routes with createLazyFileRoute, what goes in main vs lazy files, virtual routes, auto code splitting, and preloading strategies
tags:
  [
    code-splitting,
    lazy,
    createLazyFileRoute,
    virtual-routes,
    preload,
    bundle-optimization,
  ]
---

# Code Splitting

## Lazy Routes

Split components from critical config:

```ts
// routes/dashboard.tsx — critical config only
export const Route = createFileRoute('/dashboard')({
  loader: async ({ context }) =>
    context.queryClient.ensureQueryData(dashboardQueries.stats()),
});

// routes/dashboard.lazy.tsx — lazy-loaded component
export const Route = createLazyFileRoute('/dashboard')({
  component: DashboardPage,
  pendingComponent: DashboardSkeleton,
  errorComponent: DashboardError,
});
```

### What Goes Where

- **Main file:** `validateSearch`, `beforeLoad`, `loader`, `loaderDeps`, context
- **Lazy file:** `component`, `pendingComponent`, `errorComponent`, `notFoundComponent`

If a route only has a `.lazy.tsx` file (no loader/beforeLoad/validateSearch), skip the main file entirely. The router auto-generates a virtual route.

## Auto Code Splitting

Alternative to manual `.lazy.tsx` files:

```ts
TanStackRouterVite({ autoCodeSplitting: true });
```

## Virtual File Routes (v1.140+)

Programmatic route configuration when file-based conventions don't fit:

```ts
import {
  rootRoute,
  route,
  index,
  layout,
  physical,
} from '@tanstack/virtual-file-routes';

export const routes = rootRoute('root.tsx', [
  index('home.tsx'),
  route('/posts', 'posts/posts.tsx', [
    index('posts/posts-home.tsx'),
    route('$postId', 'posts/posts-detail.tsx'),
  ]),
  layout('first', 'layout/first-layout.tsx', [route('/nested', 'nested.tsx')]),
  physical('/classic', 'file-based-subtree'),
]);
```

## Preloading Strategies

| Strategy     | Behavior                  | Use Case                    |
| ------------ | ------------------------- | --------------------------- |
| `'intent'`   | Preload on hover/focus    | Default for most links      |
| `'render'`   | Preload when Link mounts  | Critical next pages         |
| `'viewport'` | Preload when Link in view | Below-fold content          |
| `false`      | No preloading             | Heavy, rarely-visited pages |

Set `defaultPreloadStaleTime: 0` when using TanStack Query to let Query manage cache freshness.

Programmatic preloading:

```ts
const router = useRouter();
await router.preloadRoute({
  to: '/posts/$postId',
  params: { postId: '123' },
});
```
