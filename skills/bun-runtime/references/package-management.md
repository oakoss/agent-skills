---
title: Package Management
description: Bun package manager commands, dependency management, workspaces, lockfile, overrides, and CI configuration
tags:
  [
    bun-install,
    bun-add,
    bun-remove,
    workspaces,
    lockfile,
    overrides,
    bunx,
    dependencies,
    ci,
  ]
---

# Package Management

## Installing Dependencies

### Basic Install

```bash
bun install
```

Reads `package.json` and writes `bun.lockb` (binary lockfile). Faster than npm/yarn/pnpm due to native resolution and hardlink-based caching.

### CI Mode (Frozen Lockfile)

```bash
bun install --frozen-lockfile
```

Fails if `bun.lockb` would change. Use in CI pipelines for reproducible builds.

### Install Options

```bash
bun install                     # Install all dependencies
bun install --production        # Skip devDependencies
bun install --frozen-lockfile   # Fail if lockfile would change
bun install --no-save           # Don't update package.json
bun install --dry-run           # Show what would be installed
bun install --force             # Re-download all packages
```

## Adding and Removing Packages

### Add Packages

```bash
bun add express                 # Production dependency
bun add -d typescript           # Dev dependency (--dev)
bun add -D @types/node          # Dev dependency (alias)
bun add --optional fsevents     # Optional dependency
bun add -g create-vite          # Global install
bun add zod@3.22                # Specific version
bun add zod@latest              # Latest version
```

### Remove Packages

```bash
bun remove lodash
bun remove -g create-vite       # Remove global
```

### Update Packages

```bash
bun update                      # Update all to latest compatible
bun update react                # Update specific package
bun update --latest             # Ignore semver ranges
```

## Running Scripts

### Package.json Scripts

```bash
bun run build                   # Run "build" script
bun run dev                     # Run "dev" script
bun run test                    # Run "test" script
```

### Run Files Directly

```bash
bun run index.ts                # Run TypeScript directly
bun run script.js               # Run JavaScript
bun index.ts                    # Shorthand (omit "run")
```

### Execute Without Installing

```bash
bunx create-vite my-app         # Like npx
bunx prisma generate            # Run package binary
bunx --bun vitest               # Force Bun runtime for the package
```

## Workspaces

### Configuration

```json
{
  "name": "my-monorepo",
  "workspaces": ["packages/*", "apps/*"]
}
```

### Workspace Commands

```bash
bun install                     # Install all workspace dependencies
bun add -d typescript --filter "packages/*"  # Add to filtered workspaces
```

### Cross-Workspace Dependencies

```json
{
  "name": "@myorg/web",
  "dependencies": {
    "@myorg/shared": "workspace:*"
  }
}
```

The `workspace:*` protocol links to the local workspace package. Bun resolves these as symlinks.

## Lockfile

Bun uses `bun.lockb`, a binary lockfile optimized for speed.

### Inspecting the Lockfile

```bash
bun bun.lockb                   # Print human-readable lockfile
```

### Generating a Yarn-Compatible Lockfile

```bash
bun install --yarn              # Also generate yarn.lock
```

### Lockfile in Version Control

Always commit `bun.lockb` to version control. It ensures deterministic installs across environments.

## Overrides and Resolutions

### Overrides (package.json)

```json
{
  "overrides": {
    "lodash": "4.17.21",
    "react": "$react"
  }
}
```

- Force a specific version for all nested dependencies
- Use `$packageName` to reference the version in your own dependencies

### Trusted Dependencies

```json
{
  "trustedDependencies": ["@prisma/client", "esbuild"]
}
```

Only packages listed in `trustedDependencies` can run postinstall scripts. This is a security feature enabled by default in Bun.

## Patching Packages

```bash
bun patch express               # Extract package for editing
# Make changes to node_modules/express/...
bun patch --commit express      # Save patch
```

Patches are stored in `patches/` directory and applied automatically on install.

## Global Configuration

### bunfig.toml

```toml
[install]
# Registry configuration
registry = "https://registry.npmjs.org"

# Scoped registries
[install.scopes]
"@myorg" = "https://npm.myorg.com"

# Cache directory
[install.cache]
dir = "~/.bun/install/cache"
```

### Environment Variables

```bash
BUN_INSTALL_CACHE_DIR=~/.bun/cache  # Custom cache location
BUN_CONFIG_REGISTRY=https://registry.npmjs.org  # Default registry
```

## Migration from npm/yarn/pnpm

Bun reads `package.json` and is compatible with the npm registry. To migrate:

```bash
rm -rf node_modules package-lock.json yarn.lock pnpm-lock.yaml
bun install
```

Bun generates `bun.lockb`. The `node_modules` structure is flat (similar to npm), using hardlinks from the global cache for disk efficiency.

### Compatibility Notes

- `package.json` scripts work as-is
- `node_modules` layout is compatible with Node.js tooling
- Lifecycle scripts (`postinstall`, `prepare`) run only for `trustedDependencies`
- `.npmrc` is partially supported (registry and auth token settings)
