---
title: Caching and Artifacts
description: Dependency caching with actions/cache, setup-action built-in caching, artifact upload/download, and build output caching
tags:
  [
    cache,
    actions/cache,
    restore-keys,
    hashFiles,
    artifact,
    upload-artifact,
    download-artifact,
    pnpm,
    npm,
    yarn,
    build-cache,
  ]
---

# Caching and Artifacts

## Dependency Caching with Setup Actions

The simplest approach uses built-in caching in setup actions. This handles cache key generation and restore automatically.

### Node.js with pnpm

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: pnpm/action-setup@v4

  - uses: actions/setup-node@v6
    with:
      node-version: 22
      cache: 'pnpm'

  - run: pnpm install --frozen-lockfile
```

### Node.js with npm

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: actions/setup-node@v6
    with:
      node-version: 22
      cache: 'npm'

  - run: npm ci
```

### Node.js with yarn

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: actions/setup-node@v6
    with:
      node-version: 22
      cache: 'yarn'

  - run: yarn install --immutable
```

### Python with pip

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: actions/setup-python@v5
    with:
      python-version: '3.12'
      cache: 'pip'

  - run: pip install -r requirements.txt
```

### Go

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: actions/setup-go@v5
    with:
      go-version: '1.22'
      cache: true

  - run: go build ./...
```

### Rust

```yaml
steps:
  - uses: actions/checkout@v6

  - uses: actions/cache@v5
    with:
      path: |
        ~/.cargo/bin/
        ~/.cargo/registry/index/
        ~/.cargo/registry/cache/
        ~/.cargo/git/db/
        target/
      key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      restore-keys: |
        ${{ runner.os }}-cargo-
```

## Manual Caching with actions/cache

Use `actions/cache@v5` when setup actions do not cover your use case or you need fine-grained control.

```yaml
steps:
  - uses: actions/checkout@v6

  - name: Cache node_modules
    id: cache-deps
    uses: actions/cache@v5
    with:
      path: node_modules
      key: deps-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
      restore-keys: |
        deps-${{ runner.os }}-

  - name: Install dependencies
    if: steps.cache-deps.outputs.cache-hit != 'true'
    run: pnpm install --frozen-lockfile
```

### Cache Key Design

Build keys from most-specific to least-specific:

```yaml
key: deps-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
restore-keys: |
  deps-${{ runner.os }}-
```

- **Exact match**: Full key hit restores the exact cache
- **Prefix match**: `restore-keys` finds the most recent partial match
- **Cache miss**: No match found, full install required

### Multiple Cache Paths

```yaml
- uses: actions/cache@v5
  with:
    path: |
      ~/.pnpm-store
      node_modules
      .next/cache
    key: all-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-${{ hashFiles('src/**') }}
    restore-keys: |
      all-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-
      all-${{ runner.os }}-
```

### Granular Save and Restore

Use separate restore and save actions for advanced patterns like always saving regardless of job outcome:

```yaml
steps:
  - uses: actions/cache/restore@v4
    with:
      path: .build-cache
      key: build-${{ runner.os }}-${{ github.sha }}
      restore-keys: |
        build-${{ runner.os }}-

  - run: pnpm build

  - uses: actions/cache/save@v4
    if: always()
    with:
      path: .build-cache
      key: build-${{ runner.os }}-${{ github.sha }}
```

## Cache Limits and Behavior

- **10 GB per repository** total cache storage
- **Caches are immutable** once created (same key cannot be overwritten)
- **7-day eviction** for caches not accessed within 7 days
- **Branch scope**: Workflow runs can restore caches from the current branch or the default branch
- **Rate limit**: 200 cache uploads per minute per repository

## Artifacts

Artifacts persist data after a workflow completes. Use artifacts to share data between jobs or preserve build outputs.

### Upload Artifact

```yaml
steps:
  - run: pnpm build

  - uses: actions/upload-artifact@v4
    with:
      name: build-output
      path: dist/
      retention-days: 7
      if-no-files-found: error
```

### Download Artifact (Same Workflow)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/
      - run: ./deploy.sh dist/
```

### Multiple Artifacts

```yaml
steps:
  - uses: actions/download-artifact@v4
    with:
      path: all-artifacts/
      merge-multiple: true
```

When `merge-multiple` is true, all artifacts are downloaded and merged into the specified path.

### Artifact vs Cache

| Feature         | Cache                        | Artifact                       |
| --------------- | ---------------------------- | ------------------------------ |
| Purpose         | Speed up dependency installs | Preserve outputs between jobs  |
| Lifetime        | 7 days (last accessed)       | Configurable retention (1-90d) |
| Size limit      | 10 GB per repo               | Varies by plan                 |
| Cross-workflow  | Yes (same branch or default) | Same workflow run only         |
| Mutable         | No (key-based)               | Yes (same name overwrites)     |
| Post-run access | No                           | Yes (downloadable from UI/API) |

## Build Output Caching

### Next.js Build Cache

```yaml
steps:
  - uses: actions/cache@v5
    with:
      path: .next/cache
      key: nextjs-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-${{ hashFiles('src/**') }}
      restore-keys: |
        nextjs-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-
        nextjs-${{ runner.os }}-

  - run: pnpm build
```

### Turborepo Remote Cache

```yaml
steps:
  - run: pnpm turbo build
    env:
      TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
      TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

### Docker Layer Caching

```yaml
steps:
  - uses: docker/setup-buildx-action@v3

  - uses: docker/build-push-action@v6
    with:
      context: .
      push: true
      tags: app:latest
      cache-from: type=gha
      cache-to: type=gha,mode=max
```

The `type=gha` backend uses GitHub Actions cache for Docker layer caching.
