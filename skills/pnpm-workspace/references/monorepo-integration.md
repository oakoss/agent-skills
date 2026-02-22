---
title: Monorepo Integration
description: End-to-end pnpm + Turborepo + Changesets pipeline, Docker deployment with pnpm deploy, and release workflow coordination
tags:
  [
    turborepo,
    changesets,
    integration,
    pipeline,
    docker,
    deploy,
    release,
    prune,
    ci,
  ]
---

# Monorepo Integration

How pnpm workspaces, Turborepo, and Changesets fit together as a stack.

## Tool Responsibilities

| Tool            | Role                                   | Scope                                                            |
| --------------- | -------------------------------------- | ---------------------------------------------------------------- |
| pnpm workspaces | Package linking, dependency management | `pnpm-workspace.yaml`, `workspace:` protocol, catalogs, lockfile |
| Turborepo       | Task orchestration, caching            | `turbo.json`, `dependsOn`, build/test/lint pipelines             |
| Changesets      | Versioning, changelog, publishing      | `.changeset/`, semver decisions, npm publish                     |

## When to Use What

```text
Setting up the monorepo?
├── Defining packages and linking    → pnpm workspaces
├── Build/test/lint pipelines        → Turborepo
└── Versioning and publishing        → Changesets

Day-to-day development?
├── Installing dependencies          → pnpm install (root)
├── Running tasks                    → turbo run build/test/lint
├── Adding a changeset               → changeset add
└── Filtering commands               → --filter (both pnpm and turbo)

Releasing packages?
├── Consuming changesets             → changeset version
├── Building in dependency order     → turbo run build
├── Publishing to npm                → changeset publish
└── CI automation                    → changesets/action
```

## End-to-End Release Pipeline

### Root package.json

```json
{
  "private": true,
  "packageManager": "pnpm@10.29.0",
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "changeset": "changeset",
    "version-packages": "changeset version",
    "ci:publish": "turbo run build && changeset publish"
  }
}
```

### Release Workflow

```bash
# 1. Developer adds changeset during feature work
pnpm changeset add

# 2. Changeset is committed with the PR
git add .changeset/ && git commit -m "feat: add feature"

# 3. CI merges PR — changesets/action detects pending changesets
#    Action opens a "Version Packages" PR with bumped versions

# 4. Merge the Version Packages PR
#    Action runs ci:publish: turbo builds in order, then changesets publishes

# 5. Tags are pushed automatically
```

### GitHub Actions CI

```yaml
name: Release
on:
  push:
    branches: [main]

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - uses: changesets/action@v1
        with:
          publish: pnpm ci:publish
          version: pnpm changeset version
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Changesets Config for pnpm + Turborepo

```json
{
  "changelog": ["@changesets/changelog-github", { "repo": "org/repo" }],
  "commit": false,
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "bumpVersionsWithWorkspaceProtocolOnly": true
}
```

`bumpVersionsWithWorkspaceProtocolOnly: true` prevents bumping bare semver ranges — only `workspace:*`, `workspace:^`, and `workspace:~` ranges trigger dependent bumps.

## Docker Deployment

Two approaches for containerizing monorepo apps: `pnpm deploy` and `turbo prune`.

### pnpm deploy (Recommended)

Copies a package and its isolated `node_modules` to a target directory. Requires `inject-workspace-packages=true` in `.npmrc` (pnpm 10+).

```dockerfile
FROM node:24-slim AS base
RUN corepack enable

FROM base AS builder
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm --filter=@myapp/web --prod deploy /prod/web

FROM base
WORKDIR /app
COPY --from=builder /prod/web .
EXPOSE 3000
CMD ["node", "dist/index.mjs"]
```

Use `--legacy` flag or `force-legacy-deploy: true` to skip the `inject-workspace-packages` requirement.

### turbo prune --docker

Creates a pruned monorepo slice optimized for Docker layer caching. Splits output into `json/` (package.json files only) and `full/` (complete source).

```dockerfile
FROM node:24-slim AS base
RUN corepack enable

FROM base AS pruner
WORKDIR /app
COPY . .
RUN pnpm dlx turbo prune @myapp/web --docker

FROM base AS installer
WORKDIR /app
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=@myapp/web

FROM base
WORKDIR /app
COPY --from=installer /app/apps/web/dist ./dist
COPY --from=installer /app/apps/web/package.json .
EXPOSE 3000
CMD ["node", "dist/index.mjs"]
```

### Which to Choose

| Factor        | pnpm deploy                    | turbo prune                |
| ------------- | ------------------------------ | -------------------------- |
| Output        | Self-contained directory       | Pruned monorepo structure  |
| Layer caching | Single COPY layer              | Separate json/full layers  |
| Build step    | Build before deploy            | Build inside Docker        |
| Lockfile      | Generates dedicated lockfile   | Prunes existing lockfile   |
| Best for      | Simple apps, production images | Complex builds, CI caching |

## Filtering: pnpm vs Turborepo

Both tools support `--filter` but with different syntax and behavior.

| Pattern           | pnpm                       | Turborepo           |
| ----------------- | -------------------------- | ------------------- |
| By name           | `--filter "web"`           | `--filter=web`      |
| With dependencies | `--filter "web..."`        | `--filter=web...`   |
| With dependents   | `--filter "...web"`        | `--filter=...web`   |
| By directory      | `--filter "./apps/*"`      | `--filter=./apps/*` |
| Git changes       | `--filter "[origin/main]"` | `--affected`        |
| Exclude           | `--filter "\!web"`         | `--filter=!web`     |

**When to use which:**

- Use **pnpm `--filter`** for package management: `pnpm --filter web add react`
- Use **Turborepo `--filter`** for task execution: `turbo run build --filter=web`

## Workspace Protocol + Changesets

When Changesets versions a package, it updates `workspace:^` and `workspace:~` ranges in consuming packages. The `updateInternalDependencies: "patch"` config controls the bump cascade.

| Protocol      | Before version         | After `@myapp/ui` bumps to 2.0.0 |
| ------------- | ---------------------- | -------------------------------- |
| `workspace:*` | Always latest local    | No version file change           |
| `workspace:^` | Caret range on publish | Updated to `^2.0.0` on publish   |
| `workspace:~` | Tilde range on publish | Updated to `~2.0.0` on publish   |
