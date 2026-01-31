---
title: Matrix and Reusable Workflows
description: Matrix strategies with include/exclude, reusable workflows with workflow_call, and composite actions
tags:
  [
    matrix,
    strategy,
    include,
    exclude,
    fail-fast,
    reusable-workflow,
    workflow_call,
    composite-action,
    inputs,
    outputs,
  ]
---

# Matrix and Reusable Workflows

## Matrix Strategy

Matrix strategies generate multiple job runs from variable combinations.

### Basic Matrix

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

This generates 6 jobs (3 Node versions x 2 operating systems).

### Include and Exclude

```yaml
strategy:
  matrix:
    node: [18, 20, 22]
    os: [ubuntu-latest, windows-latest]
    include:
      - node: 22
        os: ubuntu-latest
        coverage: true
    exclude:
      - node: 18
        os: windows-latest
```

- **`include`**: Adds properties to matching combinations or creates new combinations
- **`exclude`**: Removes specific combinations from the matrix

### Include-Only Matrix

```yaml
strategy:
  matrix:
    include:
      - name: Unit Tests
        command: test:unit
      - name: Integration Tests
        command: test:integration
      - name: E2E Tests
        command: test:e2e
```

When only `include` is used without top-level variables, each entry becomes a standalone job.

### Fail-Fast and Max Parallel

```yaml
strategy:
  fail-fast: false
  max-parallel: 3
  matrix:
    node: [18, 20, 22]
```

- **`fail-fast: true`** (default): Cancels all in-progress matrix jobs when any job fails
- **`fail-fast: false`**: Lets all jobs run to completion regardless of failures
- **`max-parallel`**: Limits concurrent matrix jobs (useful for rate-limited resources)

### Dynamic Matrix with fromJSON

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          echo 'matrix={"node":[18,20,22],"include":[{"node":22,"coverage":true}]}' >> "$GITHUB_OUTPUT"

  test:
    needs: prepare
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJSON(needs.prepare.outputs.matrix) }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

Use `fromJSON()` to generate matrix values dynamically from a previous job.

## Reusable Workflows

Reusable workflows let you define a workflow once and call it from other workflows.

### Defining a Reusable Workflow

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        required: false
        default: '22'
      working-directory:
        type: string
        required: false
        default: '.'
    secrets:
      npm-token:
        required: false
    outputs:
      coverage:
        description: 'Coverage percentage'
        value: ${{ jobs.test.outputs.coverage }}

jobs:
  test:
    runs-on: ubuntu-latest
    outputs:
      coverage: ${{ steps.coverage.outputs.value }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}

      - run: npm ci
        env:
          NPM_TOKEN: ${{ secrets.npm-token }}

      - run: npm test -- --coverage

      - name: Extract coverage
        id: coverage
        run: echo "value=$(jq '.total.lines.pct' coverage/coverage-summary.json)" >> "$GITHUB_OUTPUT"
```

### Calling a Reusable Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test-app:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: '22'
      working-directory: ./app
    secrets:
      npm-token: ${{ secrets.NPM_TOKEN }}

  test-lib:
    uses: ./.github/workflows/reusable-test.yml
    with:
      working-directory: ./lib

  report:
    needs: [test-app, test-lib]
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "App coverage: ${{ needs.test-app.outputs.coverage }}%"
          echo "Lib coverage: ${{ needs.test-lib.outputs.coverage }}%"
```

### Cross-Repository Reusable Workflows

```yaml
jobs:
  deploy:
    uses: my-org/shared-workflows/.github/workflows/deploy.yml@v1
    with:
      environment: production
    secrets: inherit
```

- Reference with `owner/repo/.github/workflows/file.yml@ref`
- `secrets: inherit` passes all caller secrets to the reusable workflow
- The `@ref` can be a branch, tag, or commit SHA

### Calling with Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        package: [app, lib, docs]
    uses: ./.github/workflows/reusable-test.yml
    with:
      working-directory: ./packages/${{ matrix.package }}
```

Matrix strategies work with reusable workflow calls. The output from the last successful matrix job is used when the reusable workflow sets outputs.

### Reusable Workflow Limits

- Maximum 4 levels of nesting (workflow calling workflow calling workflow...)
- Maximum 20 reusable workflows per workflow file
- `env` context variables set at the caller level are not propagated to the called workflow
- Reusable workflows from public repos can be used by any repo; private repos can only use workflows within the same repo or organization

## Composite Actions

Composite actions bundle multiple steps into a single reusable action.

### Creating a Composite Action

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: 'Install pnpm and project dependencies'

inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '22'

outputs:
  cache-hit:
    description: 'Whether the cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - uses: pnpm/action-setup@v4
      shell: bash

    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'pnpm'

    - name: Install dependencies
      id: cache
      run: pnpm install --frozen-lockfile
      shell: bash
```

Every `run` step in a composite action requires an explicit `shell` property.

### Using a Composite Action

```yaml
steps:
  - uses: actions/checkout@v4

  - uses: ./.github/actions/setup-project
    with:
      node-version: '20'

  - run: pnpm test
```

### Composite vs Reusable Workflow

| Feature          | Composite Action              | Reusable Workflow                |
| ---------------- | ----------------------------- | -------------------------------- |
| Granularity      | Steps within a job            | Entire jobs                      |
| Secrets access   | Passed as inputs only         | `secrets:` or `secrets: inherit` |
| Debug visibility | Appears as one step in logs   | Each step visible separately     |
| Services         | Cannot define services        | Can define service containers    |
| Matrix           | Cannot define matrix          | Can use matrix strategy          |
| Calling syntax   | `uses:` in a step             | `uses:` at the job level         |
| Location         | Any directory with action.yml | Must be in .github/workflows/    |
