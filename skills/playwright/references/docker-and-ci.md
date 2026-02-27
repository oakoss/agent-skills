---
title: Docker and CI
description: Official Playwright Docker images, Dockerfile setup, Docker Compose for local testing, GitHub Actions CI, test sharding, artifact collection, and fail-fast strategies
tags:
  [
    Docker,
    Dockerfile,
    docker-compose,
    CI,
    GitHub Actions,
    sharding,
    artifacts,
    screenshots,
    videos,
    traces,
    blob-report,
    parallel,
  ]
---

# Docker and CI

## Official Docker Images

Playwright provides pre-built Docker images with browsers and system dependencies pre-installed:

```bash
docker pull mcr.microsoft.com/playwright:v1.58.2-noble
```

**Available images:**

| Image                                               | Base         | Use Case                |
| --------------------------------------------------- | ------------ | ----------------------- |
| `mcr.microsoft.com/playwright:v1.58.2-noble`        | Ubuntu 24.04 | Node.js tests           |
| `mcr.microsoft.com/playwright:v1.58.2-jammy`        | Ubuntu 22.04 | Node.js (legacy compat) |
| `mcr.microsoft.com/playwright/python:v1.58.2-noble` | Ubuntu 24.04 | Python tests            |

Always pin to a specific version tag. The image version must match the installed `@playwright/test` package version.

## Dockerfile for Playwright Tests

### Using Official Image (Recommended)

```dockerfile
FROM mcr.microsoft.com/playwright:v1.58.2-noble

RUN groupadd -r pwuser && useradd -r -g pwuser -G audio,video pwuser
RUN mkdir -p /home/pwuser && chown -R pwuser:pwuser /home/pwuser

WORKDIR /app
COPY --chown=pwuser:pwuser package.json package-lock.json ./
RUN npm ci

COPY --chown=pwuser:pwuser . .

USER pwuser

CMD ["npx", "playwright", "test"]
```

### Using Node.js Base Image

When the official image is too large or a custom base is needed:

```dockerfile
FROM node:20-bookworm

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
RUN npx playwright install --with-deps chromium

COPY . .

RUN groupadd -r pwuser && useradd -r -g pwuser -G audio,video pwuser
RUN chown -R pwuser:pwuser /app
USER pwuser

CMD ["npx", "playwright", "test"]
```

Use `--with-deps` to install browser system dependencies alongside browser binaries.

### Required Docker Run Flags

```bash
docker run --rm --init --ipc=host my-playwright-tests
```

| Flag         | Purpose                                                   |
| ------------ | --------------------------------------------------------- |
| `--init`     | Reaps zombie processes (Node.js does not handle PID 1)    |
| `--ipc=host` | Prevents Chromium crashes from insufficient shared memory |

Alternative to `--ipc=host` when host IPC sharing is not allowed:

```bash
docker run --rm --init --shm-size=2gb my-playwright-tests
```

**Security:** Always create a non-root user. Running as root disables the Chromium sandbox, which is a security risk when testing untrusted sites.

## Docker Compose for Local Testing

```yaml
services:
  playwright:
    build: .
    init: true
    ipc: host
    environment:
      - CI=true
      - BASE_URL=http://app:3000
    depends_on:
      app:
        condition: service_healthy
    volumes:
      - ./test-results:/app/test-results
      - ./playwright-report:/app/playwright-report

  app:
    build:
      context: .
      dockerfile: Dockerfile.app
    ports:
      - '3000:3000'
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000']
      interval: 5s
      timeout: 3s
      retries: 10
```

Mount `test-results` and `playwright-report` volumes to access artifacts from the host.

Update `playwright.config.ts` to use the compose service URL:

```typescript
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
  },
});
```

## GitHub Actions CI

### Basic Workflow

```yaml
name: Playwright Tests
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: lts/*
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Run Playwright tests
        run: npx playwright test
      - uses: actions/upload-artifact@v5
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

Use `if: ${{ !cancelled() }}` to upload artifacts even when tests fail.

### Fail-Fast with Changed Tests

Run only changed test files on PRs for faster feedback:

```yaml
steps:
  - uses: actions/checkout@v6
    with:
      fetch-depth: 0
  - uses: actions/setup-node@v6
    with:
      node-version: lts/*
  - name: Install dependencies
    run: npm ci
  - name: Install Playwright Browsers
    run: npx playwright install --with-deps
  - name: Run changed tests
    if: github.event_name == 'pull_request'
    run: npx playwright test --only-changed=$GITHUB_BASE_REF
  - name: Run all tests
    run: npx playwright test
```

Requires `fetch-depth: 0` for git history access.

### CI-Optimized Config

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',

  use: {
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
});
```

**Reporter strategy:**

- `blob` in CI -- generates mergeable `.zip` files for sharded runs
- `github` in CI -- generates inline annotations on PR diffs
- `html` locally -- interactive report with Speedboard

## Sharding Across CI Workers

Split tests across parallel jobs using `--shard`:

```yaml
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: lts/*
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Run Playwright tests
        run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
      - name: Upload blob report
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report
          retention-days: 1
```

Set `fail-fast: false` so all shards complete even if one fails.

### Merging Sharded Reports

```yaml
jobs:
  merge-reports:
    if: ${{ !cancelled() }}
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: lts/*
      - name: Install dependencies
        run: npm ci
      - name: Download blob reports
        uses: actions/download-artifact@v5
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - name: Merge into HTML Report
        run: npx playwright merge-reports --reporter html ./all-blob-reports
      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        with:
          name: html-report--attempt-${{ github.run_attempt }}
          path: playwright-report
          retention-days: 14
```

## Artifact Collection

### Recording Options

```typescript
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  outputDir: './test-results',
});
```

| Option       | Values                                                     | Recommended CI Setting |
| ------------ | ---------------------------------------------------------- | ---------------------- |
| `screenshot` | `'off'`, `'on'`, `'only-on-failure'`                       | `'only-on-failure'`    |
| `trace`      | `'off'`, `'on'`, `'retain-on-failure'`, `'on-first-retry'` | `'on-first-retry'`     |
| `video`      | `'off'`, `'on'`, `'retain-on-failure'`, `'on-first-retry'` | `'on-first-retry'`     |

Artifacts are stored in `test-results/` by default. Upload this directory in CI:

```yaml
- uses: actions/upload-artifact@v5
  if: ${{ !cancelled() }}
  with:
    name: test-results
    path: test-results/
    retention-days: 7
```

### Viewing Traces

```bash
npx playwright show-trace trace.zip
```

Traces can also be viewed at [trace.playwright.dev](https://trace.playwright.dev) by uploading the zip file.

## Parallel Test Execution

### Config-Level Parallelism

```typescript
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
});
```

- `fullyParallel: true` -- runs tests within a single file in parallel
- `workers` -- number of parallel worker processes (default: half of CPU cores)
- CI runners typically have 2 cores; set `workers: 2` to match

### Per-Project Workers (v1.52+)

```typescript
export default defineConfig({
  workers: 4,
  projects: [
    { name: 'fast-tests', workers: 4 },
    { name: 'serial-tests', workers: 1 },
  ],
});
```

The global `workers` value acts as a ceiling across all projects.

### File-Level Serial Execution

Force serial execution within a specific test file:

```typescript
test.describe.configure({ mode: 'serial' });

test('step 1', async ({ page }) => {
  // runs first
});

test('step 2', async ({ page }) => {
  // runs after step 1
});
```
