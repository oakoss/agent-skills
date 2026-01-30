---
name: turborepo
description: |
  Turborepo monorepo build system and orchestration. Covers task pipelines, dependsOn syntax, caching configuration, remote cache, filtering, CI optimization, environment variables, workspace management, watch mode, and package boundaries.

  Use when configuring tasks, creating packages, setting up monorepo, sharing code between apps, running changed packages, debugging cache, optimizing CI, or resolving workspace dependencies.
---

# Turborepo

## Overview

Build system for JavaScript/TypeScript monorepos. Caches task outputs and runs tasks in parallel based on dependency graph. Always create package tasks (not root tasks), use `turbo run` in scripts, and let `dependsOn` manage execution order.

**When to use:** Monorepo task orchestration, build caching, CI optimization, workspace dependency management.

**When NOT to use:** Single-package projects, non-JavaScript monorepos, projects without build steps.

## Quick Reference

| Pattern                 | Syntax                                | Key Points                                      |
| ----------------------- | ------------------------------------- | ----------------------------------------------- |
| Dependency build        | `"dependsOn": ["^build"]`             | Build dependencies first                        |
| Same-package task       | `"dependsOn": ["codegen"]`            | Run in same package first                       |
| Specific package        | `"dependsOn": ["pkg#task"]`           | Named package's task                            |
| Parallel lint/typecheck | Transit Nodes pattern                 | Cache invalidation without sequential execution |
| Dev server              | `"persistent": true, "cache": false`  | Long-running, non-cacheable                     |
| Watch mode              | `turbo watch dev`                     | Re-run on file changes                          |
| Filter by package       | `--filter=web`                        | Single package                                  |
| Filter with deps        | `--filter=web...`                     | Package + dependencies                          |
| Changed packages        | `--affected`                          | Changed + dependents                            |
| Debug cache             | `--summarize` or `--dry`              | See hash inputs                                 |
| Package config          | `turbo.json` with `"extends": ["//"]` | Per-package overrides                           |
| Env vars in hash        | `"env": ["API_URL"]`                  | Cache invalidation on change                    |

## Decision Trees

### Configure a Task

```text
Configure a task?
+-- Define task dependencies       -> dependsOn in turbo.json
+-- Lint/check-types (parallel)    -> Transit Nodes pattern
+-- Specify build outputs          -> outputs key
+-- Handle environment variables   -> env key or globalEnv
+-- Dev/watch tasks                -> persistent: true, cache: false
+-- Package-specific config        -> Package turbo.json with extends: ["//"]
+-- Global settings                -> globalEnv, globalDependencies, cacheDir
```

### Cache Problems

```text
Cache problems?
+-- Outputs not restored           -> Missing outputs key
+-- Unexpected cache misses        -> Use --summarize or --dry to debug
+-- Skip cache entirely            -> --force or cache: false
+-- Remote cache not working       -> Check turbo login/link
+-- Environment causing misses     -> Var not in env key
```

### Filter Packages

```text
Filter packages?
+-- By package name                -> --filter=web
+-- By directory                   -> --filter=./apps/*
+-- Package + dependencies         -> --filter=web...
+-- Package + dependents           -> --filter=...web
+-- Changed + dependents           -> --affected
```

## Common Mistakes

| Mistake                                                                   | Correct Pattern                                                                                        |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Putting build logic in root `package.json` scripts instead of per-package | Define scripts in each package and use `turbo run` in root to delegate                                 |
| Using `^build` without declaring `workspace:*` dependency                 | Add the dependency in `package.json` first; `^build` only triggers for declared dependencies           |
| Chaining turbo tasks with `&&` in package scripts                         | Use `dependsOn` in `turbo.json` to declare task ordering                                               |
| Not adding environment variables to the `env` key in turbo.json           | Declare all build-affecting env vars in `env` so cache hashes correctly                                |
| Using `--parallel` flag to bypass dependency ordering                     | Configure `dependsOn` correctly or use transit nodes for parallel tasks with proper cache invalidation |

## Delegation

- **Monorepo structure exploration**: Use `Explore` agent to discover packages, workspace layout, and dependency relationships
- **Pipeline configuration and optimization**: Use `Task` agent to set up turbo.json tasks, configure caching, and debug cache misses
- **Monorepo architecture planning**: Use `Plan` agent to design package boundaries, shared libraries, and CI optimization strategy

## References

- [Task configuration and dependsOn patterns](references/task-configuration.md)
- [Caching, outputs, and debugging cache issues](references/caching.md)
- [Filtering, affected packages, and CI patterns](references/filtering-and-ci.md)
- [Workspace structure and package management](references/workspace-structure.md)
- [Environment variables and modes](references/environment-variables.md)
- [Watch mode, dev tasks, and anti-patterns](references/dev-and-anti-patterns.md)
