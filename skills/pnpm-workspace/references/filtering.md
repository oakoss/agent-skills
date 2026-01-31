---
title: Filtering
description: pnpm --filter flag patterns for targeting specific packages, dependencies, dependents, directories, and git changes
tags:
  [
    filter,
    --filter,
    -F,
    dependencies,
    dependents,
    directory,
    git,
    exclude,
    recursive,
    run,
  ]
---

# Filtering

The `--filter` flag (alias `-F`) restricts pnpm commands to specific workspace packages. Filters can match by name, dependency relationship, directory, or git changes.

## By Package Name

Match exact package names or use glob patterns:

```bash
pnpm --filter @myapp/web build

pnpm --filter "@myapp/*" build

pnpm --filter "*utils" test
```

Scope is optional if the name is unique in the workspace. If multiple packages share the same unscoped name (e.g., `@myapp/core` and `@types/core`), the filter matches nothing without the scope.

```bash
pnpm --filter web dev

pnpm --filter @myapp/web dev
```

## By Dependencies

### Package and All Its Dependencies

Suffix with `...` to include a package and everything it depends on:

```bash
pnpm --filter "web..." build
```

This builds `web` and every package `web` depends on (direct and transitive).

### Only Dependencies (Exclude the Package Itself)

Use `^...` to select only the dependencies, not the package:

```bash
pnpm --filter "web^..." build
```

This builds all dependencies of `web` but not `web` itself. Useful for ensuring dependencies are built before the consuming package.

## By Dependents

### Package and All Its Dependents

Prefix with `...` to include a package and everything that depends on it:

```bash
pnpm --filter "...@myapp/ui" test
```

This tests `@myapp/ui` and every package that depends on it.

### Only Dependents (Exclude the Package Itself)

Use `...^` to select only the dependents:

```bash
pnpm --filter "...^@myapp/ui" test
```

This tests all packages that depend on `@myapp/ui` but not `@myapp/ui` itself. Useful for verifying consumers still work after a change.

## By Directory

Use `./path` or `{path}` syntax to match packages by filesystem location:

```bash
pnpm --filter "./apps/web" build

pnpm --filter "{packages}" test

pnpm --filter "{apps}..." build
```

The `{path}` syntax can combine with dependency/dependent operators:

```bash
pnpm --filter "...{packages}" test

pnpm --filter "{packages}..." build

pnpm --filter "...{packages}..." test
```

## By Git Changes

Select packages that changed since a specific commit or branch using `[ref]`:

```bash
pnpm --filter "[origin/main]" test

pnpm --filter "[HEAD~3]" build
```

Combine with dependency/dependent operators to also test affected packages:

```bash
pnpm --filter "...[origin/main]" test

pnpm --filter "[origin/main]..." build
```

Combine with directory filters:

```bash
pnpm --filter "{packages}[origin/main]" test
```

### Test Pattern

Use `--test-pattern` with change-based filters to only run tests when specific files changed:

```bash
pnpm --filter "...[origin/main]" --test-pattern "tests/*" test
```

## Excluding Packages

Prepend `!` to exclude packages from the selection:

```bash
pnpm --filter "!@myapp/web" build

pnpm --filter "@myapp/*" --filter "!@myapp/web" build

pnpm --filter "!./apps/web" build
```

In zsh, escape the `!` or use quotes:

```bash
pnpm --filter="\!@myapp/web" build

pnpm --filter="!@myapp/web" build
```

## Combining Filters

Use multiple `--filter` flags to combine selectors. All matches are unioned:

```bash
pnpm --filter "...@myapp/ui" --filter "@myapp/web" --filter "utils..." test
```

## Common Commands with Filters

### Run Scripts

```bash
pnpm --filter @myapp/web dev

pnpm --filter @myapp/web build

pnpm --filter "@myapp/*" lint
```

### Install Dependencies

```bash
pnpm --filter @myapp/web add react

pnpm --filter @myapp/web add -D vitest

pnpm --filter @myapp/web remove lodash
```

### Recursive Commands

Run a script in all workspace packages:

```bash
pnpm -r run build

pnpm -r run test

pnpm -r run lint
```

Combine recursive with filters:

```bash
pnpm -r --filter "./packages/*" run build
```

### Execute Binaries

```bash
pnpm --filter @myapp/web exec vitest run

pnpm --filter @myapp/web dlx create-next-app
```

## CI/CD Patterns

### Build Only Changed Packages

```bash
pnpm --filter "...[origin/main]" run build
```

### Test Changed Packages and Their Dependents

```bash
pnpm --filter "...[origin/main]" run test
```

### Build a Package and Its Dependencies in Order

```bash
pnpm --filter "web..." run build
```

pnpm respects the topological dependency order, building dependencies before their consumers.

### Lint Everything Except Documentation

```bash
pnpm --filter "!@myapp/docs" -r run lint
```

## Filter Cheat Sheet

| Filter                     | Selects                                          |
| -------------------------- | ------------------------------------------------ |
| `--filter foo`             | Package named `foo`                              |
| `--filter "foo..."`        | `foo` + all its dependencies                     |
| `--filter "foo^..."`       | Only dependencies of `foo`                       |
| `--filter "...foo"`        | `foo` + all its dependents                       |
| `--filter "...^foo"`       | Only dependents of `foo`                         |
| `--filter "./apps/web"`    | Package at that directory path                   |
| `--filter "{packages}"`    | All packages under `packages/`                   |
| `--filter "[origin/main]"` | Packages changed since `origin/main`             |
| `--filter "!foo"`          | Everything except `foo`                          |
| `--filter "@scope/*"`      | All packages matching the glob                   |
| `--filter "...[main]..."`  | Changed packages + their deps + their dependents |
