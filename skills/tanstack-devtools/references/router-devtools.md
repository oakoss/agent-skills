---
title: Router Devtools
description: TanStackRouterDevtools setup, floating and embedded modes, route inspection, options, and production builds
tags:
  [
    router-devtools,
    route-tree,
    floating,
    embedded,
    production,
    TanStackRouterDevtools,
    route-inspection,
  ]
---

# Router Devtools

## Installation

```bash
pnpm add @tanstack/react-router-devtools
```

The package is separate from `@tanstack/react-router`. Devtools are automatically excluded from production bundles by default.

## Floating Mode

Place `TanStackRouterDevtools` inside a route component (typically the root route) for automatic router detection via context. Panel toggle state persists in localStorage.

### Inside Root Route (Recommended)

```tsx
import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
});
```

### Outside RouterProvider

When rendering outside the provider, pass the `router` instance explicitly:

```tsx
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

const router = createRouter({ routeTree });

function App() {
  return (
    <>
      <RouterProvider router={router} />
      <TanStackRouterDevtools router={router} />
    </>
  );
}
```

### Floating Mode Props

| Prop                | Type                                                           | Default         | Description                                  |
| ------------------- | -------------------------------------------------------------- | --------------- | -------------------------------------------- |
| `router`            | `Router`                                                       | nearest context | Router instance (required outside provider)  |
| `initialIsOpen`     | `boolean`                                                      | `false`         | Whether devtools panel starts open           |
| `panelProps`        | `object`                                                       | —               | Props passed to the panel (className, style) |
| `toggleButtonProps` | `object`                                                       | —               | Props passed to the toggle button            |
| `position`          | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right'` | `'bottom-left'` | Toggle button position                       |

## Embedded Mode

Use `TanStackRouterDevtoolsPanel` for inline rendering in custom layouts:

```tsx
import { useState } from 'react';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';

function RouterDebugPanel({ router }: { router: Router }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div style={{ height: 400 }}>
      <TanStackRouterDevtoolsPanel
        router={router}
        isOpen={isOpen}
        setIsOpen={setIsOpen}
        style={{ height: '100%' }}
      />
    </div>
  );
}
```

### Embedded Mode Props

| Prop              | Type                      | Description                       |
| ----------------- | ------------------------- | --------------------------------- |
| `router`          | `Router`                  | Router instance to connect to     |
| `style`           | `React.CSSProperties`     | Inline styles for the panel       |
| `className`       | `string`                  | CSS class for the panel           |
| `isOpen`          | `boolean`                 | Controls panel open/close state   |
| `setIsOpen`       | `(open: boolean) => void` | Toggles panel open/close state    |
| `handleDragStart` | `(e: MouseEvent) => void` | Drag handler for resizable panels |

## Production Builds

By default, `TanStackRouterDevtools` is excluded from production bundles. To enable devtools in production, import the production variant:

```tsx
import { TanStackRouterDevtoolsInProd } from '@tanstack/react-router-devtools';
```

`TanStackRouterDevtoolsInProd` accepts the same props as `TanStackRouterDevtools`.

## Lazy Loading

Code-split devtools to keep them out of the initial bundle:

```tsx
import { lazy, Suspense } from 'react';

const TanStackRouterDevtools = lazy(() =>
  import('@tanstack/react-router-devtools').then((mod) => ({
    default: mod.TanStackRouterDevtools,
  })),
);

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <Suspense fallback={null}>
        <TanStackRouterDevtools />
      </Suspense>
    </>
  ),
});
```

## Devtools Features

The router devtools panel provides:

- **Route tree visualization**: Full route hierarchy with active route highlighting
- **Match inspection**: Current route matches with params, search params, and loader data
- **Route timing**: Load and pending timing for each matched route
- **Search param viewer**: Parsed and serialized search parameters
- **Navigation history**: Recent navigations with details

## Integration with Unified Devtools

Router devtools can run as a plugin in the unified TanStack Devtools panel:

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';

<TanStackDevtools
  plugins={[
    {
      name: 'TanStack Router',
      render: <TanStackRouterDevtoolsPanel router={router} />,
    },
  ]}
/>;
```

When using the unified panel, pass the `router` prop explicitly to the panel component since it renders outside the `RouterProvider` context.
