---
title: Build Packs
description: Nixpacks auto-detection, Dockerfile builds, Docker Compose conventions, Traefik labels, and build configuration in Coolify
tags: [nixpacks, dockerfile, docker-compose, build-pack, traefik, labels]
---

# Build Packs

## Build Pack Comparison

| Build Pack     | Config Required | Control Level | Best For                             |
| -------------- | --------------- | ------------- | ------------------------------------ |
| Nixpacks       | None            | Low           | Quick deploys, standard stacks       |
| Dockerfile     | Dockerfile      | High          | Custom builds, specific dependencies |
| Docker Compose | compose.yaml    | Highest       | Multi-service stacks, databases      |

Set the build pack via API:

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"build_pack": "nixpacks"}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

Valid values: `nixpacks`, `dockerfile`, `dockercompose`

## Nixpacks

Nixpacks auto-detects the language and framework from source code, generates a Dockerfile, builds, and deploys — zero configuration needed.

### Supported Languages

Node.js, Python, Go, Rust, Ruby, PHP, Java, .NET, Elixir, Haskell, Clojure, Scala, Swift, Dart, Crystal, Zig, and more.

### Customization with nixpacks.toml

Place `nixpacks.toml` in the repository root to override auto-detection:

```toml
# Custom build phases
[phases.setup]
nixPkgs = ["nodejs_20", "pnpm"]

[phases.install]
cmds = ["pnpm install --frozen-lockfile"]

[phases.build]
cmds = ["pnpm build"]

# Environment variables baked into the image
[variables]
NODE_ENV = "production"

# Start command
[start]
cmd = "pnpm start"
```

### Common Nixpacks Overrides

```toml
# Pin Node.js version
[phases.setup]
nixPkgs = ["nodejs_24"]

# Add system dependencies (e.g., for sharp/canvas)
[phases.setup]
nixPkgs = ["nodejs_24", "vips", "pkg-config"]
aptPkgs = ["libvips-dev"]

# Custom install + build
[phases.install]
cmds = ["npm ci"]

[phases.build]
cmds = ["npm run build"]

# Cache directories between builds
[phases.install]
cacheDirectories = ["/root/.npm"]
```

### Nixpacks Environment Variables

Override behavior without `nixpacks.toml` by setting environment variables in Coolify:

| Variable                | Effect                   |
| ----------------------- | ------------------------ |
| `NIXPACKS_NODE_VERSION` | Pin Node.js version      |
| `NIXPACKS_BUILD_CMD`    | Override build command   |
| `NIXPACKS_START_CMD`    | Override start command   |
| `NIXPACKS_INSTALL_CMD`  | Override install command |
| `NIXPACKS_PKGS`         | Additional Nix packages  |
| `NIXPACKS_APT_PKGS`     | Additional apt packages  |

## Dockerfile

Full control over the build. Set `build_pack` to `dockerfile` and Coolify reads the Dockerfile from the repository.

### API Configuration

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "build_pack": "dockerfile",
    "dockerfile_location": "/Dockerfile",
    "build_command": null,
    "start_command": null
  }' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

### Build Arguments

Coolify can inject build arguments during the build process. Configure them in the application's Advanced menu. The `SOURCE_COMMIT` variable (Git commit hash) is available but disabled by default to preserve Docker cache.

## Docker Compose

The `docker-compose.yaml` file is the single source of truth. Coolify reads it and manages the stack.

### Coolify-Specific Labels

Coolify auto-applies these labels to managed containers:

```yaml
labels:
  coolify.managed: 'true'
  coolify.applicationId: '<app-id>'
  coolify.type: 'application'
```

### Traefik Integration

Make services internet-accessible with Traefik labels:

```yaml
services:
  app:
    build: .
    labels:
      - 'traefik.enable=true'
      - 'traefik.http.routers.app.rule=Host(`app.example.com`)'
      - 'traefik.http.routers.app.entrypoints=https'
      - 'traefik.http.routers.app.tls=true'
      - 'traefik.http.routers.app.tls.certresolver=letsencrypt'
      - 'traefik.http.services.app.loadbalancer.server.port=3000'

  worker:
    build: .
    command: node worker.js
    labels:
      - 'coolify.managed=true'
      # No traefik labels = not exposed to internet
```

### Health Check Exclusion

Exclude non-HTTP services from Coolify's health monitoring:

```yaml
services:
  migrations:
    build: .
    command: pnpm db:migrate
    labels:
      - 'exclude_from_hc=true'

  worker:
    build: .
    command: node worker.js
    labels:
      - 'exclude_from_hc=true'
```

### Networking

Each Compose stack deploys to an isolated network named after the resource UUID. Services within the same stack communicate by service name:

```yaml
services:
  app:
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/myapp
      REDIS_URL: redis://redis:6379

  db:
    image: postgres:16-alpine

  redis:
    image: redis:7-alpine
```

### Cross-Stack Communication

Enable the "Connect to Predefined Network" option to allow services in different stacks to communicate. Reference services using their full name: `<service>-<uuid>`.

### Storage with Compose

Coolify extends Docker Compose with custom storage fields:

```yaml
services:
  app:
    volumes:
      - data:/app/data

volumes:
  data:
    # Coolify extension: create empty directory
    # is_directory: true

    # Coolify extension: create file with content
    # content: |
    #   key=value
    #   another_key=${ENV_VAR}
```

## Domain and SSL Configuration

### Via API

```bash
# Set domain (Traefik handles SSL automatically)
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"domains": "https://app.example.com"}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"

# Force HTTPS redirect
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"is_force_https_enabled": true}' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

### Wildcard Domains

Configure a wildcard domain on the server level for automatic subdomain routing. Set in Coolify dashboard under Server > Settings > Wildcard Domain.

## Troubleshooting

| Problem                        | Cause                             | Fix                                               |
| ------------------------------ | --------------------------------- | ------------------------------------------------- |
| Build fails with Nixpacks      | Missing system dependency         | Add to `nixpacks.toml` or switch to Dockerfile    |
| "No Available Server" error    | Container health check failing    | Fix health check or add `exclude_from_hc` label   |
| Compose services can't connect | Wrong hostname                    | Use service name, not `localhost`                 |
| SSL not working                | Domain DNS not pointing to server | Update DNS A record to server IP                  |
| Old version deployed           | Docker cache or wrong commit SHA  | Set `SOURCE_COMMIT` or use `force=true` on deploy |
| Build arguments not available  | Not configured in Advanced menu   | Add build args in application Advanced settings   |
