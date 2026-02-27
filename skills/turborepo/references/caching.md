---
title: Caching and Debugging
description: Cache configuration, remote cache setup, debugging cache misses and hits, and diagnostic tools
tags: [caching, remote-cache, summarize, dry, force, outputs, hash, debugging]
---

# Caching and Debugging

## Diagnostic Tools

### --summarize

Generates a JSON file with all hash inputs. Compare two runs to find differences.

```bash
turbo build --summarize
# Creates .turbo/runs/<run-id>.json

# Compare runs
diff .turbo/runs/<first-run>.json .turbo/runs/<second-run>.json
```

### --dry / --dry=json

See what would run without executing:

```bash
turbo build --dry
turbo build --dry=json  # machine-readable output
```

### --force

Skip reading cache, re-execute all tasks:

```bash
turbo build --force
```

## Unexpected Cache Misses

**Symptom:** Task runs when you expected a cache hit.

Checklist:

1. Run with `--summarize`, compare with previous run
2. Check env vars with `--dry=json`
3. Look for lockfile/config changes in git
4. Check if environment variables are in `env` key
5. Check if `.env` files are in `inputs`
6. Verify `outputs` includes all produced files

### Common Causes

- **Environment variable changed**: Different `API_URL` between runs
- **.env file changed**: Not tracked by default, add to `inputs`
- **Lockfile changed**: Installing/updating packages changes global hash
- **turbo.json changed**: Config changes invalidate global hash

## Incorrect Cache Hits

**Symptom:** Cached output is stale/wrong.

- **Missing env var**: Task uses a var not listed in `env`
- **Missing file in inputs**: Task reads a file outside default inputs

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

## Remote Caching

Configure remote cache (Vercel or custom S3-based) for fast CI:

- Use `persistent: true` and `cache: false` for dev servers to prevent cache poisoning
- Use `--summarize` or `--dry` to debug cache behavior

### GitHub Actions Setup

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
      TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

### Alternative: actions/cache

If you can't use remote cache:

```yaml
- uses: actions/cache@v5
  with:
    path: .turbo
    key: turbo-${{ runner.os }}-${{ hashFiles('**/turbo.json', '**/package-lock.json') }}
    restore-keys: |
      turbo-${{ runner.os }}-
```

## Useful Flags

```bash
# Only show output for cache misses
turbo build --output-logs=new-only

# Show output for everything
turbo build --output-logs=full

# See why tasks are running
turbo build --verbosity=2
```
