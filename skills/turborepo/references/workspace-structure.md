---
title: Workspace Structure
description: Monorepo directory organization, package configuration, workspace dependencies, and shared configs
tags:
  [
    workspace,
    structure,
    packages,
    dependencies,
    exports,
    typescript-config,
    eslint-config,
  ]
---

# Workspace Structure

## Workspace Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

## Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "packageManager": "pnpm@9.0.0",
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "latest"
  }
}
```

Key points:

- `private: true` prevents accidental publishing
- Scripts only delegate to `turbo run` -- no actual build logic
- Minimal devDependencies (just turbo and repo tools)
- App dependencies belong in each package, not root

## Package Tasks, Not Root Tasks

```json
// apps/web/package.json
{ "scripts": { "build": "next build", "lint": "eslint .", "test": "vitest" } }

// packages/ui/package.json
{ "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }
```

```json
// Root package.json ONLY delegates
{
  "scripts": {
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```

Root Tasks (`//#taskname`) are only for tasks that truly cannot exist in packages.

## Workspace Dependencies

Use `workspace:*` for internal dependencies:

```json
{
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/utils": "workspace:*"
  }
}
```

## Shared UI Package

```json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": "./src/index.ts",
    "./styles.css": "./src/styles.css"
  },
  "peerDependencies": {
    "react": "^19.0.0"
  }
}
```

## Shared TypeScript Config

```json
// packages/typescript-config/base.json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022"
  }
}

// packages/ui/tsconfig.json
{
  "extends": "@repo/typescript-config/library.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

## Shared ESLint Config

```json
// packages/eslint-config/package.json
{
  "name": "@repo/eslint-config",
  "exports": {
    "./base": "./base.js",
    "./next": "./next.js",
    "./library": "./library.js"
  }
}
```

## Anti-Patterns

### Relative Imports Across Packages

```ts
// Bad
import { Button } from '../../packages/ui/src/button';

// Good
import { Button } from '@repo/ui/button';
```

### Shared Code Inside Apps

Extract shared code to `packages/`, not `apps/web/shared/`.

### prebuild Scripts

```json
// Bad - bypasses dependency graph
{
  "scripts": {
    "prebuild": "cd ../../packages/types && bun run build",
    "build": "next build"
  }
}

// Good - declare dependency, let turbo handle order
{
  "dependencies": { "@repo/types": "workspace:*" },
  "scripts": { "build": "next build" }
}
```

### Chaining Turbo Tasks with &&

```json
// Bad
{ "scripts": { "changeset:publish": "bun build && changeset publish" } }

// Good
{ "scripts": { "changeset:publish": "turbo run build && changeset publish" } }
```

### Root Scripts Bypassing Turbo

```json
// Bad
{ "scripts": { "build": "bun build" } }

// Good
{ "scripts": { "build": "turbo run build" } }
```

## turbo run vs turbo

Always use `turbo run` in code (package.json, CI, scripts). The shorthand `turbo <task>` is only for one-off terminal commands.

## Lockfile

A lockfile is required for reproducible builds, dependency understanding, and cache correctness.
