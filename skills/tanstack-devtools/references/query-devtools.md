---
title: Query Devtools
description: ReactQueryDevtools setup, floating and embedded modes, configuration options, production builds, and lazy loading
tags:
  [
    react-query-devtools,
    floating,
    embedded,
    production,
    lazy-loading,
    cache-viewer,
    initialIsOpen,
  ]
---

# Query Devtools

## Installation

```bash
pnpm add @tanstack/react-query-devtools
```

The package is a separate install from `@tanstack/react-query`. It is automatically tree-shaken from production builds when imported from the default entry point.

## Floating Mode

Floating mode renders a toggle button fixed to the screen corner. Panel state persists in localStorage across reloads.

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Floating Mode Props

| Prop             | Type                                                                         | Default          | Description                          |
| ---------------- | ---------------------------------------------------------------------------- | ---------------- | ------------------------------------ |
| `initialIsOpen`  | `boolean`                                                                    | `false`          | Whether devtools panel starts open   |
| `buttonPosition` | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right' \| 'relative'` | `'bottom-right'` | Position of the toggle button        |
| `position`       | `'top' \| 'bottom' \| 'left' \| 'right'`                                     | `'bottom'`       | Which edge the panel attaches to     |
| `client`         | `QueryClient`                                                                | nearest context  | Custom QueryClient instance          |
| `errorTypes`     | `{ name: string; initializer: (query: Query) => TError }[]`                  | `[]`             | Predefined errors to trigger from UI |
| `styleNonce`     | `string`                                                                     | —                | CSP nonce for inline style tags      |

## Embedded Mode

Embedded mode renders the panel inline as a regular component. Use `ReactQueryDevtoolsPanel` for custom layouts or dashboards.

```tsx
import { useState } from 'react';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';

function DebugPanel() {
  const [isOpen, setIsOpen] = useState(true);

  if (!isOpen) return null;

  return (
    <div style={{ height: 300 }}>
      <ReactQueryDevtoolsPanel
        style={{ height: '100%' }}
        onClose={() => setIsOpen(false)}
      />
    </div>
  );
}
```

### Embedded Mode Props

| Prop         | Type                                                        | Description                                 |
| ------------ | ----------------------------------------------------------- | ------------------------------------------- |
| `style`      | `React.CSSProperties`                                       | Inline styles for the panel container       |
| `className`  | `string`                                                    | CSS class for the panel container           |
| `client`     | `QueryClient`                                               | Custom QueryClient instance                 |
| `errorTypes` | `{ name: string; initializer: (query: Query) => TError }[]` | Predefined errors to trigger from UI        |
| `styleNonce` | `string`                                                    | CSP nonce for inline style tags             |
| `onClose`    | `() => void`                                                | Callback when panel close button is clicked |

## Production Builds

By default, `ReactQueryDevtools` is excluded from production bundles via `process.env.NODE_ENV` checks. To opt in to production devtools, use the production export:

```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools/production';
```

`ReactQueryDevtoolsPanel` also has a `/production` export for embedded mode in production environments.

## Lazy Loading

Reduce development bundle impact by lazy-loading devtools:

```tsx
import { lazy, Suspense } from 'react';

const ReactQueryDevtools = lazy(() =>
  import('@tanstack/react-query-devtools').then((mod) => ({
    default: mod.ReactQueryDevtools,
  })),
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <Suspense fallback={null}>
        <ReactQueryDevtools />
      </Suspense>
    </QueryClientProvider>
  );
}
```

## Devtools Features

The query devtools panel provides:

- **Query list**: All cached queries with status indicators (fresh, stale, inactive, fetching)
- **Query detail**: Selected query data, metadata, and timing information
- **Cache actions**: Manually refetch, invalidate, reset, or remove individual queries
- **Error simulation**: Trigger predefined errors on queries via the `errorTypes` prop
- **Filter and sort**: Search queries by key and sort by status, last updated, or key hash

## Integration with Unified Devtools

Query devtools can also run as a plugin in the unified TanStack Devtools panel. See the [form devtools and unified patterns](form-devtools.md) reference for the plugin approach.

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';

<TanStackDevtools
  plugins={[
    {
      id: 'tanstack-query',
      name: 'TanStack Query',
      render: <ReactQueryDevtoolsPanel />,
    },
  ]}
/>;
```
