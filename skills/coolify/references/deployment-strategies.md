---
title: Deployment Strategies
description: Auto-deploy, webhook deploys, GitHub Actions CI/CD, manual API triggers, and environment promotion patterns
tags: [deploy, auto-deploy, webhook, github-actions, ci-cd, pipeline, promotion]
---

# Deployment Strategies

## Strategy Comparison

| Strategy       | Trigger             | Control Level | Best For                        |
| -------------- | ------------------- | ------------- | ------------------------------- |
| Auto-deploy    | Git push            | Low           | Simple projects, fast iteration |
| Webhook        | API call            | Medium        | Triggered after external checks |
| GitHub Actions | Workflow completion | High          | Build + test + deploy pipeline  |
| Manual API     | Developer action    | Full          | Production releases, rollbacks  |

## Auto-Deploy

The simplest approach. Coolify redeploys automatically on every push to the configured branch.

### Setup

1. Connect repository via GitHub App integration in Coolify dashboard
2. Navigate to application > Advanced > General
3. Enable "Auto Deploy"

### Via API

```bash
# Enable auto-deploy
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"is_auto_deploy_enabled": true}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

### When to Use

- Development and staging environments
- Projects without a test suite or CI pipeline
- Solo developer workflows
- Rapid prototyping

### When NOT to Use

- Production with required test gates
- Multi-environment promotion (dev > staging > prod)
- Teams requiring code review before deploy

## Webhook Deploy

Trigger deploys programmatically via HTTP. Gives you control over when deployments happen.

### Get the Webhook URL

Each application has a unique deploy webhook URL. Find it in the application's Webhook section in the dashboard, or construct it:

```bash
# Deploy via UUID endpoint
curl -s \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_URL/api/v1/deploy?uuid=<app-uuid>&force=true"
```

### Webhook Secret (Manual Git Providers)

For non-GitHub App integrations, configure a webhook secret:

1. Generate a random secret string
2. Set it in Coolify's application Webhook settings
3. Configure your Git provider to send push webhooks to Coolify's payload URL with the secret

Coolify only processes webhooks with matching secrets.

## GitHub Actions Pipeline

The most controlled approach. Build, test, and scan in CI before triggering Coolify deployment.

### Basic: Build and Deploy

```yaml
name: Deploy to Coolify
on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

      - name: Deploy to Coolify
        run: |
          curl --fail --request GET \
            '${{ secrets.COOLIFY_WEBHOOK }}' \
            --header 'Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}'
```

### Required GitHub Secrets

| Secret            | Value                         | Where to Find                   |
| ----------------- | ----------------------------- | ------------------------------- |
| `COOLIFY_TOKEN`   | API token with `deploy` scope | Coolify > Settings > API Tokens |
| `COOLIFY_WEBHOOK` | Per-app deploy webhook URL    | Coolify > App > Webhooks        |

### Advanced: Test, Build, Deploy

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
      - run: pnpm lint

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to Coolify
        run: |
          curl --fail --request GET \
            '${{ secrets.COOLIFY_WEBHOOK }}' \
            --header 'Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}'
```

### Advanced: Update Commit SHA Before Deploy

For pre-built images, update the commit SHA so Coolify pulls the correct version:

```yaml
- name: Update commit and deploy
  run: |
    # Update the application to use the new commit
    curl --fail -X PATCH \
      -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      -d '{"git_commit_sha": "${{ github.sha }}"}' \
      "${{ secrets.COOLIFY_URL }}/api/v1/applications/${{ secrets.COOLIFY_APP_UUID }}"

    # Trigger deployment
    curl --fail \
      -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}" \
      "${{ secrets.COOLIFY_URL }}/api/v1/deploy?uuid=${{ secrets.COOLIFY_APP_UUID }}&force=true"
```

## Manual API Deploy

For production releases where you want full control:

```bash
# Deploy specific commit
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"git_commit_sha": "abc1234"}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"

curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_URL/api/v1/deploy?uuid=<uuid>&force=true"

# Rollback to previous commit
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"git_commit_sha": "prev-sha"}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"

curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_URL/api/v1/deploy?uuid=<uuid>&force=true"
```

## Pre/Post Deployment Commands

Run commands before or after deployment:

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "pre_deployment_command": "pnpm db:migrate",
    "post_deployment_command": "pnpm db:seed"
  }' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

## Coolify Setup Checklist

1. **Enable API access**: Settings > Configuration > Advanced > API Access
2. **Create API token**: Settings > API Tokens (select `deploy` + needed scopes)
3. **Note webhook URL**: Application > Webhooks section
4. **Add GitHub secrets**: `COOLIFY_TOKEN` and `COOLIFY_WEBHOOK`
5. **Test connection**: `curl -H "Authorization: Bearer $TOKEN" $URL/api/v1/version`
