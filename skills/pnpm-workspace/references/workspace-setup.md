---
title: Workspace Setup
description: pnpm-workspace.yaml configuration, workspace protocol for local linking, and catalog dependencies for version consistency
tags:
  [
    pnpm-workspace.yaml,
    workspace protocol,
    catalog,
    catalogs,
    dependencies,
    monorepo,
    setup,
    link-workspace-packages,
  ]
---

# Workspace Setup

## pnpm-workspace.yaml

The `pnpm-workspace.yaml` file at the repository root defines which directories contain workspace packages. Globs match directories that contain a `package.json`.

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'
```

Nested globs and exclusion patterns are supported:

```yaml
packages:
  - 'packages/**'
  - 'apps/**'
  - '!**/test/**'
  - '!**/__fixtures__/**'
```

A typical monorepo directory structure:

```text
workspace-root/
├── pnpm-workspace.yaml
├── package.json
├── .npmrc
├── apps/
│   ├── web/
│   │   └── package.json
│   └── mobile/
│       └── package.json
├── packages/
│   ├── ui/
│   │   └── package.json
│   └── utils/
│       └── package.json
└── tools/
    └── scripts/
        └── package.json
```

## Workspace Protocol

The `workspace:` protocol ensures dependencies resolve to local workspace packages rather than fetching from the registry.

### Basic Linking

Use `workspace:*` to link to any version of a local package:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "@myapp/ui": "workspace:*",
    "@myapp/utils": "workspace:*"
  }
}
```

### Version Range Linking

Specify a semver range to enforce version constraints. Installation fails if the local package version does not satisfy the range:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "@myapp/ui": "workspace:^2.0.0",
    "@myapp/utils": "workspace:~1.5.0"
  }
}
```

### Relative Path Linking

Link by relative path when packages are not in standard workspace directories:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "@myapp/shared": "workspace:../shared"
  }
}
```

### Alias Linking

Create an alias for a workspace package:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "core-lib": "workspace:@myapp/core@*"
  }
}
```

### Publishing Behavior

When running `pnpm publish` or `pnpm pack`, workspace protocol specifiers are automatically replaced with real versions:

| Workspace Specifier | Published As |
| ------------------- | ------------ |
| `workspace:*`       | `1.2.3`      |
| `workspace:^`       | `^1.2.3`     |
| `workspace:~`       | `~1.2.3`     |
| `workspace:^1.0.0`  | `^1.0.0`     |

This replacement happens automatically; no manual version updates are needed before publishing.

## link-workspace-packages

The `.npmrc` setting `link-workspace-packages` controls automatic linking behavior:

```ini
# .npmrc
link-workspace-packages = true
```

| Value   | Behavior                                                        |
| ------- | --------------------------------------------------------------- |
| `true`  | Local packages matching version ranges are linked automatically |
| `false` | Only `workspace:` protocol triggers local linking (recommended) |
| `deep`  | Links local packages to subdependencies as well                 |

Setting `link-workspace-packages=false` with explicit `workspace:` protocol is the recommended approach. It makes dependency relationships explicit and avoids accidental linking.

## Catalogs

Catalogs define dependency versions in `pnpm-workspace.yaml` so all workspace packages share consistent versions.

### Default Catalog

The `catalog:` key defines a default set of versions:

```yaml
packages:
  - 'apps/*'
  - 'packages/*'

catalog:
  react: ^18.3.1
  react-dom: ^18.3.1
  typescript: ^5.6.0
  vite: ^6.0.0
```

Reference the default catalog in any workspace `package.json`:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "react": "catalog:",
    "react-dom": "catalog:"
  },
  "devDependencies": {
    "typescript": "catalog:",
    "vite": "catalog:"
  }
}
```

### Named Catalogs

Use `catalogs:` (plural) for multiple version sets:

```yaml
catalogs:
  react18:
    react: ^18.3.1
    react-dom: ^18.3.1
    '@types/react': ^18.3.0
  react17:
    react: ^17.0.2
    react-dom: ^17.0.2
    '@types/react': ^17.0.0
  testing:
    vitest: ^2.0.0
    '@testing-library/react': ^16.0.0
    '@testing-library/jest-dom': ^6.0.0
```

Reference named catalogs by name:

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "react": "catalog:react18",
    "react-dom": "catalog:react18"
  },
  "devDependencies": {
    "vitest": "catalog:testing",
    "@testing-library/react": "catalog:testing"
  }
}
```

### Publishing with Catalogs

Like workspace protocol, `catalog:` specifiers are replaced with actual version ranges on `pnpm publish`:

```json
{
  "dependencies": {
    "react": "catalog:react18"
  }
}
```

Becomes after publish:

```json
{
  "dependencies": {
    "react": "^18.3.1"
  }
}
```

### Combining Default and Named Catalogs

Both `catalog` (singular, default) and `catalogs` (plural, named) can coexist:

```yaml
packages:
  - 'apps/*'
  - 'packages/*'

catalog:
  typescript: ^5.6.0
  prettier: ^3.4.0
  eslint: ^9.0.0

catalogs:
  react18:
    react: ^18.3.1
    react-dom: ^18.3.1
  react17:
    react: ^17.0.2
    react-dom: ^17.0.2
```

```json
{
  "name": "@myapp/web",
  "dependencies": {
    "react": "catalog:react18"
  },
  "devDependencies": {
    "typescript": "catalog:",
    "prettier": "catalog:"
  }
}
```

## Shared Lockfile

pnpm workspaces use a single `pnpm-lock.yaml` at the workspace root. This provides:

- Consistent dependency resolution across all packages
- Faster installs through shared dependency deduplication
- Single source of truth for the dependency tree

Always run `pnpm install` from the workspace root to keep the lockfile in sync.
