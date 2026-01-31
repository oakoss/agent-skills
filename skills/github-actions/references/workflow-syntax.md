---
title: Workflow Syntax
description: Triggers, jobs, steps, environment variables, permissions, concurrency, and workflow-level configuration
tags:
  [
    triggers,
    push,
    pull_request,
    schedule,
    workflow_dispatch,
    jobs,
    steps,
    env,
    permissions,
    concurrency,
    defaults,
  ]
---

# Workflow Syntax

## File Location and Naming

Workflow files must be stored in `.github/workflows/` with a `.yml` or `.yaml` extension. Each file defines one workflow.

```yaml
# .github/workflows/ci.yml
name: CI
run-name: CI for ${{ github.ref_name }}
```

## Triggers

### Push and Pull Request

```yaml
on:
  push:
    branches: [main, 'release/**']
    paths: ['src/**', 'package.json']
    tags: ['v*']
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
    paths-ignore: ['docs/**', '*.md']
```

Path filters reduce unnecessary runs. Use `paths` to include or `paths-ignore` to exclude. Do not use both on the same event.

### Schedule

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'
```

Cron expressions use UTC. Minimum interval is 5 minutes. Scheduled workflows run on the default branch only. During high-load periods, runs may be delayed or skipped.

### Manual Dispatch

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]
      dry-run:
        description: 'Skip actual deployment'
        type: boolean
        default: false
```

Input types: `string`, `boolean`, `choice`, `environment`. Access via `${{ inputs.environment }}`.

### Webhook Events

```yaml
on:
  release:
    types: [published]
  issues:
    types: [opened, labeled]
  workflow_call:
    inputs:
      ref:
        type: string
        required: true
    secrets:
      token:
        required: true
```

`workflow_call` makes a workflow reusable by other workflows.

## Jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        node: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: pnpm test

  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
```

Jobs run in parallel by default. Use `needs` to create dependencies. The `if` conditional controls whether a job runs.

### Runner Selection

| Label            | OS           | Use Case                  |
| ---------------- | ------------ | ------------------------- |
| `ubuntu-latest`  | Ubuntu LTS   | General CI/CD             |
| `ubuntu-24.04`   | Ubuntu 24.04 | Pin specific OS version   |
| `windows-latest` | Windows      | Windows-specific builds   |
| `macos-latest`   | macOS        | iOS/macOS builds          |
| `self-hosted`    | Custom       | Custom hardware or config |

Pin OS versions for reproducibility in production workflows.

## Steps

```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v4
    with:
      fetch-depth: 0

  - name: Setup pnpm
    uses: pnpm/action-setup@v4

  - name: Install dependencies
    run: pnpm install --frozen-lockfile

  - name: Build
    run: pnpm build
    env:
      NODE_ENV: production

  - name: Upload coverage
    if: always()
    uses: actions/upload-artifact@v4
    with:
      name: coverage
      path: coverage/
```

Steps use either `uses` (for actions) or `run` (for shell commands). The `if: always()` runs a step regardless of previous step outcomes.

### Shell Configuration

```yaml
defaults:
  run:
    shell: bash
    working-directory: ./app

steps:
  - name: PowerShell step
    run: Get-Process
    shell: pwsh
```

Available shells: `bash`, `pwsh`, `python`, `sh`, `cmd` (Windows only), `powershell` (Windows only).

## Environment Variables

```yaml
env:
  CI: true
  NODE_ENV: production

jobs:
  build:
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    steps:
      - name: Print ref
        run: echo "Branch is ${{ github.ref_name }}"
        env:
          STEP_VAR: only-here
```

Variables cascade: workflow-level, job-level, step-level. Step-level overrides job-level overrides workflow-level.

### Setting Outputs Between Steps

```yaml
steps:
  - name: Set version
    id: version
    run: echo "value=$(cat VERSION)" >> "$GITHUB_OUTPUT"

  - name: Use version
    run: echo "Version is ${{ steps.version.outputs.value }}"
```

### Setting Outputs Between Jobs

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: prepare
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.prepare.outputs.version }}"
```

## Permissions

```yaml
permissions: {}

jobs:
  build:
    permissions:
      contents: read
      packages: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```

Set `permissions: {}` at workflow level to start with zero permissions, then grant per-job. Available scopes: `actions`, `checks`, `contents`, `deployments`, `id-token`, `issues`, `packages`, `pages`, `pull-requests`, `repository-projects`, `security-events`, `statuses`.

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Groups runs by a string key. When `cancel-in-progress` is true, a new run cancels any in-progress run in the same group. Common pattern for PR workflows to avoid wasting resources on superseded commits.

### Job-Level Concurrency

```yaml
jobs:
  deploy:
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false
    steps:
      - run: ./deploy.sh
```

Use `cancel-in-progress: false` for deployments to avoid partial deploys.

## Timeouts

```yaml
jobs:
  test:
    timeout-minutes: 30
    steps:
      - name: Long test
        timeout-minutes: 15
        run: pnpm test:e2e
```

Default job timeout is 360 minutes (6 hours). Set explicit timeouts to fail fast on hung processes.

## Services (Sidecar Containers)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - run: pnpm test:integration
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/postgres
```

Service containers run alongside the job. Use health checks to wait for readiness. Only available on Linux runners.
