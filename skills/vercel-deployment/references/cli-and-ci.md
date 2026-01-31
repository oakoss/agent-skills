---
title: CLI and CI/CD
description: Vercel CLI commands, deployment workflows, GitHub integration, GitHub Actions, and monorepo setup
tags:
  [cli, ci-cd, github-actions, monorepo, turborepo, deploy, promote, preview]
---

# CLI and CI/CD

## Vercel CLI Setup

Install globally or use via npx:

```bash
npm i -g vercel
```

Authenticate:

```bash
vercel login
```

Link a local project to a Vercel project:

```bash
vercel link
```

This creates a `.vercel/` directory with `project.json` containing `orgId` and `projectId`.

## Core CLI Commands

### Deploy

```bash
vercel                    # Deploy to preview
vercel --prod             # Deploy to production
vercel --prebuilt         # Deploy pre-built output (skip build on Vercel)
```

### Build Locally

```bash
vercel build              # Build using preview environment
vercel build --prod       # Build using production environment
```

`vercel build` outputs to `.vercel/output/`. Pair with `--prebuilt` for CI pipelines where you control the build step.

### Promote

Promote an existing deployment to production without rebuilding:

```bash
vercel promote <deployment-url>
vercel promote <deployment-url> --yes    # Skip confirmation
```

### Inspect and Logs

```bash
vercel inspect <deployment-url>   # View deployment details
vercel logs <deployment-url>      # Stream function logs
vercel ls                         # List recent deployments
```

### Environment Variables

```bash
vercel env ls                           # List all variables
vercel env add VAR_NAME production      # Add variable
vercel env rm VAR_NAME production       # Remove variable
vercel env pull .env.local              # Pull dev variables locally
```

### Local Development

```bash
vercel dev                # Run local dev server with Vercel features
vercel dev --listen 4000  # Custom port
```

`vercel dev` simulates serverless functions, environment variables, and routing locally.

### Domains

```bash
vercel domains ls                        # List domains
vercel domains add example.com           # Add domain
vercel domains inspect example.com       # View DNS info
```

### Rollback

```bash
vercel rollback                          # Rollback to previous production deployment
vercel rollback <deployment-url>         # Rollback to specific deployment
```

## GitHub Integration (Zero-Config)

Connect a GitHub repository in the Vercel dashboard for automatic deployments:

- **Push to production branch** (e.g., `main`) triggers a production deployment
- **Push to any other branch** triggers a preview deployment
- **Pull requests** get preview URLs posted as comments

No configuration files needed. Vercel auto-detects the framework and configures builds.

### Disabling Auto-Deploy for Specific Branches

```json
{
  "git": {
    "deploymentEnabled": {
      "main": true,
      "develop": true,
      "feature/*": false
    }
  }
}
```

### Ignored Build Step

Skip deployments when specific files change (useful for monorepos):

```json
{
  "ignoreCommand": "git diff --quiet HEAD^ HEAD -- ."
}
```

Returns exit code 0 (no changes, skip build) or 1 (changes detected, proceed).

## GitHub Actions (Custom CI/CD)

For more control than the built-in integration, use GitHub Actions with the Vercel CLI.

### Required Secrets

Add these as GitHub repository secrets:

| Secret              | Source                                     |
| ------------------- | ------------------------------------------ |
| `VERCEL_TOKEN`      | Vercel dashboard > Settings > Tokens       |
| `VERCEL_ORG_ID`     | `.vercel/project.json` after `vercel link` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after `vercel link` |

### Preview Deployment on Pull Request

```yaml
name: Preview Deployment
on:
  pull_request:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Pull Environment
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy
        id: deploy
        run: |
          url=$(vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$url" >> "$GITHUB_OUTPUT"

      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview: ${{ steps.deploy.outputs.url }}`
            })
```

### Production Deployment on Push to Main

```yaml
name: Production Deployment
on:
  push:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Pull Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Monorepo Setup

### Dashboard Configuration

Each app in a monorepo is a separate Vercel project. Configure per project:

1. **Root Directory**: Set to the app's directory (e.g., `apps/web`)
2. **Build Command**: Framework-specific (e.g., `next build`) or Turborepo command
3. **Install Command**: Run from root (e.g., `pnpm install --frozen-lockfile`)

### Turborepo Integration

Use Turborepo for efficient monorepo builds with caching:

```json
{
  "buildCommand": "cd ../.. && npx turbo run build --filter=web",
  "installCommand": "pnpm install --frozen-lockfile"
}
```

### Monorepo with GitHub Actions

Each app gets its own workflow with a project-specific ID:

```yaml
name: Deploy Web App
on:
  push:
    branches: [main]
    paths:
      - 'apps/web/**'
      - 'packages/**'

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_WEB_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Pull Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

Use `paths` filters to deploy only when relevant files change. Set `fetch-depth: 2` for Turborepo change detection.

### Ignored Build Step for Monorepos

Use `ignoreCommand` to skip unchanged apps in automatic deployments:

```bash
npx turbo-ignore
```

Configure in `vercel.json` or Project Settings > Git > Ignored Build Step:

```json
{
  "ignoreCommand": "npx turbo-ignore"
}
```

`turbo-ignore` checks if the current app or its dependencies changed since the last successful deployment.

## Vercel CLI Quick Reference

| Command                    | Description             |
| -------------------------- | ----------------------- |
| `vercel`                   | Deploy to preview       |
| `vercel --prod`            | Deploy to production    |
| `vercel build`             | Build locally           |
| `vercel deploy --prebuilt` | Deploy pre-built output |
| `vercel promote <url>`     | Promote to production   |
| `vercel rollback`          | Rollback production     |
| `vercel dev`               | Local dev server        |
| `vercel env pull`          | Pull env vars locally   |
| `vercel logs <url>`        | Stream function logs    |
| `vercel inspect <url>`     | Deployment details      |
| `vercel domains ls`        | List domains            |
| `vercel link`              | Link local to project   |
| `vercel login`             | Authenticate            |
| `vercel whoami`            | Current user            |
