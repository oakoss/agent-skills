---
title: Compose
description: Docker Compose service definitions, networking, volumes, environment management, overrides, and development workflows
tags:
  [
    compose,
    networking,
    volumes,
    environment,
    override,
    watch,
    depends-on,
    profiles,
  ]
---

# Compose

## Service Definitions

```yaml
# compose.yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - '3000:3000'
    environment:
      NODE_ENV: production
      DATABASE_URL: postgres://user:pass@db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/health']
      interval: 30s
      timeout: 3s
      start_period: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U user -d myapp']
      interval: 10s
      timeout: 3s
      retries: 5
    ports:
      - '5432:5432'

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    ports:
      - '6379:6379'

volumes:
  db-data:
  redis-data:
```

## Compose Overrides

Use override files for environment-specific config without duplicating the base:

```yaml
# compose.override.yaml (auto-loaded in dev)
services:
  app:
    build:
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      NODE_ENV: development
      DEBUG: 'app:*'
    command: npm run dev
```

```yaml
# compose.prod.yaml (explicit: docker compose -f compose.yaml -f compose.prod.yaml up)
services:
  app:
    ports:
      - '80:3000'
    environment:
      NODE_ENV: production
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Networking

Compose creates a default bridge network. Services resolve each other by service name.

```yaml
services:
  app:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend

  nginx:
    networks:
      - frontend

networks:
  frontend:
  backend:
```

### DNS Resolution

Within the same network, services resolve by name:

```ts
// In the app service, connect to db by service name
const pool = new Pool({
  host: 'db', // resolved by Docker DNS
  port: 5432,
  database: 'myapp',
});
```

### External Networks

Connect to networks created outside Compose:

```yaml
networks:
  shared:
    external: true
    name: my-shared-network
```

## Volumes

### Named Volumes (Persistent Data)

```yaml
volumes:
  db-data:
    driver: local

services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data
```

### Bind Mounts (Development)

```yaml
services:
  app:
    volumes:
      - .:/app # sync source code
      - /app/node_modules # anonymous volume to preserve container's node_modules
```

### tmpfs (Ephemeral, In-Memory)

```yaml
services:
  app:
    tmpfs:
      - /tmp
      - /app/.cache
```

## Environment Variables

### Precedence (Highest to Lowest)

1. `docker compose run -e VAR=value`
2. `environment:` in Compose file
3. `--env-file` flag
4. `env_file:` in Compose file
5. `.env` file in project directory
6. Host environment variables

### Patterns

```yaml
services:
  app:
    # Inline values
    environment:
      NODE_ENV: production
      API_KEY: ${API_KEY} # interpolated from host or .env

    # External file
    env_file:
      - .env
      - .env.local
```

```text
# .env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=secret
POSTGRES_DB=myapp
```

## Compose Watch (Dev Hot Reload)

File watching without bind mounts — syncs files or triggers rebuild:

```yaml
services:
  app:
    build:
      context: .
    develop:
      watch:
        # Sync source changes (hot reload)
        - action: sync
          path: ./src
          target: /app/src

        # Rebuild on dependency changes
        - action: rebuild
          path: package.json

        # Restart on config changes
        - action: sync+restart
          path: ./config
          target: /app/config
```

```bash
docker compose watch
```

## depends_on with Health Checks

Control startup order with health check conditions:

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy # wait for healthy
      redis:
        condition: service_started # just wait for start
      migrations:
        condition: service_completed_successfully # wait for exit 0
```

## Profiles

Group services for selective startup:

```yaml
services:
  app:
    # no profile = always starts

  db:
    # no profile = always starts

  adminer:
    image: adminer
    profiles:
      - debug
    ports:
      - '8080:8080'

  mailhog:
    image: mailhog/mailhog
    profiles:
      - debug
    ports:
      - '8025:8025'
```

```bash
# Start default services only
docker compose up

# Start with debug tools
docker compose --profile debug up
```

## Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## Common Commands

```bash
# Start services (detached)
docker compose up -d

# Rebuild and start
docker compose up -d --build

# View logs
docker compose logs -f app

# Execute command in running container
docker compose exec app sh

# Stop and remove containers + networks
docker compose down

# Stop and remove containers + networks + volumes
docker compose down -v

# Pull latest images
docker compose pull
```
