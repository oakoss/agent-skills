---
title: Declaration Files
description: TypeScript declaration file generation, DTS bundling, isolated declarations, and type resolution strategies
tags:
  [
    dts,
    declaration,
    types,
    d.ts,
    bundle-dts,
    compilerOptions,
    isolatedDeclarations,
  ]
---

# Declaration Files

## Basic DTS Generation

Enable declaration file generation with `dts: true`. tsdown auto-detects the output path from the `types` field in `package.json`.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
});
```

This generates `.d.ts` files alongside JavaScript output. With `fixedExtension: true`, it produces `.d.mts` and `.d.cts` for ESM and CJS respectively.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  fixedExtension: true,
});
```

## Advanced DTS Configuration

Pass an object to `dts` for fine-grained control.

### Bundle Declarations

Bundle all declaration files into a single `.d.ts` file, inlining types from dependencies.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: {
    bundle: true,
  },
});
```

### Resolve External Types

Include type declarations from external packages in the bundled output.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: {
    bundle: true,
    resolve: true,
  },
});
```

### Custom Entry Point

Specify a different entry point for declaration generation.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: {
    entry: './src/types.ts',
  },
});
```

### Custom Compiler Options

Override TypeScript compiler options for declaration generation.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  dts: {
    compilerOptions: {
      composite: false,
      declaration: true,
    },
  },
});
```

## Dual Format Declarations

When publishing both ESM and CJS, generate separate declaration files with proper extensions.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  fixedExtension: true,
});
```

This produces:

```text
dist/
  index.mjs       # ESM bundle
  index.cjs       # CJS bundle
  index.d.mts     # ESM declarations
  index.d.cts     # CJS declarations
```

## package.json Types Configuration

Ensure your `package.json` exports map includes type conditions for proper resolution.

```json
{
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
  "types": "./dist/index.d.mts"
}
```

The `types` condition must come first in each export block for TypeScript to resolve it correctly.

## Multiple Entry Point Declarations

When using multiple entry points, declaration files are generated for each entry.

```ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    utils: 'src/utils/index.ts',
    types: 'src/types.ts',
  },
  format: ['esm'],
  dts: true,
});
```

Map each entry in package.json exports:

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.mts",
      "import": "./dist/index.mjs"
    },
    "./utils": {
      "types": "./dist/utils.d.mts",
      "import": "./dist/utils.mjs"
    },
    "./types": {
      "types": "./dist/types.d.mts",
      "import": "./dist/types.mjs"
    }
  }
}
```

## Validating Declarations

Use the built-in `--attw` flag (Are The Types Wrong) to validate that declaration files resolve correctly for all export conditions.

```bash
npx tsdown --attw
```

Combine with `--publint` for full package validation:

```bash
npx tsdown --publint --attw
```

## Common DTS Issues

| Issue                             | Solution                                                          |
| --------------------------------- | ----------------------------------------------------------------- |
| Missing types in output           | Verify `dts: true` is set and `tsconfig.json` exists              |
| Wrong extension for declarations  | Use `fixedExtension: true` for dual ESM/CJS                       |
| Types not resolving for consumers | Ensure `types` condition is first in exports map                  |
| Declaration bundling too slow     | Use `dts: { bundle: false }` for faster builds during development |
| External types not included       | Use `dts: { resolve: true }` to inline external types             |
