---
title: Monorepo Builds
description: Docker builds for Turborepo and pnpm workspace monorepos with turbo prune, selective builds, and layer caching optimization
tags: [monorepo, turborepo, turbo-prune, pnpm, workspace, selective-build]
---

# Monorepo Builds

## The Problem

In a monorepo, the lockfile is shared across all workspaces. Any dependency change — even in an unrelated package — invalidates Docker's layer cache for every service, causing full rebuilds.

## turbo prune

Turborepo's `prune` command extracts a minimal subset of the monorepo containing only the target workspace and its dependencies.

```bash
# Generate pruned output for the "api" workspace
turbo prune api --docker
```

### Output Structure

```text
out/
├── json/             # package.json files only (for dependency install)
│   ├── package.json
│   └── packages/
│       └── shared/
│           └── package.json
├── full/             # Full source code
│   ├── apps/
│   │   └── api/
│   └── packages/
│       └── shared/
└── pnpm-lock.yaml    # Pruned lockfile (only relevant dependencies)
```

The `--docker` flag splits output into `json/` and `full/` directories, enabling Docker to cache dependency installation separately from source code changes.

## Turborepo + pnpm Dockerfile

Three-stage build: prune, install + build, runtime.

```dockerfile
FROM node:24-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

# Stage 1: Prune the monorepo
FROM base AS pruner
RUN pnpm add -g turbo
COPY . .
RUN turbo prune api --docker

# Stage 2: Install dependencies and build
FROM base AS builder

# Copy pruned package.json files and lockfile (cached layer)
COPY --from=pruner /app/out/json/ .
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Copy full source and build
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo build --filter=api

# Stage 3: Production runtime
FROM node:24-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/apps/api/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/apps/api/package.json ./

ENV NODE_ENV=production
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Why Three Stages

1. **Pruner** — Runs `turbo prune` on the full repo, outputs minimal subset
2. **Builder** — Installs only pruned dependencies (cached when lockfile unchanged), then builds
3. **Runner** — Copies only production artifacts, no build tools

## Turborepo + npm Dockerfile

```dockerfile
FROM node:24-alpine AS base
WORKDIR /app

FROM base AS pruner
RUN npm install -g turbo
COPY . .
RUN turbo prune web --docker

FROM base AS builder
COPY --from=pruner /app/out/json/ .
RUN --mount=type=cache,target=/root/.npm npm ci
COPY --from=pruner /app/out/full/ .
RUN npx turbo build --filter=web

FROM base AS runner
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/apps/web/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=appuser:appgroup /app/apps/web/public ./apps/web/public

USER appuser
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
```

## Remote Caching in Docker

Pass Turborepo remote cache credentials as build arguments:

```dockerfile
FROM base AS builder
ARG TURBO_TOKEN
ARG TURBO_TEAM

COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile

COPY --from=pruner /app/out/full/ .
RUN TURBO_TOKEN=$TURBO_TOKEN TURBO_TEAM=$TURBO_TEAM \
    pnpm turbo build --filter=api
```

```bash
docker build \
  --build-arg TURBO_TOKEN="$TURBO_TOKEN" \
  --build-arg TURBO_TEAM="$TURBO_TEAM" \
  -f apps/api/Dockerfile \
  .
```

Pass credentials as `ARG` (not `ENV`) so they don't persist in the final image.

## pnpm Workspaces Without Turbo

For pnpm workspaces without Turborepo, use `pnpm deploy` to extract a single workspace:

```dockerfile
FROM node:24-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

FROM base AS builder
COPY . .
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
RUN pnpm --filter api build
RUN pnpm deploy --filter api --prod /app/deployed

FROM node:24-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/deployed ./

ENV NODE_ENV=production
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

`pnpm deploy` copies the workspace with only production dependencies, flattened into a standalone directory.

## .dockerignore for Monorepos

```text
**/node_modules
**/.turbo
**/.next
**/dist
**/coverage
.git
.env
.env.*
*.md
```

## CI: Build Matrix for Monorepo Services

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, web, worker]
    steps:
      - uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          file: apps/${{ matrix.service }}/Dockerfile
          context: .
          push: true
          tags: ghcr.io/myorg/${{ matrix.service }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.service }}
          cache-to: type=gha,scope=${{ matrix.service }},mode=max
```

Context is the monorepo root (`.`) so `turbo prune` has access to all workspaces.

## Common Monorepo Mistakes

| Mistake                                | Correct Pattern                                         |
| -------------------------------------- | ------------------------------------------------------- |
| Using workspace root as Docker context | Use `turbo prune --docker` for minimal context          |
| Copying full repo into every service   | Prune to only the target workspace and its dependencies |
| `ENV TURBO_TOKEN` in Dockerfile        | Use `ARG` so credentials don't persist in image layers  |
| Separate lockfiles per workspace       | Use the pruned monorepo lockfile from `turbo prune`     |
| Not using `--frozen-lockfile`          | Always use it for deterministic CI builds               |
| Cache scope collision in CI matrix     | Use `scope=${{ matrix.service }}` per service           |
