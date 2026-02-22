---
title: Multi-Tenant Data Governance
description: Workspace scoping, tenant isolation, data access revocation, PII handling, role-based sync, and audit trails for local-first multi-tenant apps
tags:
  [
    multi-tenant,
    workspace,
    tenant-isolation,
    revocation,
    pii,
    role-based-sync,
    audit,
    data-residency,
    encryption,
    cleanup,
  ]
---

## Workspace/Team Scoping

Each tenant gets isolated shapes with per-tenant where clauses. The server injects tenant context so clients never request cross-tenant data directly.

```ts
import { ShapeStream, Shape } from '@electric-sql/client';

type TenantConfig = {
  tenantId: string;
  apiBase: string;
};

function createTenantShape<T extends Record<string, unknown>>(
  table: string,
  config: TenantConfig,
  additionalWhere?: string,
): ShapeStream<T> {
  const where = additionalWhere
    ? `tenant_id = '${config.tenantId}' AND ${additionalWhere}`
    : `tenant_id = '${config.tenantId}'`;

  return new ShapeStream<T>({
    url: `${config.apiBase}/v1/shape`,
    params: { table, where },
  });
}
```

### Switching Workspaces

Tear down old shapes before starting new ones to prevent data from leaking across tenants in memory.

```ts
type ActiveShapes = Map<string, ShapeStream>;

class WorkspaceManager {
  private shapes: ActiveShapes = new Map();
  private currentTenantId: string | null = null;

  async switchWorkspace(newTenantId: string, apiBase: string): Promise<void> {
    await this.teardown();
    this.currentTenantId = newTenantId;

    const config: TenantConfig = { tenantId: newTenantId, apiBase };

    this.shapes.set('tasks', createTenantShape('tasks', config));
    this.shapes.set(
      'documents',
      createTenantShape('documents', config, `archived = false`),
    );
  }

  private async teardown(): Promise<void> {
    for (const [key, stream] of this.shapes) {
      stream.unsubscribeAll();
      this.shapes.delete(key);
    }
    this.currentTenantId = null;
  }
}
```

## Shape-Per-Tenant Pattern

The server-side proxy injects tenant scoping. Clients never construct where clauses containing tenant IDs directly.

```ts
import express from 'express';

const app = express();
const ELECTRIC_URL = process.env.ELECTRIC_URL ?? 'http://localhost:3000';

app.get('/api/shapes/:table', authenticateUser, async (req, res) => {
  const tenantId = req.user.tenantId;
  const table = req.params.table;

  const url = new URL(`${ELECTRIC_URL}/v1/shape`);
  url.searchParams.set('table', table);
  url.searchParams.set('where', `tenant_id = $1`);
  url.searchParams.set('params[1]', tenantId);

  for (const param of ['offset', 'handle', 'live'] as const) {
    const value = req.query[param];
    if (typeof value === 'string') url.searchParams.set(param, value);
  }

  const response = await fetch(url.toString());
  res.status(response.status);
  for (const [key, value] of response.headers.entries()) {
    res.setHeader(key, value);
  }
  res.send(await response.text());
});
```

### Schema Design

```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  title TEXT NOT NULL,
  assigned_to UUID,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tasks
  USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

## Data Access Revocation

When a user is removed from a team, the server stops including their data in shapes. The client must clean up stale tenant data.

```ts
async function handleRevocation(
  revokedTenantId: string,
  workspaceManager: WorkspaceManager,
  currentTenantId: string | null,
): Promise<void> {
  await clearTenantData(revokedTenantId);

  if (currentTenantId === revokedTenantId) {
    await workspaceManager.switchWorkspace('', '');
    window.location.href = '/workspace-selector';
  }
}

async function checkMembership(apiBase: string): Promise<string[]> {
  const response = await fetch(`${apiBase}/api/memberships`);
  const memberships: Array<{ tenantId: string }> = await response.json();
  return memberships.map((m) => m.tenantId);
}

