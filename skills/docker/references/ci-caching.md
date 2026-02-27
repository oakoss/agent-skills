---
title: CI Caching
description: Docker layer caching in GitHub Actions, registry cache backends, automated builds, image tagging strategies, and multi-registry push
tags: [ci, github-actions, cache, registry, buildx, tagging, ghcr, docker-hub]
---

# CI Caching

## GitHub Actions Cache Backend

The fastest CI caching option. Uses GitHub's native cache service.

```yaml
name: Build and Push

on:
  push:
    branches: [main]
  pull_request:

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Cache Modes

| Mode  | Behavior                                        | Size    |
| ----- | ----------------------------------------------- | ------- |
| `min` | Only cache final stage layers                   | Smaller |
| `max` | Cache all intermediate stages (better hit rate) | Larger  |

Use `mode=max` unless you're hitting the 10 GB GitHub cache limit.

## Registry Cache Backend

Store cache in a dedicated registry tag. Works with any CI provider.

```yaml
- name: Build and push
  uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/myorg/myapp:latest
    cache-from: type=registry,ref=ghcr.io/myorg/myapp:buildcache
    cache-to: type=registry,ref=ghcr.io/myorg/myapp:buildcache,mode=max
```

## Image Tagging Strategy

Use Docker Metadata Action for automated, semantic tags:

```yaml
- name: Docker meta
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    push: ${{ github.event_name != 'pull_request' }}
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

This produces tags like:

| Event             | Tags Generated                |
| ----------------- | ----------------------------- |
| Push to `main`    | `main`, `sha-abc1234`         |
| Push tag `v1.2.3` | `1.2.3`, `1.2`, `sha-abc1234` |
| Pull request #42  | `pr-42`                       |

## Multi-Platform CI Build

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Multi-Registry Push

Push to both Docker Hub and GHCR in one build:

```yaml
steps:
  - name: Login to Docker Hub
    uses: docker/login-action@v3
    with:
      username: ${{ vars.DOCKERHUB_USERNAME }}
      password: ${{ secrets.DOCKERHUB_TOKEN }}

  - name: Login to GHCR
    uses: docker/login-action@v3
    with:
      registry: ghcr.io
      username: ${{ github.repository_owner }}
      password: ${{ secrets.GITHUB_TOKEN }}

  - name: Build and push
    uses: docker/build-push-action@v6
    with:
      push: true
      tags: |
        myorg/myapp:latest
        ghcr.io/myorg/myapp:latest
```

## Build Matrix for Multiple Services

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, web, worker]
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: ./apps/${{ matrix.service }}
          push: true
          tags: ghcr.io/myorg/${{ matrix.service }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.service }}
          cache-to: type=gha,scope=${{ matrix.service }},mode=max
```

Use `scope` to separate cache entries per service — otherwise they overwrite each other.

## Vulnerability Scanning in CI

```yaml
- name: Build image
  uses: docker/build-push-action@v6
  with:
    load: true
    tags: myapp:scan

- name: Scan for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:scan
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1

- name: Upload scan results
  if: always()
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

## Cache Troubleshooting

| Problem                      | Cause                                | Fix                                      |
| ---------------------------- | ------------------------------------ | ---------------------------------------- |
| Cache never hits             | Different builder instance           | Ensure `setup-buildx-action` runs first  |
| Cache too large              | Using `mode=max` with many stages    | Switch to `mode=min` or registry backend |
| PR builds have no cache      | GHA cache scoped to branch           | PRs can read from base branch cache      |
| Multi-service cache conflict | Same scope for different Dockerfiles | Use `scope=<service-name>` per service   |
