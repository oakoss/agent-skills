---
title: Schema Evolution
description: Schema versioning and migration strategies for local-first databases including IndexedDB, SQLite WASM, and PGlite with forward/backward compatibility
tags:
  [
    schema,
    migration,
    versioning,
    indexeddb,
    sqlite,
    pglite,
    compatibility,
    evolution,
    upgrade,
  ]
---

## The Problem

Local-first apps store data on the client. When the server schema changes, clients that have been offline may hold data in an outdated format. Unlike server-side migrations that run once against a centralized database, local-first migrations must handle:

- Clients offline for days or weeks running old schemas
- Sync messages arriving with fields the client does not recognize
- Clients sending data with fields the server no longer expects
- Multiple schema versions active simultaneously across the user base

## Migration Strategies

| Strategy          | How it works                                       | Tradeoff                                              |
| ----------------- | -------------------------------------------------- | ----------------------------------------------------- |
| Additive-only     | Only add columns/tables, never remove or rename    | Simple but schema grows indefinitely                  |
| Versioned schemas | Explicit version numbers with migration functions  | Full control but complex multi-step upgrades          |
| Lazy migration    | Transform records on read, migrate on next write   | Low upfront cost but read performance penalty         |
| Dual-write        | Write to both old and new format during transition | Safe rollback but doubles write cost during migration |

## Additive-Only Pattern

The simplest strategy: only add new columns and tables. Never rename or remove existing ones. Mark deprecated fields with naming conventions.

```ts
type TodoV1 = { id: string; title: string; completed: boolean };

type TodoV2 = TodoV1 & { priority: number | null; assigneeId: string | null };

type TodoV3 = TodoV2 & {
  dueDate: string | null;
  _deprecated_completed: boolean;
  status: 'todo' | 'in_progress' | 'done' | null;
};
```

## IndexedDB Schema Versioning

IndexedDB has built-in versioning via `onupgradeneeded`. The callback receives the old version and fires for every version jump -- opening version 3 from version 1 fires upgrades for 2 and 3.

```ts
function openAppDB(name: string, targetVersion: number): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, targetVersion);

    request.onupgradeneeded = (event) => {
      const db = request.result;
      const tx = request.transaction!;
      const oldVersion = event.oldVersion;

      if (oldVersion < 1) {
        const todos = db.createObjectStore('todos', { keyPath: 'id' });
        todos.createIndex('createdAt', 'createdAt');
      }

      if (oldVersion < 2) {
        const todos = tx.objectStore('todos');
        todos.createIndex('priority', 'priority');
        todos.createIndex('assigneeId', 'assigneeId');
      }

      if (oldVersion < 3) {
        if (!db.objectStoreNames.contains('comments')) {
          db.createObjectStore('comments', { keyPath: 'id' });
        }
        tx.objectStore('todos').createIndex('status', 'status');
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
```

### Data Migration During Upgrade

```ts
function migrateStore(
  tx: IDBTransaction,
  storeName: string,
  transform: (record: Record<string, unknown>) => Record<string, unknown>,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const store = tx.objectStore(storeName);
    const request = store.openCursor();
    request.onsuccess = () => {
      const cursor = request.result;
      if (!cursor) {
        resolve();
        return;
      }
      cursor.update(transform(cursor.value));
      cursor.continue();
    };
    request.onerror = () => reject(request.error);
  });
}
```

## SQLite WASM Migrations

### Version Table

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now')),
  checksum TEXT
);
```

### Migration Runner

```ts
type SQLiteMigration = { version: number; up: string[]; checksum: string };

const sqliteMigrations: SQLiteMigration[] = [
  {
    version: 1,
    checksum: 'a1b2c3',
    up: [
      `CREATE TABLE todos (
        id TEXT PRIMARY KEY, title TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      )`,
      `CREATE INDEX idx_todos_created_at ON todos(created_at)`,
    ],
  },
  {
    version: 2,
    checksum: 'd4e5f6',
    up: [
      `ALTER TABLE todos ADD COLUMN priority INTEGER`,
      `ALTER TABLE todos ADD COLUMN assignee_id TEXT`,
    ],
  },
  {
    version: 3,
    checksum: 'g7h8i9',
    up: [
      `ALTER TABLE todos ADD COLUMN status TEXT DEFAULT 'todo'`,
      `UPDATE todos SET status = CASE WHEN completed = 1 THEN 'done' ELSE 'todo' END`,
    ],
  },
];

