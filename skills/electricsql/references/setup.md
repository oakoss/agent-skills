---
title: Setup
description: Installation, Postgres configuration, Docker self-hosting, environment variables, health checks, and client connection verification
tags:
  [
    install,
    docker,
    postgres,
    wal_level,
    logical-replication,
    environment-variables,
    health-check,
    docker-compose,
    self-hosted,
    electric-cloud,
  ]
---

## Packages

| Package                | Purpose                               |
| ---------------------- | ------------------------------------- |
| `@electric-sql/client` | Core ShapeStream, Shape, type helpers |
| `@electric-sql/react`  | React hooks (`useShape`)              |

```bash
npm install @electric-sql/client
npm install @electric-sql/react
```

## Postgres Configuration

Electric requires logical replication. These settings must be applied before Electric can connect.

### Enable Logical Replication

```sql
ALTER SYSTEM SET wal_level = 'logical';
```

Restart Postgres after changing `wal_level`. Verify:

```sql
SHOW wal_level;
```

Must return `logical`. If it returns `replica` or `minimal`, the change has not taken effect.

### Create a Publication

Electric uses publications to track which tables to replicate. Create one for all tables or specific tables:

```sql
CREATE PUBLICATION electric_pub FOR ALL TABLES;
```

For specific tables:

```sql
CREATE PUBLICATION electric_pub FOR TABLE items, users, orders;
```

### Grant Replication Role

The database user Electric connects with needs replication privileges:

```sql
ALTER ROLE electric_user WITH REPLICATION;
GRANT ALL ON ALL TABLES IN SCHEMA public TO electric_user;
```

### Full Postgres Setup Script

```sql
ALTER SYSTEM SET wal_level = 'logical';

CREATE ROLE electric_user WITH LOGIN PASSWORD 'electric_pass' REPLICATION;
GRANT ALL ON ALL TABLES IN SCHEMA public TO electric_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO electric_user;

CREATE PUBLICATION electric_pub FOR ALL TABLES;
```

## Docker Self-Hosting

### Single Container

```bash
docker run \
  -e DATABASE_URL="postgresql://electric_user:electric_pass@host.docker.internal:5432/mydb" \
  -e ELECTRIC_SECRET="your-secret-key" \
  -p 3000:3000 \
  electricsql/electric
```

### Docker Compose with Postgres

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: electric_user
      POSTGRES_PASSWORD: electric_pass
    command:
      - -c
      - wal_level=logical
    ports:
      - '5432:5432'
    volumes:
      - pgdata:/var/lib/postgresql/data

  electric:
    image: electricsql/electric
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://electric_user:electric_pass@postgres:5432/mydb
      ELECTRIC_INSECURE: 'true'
    ports:
      - '3000:3000'

volumes:
  pgdata:
```

For development, `ELECTRIC_INSECURE=true` disables auth requirements. Never use this in production.

### Docker Compose for Production

```yaml
services:
  electric:
    image: electricsql/electric
    environment:
      DATABASE_URL: ${DATABASE_URL}
      ELECTRIC_SECRET: ${ELECTRIC_SECRET}
      ELECTRIC_DB_POOL_SIZE: '20'
      ELECTRIC_PORT: '3000'
    ports:
      - '3000:3000'
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/v1/health']
      interval: 10s
      timeout: 5s
      retries: 3
```

## Environment Variables

| Variable                 | Required | Default  | Description                              |
| ------------------------ | -------- | -------- | ---------------------------------------- |
| `DATABASE_URL`           | Yes      | --       | Postgres connection string               |
| `ELECTRIC_SECRET`        | Prod     | --       | Secret key for production auth           |
| `ELECTRIC_INSECURE`      | No       | `false`  | Skip auth checks (dev only)              |
| `ELECTRIC_PORT`          | No       | `3000`   | HTTP port Electric listens on            |
| `ELECTRIC_DB_POOL_SIZE`  | No       | `20`     | Postgres connection pool size            |
| `ELECTRIC_CACHE_MAX_AGE` | No       | `5`      | Shape cache max age in seconds           |
| `ELECTRIC_STORAGE`       | No       | `memory` | Storage backend (`memory` or file-based) |

## Health Checks

Electric exposes a health endpoint for readiness and liveness probes:

```bash
curl http://localhost:3000/v1/health
```

Returns `200 OK` when Electric is connected to Postgres and ready to serve shapes.

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /v1/health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /v1/health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Cloud vs Self-Hosted

| Factor         | Electric Cloud               | Self-Hosted                          |
| -------------- | ---------------------------- | ------------------------------------ |
| Setup effort   | Minimal; managed service     | You manage Docker, networking, TLS   |
| Scaling        | Automatic                    | Manual horizontal scaling            |
| Cost           | Usage-based pricing          | Infrastructure cost only             |
| Data residency | Provider regions             | Full control                         |
| Best for       | Prototyping, small-mid teams | Compliance, enterprise, custom infra |

## Client Installation and Verification

### Basic ShapeStream Connection

```ts
import { ShapeStream } from '@electric-sql/client';

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
  },
});

stream.subscribe((messages) => {
  for (const msg of messages) {
    if ('key' in msg) {
      console.log('Row:', msg.key, msg.value);
    }
    if ('headers' in msg && msg.headers.control === 'up-to-date') {
      console.log('Initial sync complete');
    }
  }
});
```

### Verify Connection Works

```ts
import { Shape, ShapeStream } from '@electric-sql/client';

const stream = new ShapeStream({
  url: 'http://localhost:3000/v1/shape',
  params: {
    table: 'items',
  },
});

const shape = new Shape(stream);

shape.subscribe((data) => {
  console.log(`Synced ${data.size} rows from items table`);
});
```

### React Setup

```tsx
import { useShape } from '@electric-sql/react';

function ItemList() {
  const { data, isLoading, isError, error } = useShape<{
    id: string;
    title: string;
  }>({
    url: 'http://localhost:3000/v1/shape',
    params: {
      table: 'items',
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error?.message}</div>;

  return (
    <ul>
      {data.map((item) => (
        <li key={item.id}>{item.title}</li>
      ))}
    </ul>
  );
}
```

## Troubleshooting Checklist

| Symptom                 | Cause                                 | Fix                                               |
| ----------------------- | ------------------------------------- | ------------------------------------------------- |
| Electric fails to start | `wal_level` not set to `logical`      | `ALTER SYSTEM SET wal_level = 'logical'`, restart |
| No data syncing         | No publication created                | `CREATE PUBLICATION electric_pub FOR ALL TABLES`  |
| Connection refused      | Postgres not reachable from Electric  | Check `DATABASE_URL` host and Docker networking   |
| 401 on shape requests   | `ELECTRIC_SECRET` mismatch or not set | Set matching secret or use `ELECTRIC_INSECURE`    |
| Shapes return empty     | Table not in publication              | Add table to publication or use `FOR ALL TABLES`  |
