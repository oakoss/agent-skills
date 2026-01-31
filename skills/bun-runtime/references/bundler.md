---
title: Bundler
description: Bun.build() API, entrypoints, output formats, code splitting, plugins, tree-shaking, loaders, and CLI usage
tags:
  [
    Bun.build,
    bundler,
    entrypoints,
    plugins,
    tree-shaking,
    code-splitting,
    minify,
    sourcemap,
    loaders,
    target,
  ]
---

# Bundler

## Basic Usage

### Programmatic API

```ts
const result = await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
});

if (!result.success) {
  console.error('Build failed:');
  for (const log of result.logs) {
    console.error(log);
  }
  process.exit(1);
}

for (const output of result.outputs) {
  console.log(`${output.kind}: ${output.path} (${output.size} bytes)`);
}
```

### CLI Equivalent

```bash
bun build ./src/index.ts --outdir ./dist
```

## Configuration Options

### Full Configuration

```ts
const result = await Bun.build({
  entrypoints: ['./src/index.tsx', './src/worker.ts'],
  outdir: './dist',
  target: 'browser',
  format: 'esm',
  splitting: true,
  minify: true,
  sourcemap: 'linked',
  external: ['react', 'react-dom'],
  define: {
    'process.env.API_URL': JSON.stringify('https://api.example.com'),
  },
  naming: {
    entry: '[dir]/[name]-[hash].[ext]',
    chunk: 'chunks/[name]-[hash].[ext]',
    asset: 'assets/[name]-[hash].[ext]',
  },
  drop: ['console', 'debugger'],
  banner: '"use client";',
  footer: '// Built with Bun',
});
```

### CLI Flags

```bash
bun build ./src/index.tsx --outdir ./dist \
  --target browser \
  --format esm \
  --splitting \
  --minify \
  --sourcemap=linked \
  --external react \
  --external react-dom
```

## Target

| Target      | Description                    | Output                                    |
| ----------- | ------------------------------ | ----------------------------------------- |
| `"browser"` | Default. Standard web browsers | Standard ESM/IIFE                         |
| `"bun"`     | Bun runtime                    | Bun-optimized, supports `bun:` imports    |
| `"node"`    | Node.js runtime                | Node-compatible, respects `node:` imports |

```ts
await Bun.build({
  entrypoints: ['./src/server.ts'],
  outdir: './dist',
  target: 'bun',
});
```

## Format

| Format   | Description                                                 |
| -------- | ----------------------------------------------------------- |
| `"esm"`  | Default. ES modules with `import`/`export`                  |
| `"cjs"`  | CommonJS with `require`/`module.exports`                    |
| `"iife"` | Immediately Invoked Function Expression for `<script>` tags |

## Code Splitting

```ts
await Bun.build({
  entrypoints: ['./src/index.ts', './src/admin.ts'],
  outdir: './dist',
  splitting: true,
});
```

Shared modules between entrypoints are extracted into separate chunks. Only works with `"esm"` format.

## Minification

```ts
await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  minify: true,
});

await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  minify: {
    whitespace: true,
    identifiers: true,
    syntax: true,
  },
});
```

## Source Maps

| Option       | Description                                    |
| ------------ | ---------------------------------------------- |
| `"none"`     | No source maps (default)                       |
| `"linked"`   | Separate `.map` file with reference comment    |
| `"inline"`   | Embedded in output as data URL                 |
| `"external"` | Separate `.map` file without reference comment |

## Loaders

Map file extensions to built-in loaders:

```ts
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  outdir: './dist',
  loader: {
    '.png': 'dataurl',
    '.txt': 'file',
    '.svg': 'text',
  },
});
```

### Built-in Loaders

| Loader    | Extensions            | Description                    |
| --------- | --------------------- | ------------------------------ |
| `js`      | `.js`, `.mjs`, `.cjs` | JavaScript                     |
| `jsx`     | `.jsx`                | JavaScript + JSX               |
| `ts`      | `.ts`, `.mts`, `.cts` | TypeScript                     |
| `tsx`     | `.tsx`                | TypeScript + JSX               |
| `json`    | `.json`               | JSON, imported as object       |
| `toml`    | `.toml`               | TOML, imported as object       |
| `text`    | `.txt`                | Import as string               |
| `file`    | any                   | Copy to outdir, import as path |
| `dataurl` | any                   | Import as base64 data URL      |

## External Packages

Exclude packages from the bundle:

```ts
await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  external: ['express', 'pg', '@prisma/client'],
});
```

## Plugins

### Plugin Structure

```ts
import { type BunPlugin } from 'bun';

const envPlugin: BunPlugin = {
  name: 'env-loader',
  setup(build) {
    build.onResolve({ filter: /^env$/ }, (args) => {
      return { path: args.path, namespace: 'env' };
    });

    build.onLoad({ filter: /.*/, namespace: 'env' }, () => {
      return {
        contents: `export default ${JSON.stringify(Bun.env)}`,
        loader: 'json',
      };
    });
  },
};

await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  plugins: [envPlugin],
});
```

### Plugin Hooks

| Hook        | Description                                 |
| ----------- | ------------------------------------------- |
| `onResolve` | Intercept module resolution, remap paths    |
| `onLoad`    | Intercept module loading, transform content |

### onResolve Handler

```ts
build.onResolve({ filter: /\.yaml$/ }, (args) => {
  return {
    path: resolve(args.importer, '..', args.path),
    namespace: 'yaml',
  };
});
```

### onLoad Handler

```ts
build.onLoad({ filter: /\.yaml$/, namespace: 'yaml' }, async (args) => {
  const text = await Bun.file(args.path).text();
  const parsed = YAML.parse(text);
  return {
    contents: `export default ${JSON.stringify(parsed)}`,
    loader: 'json',
  };
});
```

## Define Global Constants

```ts
await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    'process.env.API_URL': JSON.stringify('https://api.example.com'),
    __DEV__: 'false',
  },
});
```

## Bytecode Compilation

Generate bytecode for faster startup (Bun target only):

```ts
await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
  target: 'bun',
  bytecode: true,
});
```

```bash
bun build ./src/index.ts --outdir ./dist --bytecode
```

Bytecode is limited to `cjs` format with `target: "bun"`.

## Build Result

```ts
const result = await Bun.build({
  entrypoints: ['./src/index.ts'],
  outdir: './dist',
});

result.success; // boolean
result.outputs; // BuildArtifact[]
result.logs; // BuildMessage[]

for (const output of result.outputs) {
  output.path; // Absolute file path
  output.size; // Size in bytes
  output.kind; // "entry-point" | "chunk" | "asset"
  output.hash; // Content hash

  await output.text(); // Read as string
  await output.arrayBuffer(); // Read as ArrayBuffer
}
```
