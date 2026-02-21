---
title: Container Builds
description: Multi-stage Dockerfiles, Docker layer caching in CI, buildx multi-platform builds, image scanning, registry push, and size optimization
tags:
  [
    docker,
    dockerfile,
    buildx,
    multi-stage,
    trivy,
    snyk,
    ghcr,
    ecr,
    layer-caching,
    distroless,
  ]
---

# Container Builds

## Multi-Stage Dockerfile

Separate build tooling from the runtime image to keep the final image small and free of dev dependencies.

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ['node', 'dist/index.js']
```

### Distroless Runtime (Minimal Attack Surface)

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM gcr.io/distroless/nodejs22-debian12 AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ['dist/index.js']
```

### Alpine vs Distroless

| Image base          | Size   | Shell | Package manager | Use case                   |
| ------------------- | ------ | ----- | --------------- | -------------------------- |
| `node:22-alpine`    | ~50 MB | ash   | apk             | Needs runtime shell tools  |
| `distroless/nodejs` | ~30 MB | none  | none            | Hardened production        |
| `scratch`           | 0 MB   | none  | none            | Statically linked binaries |

## .dockerignore

Always add a `.dockerignore` to exclude build artifacts and sensitive files.

```text
node_modules
.git
.env*
dist
coverage
*.log
.DS_Store
```

## Docker Layer Caching in CI

### Cache with --cache-from (BuildKit)

```yaml
- name: Build image
  run: |
    docker build \
      --cache-from ghcr.io/${{ github.repository }}:cache \
      --build-arg BUILDKIT_INLINE_CACHE=1 \
      -t ghcr.io/${{ github.repository }}:${{ github.sha }} \
      .
```

### Cache with GitHub Actions cache backend (buildx)

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

`type=gha` uses GitHub Actions cache storage — no registry needed and automatically evicted per cache policy.

### Registry cache backend (persistent across runners)

```yaml
- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
    cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
```

## buildx Multi-Platform Builds

Build a single image manifest supporting both `linux/amd64` (x86 servers) and `linux/arm64` (Graviton, Apple Silicon).

```yaml
name: Build multi-platform image

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

QEMU is needed for cross-compilation on the `ubuntu-latest` runner. Native arm64 runners skip QEMU but cost more.

## Image Scanning

Scan images for CVEs before pushing to production registries.

### Trivy (free, runs in CI)

```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
    format: table
    exit-code: '1'
    severity: CRITICAL,HIGH
    ignore-unfixed: true
```

`exit-code: '1'` fails the pipeline on critical/high CVEs. `ignore-unfixed: true` skips vulnerabilities with no available fix.

### Trivy filesystem scan (scan before build)

```yaml
- name: Scan filesystem
  uses: aquasecurity/trivy-action@0.28.0
  with:
    scan-type: fs
    scan-ref: .
    format: sarif
    output: trivy-results.sarif

- name: Upload to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

### Snyk container scan

```yaml
- name: Scan image with Snyk
  uses: snyk/actions/docker@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    image: ghcr.io/${{ github.repository }}:${{ github.sha }}
    args: --severity-threshold=high
```

## Pushing to Registries

### GitHub Container Registry (GHCR)

```yaml
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.sha }}
```

`GITHUB_TOKEN` is sufficient — no separate secret needed for GHCR when pushing from the same repository.

### Amazon ECR (with OIDC)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v5
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/github-actions-ecr
          aws-region: us-east-1

      - name: Log in to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

### Docker Hub

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ vars.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

Use an access token (not password). Store username as a variable (`vars.`), token as a secret.

## Image Tagging Strategy

```yaml
- name: Extract metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=sha,prefix=sha-
      type=ref,event=branch
      type=semver,pattern={{version}}
      type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
```

`docker/metadata-action` generates consistent tags from git context. Pass `steps.meta.outputs.tags` to `docker/build-push-action`.

## Full Pipeline: Build → Test → Scan → Push

```yaml
name: Container CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write
  security-events: write

jobs:
  build-scan-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image (no push)
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run unit tests inside container
        run: docker run --rm app:${{ github.sha }} pnpm test

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: app:${{ github.sha }}
          exit-code: '1'
          severity: CRITICAL,HIGH
          ignore-unfixed: true

      - name: Log in to GHCR
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
```

Push only on `main` merges. PRs build and scan without pushing.

## Size Optimization Checklist

| Technique                     | Impact                                      |
| ----------------------------- | ------------------------------------------- |
| Multi-stage build             | Strips build tools from runtime image       |
| `.dockerignore`               | Excludes `node_modules`, `.git`, logs       |
| Copy only production deps     | `pnpm install --prod` in runtime stage      |
| Use Alpine or distroless base | 50-200 MB smaller than full Debian          |
| Combine `RUN` commands        | Fewer layers, smaller image                 |
| Remove package manager cache  | `apk add --no-cache` or `rm -rf /var/cache` |

```dockerfile
RUN apk add --no-cache curl \
  && addgroup -S appgroup \
  && adduser -S appuser -G appgroup

USER appuser
```

Run as a non-root user — required for CIS benchmarks and most production security policies.
