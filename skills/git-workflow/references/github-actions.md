---
title: GitHub Actions
description: Reusable workflows, matrix testing, deployment environments with gates, AI automation, and security best practices
tags: [github-actions, ci-cd, reusable-workflows, matrix, oidc, deployment]
---

# GitHub Actions

## Reusable Workflows

Avoid duplication by creating modular workflow templates:

```yaml
# .github/workflows/standard-ci.yml
name: Standard CI
on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: ${{ inputs.node-version }}
      - run: pnpm install && pnpm run lint && pnpm test
```

Calling a reusable workflow:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  ci:
    uses: ./.github/workflows/standard-ci.yml
    with:
      node-version: '22'
```

## Dynamic Matrix Testing

Test across multiple environments and configurations simultaneously:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [22, 24]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: ${{ matrix.node }}
      - run: pnpm install && pnpm test
```

## Deployment Environments and Gates

Use environments to manage secrets and required approvals:

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: pnpm deploy:staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - run: pnpm deploy:production
```

Environment configuration:

- **Staging**: Automatic deploy on `main` merge
- **Production**: Requires reviewer approval and successful smoke tests

## Composite Actions

Bundle multiple steps into a reusable action:

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install dependencies and setup environment
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v6
      with:
        node-version: '22'
    - uses: pnpm/action-setup@v4
    - run: pnpm install --frozen-lockfile
      shell: bash
```

## Security Best Practices

- **Least Privilege**: Use `permissions` block to limit what `GITHUB_TOKEN` can do
- **Secret Masking**: Ensure logs never contain sensitive data
- **OIDC Connect**: Authenticate with AWS/GCP/Azure without long-lived secrets
- **Pin action versions**: Use SHA hashes instead of tags for third-party actions

```yaml
permissions:
  contents: read
  pull-requests: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6 # pin to SHA in production
```

## AI-Assisted Automation

- **Automated code review**: Trigger LLM audits on every PR
- **Auto-remediation**: If CI fails due to lint errors, commit the fix automatically
- **PR summarization**: Generate changelog entries from commit messages
