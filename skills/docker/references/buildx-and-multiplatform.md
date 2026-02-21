---
title: Buildx and Multi-Platform
description: Multi-platform image builds with Docker Buildx, QEMU emulation, cross-compilation, and manifest lists for ARM and x86
tags: [buildx, multi-platform, arm64, amd64, qemu, cross-compile, manifest]
---

# Buildx and Multi-Platform

## Why Multi-Platform

ARM is everywhere: Apple Silicon (M1-M4), AWS Graviton, Azure Ampere, Fly.io, Raspberry Pi. Building for both `linux/amd64` and `linux/arm64` ensures images run natively on any target without emulation overhead.

## Setup

```bash
# Create a new builder with multi-platform support
docker buildx create --name multiplatform --use --bootstrap

# Verify available platforms
docker buildx inspect --bootstrap
# Platforms: linux/amd64, linux/arm64, linux/arm/v7, ...
```

## Basic Multi-Platform Build

```bash
# Build and push for both platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t myregistry/myapp:latest \
  .
```

Docker creates a manifest list — a single tag pointing to platform-specific images. `docker pull` automatically selects the right one.

## Cross-Compilation (Fastest)

For compiled languages, cross-compile in the build stage instead of emulating. This is significantly faster than QEMU.

### Go

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS builder
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} \
    go build -o /server ./cmd/server

FROM scratch
COPY --from=builder /server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/server"]
```

### Rust

```dockerfile
FROM --platform=$BUILDPLATFORM rust:1.80-alpine AS builder
ARG TARGETPLATFORM

RUN apk add --no-cache musl-dev
RUN case "$TARGETPLATFORM" in \
      "linux/amd64") echo "x86_64-unknown-linux-musl" > /target ;; \
      "linux/arm64") echo "aarch64-unknown-linux-musl" > /target ;; \
    esac && \
    rustup target add $(cat /target)

WORKDIR /app
COPY . .
RUN cargo build --release --target $(cat /target)

FROM scratch
COPY --from=builder /app/target/*/release/myapp /myapp
ENTRYPOINT ["/myapp"]
```

## QEMU Emulation (Simpler, Slower)

For interpreted languages (Node.js, Python), QEMU emulates the target architecture. No Dockerfile changes needed.

```bash
# Install QEMU user-static binaries (one-time setup)
docker run --privileged --rm tonistiigi/binfmt --install all

# Build with emulation
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry/myapp:latest \
  --push .
```

## Build Arguments

Docker injects these ARGs automatically in multi-platform builds:

| ARG              | Example       | Description                      |
| ---------------- | ------------- | -------------------------------- |
| `BUILDPLATFORM`  | `linux/amd64` | Platform of the build host       |
| `TARGETPLATFORM` | `linux/arm64` | Target platform being built      |
| `TARGETOS`       | `linux`       | OS component of target           |
| `TARGETARCH`     | `arm64`       | Architecture component of target |
| `TARGETVARIANT`  | `v7`          | ARM variant (v6, v7, v8)         |
| `BUILDOS`        | `linux`       | OS component of build host       |
| `BUILDARCH`      | `amd64`       | Architecture of build host       |

Use `--platform=$BUILDPLATFORM` on the builder stage to run natively:

```dockerfile
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder
# Runs natively on host, not emulated
```

## Local Testing

```bash
# Build for a specific platform locally (no push)
docker buildx build \
  --platform linux/arm64 \
  --load \
  -t myapp:arm64-test \
  .

# Note: --load only works with a single platform
# For multi-platform, use --push to a registry
```

## Platform-Specific Dependencies

```dockerfile
FROM node:20-alpine AS builder
ARG TARGETARCH

RUN if [ "$TARGETARCH" = "arm64" ]; then \
      apk add --no-cache python3 make g++; \
    fi

COPY package.json package-lock.json ./
RUN npm ci
```

## Performance Comparison

| Method            | Speed        | Dockerfile Changes | Best For              |
| ----------------- | ------------ | ------------------ | --------------------- |
| Cross-compilation | Fast         | Yes (ARGs)         | Go, Rust, C/C++       |
| QEMU emulation    | 3-10x slower | None               | Node.js, Python, Ruby |
| Native runners    | Fast         | None               | CI with ARM runners   |

## CI with Multi-Platform

See [CI caching reference](ci-caching.md) for GitHub Actions workflows with multi-platform builds.
