---
title: Filtering and CI Patterns
description: Filter syntax, affected packages, directory-based filtering, exclusions, and GitHub Actions CI workflows
tags: [filter, affected, CI, github-actions, scope, directory, exclusions]
---

# Filtering and CI Patterns

## Filter Syntax

### Single Package

```bash
turbo run build --filter=web
turbo run test --filter=@acme/api
```

### Package with Dependencies

Build a package and everything it depends on:

```bash
turbo run build --filter=web...
```

### Package Dependents

Run in all packages that depend on a library:

```bash
turbo run test --filter=...ui
```

### Dependents Only (Exclude Target)

```bash
turbo run test --filter=...^ui
```

### Changed Packages

```bash
turbo run lint --filter=[HEAD^1]
turbo run lint --filter=[main...HEAD]
```

### Changed + Dependents

```bash
turbo run build test --filter=...[HEAD^1]
# Or shortcut:
turbo run build test --affected
```

### Directory-Based

```bash
turbo run build --filter=./apps/*
turbo run build --filter=./apps/web --filter=./apps/api
```

### Scope-Based

```bash
turbo run build --filter=@acme/*
```

### Exclusions

```bash
turbo run build --filter=./apps/* --filter=!admin
turbo run lint --filter=!legacy-app --filter=!deprecated-pkg
```

### Custom Affected Base

```bash
turbo run build --affected --affected-base=origin/develop
```

## Debugging Filters

```bash
turbo run build --filter=web... --dry
turbo run build --filter=...[HEAD^1] --dry=json
```

## GitHub Actions CI

### Complete Example

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
      TURBO_TEAM: ${{ vars.TURBO_TEAM }}

    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 2

      - uses: pnpm/action-setup@v3
        with:
          version: 9

      - uses: actions/setup-node@v6
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build
        run: turbo run build --affected

      - name: Test
        run: turbo run test --affected

      - name: Lint
        run: turbo run lint --affected
```

### Package Manager Setup

```yaml
# pnpm
- uses: pnpm/action-setup@v3
  with:
    version: 9
- run: pnpm install --frozen-lockfile

# Yarn
- run: yarn install --frozen-lockfile

# Bun
- uses: oven-sh/setup-bun@v1
- run: bun install --frozen-lockfile
```

### Remote Cache Setup

1. Create Vercel access token at Vercel Dashboard
2. Add `TURBO_TOKEN` as repository secret
3. Add `TURBO_TEAM` as repository variable
4. Reference in workflow `env` block

## CI Patterns Summary

| Scenario            | Command                                                     |
| ------------------- | ----------------------------------------------------------- |
| PR validation       | `turbo run build test lint --affected`                      |
| Deploy changed apps | `turbo run deploy --filter=./apps/* --filter=[main...HEAD]` |
| Full rebuild of app | `turbo run build --filter=production-app...`                |
