---
title: CI Sharding
description: Playwright test sharding across CI machines, GitHub Actions workflow, workers vs sharding, blob report merging, and browser caching
tags: [sharding, ci, github-actions, parallelism, blob-reports, browser-cache]
---

# CI Sharding

## What is Sharding

Sharding splits a test suite into multiple parts that run on separate machines in parallel. This dramatically reduces total execution time for large suites.

## GitHub Actions Workflow

```yaml
jobs:
  e2e:
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: npx playwright test --shard=${{ matrix.shard }}/4
```

## Workers vs Sharding

- **Workers**: Local parallelism on a single machine. Usually set equal to the number of CPU cores.
- **Sharding**: Global parallelism across multiple machines. Each shard runs a subset of tests independently.

Use both together for maximum throughput: multiple workers per shard.

## Blob Reports (Merging Results)

When sharding, each machine produces its own test report. Use blob reports to merge them:

1. Each shard runs: `npx playwright test --reporter=blob`
2. Upload blob artifacts from each shard
3. Final job runs: `npx playwright merge-reports ./all-blobs`

## Browser Caching

Speed up CI by caching downloaded browser binaries:

```yaml
- name: Cache Playwright Browsers
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: ${{ runner.os }}-playwright-${{ env.PLAYWRIGHT_VERSION }}
```

Pin the Playwright version in your cache key to ensure browsers are re-downloaded when the version changes.
