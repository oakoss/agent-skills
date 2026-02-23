---
title: Multi-Tenant Architecture
description: Per-tenant database isolation, platform API for provisioning, token management, and multi-database patterns
tags:
  [
    multi-tenant,
    platform-api,
    provisioning,
    per-tenant,
    database-per-tenant,
    token,
  ]
---

# Multi-Tenant Architecture

Turso supports a database-per-tenant model where each tenant gets an isolated SQLite database. The platform API enables programmatic provisioning.

## Architecture Overview

```text
Platform API
  └── Organization
        └── Group (location/region)
              ├── tenant-abc.db
              ├── tenant-def.db
              └── tenant-ghi.db
```

Groups define where databases are hosted. All databases in a group share the same locations. Each tenant database is fully isolated with independent schema, data, and access tokens.

## Platform API

### Create a Database

```bash
curl -L -X POST 'https://api.turso.tech/v1/organizations/{org}/databases' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{ "name": "tenant-abc", "group": "default" }'
```

### TypeScript Provisioning

```ts
const TURSO_API_TOKEN = process.env.TURSO_API_TOKEN!;
const TURSO_ORG = process.env.TURSO_ORG!;

async function createTenantDatabase(tenantId: string) {
  const response = await fetch(
    `https://api.turso.tech/v1/organizations/${TURSO_ORG}/databases`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${TURSO_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: `tenant-${tenantId}`,
        group: 'default',
      }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to create database: ${response.statusText}`);
  }

  return response.json();
}
```

### Create Auth Token for a Database

```bash
turso db tokens create tenant-abc
turso db tokens create tenant-abc --read-only
turso db tokens create tenant-abc --expiration 7d
```

### Token Generation via API

```ts
async function createDatabaseToken(
  dbName: string,
  options?: { readOnly?: boolean; expiration?: string },
) {
  const params = new URLSearchParams();
  if (options?.expiration) params.set('expiration', options.expiration);

  const response = await fetch(
    `https://api.turso.tech/v1/organizations/${TURSO_ORG}/databases/${dbName}/auth/tokens?${params}`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${TURSO_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        permissions: {
          read_attach: options?.readOnly ? { databases: ['*'] } : undefined,
        },
      }),
    },
  );

  return response.json();
}
```

## Tenant Connection Factory

```ts
import { createClient, type Client } from '@libsql/client';

const clients = new Map<string, Client>();

function getTenantClient(tenantId: string): Client {
  const existing = clients.get(tenantId);
  if (existing) return existing;

  const client = createClient({
    url: `libsql://tenant-${tenantId}-${process.env.TURSO_ORG}.turso.io`,
    authToken: process.env[`TURSO_TOKEN_${tenantId.toUpperCase()}`],
  });

  clients.set(tenantId, client);
  return client;
}
```

## Schema Management Across Tenants

Apply schema changes to all tenant databases using the platform API:

```ts
async function listDatabases(): Promise<string[]> {
  const response = await fetch(
    `https://api.turso.tech/v1/organizations/${TURSO_ORG}/databases`,
    {
      headers: { Authorization: `Bearer ${TURSO_API_TOKEN}` },
    },
  );

  const data = await response.json();
  return data.databases.map((db: { name: string }) => db.name);
}

async function migrateAllTenants(migrationSql: string) {
  const databases = await listDatabases();
  const tenantDbs = databases.filter((name) => name.startsWith('tenant-'));

  const results = await Promise.allSettled(
    tenantDbs.map(async (dbName) => {
      const client = createClient({
        url: `libsql://${dbName}-${TURSO_ORG}.turso.io`,
        authToken: TURSO_API_TOKEN,
      });

      try {
        await client.execute(migrationSql);
        return { db: dbName, status: 'success' };
      } finally {
        client.close();
      }
    }),
  );

  return results;
}
```

## Multi-Tenant vs Shared Database

| Approach              | Isolation | Provisioning | Schema Changes | Cost         |
| --------------------- | --------- | ------------ | -------------- | ------------ |
| Database-per-tenant   | Full      | Platform API | Per-database   | Per-database |
| Shared with row-level | Logical   | None         | Single schema  | Shared       |

Database-per-tenant is preferred when tenants need isolated data, independent backup/restore, or different performance profiles. Use shared databases with row-level filtering for simpler applications with many low-usage tenants.
