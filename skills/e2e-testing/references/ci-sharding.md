---
title: CI Sharding
description: Playwright test sharding across CI machines, GitHub Actions workflow, workers vs sharding, blob report merging, browser caching, and retry strategies
tags:
  [
    sharding,
    ci,
    github-actions,
    parallelism,
    blob-reports,
    browser-cache,
    retry,
  ]
---

# CI Sharding

## What is Sharding

Sharding splits a test suite across multiple CI machines that run in parallel. Each machine runs a subset of tests independently, reducing total execution time for large suites.

## GitHub Actions Workflow

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Cache Playwright Browsers
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Tests
        run: npx playwright test --shard=${{ matrix.shard }}/4

      - name: Upload blob report
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}
    needs: e2e
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci

      - name: Download blob reports
        uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true

      - name: Merge reports
        run: npx playwright merge-reports --reporter=html ./all-blob-reports

      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        with:
          name: html-report
          path: playwright-report/
          retention-days: 14
```

## Workers vs Sharding

| Dimension | Workers                              | Sharding                    |
| --------- | ------------------------------------ | --------------------------- |
| Scope     | Single machine                       | Multiple machines           |
| Config    | `workers` in config or `--workers=N` | `--shard=X/N` on CLI        |
| Use case  | Maximize CPU utilization locally     | Distribute across CI matrix |

Use both together for maximum throughput: multiple workers per shard.

```ts
export default defineConfig({
  workers: process.env.CI ? 2 : undefined,
});
```

## Blob Reports (Merging Results)

When sharding, each machine produces its own test report. Use blob reports to merge them:

1. Configure the blob reporter in `playwright.config.ts`:

```ts
export default defineConfig({
  reporter: process.env.CI ? 'blob' : 'html',
});
```

2. Each shard uploads its blob report as a CI artifact
3. A final job downloads all blobs and merges them:

```bash
npx playwright merge-reports --reporter=html ./all-blob-reports
```

## Browser Caching

Cache downloaded browser binaries to speed up CI:

```yaml
- name: Cache Playwright Browsers
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
```

The cache key uses the lockfile hash so browsers are re-downloaded when the Playwright version changes.

## Retry Strategy

Configure retries to handle flaky tests in CI without masking real failures:

```ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    trace: 'on-first-retry',
  },
});
```

- `retries: 2` in CI gives tests two extra attempts
- `trace: 'on-first-retry'` captures a trace on the first retry for debugging without the overhead of tracing every run

## Trace Upload

Upload traces as artifacts for debugging CI failures:

```yaml
- name: Upload traces
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: traces-${{ matrix.shard }}
    path: test-results/
    retention-days: 7
```

View traces locally or at `trace.playwright.dev`.

## Playwright Configuration for CI

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

Key CI settings:

- `forbidOnly`: Fail if `.only` is left in tests
- `retries`: Allow retries only in CI
- `workers`: Limit parallelism to avoid resource contention
- `trace: 'on-first-retry'`: Capture traces only on retries
- `screenshot: 'only-on-failure'`: Save screenshots on failures for quick triage
