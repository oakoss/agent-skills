---
title: Shared Configs
description: Sharing TypeScript, ESLint, and Prettier configuration across pnpm workspace packages
tags: [tsconfig, eslint, prettier, shared, configuration, extends, monorepo]
---

# Shared Configs

Centralizing configuration in a pnpm workspace avoids duplication and ensures consistency across packages. Common shared configs include TypeScript, ESLint, and Prettier.

## Shared TypeScript Configuration

### Base tsconfig Package

Create a shared config package that other packages extend:

```text
packages/
├── tsconfig/
│   ├── package.json
│   ├── base.json
│   ├── react.json
│   └── node.json
├── web/
│   ├── package.json
│   └── tsconfig.json
└── api/
    ├── package.json
    └── tsconfig.json
```

The shared package `package.json`:

```json
{
  "name": "@myapp/tsconfig",
  "version": "1.0.0",
  "private": true,
  "files": ["*.json"]
}
```

### Base Configuration

A strict base that all packages inherit:

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "exclude": ["node_modules", "dist"]
}
```

### React Configuration

Extends the base with JSX and DOM settings:

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}
```

### Node Configuration

Extends the base with Node.js-specific settings:

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["ES2022"],
    "module": "Node16",
    "moduleResolution": "Node16"
  }
}
```

### Consuming the Shared Config

Add the config package as a workspace dependency:

```json
{
  "name": "@myapp/web",
  "devDependencies": {
    "@myapp/tsconfig": "workspace:*"
  }
}
```

Extend from the shared config in `tsconfig.json`:

```json
{
  "extends": "@myapp/tsconfig/react.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

For the Node API package:

```json
{
  "extends": "@myapp/tsconfig/node.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

## Shared ESLint Configuration

### ESLint Config Package

Create a shared ESLint config as a workspace package:

```text
packages/
├── eslint-config/
│   ├── package.json
│   └── index.js
├── web/
│   ├── package.json
│   └── eslint.config.js
└── api/
    ├── package.json
    └── eslint.config.js
```

The config package `package.json`:

```json
{
  "name": "@myapp/eslint-config",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./index.js"
  },
  "dependencies": {
    "@eslint/js": "^9.0.0",
    "typescript-eslint": "^8.0.0"
  },
  "devDependencies": {
    "@myapp/tsconfig": "workspace:*"
  }
}
```

### Flat Config (ESLint v9+)

The shared config exports an array of config objects:

```js
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strict,
  {
    rules: {
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
  {
    ignores: ['**/dist/**', '**/node_modules/**'],
  },
);
```

### Consuming ESLint Config

Add the dependency:

```json
{
  "name": "@myapp/web",
  "devDependencies": {
    "@myapp/eslint-config": "workspace:*"
  }
}
```

Spread the shared config and add package-specific overrides:

```js
import baseConfig from '@myapp/eslint-config';

export default [
  ...baseConfig,
  {
    rules: {
      'no-console': 'warn',
    },
  },
];
```

## Shared Prettier Configuration

### Root Prettier Config

Prettier config at the workspace root applies to all packages. No shared package needed:

```json
{
  "singleQuote": true,
  "semi": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 80
}
```

Place this in the workspace root as `.prettierrc` or `prettier.config.js`.

### Prettier Config as a Package

For more complex setups, create a shared package:

```json
{
  "name": "@myapp/prettier-config",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./index.js"
  }
}
```

```js
export default {
  singleQuote: true,
  semi: true,
  tabWidth: 2,
  trailingComma: 'all',
  printWidth: 80,
  plugins: ['prettier-plugin-tailwindcss'],
};
```

Reference in each package's `package.json`:

```json
{
  "name": "@myapp/web",
  "prettier": "@myapp/prettier-config",
  "devDependencies": {
    "@myapp/prettier-config": "workspace:*"
  }
}
```

## Root package.json Scripts

Define workspace-wide scripts in the root `package.json`:

```json
{
  "name": "@myapp/root",
  "private": true,
  "scripts": {
    "build": "pnpm -r run build",
    "dev": "pnpm --filter @myapp/web dev",
    "lint": "pnpm -r run lint",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "pnpm -r run typecheck",
    "test": "pnpm -r run test",
    "clean": "pnpm -r exec rm -rf dist node_modules/.cache"
  }
}
```

## .npmrc Workspace Settings

Common workspace-related `.npmrc` settings at the workspace root:

```ini
link-workspace-packages=false
prefer-workspace-packages=true
shared-workspace-lockfile=true
save-workspace-protocol=rolling
```

| Setting                     | Recommended | Description                                           |
| --------------------------- | ----------- | ----------------------------------------------------- |
| `link-workspace-packages`   | `false`     | Require explicit `workspace:` protocol                |
| `prefer-workspace-packages` | `true`      | Prefer local packages over registry                   |
| `shared-workspace-lockfile` | `true`      | Single lockfile at workspace root (default)           |
| `save-workspace-protocol`   | `rolling`   | Auto-add `workspace:^` when installing local packages |
