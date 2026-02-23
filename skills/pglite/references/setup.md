---
title: Setup
description: Installation, PGlite.create() factory, storage backends (memory, idb, opfs-ahp, filesystem), and configuration options
tags:
  [
    install,
    create,
    storage,
    idb,
    opfs,
    memory,
    filesystem,
    configuration,
    relaxedDurability,
  ]
---

# Setup

## Installation

```bash
npm install @electric-sql/pglite
```

For framework-specific packages:

```bash
npm install @electric-sql/pglite-react
npm install @electric-sql/pglite-vue
```

## Creating an Instance

Always use the `PGlite.create()` static factory method. It awaits the database ready state internally, so the returned instance is immediately usable.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();
```

The legacy `new PGlite()` constructor requires manually awaiting `.waitReady` and is not recommended.

## Storage Backends

### In-Memory (Default)

Ephemeral storage that is lost when the process or tab closes. Best for testing and prototyping.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();
```

### IndexedDB (Browser)

Persistent browser storage using IndexedDB. Works in all modern browsers including Safari.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create('idb://my-database');
```

### OPFS-AHP (Browser Worker)

Origin Private File System with Access Handle Pool. Provides the best browser performance but requires a Web Worker context and does not work in Safari.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create('opfs-ahp://my-database');
```

OPFS-AHP constraints:

- Must run inside a Web Worker (not the main thread)
- Not supported in Safari
- Best combined with `PGliteWorker` for multi-tab setups

### Filesystem (Node.js / Bun)

Persists to the local filesystem. Provide a directory path.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create('./path/to/pgdata');
```

## Configuration Options

Pass an options object as the second argument (or as the first argument with `dataDir` included).

```ts
import { PGlite } from '@electric-sql/pglite';
import { vector } from '@electric-sql/pglite/vector';
import { live } from '@electric-sql/pglite/live';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  relaxedDurability: true,
  extensions: {
    vector,
    live,
  },
});
```

### Key Options

| Option              | Type                        | Description                                      |
| ------------------- | --------------------------- | ------------------------------------------------ |
| `dataDir`           | `string`                    | Storage backend URI or filesystem path           |
| `relaxedDurability` | `boolean`                   | Skips fsync for better browser write performance |
| `extensions`        | `Record<string, Extension>` | Extensions to load at construction time          |
| `loadDataDir`       | `Blob \| File`              | Restore from a previous `dumpDataDir()` export   |
| `debug`             | `1-5`                       | Postgres debug level                             |
| `initialMemory`     | `number`                    | Initial WASM memory allocation in bytes          |

### Relaxed Durability

Enabling `relaxedDurability` significantly improves write performance in the browser by skipping fsync calls. Data remains consistent within a session but may be lost on unexpected tab closure.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  relaxedDurability: true,
});
```

Recommended for browser apps where occasional data loss on crash is acceptable (local-first apps that sync with a server).

## TypeScript Configuration

PGlite ships with full TypeScript types. No additional `@types` packages are needed.

```ts
import {
  type PGliteOptions,
  type QueryResult,
  PGlite,
} from '@electric-sql/pglite';
```

## Verifying the Setup

Run a simple query to confirm the instance is working:

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

const result = await db.query<{ version: string }>('SELECT version()');
console.log(result.rows[0].version);
```

This returns the embedded PostgreSQL 17.4 version string.