async function pruneRevokedTenants(apiBase: string): Promise<void> {
  const activeTenants = await checkMembership(apiBase);
  const localTenants = await getLocalTenantIds();

  for (const localTenantId of localTenants) {
    if (!activeTenants.includes(localTenantId)) {
      await clearTenantData(localTenantId);
    }
  }
}
```

## Local Data Cleanup

Clear IndexedDB and OPFS data when a user loses access to a tenant or logs out.

```ts
async function clearTenantData(tenantId: string): Promise<void> {
  const dbName = `tenant_${tenantId}`;

  const deleteRequest = indexedDB.deleteDatabase(dbName);
  await new Promise<void>((resolve, reject) => {
    deleteRequest.onsuccess = () => resolve();
    deleteRequest.onerror = () => reject(deleteRequest.error);
    deleteRequest.onblocked = () => resolve();
  });
}

async function clearAllLocalData(): Promise<void> {
  const databases = await indexedDB.databases();
  for (const db of databases) {
    if (db.name?.startsWith('tenant_')) {
      indexedDB.deleteDatabase(db.name);
    }
  }

  const root = await navigator.storage.getDirectory();
  for await (const [name] of root.entries()) {
    if (name.startsWith('tenant_')) {
      await root.removeEntry(name, { recursive: true });
    }
  }
}

async function getLocalTenantIds(): Promise<string[]> {
  const databases = await indexedDB.databases();
  return databases
    .map((db) => db.name)
    .filter((name): name is string => name?.startsWith('tenant_') ?? false)
    .map((name) => name.replace('tenant_', ''));
}
```

## PII and Sensitive Data

### Data Expiration (TTL on Local Records)

```ts
type TTLRecord<T> = T & {
  _expiresAt: number;
};

function withTTL<T>(record: T, ttlMs: number): TTLRecord<T> {
  return { ...record, _expiresAt: Date.now() + ttlMs };
}

async function purgeExpired(
  db: IDBDatabase,
  storeName: string,
): Promise<number> {
  const tx = db.transaction(storeName, 'readwrite');
  const store = tx.objectStore(storeName);
  const index = store.index('_expiresAt');
  const range = IDBKeyRange.upperBound(Date.now());
  let purged = 0;

  const request = index.openCursor(range);
  return new Promise((resolve, reject) => {
    request.onsuccess = () => {
      const cursor = request.result;
      if (cursor) {
        cursor.delete();
        purged++;
        cursor.continue();
      } else {
        resolve(purged);
      }
    };
    request.onerror = () => reject(request.error);
  });
}

// Run on app startup and periodically
const PURGE_INTERVAL_MS = 5 * 60 * 1000;
setInterval(() => purgeExpired(db, 'sensitive_records'), PURGE_INTERVAL_MS);
```

### Encrypting Sensitive Fields at Rest

```ts
async function encryptField(
  key: CryptoKey,
  plaintext: string,
): Promise<string> {
  const encoder = new TextEncoder();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    encoder.encode(plaintext),
  );

  const combined = new Uint8Array(
    iv.length + new Uint8Array(ciphertext).length,
  );
  combined.set(iv);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return btoa(String.fromCharCode(...combined));
}

async function decryptField(key: CryptoKey, encoded: string): Promise<string> {
  const combined = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const ciphertext = combined.slice(12);

  const plaintext = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    ciphertext,
  );
  return new TextDecoder().decode(plaintext);
}
```

### Clearing Data on Session Expiry

```ts
async function onSessionExpired(): Promise<void> {
  await clearAllLocalData();
  sessionStorage.clear();
  localStorage.removeItem('auth_token');
  window.location.href = '/login';
}
```

## Role-Based Sync

Different shapes for different roles. Admin sees all team data, members see only their own.

```ts
type UserRole = 'admin' | 'manager' | 'member';

type RoleShapeConfig = {
  table: string;
  where?: string;
};

function getShapesForRole(
  role: UserRole,
  tenantId: string,
  userId: string,
): RoleShapeConfig[] {
  const base = [
    { table: 'projects', where: `tenant_id = '${tenantId}'` },
    { table: 'labels', where: `tenant_id = '${tenantId}'` },
  ];

  switch (role) {
    case 'admin':
      return [
        ...base,
        { table: 'tasks', where: `tenant_id = '${tenantId}'` },
        { table: 'members', where: `tenant_id = '${tenantId}'` },
        { table: 'audit_log', where: `tenant_id = '${tenantId}'` },
      ];
    case 'manager':
      return [
        ...base,
        { table: 'tasks', where: `tenant_id = '${tenantId}'` },
        { table: 'members', where: `tenant_id = '${tenantId}'` },
      ];
    case 'member':
      return [
        ...base,
        {
          table: 'tasks',
          where: `tenant_id = '${tenantId}' AND assigned_to = '${userId}'`,
        },
      ];
  }
}
```

When a user's role changes, tear down existing shapes and reinitialize with `getShapesForRole` using the new role.

## Shared vs Private Data

Some collections are shared across all users (reference data), while others are scoped per-user or per-tenant.

```ts
type ShapeCategory = 'public' | 'tenant' | 'private';

