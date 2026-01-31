---
title: Dual Format
description: ESM and CJS dual builds, conditional exports, file extensions, type declarations, and the dual package hazard
tags:
  [
    esm,
    cjs,
    dual-package,
    conditional-exports,
    mjs,
    cjs,
    type-module,
    tsup,
    unbuild,
  ]
---

# Dual Format

## Why Dual Format

Not all consumers support ESM yet. Legacy Node.js applications, older bundlers, and tools like Jest (without ESM transform) may require CJS. Dual-format packages serve both audiences from a single codebase.

Node.js v22+ supports `require()` of ESM modules natively, which reduces the need for dual publishing over time. For new packages targeting current Node.js versions, ESM-only may be sufficient.

## Conditional Exports

The `exports` field supports per-condition resolution. Node.js and bundlers evaluate conditions top-to-bottom and use the first match:

```json
{
  "name": "my-lib",
  "type": "module",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  }
}
```

### Condition Evaluation Order

Conditions are matched in the order they appear in the object. Place more specific conditions before general ones:

```json
{
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      },
      "default": "./dist/index.js"
    }
  }
}
```

The `types` condition must always be first within each nested block. The `default` condition at the end acts as a fallback.

### Available Conditions

| Condition     | Matched When                           |
| ------------- | -------------------------------------- |
| `types`       | TypeScript resolving type declarations |
| `import`      | Loaded via `import` or `import()`      |
| `require`     | Loaded via `require()`                 |
| `node`        | Running in Node.js                     |
| `browser`     | Bundler targeting browser              |
| `development` | Development mode (bundler-specific)    |
| `production`  | Production mode (bundler-specific)     |
| `default`     | Fallback; always matches               |

## File Extensions

With `"type": "module"` in package.json:

| Extension | Interpreted As | Type Declaration |
| --------- | -------------- | ---------------- |
| `.js`     | ESM            | `.d.ts`          |
| `.mjs`    | ESM (always)   | `.d.mts`         |
| `.cjs`    | CJS (always)   | `.d.cts`         |

Explicit extensions (`.mjs`/`.cjs`) are unambiguous regardless of the `type` field. For dual-format packages with `"type": "module"`, use `.js` for ESM and `.cjs` for CJS output.

## Type Declarations for Dual Format

TypeScript must resolve the correct type declarations for each format. Mismatched types cause resolution failures.

### Colocated Type Declarations (Recommended)

Place `.d.ts` next to `.js` and `.d.cts` next to `.cjs`:

```text
dist/
  index.js       # ESM
  index.d.ts     # Types for ESM
  index.cjs      # CJS
  index.d.cts    # Types for CJS
```

With `"type": "module"`, TypeScript automatically associates `.d.ts` with `.js` (ESM) and `.d.cts` with `.cjs` (CJS).

### Explicit Type Conditions

Always specify `types` as the first condition:

```json
{
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  }
}
```

If `types` is not first, TypeScript may skip it and fail to find declarations.

## Build Tool Configuration

### tsup

Generates ESM, CJS, and type declarations in one command:

```ts
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
  outDir: 'dist',
});
```

```bash
npx tsup
```

Output structure:

```text
dist/
  index.js       # ESM
  index.cjs      # CJS
  index.d.ts     # ESM types
  index.d.cts    # CJS types
```

### unbuild

Configuration-light build tool used by Nuxt:

```ts
import { defineBuildConfig } from 'unbuild';

export default defineBuildConfig({
  entries: ['src/index'],
  declaration: true,
  rollup: {
    emitCJS: true,
  },
});
```

### Rollup

For fine-grained control:

```ts
import typescript from '@rollup/plugin-typescript';

export default [
  {
    input: 'src/index.ts',
    output: [
      { file: 'dist/index.js', format: 'esm' },
      { file: 'dist/index.cjs', format: 'cjs' },
    ],
    plugins: [typescript()],
  },
];
```

## The Dual Package Hazard

When a package provides both ESM and CJS entry points, a consumer might load both versions in the same process. This creates two separate module instances with separate state, breaking singletons, `instanceof` checks, and identity comparisons.

### Mitigation Strategies

**Stateless packages** are safe. If your library is purely functional with no module-level state, the hazard does not apply.

**Isolate state** by extracting shared state into an internal CJS module that both ESM and CJS entry points import:

```json
{
  "exports": {
    ".": {
      "import": "./dist/wrapper.js",
      "require": "./dist/index.cjs"
    },
    "./state": "./dist/state.cjs"
  }
}
```

The ESM wrapper imports from the CJS state module, ensuring a single instance.

**Document the hazard.** If your library maintains state, note in your README that consumers should not mix import styles.

## Complete Dual-Format package.json

```json
{
  "name": "my-lib",
  "version": "1.0.0",
  "type": "module",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    },
    "./package.json": "./package.json"
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist"],
  "sideEffects": false,
  "engines": {
    "node": ">=18"
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts --clean",
    "prepublishOnly": "npm run build"
  }
}
```

## Validation

Verify your dual-format setup works across all resolution modes:

```bash
npx @arethetypeswrong/cli --pack .
```

Expected output shows green checkmarks for all resolution modes: `node10`, `node16-cjs`, `node16-esm`, and `bundler`.

Test the package as consumers would:

```bash
node -e "import('my-lib').then(m => console.log(Object.keys(m)))"
node -e "console.log(Object.keys(require('my-lib')))"
```
