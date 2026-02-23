---
title: Environment Variables
description: Managing per-project environment variables, dotenv files, PATH extensions, and redaction in mise
tags: [env, dotenv, path, redact, required, source, per-directory, secrets]
---

# Environment Variables

## Basic Environment Variables

Set environment variables in the `[env]` section of `mise.toml`. Variables activate automatically when you `cd` into the project directory:

```toml
[env]
NODE_ENV = "development"
DATABASE_URL = "postgres://localhost/mydb"
API_BASE_URL = "http://localhost:3000"
```

## Loading .env Files

Load variables from dotenv files:

```toml
[env]
_.file = ".env"
```

Load multiple files (later files override earlier ones):

```toml
[env]
_.file = [".env", ".env.local"]
```

The `.env.local` file should be gitignored for developer-specific overrides and secrets.

## Per-Environment Configuration

Use environment-specific config files with `MISE_ENV`:

```bash
# Activates mise.staging.toml
MISE_ENV=staging mise run deploy
```

Pin an environment in a local config:

```bash
mise use --env local node@22
```

This writes to `.mise.local.toml`, which should be gitignored.

## Extending PATH

Add directories to the front of `PATH`:

```toml
[env]
_.path = ["./bin", "./node_modules/.bin", "./scripts"]
```

This prepends the listed directories to `PATH` when inside the project.

## Sourcing Shell Scripts

Load environment variables from a shell script:

```toml
[env]
_.source = "./scripts/env.sh"
```

The script is sourced in a subshell and any exported variables are captured.

## Required Variables

Mark variables as required without setting a value. Mise errors if they are not set in the environment:

```toml
[env]
DATABASE_URL = { required = true }
API_KEY = { required = true }
```

This is useful for documenting required secrets without committing their values.

## Redacted Variables

Mark sensitive values as redacted to hide them from `mise env` output and logs:

```toml
[env]
API_KEY = { value = "sk-abc123", redact = true }
```

## Variable Templates

Use templates to reference other variables or dynamic values:

```toml
[env]
PROJECT_ROOT = "{{cwd}}"
LOG_DIR = "{{cwd}}/logs"
PATH_ADDITION = "{{cwd}}/bin"
```

## Debugging Environment

Inspect the active environment:

```bash
# Show all environment variables mise would set
mise env

# Show env for a specific tool
mise env node

# Print as shell export statements
mise env --shell bash

# Check which config files are loaded
mise doctor
```

## Environment Variable Precedence

Variables are resolved in this order (highest priority first):

1. Shell environment (already set before mise)
2. Task-level `env` overrides
3. `mise.toml` `[env]` section in current directory
4. `mise.toml` `[env]` in parent directories
5. `_.file` dotenv files
6. `~/.config/mise/config.toml` global config

## Practical Patterns

### Development vs Production Separation

```toml
# mise.toml (committed)
[env]
NODE_ENV = "development"
LOG_LEVEL = "debug"
_.file = [".env", ".env.local"]
```

```text
# .env (committed, safe defaults)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp_dev
```

```text
# .env.local (gitignored, secrets)
DATABASE_PASSWORD=mysecretpassword
API_KEY=sk-live-abc123
```

### Monorepo with Nested Configs

```toml
# apps/api/mise.toml
[env]
PORT = "3001"
SERVICE_NAME = "api"
```

```toml
# apps/web/mise.toml
[env]
PORT = "3000"
SERVICE_NAME = "web"
NEXT_PUBLIC_API_URL = "http://localhost:3001"
```

Each subdirectory gets its own environment when you `cd` into it.
