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
| `defaultStructuralSharing` | `boolean`                                     | `true`   | Optimize loader data re-renders |
