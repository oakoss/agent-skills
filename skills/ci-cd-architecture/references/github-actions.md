---
title: GitHub Actions
description: Hardened workflows, OIDC cloud authentication, matrix builds, Bun CI optimization, and security best practices
tags:
  [github-actions, oidc, matrix, bun, security, caching, permissions, pinning]
---

# GitHub Actions

## Hardened Production Workflow

A production-ready workflow with OIDC authentication, Bun caching, and strict permissions.

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Cache Bun Dependencies
        uses: actions/cache@v5
        with:
          path: ~/.bun/install/cache
          key: ${{ runner.os }}-bun-${{ hashFiles('**/bun.lock', '**/bun.lockb') }}
          restore-keys: |
            ${{ runner.os }}-bun-

      - name: Install dependencies
        run: bun install --frozen-lockfile

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v5
        with:
          role-to-assume: arn:aws:iam::1234567890:role/github-actions-deploy
          aws-region: us-east-1

      - name: Build & Deploy
        run: bun run build && bun run deploy
```

## OIDC Cloud Authentication

Long-lived AWS/Azure/GCP keys must not be used in production pipelines. OIDC provides short-lived, dynamically generated tokens.

### How OIDC Works

1. Workflow requests a JWT from GitHub's OIDC provider
2. Cloud provider validates the token against a trust policy
3. Cloud provider issues a short-lived access token (typically 1 hour)
4. Token expires automatically after the job completes

### AWS OIDC Setup

Required components in AWS:

- An OIDC identity provider pointing to `https://token.actions.githubusercontent.com`
- An IAM role with a trust policy scoped to the repository
- The audience set to `sts.amazonaws.com`

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v5
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
      aws-region: us-east-1
      role-session-name: GitHubActionsSession
```

The IAM trust policy must include a `sub` condition to restrict which repositories and branches can assume the role. Without this condition, any GitHub repository could potentially assume the role.

### Azure OIDC Setup

Azure uses workload identity federation. Configure a federated credential on an Azure AD app registration with:

- Issuer: `https://token.actions.githubusercontent.com`
- Subject: scoped to your repository and branch
- Audience: `api://AzureADTokenExchange`

### GCP OIDC Setup

GCP uses Workload Identity Federation. Create a Workload Identity Pool and Provider, then grant the pool access to a service account. Use `google-github-actions/auth` action with `workload_identity_provider` and `service_account` parameters.

## Permission Scoping

Explicitly define `permissions` at the job level. Never rely on defaults, which are overly broad.

```yaml
permissions:
  contents: read
  id-token: write
  # Only add write permissions where strictly necessary
```

Common permission combinations:

| Use Case           | Permissions Needed                       |
| ------------------ | ---------------------------------------- |
| Read-only checkout | `contents: read`                         |
| OIDC cloud deploy  | `id-token: write`, `contents: read`      |
| PR comment         | `pull-requests: write`, `contents: read` |
| Package publish    | `packages: write`, `contents: read`      |

## Bun CI Optimization

### Caching Strategy

Bun stores downloaded packages in a global cache at `~/.bun/install/cache`. Bun 1.2+ introduced a text-based `bun.lock` format alongside the legacy binary `bun.lockb`. Hash whichever lockfile format the project uses.

```yaml
- name: Cache Bun Dependencies
  uses: actions/cache@v5
  with:
    path: ~/.bun/install/cache
    key: ${{ runner.os }}-bun-${{ hashFiles('**/bun.lock', '**/bun.lockb') }}
    restore-keys: |
      ${{ runner.os }}-bun-
```

### Performance Tips

- Use `bun install --frozen-lockfile` for deterministic installs
- Use `bun test` for sub-second unit and integration test execution
- Use `bun run` instead of `npx` for script execution

## Matrix Builds

Run tests across multiple runtime versions in parallel.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20, 22, 24]
    steps:
      - uses: actions/checkout@v6
      - name: Run Tests
        run: bun test
```

## Multi-Stage Pipeline

Separate test and deploy into distinct jobs with dependencies.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun test
      - run: bun run lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Deploy
        run: bun run deploy
```

## Enterprise Pipeline Stages

```text
Build -> Test -> Security Scan -> Stage Deploy -> Integration Tests -> Prod Deploy
```

Features at scale: multi-environment (dev/staging/prod), blue-green deployments, canary releases, automated rollbacks, SAST/DAST scanning.

## Security Hardening

### Action Pinning

Pin third-party actions to a full commit SHA, not a tag or branch. Tags can be moved by maintainers (or attackers), but commit SHAs are immutable.

```yaml
# Vulnerable — tag can be repointed
- uses: some-org/some-action@v1

# Secure — immutable reference
- uses: some-org/some-action@a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
```

### Egress Control with StepSecurity

StepSecurity Harden-Runner monitors and optionally blocks outbound network traffic from GitHub Actions runners. It detects unauthorized data exfiltration and supply chain attacks at the DNS, HTTPS, and network layers.

```yaml
steps:
  - uses: step-security/harden-runner@v2
    with:
      egress-policy: audit
```

Start with `audit` mode to build a baseline, then switch to `block` mode with an explicit allowlist of domains.

### Ephemeral Runners

For self-hosted runners, use just-in-time (JIT) runners that are destroyed after a single job execution. This prevents persistent state from leaking between jobs or being compromised.

## Troubleshooting

**Workflow YAML errors**: Use `act` or dry-run commits to verify syntax and job dependencies before merging.

**OIDC failures**: Verify the trust relationship configuration in the cloud provider's IAM. Confirm `id-token: write` is set at the job level, not just at the workflow level if jobs override permissions.

**Cache misses**: Check that cache keys include the correct lockfile hash. Verify the cache path matches the package manager's install directory. Bun 1.2+ projects use `bun.lock` (text) instead of `bun.lockb` (binary).

**Slow pipelines**: Cache dependencies, use Bun for faster installs and test execution, parallelize independent jobs with matrix builds.
