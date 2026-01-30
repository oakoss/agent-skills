---
title: Environment Variables
description: env key configuration, globalEnv, strict vs loose modes, framework inference, and .env file handling
tags:
  [
    environment,
    env,
    globalEnv,
    strict-mode,
    loose-mode,
    framework-inference,
    dotenv,
  ]
---

# Environment Variables

## env Key

Variables listed in `env` affect cache hits -- changing the value invalidates cache.

```json
{
  "tasks": {
    "build": {
      "env": ["API_URL", "NEXT_PUBLIC_*", "!DEBUG"]
    }
  }
}
```

Use wildcards (`*`) for framework-prefixed vars. Use `!` to exclude from hash.

## globalEnv

Variables that affect all tasks globally:

```json
{
  "globalEnv": ["NODE_ENV"],
  "globalDependencies": [".env"]
}
```

## .env Files in Inputs

Turbo does NOT load `.env` files (your framework does), but Turbo needs to know about changes:

```json
{
  "tasks": {
    "build": {
      "env": ["API_URL"],
      "inputs": ["$TURBO_DEFAULT$", ".env", ".env.*"]
    }
  }
}
```

## Strict Mode (Default)

Only explicitly configured variables are available to tasks. Unlisted vars are filtered out.

Benefits: Guarantees cache correctness, prevents accidental dependencies, reproducible builds.

```bash
turbo run build --env-mode=strict
```

## Loose Mode

All system environment variables are available but only `env`/`globalEnv` vars affect the hash:

```bash
turbo run build --env-mode=loose
```

Risks: Cache may restore incorrect results if unhashed vars changed. Use for migrating legacy projects.

## Framework Inference

Turborepo auto-detects frameworks and includes their conventional env vars:

| Framework        | Pattern             |
| ---------------- | ------------------- |
| Next.js          | `NEXT_PUBLIC_*`     |
| Vite             | `VITE_*`            |
| Create React App | `REACT_APP_*`       |
| Gatsby           | `GATSBY_*`          |
| Nuxt             | `NUXT_*`, `NITRO_*` |
| Expo             | `EXPO_PUBLIC_*`     |
| Astro            | `PUBLIC_*`          |
| SvelteKit        | `PUBLIC_*`          |

### Disabling Framework Inference

```bash
turbo run build --framework-inference=false
```

Or exclude specific patterns:

```json
{
  "tasks": {
    "build": {
      "env": ["!NEXT_PUBLIC_*"]
    }
  }
}
```

## passThroughEnv

Variables available at runtime but NOT included in cache hash:

```json
{
  "tasks": {
    "build": {
      "passThroughEnv": ["AWS_SECRET_KEY", "GITHUB_TOKEN"]
    }
  }
}
```

Changes to these vars won't cause cache misses.

## globalPassThroughEnv

For CI variables that need to be available but shouldn't affect cache:

```json
{
  "globalPassThroughEnv": ["GITHUB_TOKEN", "CI"]
}
```

## Anti-Patterns

### Environment Variables Not Hashed

```json
// Bad: API_URL changes won't rebuild
{ "tasks": { "build": { "outputs": ["dist/**"] } } }

// Good: API_URL in hash
{ "tasks": { "build": { "outputs": ["dist/**"], "env": ["API_URL"] } } }
```

### Overly Broad globalDependencies

```json
// Bad: affects all hashes
{ "globalDependencies": ["**/.env.*local"] }

// Better: task-level inputs
{
  "globalDependencies": [".env"],
  "tasks": {
    "build": { "inputs": ["$TURBO_DEFAULT$", ".env*"] }
  }
}
```

### Root .env File

Package `.env` files in each app, not a single root `.env`. Root `.env` creates implicit coupling, coarse cache invalidation, and security risks.

## NOT an Anti-Pattern

A large `env` array (50+ variables) is fine. It means thorough environment declaration.

## Checking Environment Mode

```bash
turbo run build --dry=json | jq '.tasks[].environmentVariables'
```