async function runSQLiteMigrations(
  db: {
    exec: (sql: string) => void;
    selectObjects: (sql: string) => Record<string, unknown>[];
  },
  migrations: SQLiteMigration[],
): Promise<number> {
  db.exec(`CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT (datetime('now')), checksum TEXT
  )`);

  const applied = db.selectObjects(
    'SELECT version, checksum FROM schema_migrations ORDER BY version',
  );
  const appliedMap = new Map(
    applied.map((r) => [r.version as number, r.checksum as string]),
  );
  let count = 0;

  for (const migration of migrations) {
    if (appliedMap.has(migration.version)) {
      if (appliedMap.get(migration.version) !== migration.checksum) {
        throw new Error(`Checksum mismatch for migration ${migration.version}`);
      }
      continue;
    }

    db.exec('BEGIN TRANSACTION');
    try {
      for (const statement of migration.up) db.exec(statement);
      db.exec(
        `INSERT INTO schema_migrations (version, checksum) VALUES (${migration.version}, '${migration.checksum}')`,
      );
      db.exec('COMMIT');
      count++;
    } catch (error) {
      db.exec('ROLLBACK');
      throw error;
    }
  }
  return count;
}
```

## PGlite Migrations

PGlite supports Postgres-style DDL with `IF NOT EXISTS` guards for safe re-runs.

```ts
import { type PGlite } from '@electric-sql/pglite';

const pgliteMigrations = [
  {
    version: 1,
    up: `
      CREATE TABLE IF NOT EXISTS todos (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `,
  },
  {
    version: 2,
    up: `
      ALTER TABLE todos ADD COLUMN IF NOT EXISTS priority INTEGER;
      ALTER TABLE todos ADD COLUMN IF NOT EXISTS assignee_id UUID;
    `,
  },
  {
    version: 3,
    up: `
      DO $$ BEGIN
        CREATE TYPE todo_status AS ENUM ('todo', 'in_progress', 'done');
      EXCEPTION WHEN duplicate_object THEN NULL;
      END $$;
      ALTER TABLE todos ADD COLUMN IF NOT EXISTS status todo_status DEFAULT 'todo';
      UPDATE todos SET status = CASE WHEN completed THEN 'done' ELSE 'todo' END WHERE status IS NULL;
    `,
  },
];

async function runPGliteMigrations(db: PGlite): Promise<number> {
  await db.exec(`CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
  )`);

  const result = await db.query<{ version: number }>(
    'SELECT version FROM schema_migrations ORDER BY version',
  );
  const applied = new Set(result.rows.map((r) => r.version));
  let count = 0;

  for (const migration of pgliteMigrations) {
    if (applied.has(migration.version)) continue;
    await db.transaction(async (tx) => {
      await tx.exec(migration.up);
      await tx.exec(
        `INSERT INTO schema_migrations (version) VALUES (${migration.version})`,
      );
    });
    count++;
  }
  return count;
}
```

## Sync-Aware Migrations

When the server schema is ahead of the client, sync messages may contain fields the client does not recognize. Project incoming data to the client schema and store unknown fields separately for round-trip safety.

```ts
type SyncRecord = Record<string, unknown>;

type SchemaDefinition = {
  knownFields: Set<string>;
  requiredFields: Set<string>;
  defaults: Record<string, unknown>;
};

function projectWithOverflow(
  record: SyncRecord,
  schema: SchemaDefinition,
): { projected: SyncRecord; overflow: SyncRecord } {
  const projected: SyncRecord = {};
  const overflow: SyncRecord = {};

  for (const [key, value] of Object.entries(record)) {
    if (schema.knownFields.has(key)) projected[key] = value;
    else overflow[key] = value;
  }

  for (const field of schema.requiredFields) {
    if (!(field in projected)) projected[field] = schema.defaults[field];
  }

  return { projected, overflow };
}