type ShapeDefinition = {
  table: string;
  category: ShapeCategory;
  buildWhere: (ctx: { tenantId: string; userId: string }) => string | undefined;
};

const SHAPE_DEFINITIONS: ShapeDefinition[] = [
  { table: 'countries', category: 'public', buildWhere: () => undefined },
  { table: 'plan_features', category: 'public', buildWhere: () => undefined },
  {
    table: 'projects',
    category: 'tenant',
    buildWhere: (ctx) => `tenant_id = '${ctx.tenantId}'`,
  },
  {
    table: 'user_preferences',
    category: 'private',
    buildWhere: (ctx) => `user_id = '${ctx.userId}'`,
  },
  {
    table: 'drafts',
    category: 'private',
    buildWhere: (ctx) =>
      `tenant_id = '${ctx.tenantId}' AND user_id = '${ctx.userId}'`,
  },
];

function initializeShapes(
  definitions: ShapeDefinition[],
  ctx: { tenantId: string; userId: string },
  apiBase: string,
): Map<string, ShapeStream> {
  const shapes = new Map<string, ShapeStream>();

  for (const def of definitions) {
    const where = def.buildWhere(ctx);
    const params: Record<string, string> = { table: def.table };
    if (where) params.where = where;

    shapes.set(
      def.table,
      new ShapeStream({ url: `${apiBase}/v1/shape`, params }),
    );
  }

  return shapes;
}
```

## Audit Trail

Track who changed what locally and sync audit events to the server to maintain attribution.

```ts
type AuditEvent = {
  id: string;
  tenantId: string;
  userId: string;
  action: 'create' | 'update' | 'delete';
  table: string;
  recordId: string;
  changes: Record<string, { from: unknown; to: unknown }>;
  timestamp: string;
  synced: boolean;
};

async function recordAuditEvent(
  db: IDBDatabase,
  event: Omit<AuditEvent, 'id' | 'synced'>,
): Promise<void> {
  const tx = db.transaction('audit_events', 'readwrite');
  const store = tx.objectStore('audit_events');
  store.add({ ...event, id: crypto.randomUUID(), synced: false });
}

async function flushAuditEvents(
  db: IDBDatabase,
  apiBase: string,
): Promise<void> {
  const tx = db.transaction('audit_events', 'readonly');
  const index = tx.objectStore('audit_events').index('synced');

  const unsynced: AuditEvent[] = await new Promise((resolve, reject) => {
    const req = index.getAll(false);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });

  if (unsynced.length === 0) return;

  const response = await fetch(`${apiBase}/api/audit-events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(unsynced),
  });

  if (response.ok) {
    const writeTx = db.transaction('audit_events', 'readwrite');
    const store = writeTx.objectStore('audit_events');
    for (const event of unsynced) {
      store.put({ ...event, synced: true });
    }
  }
}
```

## Data Residency

Configure Electric instances per region to ensure local data respects geographic constraints.

```ts
type Region = 'us-east' | 'eu-west' | 'ap-southeast';

const REGIONAL_ENDPOINTS: Record<Region, string> = {
  'us-east': 'https://electric-us.example.com',
  'eu-west': 'https://electric-eu.example.com',
  'ap-southeast': 'https://electric-ap.example.com',
};

async function initializeRegionalSync(
  tenantId: string,
  tenantRegion: Region,
): Promise<ShapeStream> {
  const endpoint = REGIONAL_ENDPOINTS[tenantRegion];

  return new ShapeStream({
    url: `${endpoint}/v1/shape`,
    params: {
      table: 'tasks',
      where: `tenant_id = '${tenantId}'`,
    },
  });
}
```
