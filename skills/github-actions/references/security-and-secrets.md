---
title: Security and Secrets
description: Secrets management, OIDC tokens, environment protection rules, permissions hardening, and supply chain security
tags:
  [
    secrets,
    OIDC,
    id-token,
    permissions,
    environment,
    protection-rules,
    supply-chain,
    SHA-pinning,
    pull_request_target,
    GITHUB_TOKEN,
  ]
---

# Security and Secrets

## Secrets Management

### Secret Scopes

| Scope        | Access                          | Use Case                    |
| ------------ | ------------------------------- | --------------------------- |
| Repository   | Single repo workflows           | API keys for one project    |
| Organization | Selected or all repos in org    | Shared service credentials  |
| Environment  | Jobs targeting that environment | Production-only deploy keys |

### Using Secrets in Workflows

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Secrets are masked in logs automatically. GitHub redacts exact string matches, so avoid storing structured data (JSON, YAML) as a single secret. Create individual secrets per value instead.

### Secret Restrictions

- Secrets cannot be used in `if:` conditionals directly
- Any user with write access to a repo has read access to all repo-level secrets
- Secrets are not passed to workflows triggered by forks (except `pull_request_target`)
- Maximum 100 organization secrets, 100 repository secrets, 100 environment secrets

### Managing Secrets via CLI

```bash
# Set a repository secret
gh secret set API_KEY --body "sk-abc123"

# Set from a file
gh secret set DEPLOY_KEY < deploy-key.pem

# Set an environment secret
gh secret set API_KEY --env production --body "sk-prod-abc123"

# List secrets
gh secret list
```

## Environment Protection Rules

Environments add deployment safeguards with required reviewers, wait timers, and branch restrictions.

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: ./deploy.sh staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - run: ./deploy.sh production
```

### Protection Rule Options

| Rule                | Effect                                              |
| ------------------- | --------------------------------------------------- |
| Required reviewers  | Pauses workflow until approved (up to 6 reviewers)  |
| Wait timer          | Delays job start by 0-43200 minutes                 |
| Branch restrictions | Limits which branches can deploy to the environment |
| Custom rules        | Org-level deployment protection via GitHub Apps     |

### Environment-Scoped Secrets

Environment secrets override repository secrets of the same name. Use this to have different credentials per environment:

```yaml
jobs:
  deploy:
    environment: ${{ inputs.environment }}
    steps:
      - run: ./deploy.sh
        env:
          API_URL: ${{ secrets.API_URL }}
```

The value of `API_URL` comes from the environment secret, not the repository secret.

## Permissions Hardening

### Principle of Least Privilege

```yaml
permissions: {}

jobs:
  build:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm build

  publish:
    permissions:
      contents: read
      packages: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm publish
```

Set `permissions: {}` at the workflow level to start with no permissions. Grant only what each job needs.

### Common Permission Sets

| Task                      | Required Permissions              |
| ------------------------- | --------------------------------- |
| Checkout code             | `contents: read`                  |
| Push commits/tags         | `contents: write`                 |
| Create/update PRs         | `pull-requests: write`            |
| Publish packages          | `packages: write`                 |
| Deploy to Pages           | `pages: write`, `id-token: write` |
| OIDC cloud authentication | `id-token: write`                 |
| Update check runs         | `checks: write`                   |
| Post PR comments          | `pull-requests: write`            |
| Upload security results   | `security-events: write`          |

### GITHUB_TOKEN Default Permissions

Organizations created before February 2023 may have `read-write` as the default. Change to `read` in repository or organization settings under Actions > General > Workflow permissions.

## OIDC Authentication

OIDC eliminates long-lived cloud credentials by issuing short-lived tokens per workflow run.

### How It Works

1. Workflow requests an OIDC token from GitHub's identity provider
2. Cloud provider validates the token against configured trust policy
3. Cloud provider issues short-lived access credentials
4. Workflow uses temporary credentials for cloud operations

### AWS with OIDC

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions
          aws-region: us-east-1

      - run: aws s3 sync dist/ s3://my-bucket/
```

### Google Cloud with OIDC

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/pool/providers/github
          service_account: deploy@project.iam.gserviceaccount.com

      - uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: my-app
          region: us-central1
          image: gcr.io/project/app:latest
```

### Azure with OIDC

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-app
```

### OIDC Token Claims

The OIDC token includes claims that cloud providers use for authorization:

| Claim         | Example                             | Use For                  |
| ------------- | ----------------------------------- | ------------------------ |
| `sub`         | `repo:org/repo:ref:refs/heads/main` | Branch-level access      |
| `repository`  | `org/repo`                          | Repo-level access        |
| `environment` | `production`                        | Environment-level access |
| `actor`       | `username`                          | User-level access        |
| `ref`         | `refs/heads/main`                   | Branch filtering         |

## Supply Chain Security

### Pin Actions to Commit SHA

```yaml
# Vulnerable - tag can be moved to malicious code
- uses: actions/checkout@v4

# Secure - pinned to exact commit
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

Pin third-party actions to full commit SHAs. Use Dependabot to keep pinned SHAs updated:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

### Avoid pull_request_target Pitfalls

```yaml
# DANGEROUS - runs PR code with write permissions
on: pull_request_target
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm test
```

`pull_request_target` runs with the base branch context and write permissions. Never checkout and execute code from the PR head in this context. Use `pull_request` for running untrusted code.

### Safe pull_request_target Pattern

```yaml
on: pull_request_target

jobs:
  label:
    permissions:
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
```

Only use `pull_request_target` for operations that do not execute PR code, such as labeling or commenting.

### Script Injection Prevention

```yaml
# Vulnerable - untrusted input in shell
- run: echo "Title is ${{ github.event.pull_request.title }}"

# Safe - pass through environment variable
- run: echo "Title is $TITLE"
  env:
    TITLE: ${{ github.event.pull_request.title }}
```

Never interpolate user-controlled values (`github.event.*.title`, `github.event.*.body`) directly in `run:` blocks. Pass them through environment variables instead.

### Security Scanning Tools

| Tool       | Purpose                           | Integration                        |
| ---------- | --------------------------------- | ---------------------------------- |
| Dependabot | Dependency vulnerability scanning | Built-in, `.github/dependabot.yml` |
| CodeQL     | Static analysis for security bugs | `github/codeql-action`             |
| Trivy      | Container and filesystem scanning | `aquasecurity/trivy-action`        |
| zizmor     | GitHub Actions static analysis    | Checks workflow misconfigs         |
