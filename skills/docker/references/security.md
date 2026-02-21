---
title: Security
description: Non-root containers, build secrets, image scanning, read-only filesystems, and production hardening patterns
tags:
  [
    security,
    non-root,
    secrets,
    scanning,
    hardening,
    trivy,
    distroless,
    read-only,
  ]
---

# Security

## Non-Root Users

Never run production containers as root. Create a dedicated user in the final stage.

### Alpine (Node.js)

```dockerfile
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/dist ./dist

USER appuser
```

### Debian/Ubuntu (Python)

```dockerfile
RUN useradd --create-home --shell /bin/bash --uid 1001 appuser

COPY --from=builder --chown=appuser:appuser /app .

USER appuser
```

### Pre-Built Non-Root Images

Some images come with non-root users:

```dockerfile
# Nginx unprivileged (runs as nginx user on port 8080)
FROM nginxinc/nginx-unprivileged:alpine
USER nginx

# Distroless (runs as nonroot by default)
FROM gcr.io/distroless/nodejs20-debian12
USER nonroot
```

## Build Secrets

Never bake secrets into image layers. Use build-time secret mounts.

```dockerfile
# Dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm ci --registry=https://npm.pkg.github.com

# Build command
# docker build --secret id=npm_token,src=.npm_token .
```

### Compose Secrets

```yaml
services:
  app:
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    environment: API_KEY
```

Access secrets in the container at `/run/secrets/<name>`:

```ts
import { readFileSync } from 'node:fs';

const dbPassword = readFileSync('/run/secrets/db_password', 'utf8').trim();
```

## Image Scanning

### Trivy

```bash
# Scan an image for vulnerabilities
trivy image myapp:latest

# Fail on HIGH or CRITICAL
trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest

# Scan Dockerfile for misconfigurations
trivy config Dockerfile

# JSON output for CI
trivy image --format json --output results.json myapp:latest
```

### Docker Scout

```bash
# Quick vulnerability overview
docker scout quickview myapp:latest

# Detailed CVE list
docker scout cves myapp:latest

# Compare two images
docker scout compare myapp:latest myapp:previous
```

### CI Integration

```yaml
# GitHub Actions
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

## Read-Only Root Filesystem

Prevent runtime file modification:

```yaml
# compose.yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
```

```bash
# docker run
docker run --read-only --tmpfs /tmp myapp:latest
```

## Security Headers and Network Hardening

### Drop Capabilities

```yaml
services:
  app:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE # only if binding to ports < 1024
    security_opt:
      - no-new-privileges:true
```

### Docker Run Equivalent

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp \
  --user 1001:1001 \
  myapp:latest
```

## Distroless Images

No shell, no package manager, minimal attack surface:

```dockerfile
FROM golang:1.23 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o /server

FROM gcr.io/distroless/static-debian12
COPY --from=builder /server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

```dockerfile
FROM node:24-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
USER nonroot
CMD ["dist/server.js"]
```

## Production Hardening Checklist

| Area            | Check                                              |
| --------------- | -------------------------------------------------- |
| Base image      | Pinned to specific version, not `latest`           |
| Non-root        | `USER` directive in final stage                    |
| Secrets         | No secrets in ENV, layers, or build args           |
| Read-only       | `--read-only` with tmpfs for writable dirs         |
| Capabilities    | `cap_drop: ALL`, only add what's needed            |
| Privileges      | `no-new-privileges: true`                          |
| Health check    | `HEALTHCHECK` in Dockerfile or orchestrator config |
| Scanning        | Trivy or Scout in CI, fail on HIGH/CRITICAL        |
| .dockerignore   | Excludes `.env`, `.git`, `node_modules`            |
| Image size      | Multi-stage build, alpine or distroless base       |
| Init process    | `--init` or tini for signal handling               |
| Logging         | Log to stdout/stderr, collect with orchestrator    |
| Resource limits | Memory and CPU limits set in deployment            |

## Common Docker Security Mistakes

| Mistake                                  | Fix                                               |
| ---------------------------------------- | ------------------------------------------------- |
| `ENV API_KEY=secret` in Dockerfile       | Use runtime secrets or `--mount=type=secret`      |
| Running as root                          | Add `USER` directive with non-root user           |
| Using `latest` tag                       | Pin base image version                            |
| No vulnerability scanning                | Add Trivy/Scout to CI pipeline                    |
| Exposing Docker socket to containers     | Use Docker-in-Docker or rootless Docker if needed |
| `--privileged` flag                      | Use specific `--cap-add` instead                  |
| Storing secrets in environment variables | Use Docker secrets (`/run/secrets/`) or vault     |
| No resource limits                       | Set memory and CPU limits in orchestrator         |
