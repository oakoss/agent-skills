---
title: Query Integration
description: Setting up TanStack Router with Query context, SSR integration, and setupRouterSsrQueryIntegration
tags: [query, setup, context, SSR, setupRouterSsrQueryIntegration, QueryClient]
---

# Query Integration

## Root Route with Context

```tsx
// routes/__root.tsx
import { createRootRouteWithContext } from '@tanstack/react-router';
import { QueryClient } from '@tanstack/react-query';

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});
```

## Router with SSR Integration

```tsx
// router.tsx
import { QueryClient } from '@tanstack/react-query';
import { createRouter } from '@tanstack/react-router';
import { setupRouterSsrQueryIntegration } from '@tanstack/react-router-ssr-query';
import { routeTree } from './routeTree.gen';

export function getRouter() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 2,
        refetchOnWindowFocus: false,
      },
    },
  });

  const router = createRouter({
    routeTree,
    context: { queryClient },
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0, // Query manages caching
    scrollRestoration: true,
    defaultStructuralSharing: true,
  });

  setupRouterSsrQueryIntegration({
    router,
    queryClient,
  });

  return router;
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}
```

## SSR Data Flow

```text
Server:
  1. getRouter() creates fresh QueryClient + Router per request
  2. setupRouterSsrQueryIntegration connects them
  3. Router matches routes, runs loaders
  4. Loaders call ensureQueryData -> data cached
  5. Integration auto-dehydrates QueryClient state
  6. HTML + serialized state streamed to client

Client:
  1. getRouter() creates fresh QueryClient + Router
  2. Integration auto-hydrates state from server
  3. useSuspenseQuery finds data in cache - no refetch
  4. App is interactive with data already loaded
```

## setupRouterSsrQueryIntegration Options

| Option            | Type        | Default  | Description                                |
| ----------------- | ----------- | -------- | ------------------------------------------ |
| `router`          | Router      | Required | Router instance                            |
| `queryClient`     | QueryClient | Required | QueryClient instance                       |
| `handleRedirects` | boolean     | `true`   | Intercept redirects from queries/mutations |
| `wrapQueryClient` | boolean     | `true`   | Auto-wrap with QueryClientProvider         |

## Custom Provider with DevTools

When you need DevTools, disable automatic wrapping and provide your own:

```tsx
export function getRouter() {
  const queryClient = new QueryClient();
  const router = createRouter({
    routeTree,
    context: { queryClient },
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0,
    scrollRestoration: true,
  });

  setupRouterSsrQueryIntegration({
    router,
    queryClient,
    wrapQueryClient: false,
  });

  router.options.Wrap = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );

  return router;
}
```

## Root Route with Additional Context

```tsx
interface RouterContext {
  queryClient: QueryClient;
  user: User | null;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
  beforeLoad: async ({ context }) => {
    await context.queryClient.ensureQueryData(authQueryOptions);
  },
});
```

## Testing with Mock QueryClient

```tsx
function renderWithProviders(route: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const router = createRouter({
    routeTree,
    context: { queryClient },
    Wrap: ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    ),
  });

  return {
    ...render(<RouterProvider router={router} />),
    queryClient,
  };
}
```

## Vite Configuration for TanStack Start

```ts
// vite.config.ts
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [tanstackStart(), react()],
});
```

TanStack Start handles client hydration and SSR automatically via the Vite plugin. No separate entry files needed.