function rehydrateForSync(
  projected: SyncRecord,
  overflow: SyncRecord,
): SyncRecord {
  return { ...projected, ...overflow };
}
```

## Forward/Backward Compatibility

### Version Negotiation

```ts
type VersionEnvelope = { schemaVersion: number; data: SyncRecord };

function handleIncoming(
  envelope: VersionEnvelope,
  clientVersion: number,
  schema: SchemaDefinition,
): SyncRecord {
  if (envelope.schemaVersion === clientVersion) return envelope.data;
  if (envelope.schemaVersion > clientVersion)
    return projectWithOverflow(envelope.data, schema).projected;
  return applyDefaults(envelope.data, envelope.schemaVersion, clientVersion);
}

function applyDefaults(
  record: SyncRecord,
  fromVersion: number,
  targetVersion: number,
): SyncRecord {
  const versionDefaults: Record<number, Record<string, unknown>> = {
    2: { priority: null, assigneeId: null },
    3: { status: 'todo', dueDate: null },
  };

  let result = { ...record };
  for (let v = fromVersion + 1; v <= targetVersion; v++) {
    if (versionDefaults[v]) {
      for (const [key, val] of Object.entries(versionDefaults[v])) {
        if (!(key in result)) result[key] = val;
      }
    }
  }
  return result;
}
```

## Data Transformation Between Versions

```ts
type TransformFn = (record: SyncRecord) => SyncRecord;

const transforms: Record<string, TransformFn> = {
  '1->2': (record) => ({ ...record, priority: null, assigneeId: null }),

  '2->3': (record) => {
    const tags =
      typeof record.tags === 'string'
        ? JSON.parse(record.tags as string)
        : (record.tags ?? []);
    return { ...record, tags, status: record.completed ? 'done' : 'todo' };
  },

  // String field split into multiple fields
  '3->4': (record) => {
    const fullName = record.assigneeName as string | null;
    return {
      ...record,
      assigneeFirstName: fullName?.split(' ')[0] ?? null,
      assigneeLastName: fullName?.split(' ').slice(1).join(' ') ?? null,
    };
  },
};

function migrateRecord(
  record: SyncRecord,
  fromVersion: number,
  toVersion: number,
): SyncRecord {
  let current = { ...record };
  for (let v = fromVersion; v < toVersion; v++) {
    const key = `${v}->${v + 1}`;
    const transform = transforms[key];
    if (!transform) throw new Error(`No transform found for ${key}`);
    current = transform(current);
  }
  return current;
}
```

## Testing Migrations

### Migration Verification Checklist

| Check              | Method                                               |
| ------------------ | ---------------------------------------------------- |
| No data loss       | Row counts match before and after migration          |
| Null handling      | Nullable fields default correctly for existing rows  |
| Index creation     | Query planner uses new indexes                       |
| Foreign keys       | References remain valid after schema changes         |
| Round-trip safety  | Data survives migrate-up then migrate-down           |
| Multi-version jump | Migrating from v1 to v5 directly produces same state |
| Idempotency        | Running same migration twice does not error          |

### Snapshot Test Pattern

```ts
async function verifyMigration(
  db: {
    exec: (sql: string) => void;
    selectObjects: (sql: string) => Record<string, unknown>[];
  },
  seedSql: string[],
  migrations: SQLiteMigration[],
  fromVersion: number,
  toVersion: number,
): Promise<{ passed: boolean; errors: string[] }> {
  const errors: string[] = [];
  db.exec('BEGIN TRANSACTION');
  try {
    for (const sql of seedSql) db.exec(sql);
    const pending = migrations.filter(
      (m) => m.version > fromVersion && m.version <= toVersion,
    );
    for (const migration of pending) {
      for (const statement of migration.up) db.exec(statement);
    }
    const todos = db.selectObjects('SELECT * FROM todos');
    if (todos.length === 0) errors.push('No rows survived migration');
  } finally {
    db.exec('ROLLBACK');
  }
  return { passed: errors.length === 0, errors };
}
```
