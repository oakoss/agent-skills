---
title: Package.json Configuration
description: Exports field, main/module/types, files allowlist, sideEffects, engines, and peerDependencies for npm packages
tags:
  [
    exports,
    main,
    module,
    types,
    files,
    sideEffects,
    engines,
    peerDependencies,
    subpath-exports,
  ]
---

# Package.json Configuration

## The `exports` Field

The `exports` field is the modern standard for defining package entry points. It replaces `main` and `module`, provides encapsulation (consumers cannot import internal files), and supports conditional resolution per environment.

### Basic Single Entry Point

```json
{
  "name": "my-lib",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    }
  }
}
```

### Subpath Exports

Expose specific modules without leaking internals:

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./utils": {
      "types": "./dist/utils.d.ts",
      "default": "./dist/utils.js"
    },
    "./hooks": {
      "types": "./dist/hooks.d.ts",
      "default": "./dist/hooks.js"
    },
    "./package.json": "./package.json"
  }
}
```

Consumers can now `import { debounce } from 'my-lib/utils'` but cannot `import { internal } from 'my-lib/dist/internal'`.

### Subpath Patterns

Use wildcards for packages with many entry points:

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./*": {
      "types": "./dist/*.d.ts",
      "default": "./dist/*.js"
    }
  }
}
```

### Always Include `./package.json`

Many tools (bundlers, linters, framework CLIs) read `package.json` directly. Without this entry, the `exports` encapsulation blocks access:

```json
{
  "exports": {
    ".": { "types": "./dist/index.d.ts", "default": "./dist/index.js" },
    "./package.json": "./package.json"
  }
}
```

## Legacy Fields: `main`, `module`, `types`

Keep these for backward compatibility with older tools and bundlers:

```json
{
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  }
}
```

| Field     | Used By                                         | Notes                                        |
| --------- | ----------------------------------------------- | -------------------------------------------- |
| `main`    | Node.js (pre-exports), older bundlers           | CJS entry; fallback when `exports` is absent |
| `module`  | Bundlers (webpack, Rollup, esbuild)             | ESM entry; not recognized by Node.js         |
| `types`   | TypeScript (pre-exports support)                | Top-level type declaration entry             |
| `exports` | Node.js 12.7+, modern bundlers, TypeScript 4.7+ | Preferred; takes precedence over all above   |

## `files` Allowlist

Controls which files are included in the published package. Without it, everything not in `.gitignore` or `.npmignore` is published:

```json
{
  "files": ["dist", "LICENSE"]
}
```

Certain files are always included regardless: `package.json`, `README.md`, `LICENSE`/`LICENCE`, and the `main` entry file. Certain files are always excluded: `node_modules`, `.git`, `.npmrc`.

Verify contents before publishing:

```bash
npm pack --dry-run
```

## `sideEffects`

Tells bundlers whether modules have side effects (code that runs on import). Setting this enables aggressive tree-shaking:

```json
{
  "sideEffects": false
}
```

If specific files do have side effects (CSS imports, polyfills):

```json
{
  "sideEffects": ["./dist/polyfill.js", "**/*.css"]
}
```

## `engines`

Document the minimum runtime version required:

```json
{
  "engines": {
    "node": ">=18"
  }
}
```

This is advisory by default. Consumers can enforce it with `engine-strict=true` in their `.npmrc`. Use this to communicate which Node.js APIs your package depends on.

## `peerDependencies`

Declare dependencies that must be provided by the consuming project:

```json
{
  "peerDependencies": {
    "react": "^18.0.0 || ^19.0.0",
    "react-dom": "^18.0.0 || ^19.0.0"
  },
  "peerDependenciesMeta": {
    "react-dom": {
      "optional": true
    }
  }
}
```

Guidelines:

- Framework packages (React, Vue, Angular) should always be peers
- npm 7+ auto-installs peer dependencies
- Use `peerDependenciesMeta` to mark optional peers (e.g., `react-dom` for a lib that also works in React Native)
- Specify broad version ranges to avoid conflicts in consumer projects

## `type` Field

Controls how Node.js interprets `.js` files:

```json
{
  "type": "module"
}
```

| `type` value           | `.js` interpreted as | CJS files use   | ESM files use   |
| ---------------------- | -------------------- | --------------- | --------------- |
| `"module"`             | ESM                  | `.cjs`          | `.js` or `.mjs` |
| `"commonjs"` (default) | CJS                  | `.js` or `.cjs` | `.mjs`          |

For dual-format packages, `"type": "module"` is the recommended default. Use `.cjs` extension for any CommonJS output files.
