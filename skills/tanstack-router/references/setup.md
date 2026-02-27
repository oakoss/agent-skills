---
title: Setup
description: Installation, Vite plugin configuration, file structure conventions, app setup with RouterProvider, and recommended router default options
tags:
  [
    setup,
    installation,
    vite-plugin,
    file-structure,
    RouterProvider,
    createRouter,
    configuration,
  ]
---

# Setup

## Installation

```bash
npm install @tanstack/react-router @tanstack/router-devtools
npm install -D @tanstack/router-plugin
npm install @tanstack/zod-adapter zod  # Optional: Zod validation
```

## Vite Config

TanStackRouterVite MUST come before `react()`:

```ts
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';

export default defineConfig({
  plugins: [TanStackRouterVite(), react()],
});
```

## File Structure

```sh
src/routes/
├── __root.tsx         → createRootRoute() with <Outlet />
├── index.tsx          → createFileRoute('/')
└── posts.$postId.tsx  → createFileRoute('/posts/$postId')
```

## App Setup

```ts
import { createRouter, RouterProvider } from '@tanstack/react-router';
import { routeTree } from './routeTree.gen';

const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

<RouterProvider router={router} />
```

## Router Default Options

```ts
export function getRouter() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { refetchOnWindowFocus: false, staleTime: 1000 * 60 * 2 },
    },
  });

  const router = createRouter({
    routeTree,
    context: { queryClient, user: null },
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0,
    defaultErrorComponent: DefaultCatchBoundary,
    defaultNotFoundComponent: DefaultNotFound,
    scrollRestoration: true,
    defaultStructuralSharing: true,
    defaultPendingComponent: () => <div className="loading-bar" />,
    defaultPendingMinMs: 200,
    defaultPendingMs: 1000,
  });

  return router;
}
```

| Option                     | Type                                          | Default  | Description                     |
| -------------------------- | --------------------------------------------- | -------- | ------------------------------- |
| `defaultPreload`           | `false \| 'intent' \| 'render' \| 'viewport'` | `false`  | When to preload routes          |
| `defaultPreloadStaleTime`  | `number`                                      | `30000`  | Preloaded data freshness (ms)   |
| `defaultErrorComponent`    | `Component`                                   | Built-in | Global error boundary           |
| `defaultNotFoundComponent` | `Component`                                   | Built-in | Global 404 page                 |
| `scrollRestoration`        | `boolean`                                     | `false`  | Restore scroll on navigation    |
| `defaultStructuralSharing` | `boolean`                                     | `false`  | Optimize loader data re-renders |
| `defaultPendingComponent`  | `Component`                                   | None     | Shown during route transitions  |
| `defaultPendingMs`         | `number`                                      | `1000`   | Delay before showing pending UI |
| `defaultPendingMinMs`      | `number`                                      | `500`    | Minimum time pending UI shows   |

## DefaultCatchBoundary Component

Global error boundary for unhandled route errors:

```tsx
import {
  ErrorComponent,
  Link,
  rootRouteId,
  useMatch,
  useRouter,
} from '@tanstack/react-router';

function DefaultCatchBoundary({ error }: { error: unknown }) {
  const router = useRouter();
  const isRoot = useMatch({
    strict: false,
    select: (state) => state.id === rootRouteId,
  });

  return (
    <div>
      <ErrorComponent error={error} />
      <div>
        <button onClick={() => router.invalidate()}>Try Again</button>
        {isRoot ? (
          <a href="/">Home</a>
        ) : (
          <Link
            to="/"
            onClick={(e) => {
              e.preventDefault();
              router.navigate({ to: '/' });
            }}
          >
            Home
          </Link>
        )}
      </div>
    </div>
  );
}
```

## DefaultNotFound Component

Global 404 component for unmatched routes:

```tsx
function DefaultNotFound() {
  return (
    <div>
      <p>Page not found</p>
      <Link to="/">Go home</Link>
    </div>
  );
}
```

## DefaultPendingComponent

Shown after `defaultPendingMs` delay to avoid flash for fast transitions:

```tsx
function DefaultPendingComponent() {
  return <div className="route-loading-indicator" />;
}
```

Timing: if navigation completes within `defaultPendingMs`, no pending UI flashes. Once shown, it stays for at least `defaultPendingMinMs` to prevent layout thrash.

## SSR with TanStack Query

### Recommended: `@tanstack/react-router-ssr-query`

Automates dehydration/hydration and streaming for SSR with TanStack Query:

```ts
import { setupRouterSsrQueryIntegration } from '@tanstack/react-router-ssr-query';

const queryClient = new QueryClient();
const router = createRouter({ routeTree, context: { queryClient } });

setupRouterSsrQueryIntegration({ router, queryClient });
```

Install: `npm install @tanstack/react-router-ssr-query`

The legacy `@tanstack/react-router-with-query` (`routerWithQueryClient`) requires `@tanstack/react-start` and is superseded by this package.

### Manual dehydrate/hydrate/Wrap

For custom SSR integration without the helper package, use `dehydrate`, `hydrate`, and `Wrap` router options:

```ts
export function createAppRouter() {
  const queryClient = new QueryClient();
  return createRouter({
    routeTree,
    context: { queryClient },
    dehydrate: () => ({
      queryClientState: dehydrate(queryClient),
    }),
    hydrate: (dehydrated) => {
      hydrate(queryClient, dehydrated.queryClientState);
    },
    Wrap: ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    ),
  });
}
```
