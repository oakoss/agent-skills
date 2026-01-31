---
title: Advanced Features
description: Plugins, code splitting, tree shaking, watch mode, clean output, build validation, and programmatic API usage
tags:
  [
    plugins,
    code-splitting,
    treeshake,
    watch,
    clean,
    publint,
    attw,
    report,
    programmatic,
    onSuccess,
    banner,
  ]
---

# Advanced Features

## Plugins

tsdown supports the entire Rolldown plugin ecosystem and is compatible with most Rollup plugins.

```ts
import { defineConfig } from 'tsdown';
import somePlugin from 'rolldown-plugin-example';

export default defineConfig({
  entry: ['src/index.ts'],
  plugins: [somePlugin()],
});
```

## Customizing Rolldown Options

For advanced scenarios, use `inputOptions` and `outputOptions` to access Rolldown's full configuration.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  inputOptions: {
    resolve: {
      alias: {
        '@': './src',
      },
    },
  },
  outputOptions: {
    banner: '/* Built with tsdown */',
  },
});
```

## Tree Shaking

Enable dead code elimination to reduce bundle size.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  treeshake: true,
});
```

Tree shaking works with ESM output by default. Mark side-effect-free packages in `package.json`:

```json
{
  "sideEffects": false
}
```

Or specify files with side effects:

```json
{
  "sideEffects": ["./src/polyfills.ts", "*.css"]
}
```

## Minification

Reduce output size for production builds.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  minify: true,
});
```

Combine with tree shaking for maximum size reduction:

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  treeshake: true,
  minify: true,
});
```

## Source Maps

Generate source maps for debugging.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  sourcemap: true,
});
```

## Watch Mode

Automatically rebuild when source files change. Useful during development.

```bash
npx tsdown --watch
```

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  watch: true,
});
```

## onSuccess Hook

Run a callback after each successful build. Receives the config and an abort signal for watch mode.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  watch: true,
  onSuccess: async (_config, _signal) => {
    console.log('Build completed!');
  },
});
```

## Clean Output

Remove the output directory before each build to avoid stale files.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  outDir: 'dist',
  clean: true,
});
```

## Banner and Footer

Prepend or append content to output files. Useful for CLI tools or license headers.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/cli.ts'],
  format: 'cjs',
  banner: {
    js: '#!/usr/bin/env node',
  },
});
```

## Build Validation

### publint

Validate package.json configuration and exports against common publishing mistakes.

```bash
npx tsdown --publint
```

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: true,
  publint: {
    level: 'warning',
    strict: true,
  },
});
```

### Are The Types Wrong (attw)

Check that TypeScript declaration files resolve correctly for all export conditions.

```bash
npx tsdown --attw
```

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: true,
  attw: {
    format: 'table-flipped',
  },
});
```

### Size Report

Generate bundle size reports with compression statistics.

```bash
npx tsdown --report
```

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  report: {
    gzip: true,
    brotli: true,
  },
});
```

### Combined Validation

```bash
npx tsdown --publint --attw --report
```

## Programmatic API

Use tsdown programmatically in Node.js scripts for custom build workflows.

```ts
import { build } from 'tsdown';

await build({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  outDir: 'dist',
  dts: true,
  clean: true,
});
```

### Advanced Programmatic Build

```ts
import { build } from 'tsdown';

await build({
  entry: {
    index: 'src/index.ts',
    cli: 'src/cli.ts',
  },
  format: ['esm', 'cjs'],
  outDir: 'dist',
  clean: true,
  dts: {
    bundle: true,
    resolve: true,
  },
  sourcemap: true,
  treeshake: true,
  platform: 'node',
  target: 'node18',
  external: ['react', 'vue'],
});
```

### Build with Error Handling

```ts
import { build } from 'tsdown';

try {
  await build({
    entry: ['src/index.ts'],
    format: ['esm'],
    logLevel: 'info',
    failOnWarn: true,
  });
} catch (error) {
  console.error('Build failed:', error);
  process.exit(1);
}
```

## CLI Quick Reference

```bash
npx tsdown                              # Build with defaults
npx tsdown src/index.ts src/cli.ts      # Specific entries
npx tsdown --format esm,cjs --dts       # Dual format with declarations
npx tsdown --minify --sourcemap         # Production build
npx tsdown --watch                      # Development watch mode
npx tsdown --target es2020 --platform node  # Target environment
npx tsdown --clean                      # Clean before build
npx tsdown --publint --attw --report    # Full validation
```

## Node.js Version Requirement

tsdown requires Node.js version 20.19 or higher.

## Getting Started with create-tsdown

Scaffold a new library project with the `create-tsdown` CLI.

```bash
npx create-tsdown my-library
```

Provides starter templates for pure TypeScript libraries and frontend libraries (React, Vue, Solid, Svelte).
