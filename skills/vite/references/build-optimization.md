---
title: Build Optimization
description: Vite build configuration, code splitting, manual chunks, tree-shaking, and output control
tags:
  [
    build,
    rollupOptions,
    manualChunks,
    chunks,
    tree-shaking,
    minify,
    target,
    sourcemap,
    multi-page,
  ]
---

# Build Optimization

## Build Defaults

Vite produces optimized production builds with sensible defaults:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'es2020',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild',
    cssMinify: 'esbuild',
  },
});
```

| Option                  | Default          | Purpose                                                |
| ----------------------- | ---------------- | ------------------------------------------------------ |
| `target`                | `'modules'`      | Browser target (`'es2020'`, `'esnext'`, `'chrome100'`) |
| `outDir`                | `'dist'`         | Output directory                                       |
| `assetsDir`             | `'assets'`       | Nested directory for generated assets                  |
| `sourcemap`             | `false`          | `true`, `'inline'`, or `'hidden'`                      |
| `minify`                | `'esbuild'`      | `'esbuild'`, `'terser'`, or `false`                    |
| `cssMinify`             | same as `minify` | CSS-specific minifier                                  |
| `assetsInlineLimit`     | `4096`           | Inline assets smaller than this (bytes) as base64      |
| `chunkSizeWarningLimit` | `500`            | Warn on chunks exceeding this size (kB)                |

## Code Splitting

Vite automatically splits code at dynamic `import()` boundaries. Each dynamic import becomes a separate chunk:

```ts
const AdminPanel = lazy(() => import('./admin/AdminPanel'))

const routes = [
  { path: '/admin', element: <AdminPanel /> },
]
```

## Manual Chunks

Control chunk grouping with `manualChunks`:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-popover'],
        },
      },
    },
  },
});
```

### Function-Based Manual Chunks

For dynamic grouping logic:

```ts
manualChunks(id) {
  if (id.includes('node_modules')) {
    if (id.includes('react')) return 'vendor-react'
    if (id.includes('@radix-ui')) return 'vendor-ui'
    return 'vendor'
  }
}
```

Be cautious with function-based splitting: overly aggressive grouping can create circular dependencies between chunks.

## Rollup Options

Pass options directly to the underlying Rollup bundler:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash][extname]',
      },
      treeshake: {
        moduleSideEffects: false,
      },
    },
  },
});
```

### Output File Naming

| Pattern     | Description                     |
| ----------- | ------------------------------- |
| `[name]`    | Original file/chunk name        |
| `[hash]`    | Content hash for cache busting  |
| `[extname]` | File extension with leading dot |

## Multi-Page Application

Specify multiple HTML entry points for multi-page builds:

```ts
import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(import.meta.dirname, 'index.html'),
        admin: resolve(import.meta.dirname, 'admin/index.html'),
        login: resolve(import.meta.dirname, 'login/index.html'),
      },
    },
  },
});
```

Each entry gets its own chunk graph. During dev, navigate directly to the HTML file path (e.g., `/admin/index.html`).

## Tree-Shaking

Vite uses Rollup's tree-shaking by default. To maximize effectiveness:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
      },
    },
  },
});
```

Mark packages as side-effect-free in `package.json`:

```json
{
  "sideEffects": false
}
```

Or specify files with side effects:

```json
{
  "sideEffects": ["*.css", "./src/polyfills.ts"]
}
```

## CSS Code Splitting

By default, CSS used by async chunks is extracted into separate files and loaded on demand. Disable to inline all CSS into JS:

```ts
build: {
  cssCodeSplit: false,
}
```

## Build Analysis

Visualize bundle composition with `rollup-plugin-visualizer`:

```ts
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    visualizer({
      filename: 'stats.html',
      open: true,
      gzipSize: true,
    }),
  ],
});
```

## Watch Mode

Rebuild on file changes (useful for library development):

```ts
export default defineConfig({
  build: {
    watch: {},
  },
});
```

## Dependency Pre-Bundling

Vite pre-bundles dependencies with esbuild for faster dev startup. Configure explicitly when auto-detection misses dependencies:

```ts
export default defineConfig({
  optimizeDeps: {
    include: ['linked-package'],
    exclude: ['large-esm-package'],
  },
});
```
