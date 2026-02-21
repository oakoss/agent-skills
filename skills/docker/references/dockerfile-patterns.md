---
title: Dockerfile Patterns
description: Multi-stage builds, layer caching, base image selection, build cache mounts, and image optimization techniques
tags:
  [
    dockerfile,
    multi-stage,
    layer-caching,
    alpine,
    build-cache,
    dockerignore,
    optimization,
  ]
---

# Dockerfile Patterns

## Multi-Stage Builds

Separate build-time dependencies from the runtime image. Only copy artifacts needed for production.

### Node.js Application

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS production
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

ENV NODE_ENV=production
USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/server.js"]
```

### Static Site with Nginx

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine AS production

COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

USER nginx
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Python Application

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim AS production
WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appuser /app .

ENV PATH="/home/appuser/.local/bin:$PATH"
USER appuser
EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

## Layer Caching Strategy

Docker caches each layer. When a layer changes, all subsequent layers rebuild. Order instructions from least to most frequently changed.

```dockerfile
# 1. Base image (rarely changes)
FROM node:20-alpine
WORKDIR /app

# 2. Dependencies (changes when lockfile changes)
COPY package.json package-lock.json ./
RUN npm ci

# 3. Source code (changes frequently)
COPY . .
RUN npm run build
```

### Build Cache Mounts

Persist package manager caches across builds without baking them into layers:

```dockerfile
# npm
RUN --mount=type=cache,target=/root/.npm npm ci

# pnpm
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Go modules
RUN --mount=type=cache,target=/go/pkg/mod \
    go build -o /app ./cmd/server
```

## Base Image Selection

| Base Image           | Size    | Use Case                              |
| -------------------- | ------- | ------------------------------------- |
| `alpine`             | ~5 MB   | Minimal containers, CLI tools         |
| `node:20-alpine`     | ~130 MB | Node.js apps, smallest Node base      |
| `node:20-slim`       | ~200 MB | Node.js when alpine has musl issues   |
| `python:3.12-slim`   | ~150 MB | Python apps, smaller than full image  |
| `golang:1.23`        | ~800 MB | Go builds (use scratch for runtime)   |
| `scratch`            | 0 MB    | Static binaries (Go, Rust)            |
| `distroless`         | ~20 MB  | Minimal runtime, no shell             |
| `nginx-unprivileged` | ~40 MB  | Static file serving, non-root default |

### Pin Base Image Versions

```dockerfile
# Pin to major.minor for stability
FROM node:20-alpine

# Pin to digest for maximum reproducibility
FROM node:20-alpine@sha256:abc123...

# Use ARG for flexible version control
ARG NODE_VERSION=20-alpine
FROM node:${NODE_VERSION}
```

## .dockerignore

Exclude files from the build context to speed up builds and avoid leaking secrets:

```text
node_modules
.git
.gitignore
.env
.env.*
*.md
dist
coverage
.nyc_output
.cache
.DS_Store
Dockerfile
docker-compose*.yml
.dockerignore
```

## Health Checks

```dockerfile
# HTTP endpoint check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Node.js without curl dependency
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# TCP port check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD nc -z localhost 5432 || exit 1
```

| Parameter        | Default | Guidance                                       |
| ---------------- | ------- | ---------------------------------------------- |
| `--interval`     | 30s     | Time between checks                            |
| `--timeout`      | 30s     | Max time for a single check (use 3-5s)         |
| `--start-period` | 0s      | Grace period for container startup (use 5-30s) |
| `--retries`      | 3       | Consecutive failures before unhealthy          |

## Init Process

Containers need an init process for proper signal handling and zombie process reaping:

```dockerfile
# Option 1: Docker --init flag (adds tini automatically)
# docker run --init myimage

# Option 2: Install tini explicitly
RUN apk add --no-cache tini
ENTRYPOINT ["tini", "--"]
CMD ["node", "dist/server.js"]
```

## ENTRYPOINT vs CMD

```dockerfile
# ENTRYPOINT: the executable (hard to override)
# CMD: default arguments (easy to override)

# Fixed executable, overridable args
ENTRYPOINT ["node"]
CMD ["dist/server.js"]
# docker run myimage dist/worker.js  -> node dist/worker.js

# Most common: CMD only (easy to override everything)
CMD ["node", "dist/server.js"]
# docker run myimage sh  -> sh

# Always use exec form (JSON array), not shell form
CMD ["node", "server.js"]     # exec form (PID 1, receives signals)
# CMD node server.js          # shell form (wrapped in /bin/sh, misses signals)
```

## Go: Scratch Runtime

Go produces static binaries that need no OS:

```dockerfile
FROM golang:1.23 AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /server ./cmd/server

FROM scratch
COPY --from=builder /server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

EXPOSE 8080
ENTRYPOINT ["/server"]
```
