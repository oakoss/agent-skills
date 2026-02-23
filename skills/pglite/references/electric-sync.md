---
title: Electric Sync
description: PGlite sync with Electric using syncShapeToTable, syncShapesToTables for transactional sync, limitations, and shapeKey persistence
tags:
  [
    electric,
    sync,
    syncShapeToTable,
    syncShapesToTables,
    shape,
    shapeKey,
    pglite-sync,
  ]
---

# Electric Sync

## Overview

The `@electric-sql/pglite-sync` package enables one-way, read-only sync from an Electric server to a local PGlite database. Data flows from the server Postgres to PGlite via Electric Shapes. Local writes to synced tables are not replicated back to the server.

## Installation

```bash
npm install @electric-sql/pglite @electric-sql/pglite-sync
```

## Setup

Register the sync extension at construction time.

```ts
import { PGlite } from '@electric-sql/pglite';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: {
    electric: electricSync(),
  },
});
```

## syncShapeToTable

Sync a single Electric Shape into a local PGlite table.

```ts
import { PGlite } from '@electric-sql/pglite';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: {
    electric: electricSync(),
  },
});

await db.exec(`
  CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY,
    task TEXT NOT NULL,
    done BOOLEAN DEFAULT false
  )
`);

const shape = await db.electric.syncShapeToTable({
  shape: {
    url: 'https://my-electric-server.com/v1/shape',
    params: {
      table: 'todos',
    },
  },
  table: 'todos',
  primaryKey: ['id'],
});
```

The `shape` object returned provides control over the sync:

```ts
shape.unsubscribe();

shape.isUpToDate;

shape.subscribe(() => {
  console.log('Sync state changed, up to date:', shape.isUpToDate);
});
```

## Shape Options

| Option                 | Type       | Description                            |
| ---------------------- | ---------- | -------------------------------------- |
| `shape.url`            | `string`   | Electric server shape endpoint URL     |
| `shape.params.table`   | `string`   | Source table name on the server        |
| `shape.params.where`   | `string`   | SQL WHERE clause to filter rows        |
| `shape.params.columns` | `string[]` | Subset of columns to sync              |
| `table`                | `string`   | Local PGlite table to sync into        |
| `primaryKey`           | `string[]` | Primary key columns of the local table |
| `shapeKey`             | `string`   | Persistence key for resuming sync      |

### Filtered Sync

```ts
import { PGlite } from '@electric-sql/pglite';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: { electric: electricSync() },
});

await db.electric.syncShapeToTable({
  shape: {
    url: 'https://my-electric-server.com/v1/shape',
    params: {
      table: 'todos',
      where: "user_id = '123'",
      columns: ['id', 'task', 'done'],
    },
  },
  table: 'todos',
  primaryKey: ['id'],
});
```

## syncShapesToTables (Transactional)

Sync multiple shapes atomically. Changes across tables are applied in a single transaction.

```ts
import { PGlite } from '@electric-sql/pglite';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: { electric: electricSync() },
});

await db.exec(`
  CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title TEXT NOT NULL
  );
`);

const sync = await db.electric.syncShapesToTables({
  shapes: {
    projects: {
      shape: {
        url: 'https://my-electric-server.com/v1/shape',
        params: { table: 'projects' },
      },
      table: 'projects',
      primaryKey: ['id'],
    },
    tasks: {
      shape: {
        url: 'https://my-electric-server.com/v1/shape',
        params: { table: 'tasks' },
      },
      table: 'tasks',
      primaryKey: ['id'],
    },
  },
});
```

Transactional sync ensures referential integrity across related tables.

## shapeKey for Persistence

The `shapeKey` option enables sync resumption after page reloads. Without it, sync starts from scratch each time.

```ts
import { PGlite } from '@electric-sql/pglite';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: { electric: electricSync() },
});

await db.electric.syncShapeToTable({
  shape: {
    url: 'https://my-electric-server.com/v1/shape',
    params: { table: 'todos' },
  },
  table: 'todos',
  primaryKey: ['id'],
  shapeKey: 'todos-sync',
});
```

PGlite stores the sync cursor internally. On reload, it resumes from the last known position instead of re-fetching all data.

## Limitations

- **Read-only sync**: Data flows one way from server to PGlite. Local writes are not replicated back.
- **No conflict resolution**: Since sync is one-way, server data overwrites local data.
- **Schema must match**: The local PGlite table schema must be compatible with the synced Shape columns.
- **No DDL sync**: Schema changes on the server are not automatically applied locally.
- **Shape constraints**: Shapes follow Electric's Shape API constraints (single table, optional WHERE filter).

## Combining Sync with Live Queries

Synced data triggers live query updates automatically.

```ts
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';
import { electricSync } from '@electric-sql/pglite-sync';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: {
    live,
    electric: electricSync(),
  },
});

await db.electric.syncShapeToTable({
  shape: {
    url: 'https://my-electric-server.com/v1/shape',
    params: { table: 'todos' },
  },
  table: 'todos',
  primaryKey: ['id'],
  shapeKey: 'todos-sync',
});

const { unsubscribe } = await db.live.query(
  'SELECT * FROM todos WHERE done = false ORDER BY id',
  [],
  (result) => {
    console.log('Todos updated from server:', result.rows);
  },
);
```

Server-side changes flow through Electric to PGlite, which triggers the live query callback. This provides a fully reactive pipeline from server to UI.
