---
title: Task Configuration
description: dependsOn syntax, transit nodes, outputs, inputs, task options, and package configurations
tags: [tasks, dependsOn, outputs, inputs, transit-nodes, persistent, turbo-json]
---

# Task Configuration

## Standard Build Pipeline

```json
{
  "$schema": "https://turborepo.dev/schema.v2.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## dependsOn Syntax

```json
{
  "tasks": {
    "build": { "dependsOn": ["^build"] },
    "test": { "dependsOn": ["build"] },
    "deploy": { "dependsOn": ["web#build"] }
  }
}
```

| Syntax           | Meaning                                             |
| ---------------- | --------------------------------------------------- |
| `^build`         | Run build in DEPENDENCIES first (upstream packages) |
| `build` (no `^`) | Run build in SAME PACKAGE first                     |
| `pkg#task`       | Specific package's task                             |

The `^` prefix is crucial -- without it, you're referencing the same package.

## Transit Nodes for Parallel Tasks

Tasks like lint and typecheck can run in parallel but need dependency-aware caching:

```json
{
  "tasks": {
    "transit": { "dependsOn": ["^transit"] },
    "lint": { "dependsOn": ["transit"] },
    "check-types": { "dependsOn": ["transit"] }
  }
}
```

**DO NOT use `dependsOn: ["^lint"]`** -- this forces sequential execution.
**DO NOT use `dependsOn: []`** -- this breaks cache invalidation.

The `transit` task creates dependency relationships without running anything (no matching script).

## outputs

Glob patterns for files to cache. If omitted, nothing is cached.

```json
{
  "tasks": {
    "build": {
      "outputs": ["dist/**", "build/**"]
    }
  }
}
```

**Framework examples:**

| Framework      | outputs                           |
| -------------- | --------------------------------- |
| Next.js        | `[".next/**", "!.next/cache/**"]` |
| Vite/Rollup    | `["dist/**"]`                     |
| tsc            | `["dist/**"]` or custom `outDir`  |
| tsc --noEmit   | `.tsbuildinfo` file location      |
| Lint/typecheck | `[]` (no file outputs)            |

## inputs

Files considered when calculating task hash. Defaults to all tracked files.

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "$TURBO_DEFAULT$",
        "!README.md",
        "$TURBO_ROOT$/tsconfig.base.json"
      ]
    }
  }
}
```

| Value                 | Meaning                                 |
| --------------------- | --------------------------------------- |
| `$TURBO_DEFAULT$`     | Include default inputs, then add/remove |
| `$TURBO_ROOT$/<path>` | Reference files from repo root          |

## Task Options Reference

| Option           | Default | Description                                            |
| ---------------- | ------- | ------------------------------------------------------ |
| `cache`          | `true`  | Enable/disable caching                                 |
| `persistent`     | `false` | Long-running tasks that don't exit                     |
| `interactive`    | `false` | Allow stdin input                                      |
| `interruptible`  | `false` | Allow `turbo watch` to restart                         |
| `outputLogs`     | `full`  | `full`, `hash-only`, `new-only`, `errors-only`, `none` |
| `with`           | -       | Run tasks alongside (concurrent, not sequential)       |
| `description`    | -       | Human-readable task description                        |
| `passThroughEnv` | -       | Available at runtime but NOT in cache hash             |

## Package Configurations

Use per-package `turbo.json` instead of cluttering root with `package#task` overrides:

```json
{
  "extends": ["//"],
  "tasks": {
    "test": { "outputs": ["coverage/**"] }
  }
}
```

## Dev Task with ^dev Pattern (for turbo watch)

```json
{
  "tasks": {
    "dev": {
      "dependsOn": ["^dev"],
      "cache": false,
      "persistent": false
    }
  }
}
```

```json
{
  "extends": ["//"],
  "tasks": {
    "dev": { "persistent": true }
  }
}
```

Packages run one-shot `dev` scripts; apps override with `persistent: true`. Use with `turbo watch dev`.
