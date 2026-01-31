---
title: Code Splitting
description: Lazy routes with createLazyFileRoute, critical vs lazy file separation, auto code splitting, preloading strategies with intent/render/viewport, and programmatic preloading
tags:
  [
    code-splitting,
    lazy,
    createLazyFileRoute,
    autoCodeSplitting,
    preload,
    bundle-optimization,
    getRouteApi,
  ]
---

# Code Splitting

## Lazy Routes

Split components from critical config into two files:

```ts
// routes/dashboard.tsx — critical config only
export const Route = createFileRoute('/dashboard')({
  validateSearch: z.object({ tab: z.string().optional() }),
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) throw redirect({ to: '/login' });
  },
  loader: async ({ context }) =>
    context.queryClient.ensureQueryData(dashboardQueries.stats()),
});

// routes/dashboard.lazy.tsx — lazy-loaded component
import { createLazyFileRoute } from '@tanstack/react-router';

export const Route = createLazyFileRoute('/dashboard')({
  component: DashboardPage,
  pendingComponent: DashboardSkeleton,
  errorComponent: DashboardError,
});
```

### What Goes Where

| Main file (`.tsx`) | Lazy file (`.lazy.tsx`) |
| ------------------ | ----------------------- |
| `validateSearch`   | `component`             |
| `beforeLoad`       | `pendingComponent`      |
| `loader`           | `errorComponent`        |
| `loaderDeps`       | `notFoundComponent`     |
| context setup      |                         |

If a route only has a `.lazy.tsx` file (no loader/beforeLoad/validateSearch), skip the main file entirely. The router auto-generates a virtual route.

### Type Safety in Lazy Files

Use `getRouteApi` for type-safe hooks in lazy files since the `Route` export from the main file is not available:

```ts
// routes/dashboard.lazy.tsx
import { createLazyFileRoute, getRouteApi } from '@tanstack/react-router';

const dashboardRoute = getRouteApi('/dashboard');

export const Route = createLazyFileRoute('/dashboard')({
  component: DashboardPage,
});

function DashboardPage() {
  const data = dashboardRoute.useLoaderData();
  const { tab } = dashboardRoute.useSearch();
  return <Dashboard data={data} activeTab={tab} />;
}
```

## Auto Code Splitting

Alternative to manual `.lazy.tsx` files — the plugin splits routes automatically:

```ts
TanStackRouterVite({ autoCodeSplitting: true });
```

Auto splitting moves `component`, `pendingComponent`, `errorComponent`, and `notFoundComponent` to separate chunks. Critical config (`loader`, `beforeLoad`, `validateSearch`) stays in the main bundle.

When using virtual file routes, always use `autoCodeSplitting` instead of manual lazy files. Manual `createLazyFileRoute` is silently replaced in virtual route mode (see Known Issues #18).

## Preloading Strategies

| Strategy     | Behavior                  | Use Case                    |
| ------------ | ------------------------- | --------------------------- |
| `'intent'`   | Preload on hover/focus    | Default for most links      |
| `'render'`   | Preload when Link mounts  | Critical next pages         |
| `'viewport'` | Preload when Link in view | Below-fold content          |
| `false`      | No preloading             | Heavy, rarely-visited pages |

Configure globally and override per-link:

```ts
const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  defaultPreloadDelay: 50,
  defaultPreloadStaleTime: 30_000,
});

// Override for specific links
<Link to="/heavy-page" preload={false}>Heavy Page</Link>
<Link to="/critical-page" preload="render">Critical Page</Link>
```

Set `defaultPreloadStaleTime: 0` when using TanStack Query to let Query manage cache freshness.

## Programmatic Preloading

Preload routes in response to events:

```ts
const router = useRouter();

async function handleMouseEnter(postId: string) {
  await router.preloadRoute({
    to: '/posts/$postId',
    params: { postId },
  });
}
```

Preloading loads both the route code (lazy chunks) and executes loaders. The `preloadDelay` setting prevents excessive requests on quick mouse movements.
