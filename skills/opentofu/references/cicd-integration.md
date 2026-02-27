---
title: CI/CD Integration
description: GitHub Actions pipelines, drift detection, plan/apply workflow automation, and approval gates
tags: [cicd, github-actions, drift-detection, plan, apply, automation, pipeline]
---

# CI/CD Integration

## OpenTofu GitHub Actions Pipeline

### Plan on Pull Request

```yaml
name: OpenTofu Plan
on:
  pull_request:
    paths:
      - 'infra/**'

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v6

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        run: tofu init -input=false

      - name: Validate
        run: tofu validate

      - name: Plan
        id: plan
        run: tofu plan -input=false -no-color -out=plan.tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Comment Plan
        uses: actions/github-script@v7
        with:
          script: |
            const output = `${{ steps.plan.outputs.stdout }}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## OpenTofu Plan\n\`\`\`\n${output}\n\`\`\``
            });
```

### Apply on Merge

```yaml
name: OpenTofu Apply
on:
  push:
    branches: [main]
    paths:
      - 'infra/**'

permissions:
  contents: read

jobs:
  apply:
    runs-on: ubuntu-latest
    environment: production
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v6

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        run: tofu init -input=false

      - name: Apply
        run: tofu apply -input=false -auto-approve
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Drift Detection

Schedule periodic plans to detect infrastructure drift.

```yaml
name: Drift Detection
on:
  schedule:
    - cron: '0 6 * * *'

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v6

      - uses: opentofu/setup-opentofu@v1

      - name: Init
        run: tofu init -input=false

      - name: Detect Drift
        id: drift
        run: |
          tofu plan -input=false -no-color -detailed-exitcode 2>&1 | tee plan.txt
          echo "exitcode=${PIPESTATUS[0]}" >> "$GITHUB_OUTPUT"
        continue-on-error: true
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Notify on Drift
        if: steps.drift.outputs.exitcode == '2'
        run: |
          echo "::warning::Infrastructure drift detected! Review plan.txt"
```

Exit codes: `0` = no changes, `1` = error, `2` = changes detected (drift).

## Pulumi GitHub Actions Pipeline

```yaml
name: Pulumi
on:
  pull_request:
    paths:
      - 'infra/**'
  push:
    branches: [main]
    paths:
      - 'infra/**'

jobs:
  preview:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 20

      - run: npm ci

      - uses: pulumi/actions@v5
        with:
          command: preview
          stack-name: org/dev
          work-dir: infra
          comment-on-pr: true
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 20

      - run: npm ci

      - uses: pulumi/actions@v5
        with:
          command: up
          stack-name: org/production
          work-dir: infra
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Multi-Environment Pipeline Pattern

```yaml
name: Deploy Infrastructure
on:
  push:
    branches: [main]

jobs:
  deploy:
    strategy:
      max-parallel: 1
      matrix:
        environment: [dev, staging, production]
    runs-on: ubuntu-latest
    environment: ${{ matrix.environment }}
    steps:
      - uses: actions/checkout@v6

      - uses: opentofu/setup-opentofu@v1

      - name: Init
        run: tofu init -input=false -backend-config="environments/${{ matrix.environment }}/backend.hcl"

      - name: Plan
        run: tofu plan -input=false -var-file="environments/${{ matrix.environment }}/terraform.tfvars" -out=plan.tfplan

      - name: Apply
        run: tofu apply -input=false plan.tfplan
```

## Secret Management in CI

Avoid hardcoded credentials. Use OIDC for cloud provider authentication:

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/tofu-deploy
      aws-region: us-east-1

  - run: tofu apply -input=false -auto-approve
```

This eliminates long-lived access keys by using GitHub's OIDC token exchange.
