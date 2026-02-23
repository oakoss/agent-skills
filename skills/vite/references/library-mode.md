---
title: Library Mode
description: Vite library mode configuration for publishing ES, CJS, and UMD packages with TypeScript declarations
tags: [library, build.lib, formats, externals, dts, package.json, umd, esm, cjs]
---

# Library Mode

## Basic Library Config

Configure Vite to build a publishable library:

```ts
import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    lib: {
      entry: resolve(import.meta.dirname, 'src/index.ts'),
      name: 'MyLibrary',
      formats: ['es', 'cjs'],
      fileName: (format) => `my-library.${format}.js`,
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
        },
      },
    },
  },
});
```

## Output Formats

| Format   | Extension      | Use Case                              |
| -------- | -------------- | ------------------------------------- |
| `'es'`   | `.mjs` / `.js` | ESM consumers (bundlers, modern Node) |
| `'cjs'`  | `.cjs` / `.js` | CommonJS consumers (legacy Node)      |
| `'umd'`  | `.umd.js`      | Browser `<script>` tag and AMD/CJS    |
| `'iife'` | `.iife.js`     | Browser `<script>` tag only           |

`name` is required for UMD/IIFE formats (the global variable name).

## Externalizing Dependencies

Peer dependencies must be externalized to avoid bundling them into the library:

```ts
build: {
  rollupOptions: {
    external: ['react', 'react-dom', 'react/jsx-runtime'],
    output: {
      globals: {
        react: 'React',
        'react-dom': 'ReactDOM',
        'react/jsx-runtime': 'jsxRuntime',
      },
    },
  },
}
```

`globals` maps external module names to global variable names (only needed for UMD/IIFE).

### Externalizing All Dependencies

For Node.js libraries, externalize everything in `dependencies`:

```ts
import { defineConfig } from 'vite';
import pkg from './package.json' with { type: 'json' };

export default defineConfig({
  build: {
    lib: {
      entry: 'src/index.ts',
      formats: ['es', 'cjs'],
    },
    rollupOptions: {
      external: [
        ...Object.keys(pkg.dependencies ?? {}),
        ...Object.keys(pkg.peerDependencies ?? {}),
      ],
    },
  },
});
```

## TypeScript Declarations

Generate `.d.ts` files alongside the library output using `vite-plugin-dts`:

```ts
import { defineConfig } from 'vite';
import dts from 'vite-plugin-dts';

export default defineConfig({
  plugins: [
    dts({
      include: ['src'],
      rollupTypes: true,
    }),
  ],
  build: {
    lib: {
      entry: 'src/index.ts',
      formats: ['es', 'cjs'],
    },
  },
});
```

`rollupTypes: true` bundles all declarations into a single `.d.ts` file.

## Package.json Exports

Configure `package.json` for dual ESM/CJS publishing:

```json
{
  "name": "my-library",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/my-library.cjs.js",
  "module": "./dist/my-library.es.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/my-library.es.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/my-library.cjs.js"
      }
    }
  },
  "files": ["dist"],
  "peerDependencies": {
    "react": "^18.0.0 || ^19.0.0"
  }
}
```

The `types` condition must come first in each export block.

## Multiple Entry Points

Build a library with multiple entry points:

```ts
import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    lib: {
      entry: {
        index: resolve(import.meta.dirname, 'src/index.ts'),
        utils: resolve(import.meta.dirname, 'src/utils/index.ts'),
        hooks: resolve(import.meta.dirname, 'src/hooks/index.ts'),
      },
      formats: ['es', 'cjs'],
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        preserveModules: true,
        preserveModulesRoot: 'src',
      },
    },
  },
});
```

With `preserveModules`, the output mirrors the source directory structure for optimal tree-shaking.

## CSS in Libraries

By default, CSS is extracted to a separate file. Consumers must import it explicitly:

```ts
import 'my-library/dist/style.css';
```

To inject CSS at runtime instead (no separate import needed), use `vite-plugin-css-injected-by-js`:

```ts
import { defineConfig } from 'vite';
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';

export default defineConfig({
  plugins: [cssInjectedByJsPlugin()],
  build: {
    lib: {
      entry: 'src/index.ts',
      formats: ['es'],
    },
  },
});
```

## Library Build Without Minification

Libraries are typically published unminified so consumers can tree-shake and minify in their own builds:

```ts
build: {
  lib: { entry: 'src/index.ts', formats: ['es'] },
  minify: false,
  sourcemap: true,
}
```
