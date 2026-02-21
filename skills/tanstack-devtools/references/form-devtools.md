---
title: Form Devtools and Unified Panel
description: TanStack Form devtools plugin, unified TanStack Devtools panel setup, Vite plugin configuration, and multi-library devtools patterns
tags:
  [
    form-devtools,
    unified-devtools,
    TanStackDevtools,
    vite-plugin,
    plugins,
    multi-library,
  ]
---

# Form Devtools and Unified Panel

## Form Devtools

TanStack Form devtools are available through the unified TanStack Devtools panel as a plugin. There is no standalone floating component for form devtools.

### Installation

```bash
pnpm add @tanstack/react-devtools @tanstack/react-form-devtools
```

Both the unified devtools adapter and the form-specific plugin package are required.

### Basic Setup

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactFormDevtoolsPanel } from '@tanstack/react-form-devtools';

function App() {
  return (
    <>
      <YourApp />
      <TanStackDevtools
        plugins={[
          {
            id: 'tanstack-form',
            name: 'TanStack Form',
            render: <ReactFormDevtoolsPanel />,
            defaultOpen: true,
          },
        ]}
      />
    </>
  );
}
```

## Unified TanStack Devtools

The unified devtools panel combines Query, Router, and Form devtools into a single interface. It replaces multiple floating panels with one centralized tool.

### Installation

```bash
pnpm add @tanstack/react-devtools @tanstack/react-query-devtools @tanstack/react-router-devtools @tanstack/react-form-devtools
```

Install the core adapter and each library-specific plugin you need.

### Full Setup with All Plugins

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';
import { ReactFormDevtoolsPanel } from '@tanstack/react-form-devtools';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <TanStackDevtools
        plugins={[
          {
            id: 'tanstack-query',
            name: 'TanStack Query',
            render: <ReactQueryDevtoolsPanel />,
            defaultOpen: true,
          },
          {
            id: 'tanstack-router',
            name: 'TanStack Router',
            render: <TanStackRouterDevtoolsPanel router={router} />,
          },
          {
            id: 'tanstack-form',
            name: 'TanStack Form',
            render: <ReactFormDevtoolsPanel />,
          },
        ]}
      />
    </QueryClientProvider>
  );
}
```

### Config Options

```tsx
<TanStackDevtools
  config={{
    position: 'bottom-right',
    panelLocation: 'bottom',
    theme: 'dark',
    defaultOpen: false,
    hideUntilHover: false,
    openHotkey: ['Shift', 'D'],
    inspectHotkey: ['Shift', 'I'],
    requireUrlFlag: false,
    urlFlag: 'devtools',
  }}
  eventBusConfig={{
    debug: false,
    connectToServerBus: true,
    port: 42069,
  }}
  plugins={[...]}
/>
```

### Config Reference

| Option           | Type                                                                                              | Default          | Description                                  |
| ---------------- | ------------------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------- |
| `position`       | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right' \| 'middle-left' \| 'middle-right'` | `'bottom-right'` | Trigger button location                      |
| `panelLocation`  | `'top' \| 'bottom'`                                                                               | `'bottom'`       | Panel slide direction                        |
| `theme`          | `'dark' \| 'light'`                                                                               | `'dark'`         | Color scheme                                 |
| `defaultOpen`    | `boolean`                                                                                         | `false`          | Open on initial load                         |
| `hideUntilHover` | `boolean`                                                                                         | `false`          | Hide trigger until hover                     |
| `openHotkey`     | `KeyboardKey[]`                                                                                   | —                | Panel toggle shortcut                        |
| `inspectHotkey`  | `KeyboardKey[]`                                                                                   | —                | Source inspector shortcut                    |
| `requireUrlFlag` | `boolean`                                                                                         | `false`          | Require URL param to activate                |
| `urlFlag`        | `string`                                                                                          | `'devtools'`     | URL param name when `requireUrlFlag` is true |
| `triggerImage`   | `string`                                                                                          | —                | Custom trigger button image URL              |

### Event Bus Config

| Option               | Type      | Default | Description                         |
| -------------------- | --------- | ------- | ----------------------------------- |
| `debug`              | `boolean` | `false` | Enable event bus debug logging      |
| `connectToServerBus` | `boolean` | `false` | Connect to external devtools server |
| `port`               | `number`  | `42069` | Server communication port           |

## Vite Plugin

The `@tanstack/devtools-vite` plugin enhances the development experience with source injection, enhanced logging, and automatic production removal.

```ts
import { defineConfig } from 'vite';
import { devtools } from '@tanstack/devtools-vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    devtools({
      removeDevtoolsOnBuild: true,
      logging: true,
      enhancedLogs: { enabled: true },
      injectSource: {
        enabled: true,
        ignore: {
          files: [/node_modules/, /\.test\.(ts|tsx)$/],
          components: [/^Internal/, /^Private/],
        },
      },
      eventBusConfig: {
        enabled: true,
        port: 42069,
      },
    }),
    react(),
  ],
});
```

### Vite Plugin Options

| Option                   | Type                    | Description                               |
| ------------------------ | ----------------------- | ----------------------------------------- |
| `removeDevtoolsOnBuild`  | `boolean`               | Strip devtools from production builds     |
| `logging`                | `boolean`               | Console logging for plugin actions        |
| `enhancedLogs.enabled`   | `boolean`               | Add file/line info to console logs        |
| `injectSource.enabled`   | `boolean`               | Add `data-tsd-source` attributes to JSX   |
| `injectSource.ignore`    | `{ files, components }` | Patterns to exclude from source injection |
| `eventBusConfig.enabled` | `boolean`               | Enable event bus server                   |
| `eventBusConfig.port`    | `number`                | Event bus server port                     |

## Next.js Considerations

When using unified devtools in Next.js, wrap the devtools component in a client component to avoid server-side rendering errors:

```tsx
'use client';

import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';

export function DevtoolsProvider() {
  return (
    <TanStackDevtools
      plugins={[
        {
          id: 'tanstack-query',
          name: 'TanStack Query',
          render: <ReactQueryDevtoolsPanel />,
        },
      ]}
    />
  );
}
```

Then render `<DevtoolsProvider />` in your root layout.
