---
title: Configuration
description: tsdown.config.ts setup, entry points, output formats, target environments, platform options, and external dependency handling
tags:
  [
    config,
    entry,
    format,
    esm,
    cjs,
    iife,
    umd,
    target,
    platform,
    external,
    noExternal,
    defineConfig,
  ]
---

# Configuration

## Config File

tsdown searches for configuration files in the current working directory and parent directories. Supported file names:

- `tsdown.config.ts` (recommended)
- `tsdown.config.mts`, `tsdown.config.cts`
- `tsdown.config.js`, `tsdown.config.mjs`, `tsdown.config.cjs`
- `tsdown.config.json`

Configuration can also be defined in the `tsdown` field of `package.json`.

### Basic Config

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  outDir: 'dist',
  dts: true,
  clean: true,
});
```

### Custom Config Path

```bash
npx tsdown --config custom.config.ts
npx tsdown --no-config
```

## Entry Points

Entry points can be a string, array, or object for named entries.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
});
```

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    cli: 'src/cli.ts',
    utils: 'src/utils/index.ts',
  },
});
```

When no entry is specified, tsdown auto-detects `src/index.ts`.

## Output Formats

tsdown supports four output formats: `esm`, `cjs`, `iife`, and `umd`.

### Dual ESM/CJS Output

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  fixedExtension: true,
});
```

Setting `fixedExtension: true` ensures `.mjs`/`.cjs` extensions regardless of package.json `type` field. This is recommended for dual-format packages.

### Custom Extensions

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  outExtensions({ format, pkgType }) {
    return {
      js: format === 'esm' ? '.mjs' : '.cjs',
      dts: format === 'esm' ? '.d.mts' : '.d.cts',
    };
  },
});
```

### IIFE with Global Name

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: 'iife',
  globalName: 'MyLib',
});
```

## Target Environment

Set the compilation target for syntax downleveling.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  target: 'node18',
});
```

Valid targets include ES versions (`es2020`, `es2022`) and Node versions (`node18`, `node20`).

## Platform

Controls module resolution and built-in handling.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  platform: 'node',
});
```

| Platform  | Behavior                                               |
| --------- | ------------------------------------------------------ |
| `node`    | Node built-ins (`node:fs`, etc.) auto-externalized     |
| `browser` | No built-in externalization, browser-compatible output |
| `neutral` | No platform-specific behavior                          |

## External Dependencies

By default, all `node_modules` dependencies are externalized. Use `external`, `noExternal`, and `inlineOnly` to customize.

### Explicit Externals

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  external: ['react', 'vue'],
});
```

### Bundle Specific Dependencies

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  noExternal: ['lodash-es', 'tiny-invariant'],
});
```

### Strict Inline Mode

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  inlineOnly: ['lodash-es', 'debug'],
});
```

With `inlineOnly`, tsdown throws an error if any other dependencies are imported but not listed.

### Regex Patterns

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  external: [/^node:/, /^@types\//],
  noExternal: [/^lodash/],
});
```

### Dynamic Resolution

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  noExternal: (id, _importer) => {
    if (id.startsWith('lodash/')) return true;
    return false;
  },
});
```

### Skip All node_modules

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  skipNodeModulesBundle: true,
});
```

## Multiple Configurations

Build multiple outputs with different settings in a single run.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig([
  {
    entry: ['src/index.ts'],
    format: ['esm'],
    outDir: 'dist/esm',
  },
  {
    entry: ['src/cli.ts'],
    format: ['cjs'],
    outDir: 'dist/cjs',
    banner: {
      js: '#!/usr/bin/env node',
    },
  },
]);
```

## Dynamic Configuration

Access CLI options in the config function.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig((cliOptions) => {
  return {
    entry: ['src/index.ts'],
    format: ['esm', 'cjs'],
    minify: process.env.NODE_ENV === 'production',
    dts: cliOptions.dts ?? true,
  };
});
```

## Recommended package.json Setup

```json
{
  "name": "my-library",
  "type": "module",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.mts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.mts",
  "scripts": {
    "build": "tsdown"
  }
}
```
