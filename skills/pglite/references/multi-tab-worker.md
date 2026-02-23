---
title: Multi-Tab Worker
description: PGliteWorker for multi-tab architecture, leader election, worker file setup, isLeader, and onLeaderChange
tags:
  [
    PGliteWorker,
    worker,
    multi-tab,
    leader-election,
    isLeader,
    onLeaderChange,
    SharedWorker,
  ]
---

# Multi-Tab Worker

## Problem

PGlite uses a single-writer model. When multiple browser tabs open the same database, concurrent writes cause corruption. `PGliteWorker` solves this with automatic leader election: one tab holds the database lock, and other tabs proxy queries through it.

## Installation

`PGliteWorker` is included in the main package:

```bash
npm install @electric-sql/pglite
```

## Worker File Setup

Create a dedicated worker file that initializes PGlite and calls `worker()` to expose it.

```ts
// pglite-worker.ts
import { PGlite } from '@electric-sql/pglite';
import { worker } from '@electric-sql/pglite/worker';
import { live } from '@electric-sql/pglite/live';

worker({
  async init() {
    return await PGlite.create({
      dataDir: 'idb://my-app',
      relaxedDurability: true,
      extensions: { live },
    });
  },
});
```

The `worker()` function wraps the PGlite instance with message handling for cross-tab communication.

## Using PGliteWorker

In the main thread, create a `PGliteWorker` that connects to the worker file.

```ts
import { PGliteWorker } from '@electric-sql/pglite/worker';
import { live } from '@electric-sql/pglite/live';

const db = new PGliteWorker(
  new Worker(new URL('./pglite-worker.ts', import.meta.url), {
    type: 'module',
  }),
  {
    extensions: { live },
  },
);

await db.query('SELECT * FROM todos');
```

The `PGliteWorker` instance exposes the same API as a regular `PGlite` instance: `query`, `sql`, `exec`, `transaction`, and extension methods all work transparently.

## Leader Election

PGliteWorker uses automatic leader election across tabs. Only the leader tab holds the actual database connection. Other tabs route queries through the leader.

### Checking Leader Status

```ts
import { PGliteWorker } from '@electric-sql/pglite/worker';

const db = new PGliteWorker(
  new Worker(new URL('./pglite-worker.ts', import.meta.url), {
    type: 'module',
  }),
);

if (db.isLeader) {
  console.log('This tab is the database leader');
}
```

### Listening for Leader Changes

When the leader tab closes, a new leader is elected automatically. Listen for leadership transitions.

```ts
import { PGliteWorker } from '@electric-sql/pglite/worker';

const db = new PGliteWorker(
  new Worker(new URL('./pglite-worker.ts', import.meta.url), {
    type: 'module',
  }),
);

db.onLeaderChange((isLeader) => {
  if (isLeader) {
    console.log('This tab became the leader');
  } else {
    console.log('This tab lost leadership');
  }
});
```

## Architecture Overview

```text
Tab A (Leader)          Tab B (Follower)        Tab C (Follower)
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│ PGliteWorker│        │ PGliteWorker│        │ PGliteWorker│
│  (active DB)│◄───────│  (proxy)    │        │  (proxy)    │
│             │        │             │        │             │
└─────┬───────┘        └─────────────┘        └──────┬──────┘
      │                                              │
      │            ◄─────────────────────────────────┘
      ▼
┌─────────────┐
│  PGlite     │
│  (idb://)   │
└─────────────┘
```

When Tab A closes, leadership transfers automatically to Tab B or Tab C.

## Full React Example

```tsx
// pglite-worker.ts
import { PGlite } from '@electric-sql/pglite';
import { worker } from '@electric-sql/pglite/worker';
import { live } from '@electric-sql/pglite/live';

worker({
  async init() {
    return await PGlite.create({
      dataDir: 'idb://my-app',
      relaxedDurability: true,
      extensions: { live },
    });
  },
});
```

```tsx
// db.ts
import { PGliteWorker } from '@electric-sql/pglite/worker';
import { live } from '@electric-sql/pglite/live';

export const db = new PGliteWorker(
  new Worker(new URL('./pglite-worker.ts', import.meta.url), {
    type: 'module',
  }),
  {
    extensions: { live },
  },
);
```

```tsx
// App.tsx
import { PGliteProvider } from '@electric-sql/pglite-react';
import { db } from './db';

function App() {
  return (
    <PGliteProvider db={db}>
      <TodoApp />
    </PGliteProvider>
  );
}
```

The `PGliteWorker` instance is compatible with `PGliteProvider`, so all React hooks work with the multi-tab setup without any changes.

## OPFS-AHP with Worker

For maximum performance, combine OPFS-AHP storage with the worker pattern. OPFS-AHP requires a worker context, making this a natural pairing.

```ts
// pglite-worker.ts
import { PGlite } from '@electric-sql/pglite';
import { worker } from '@electric-sql/pglite/worker';
import { live } from '@electric-sql/pglite/live';

worker({
  async init() {
    return await PGlite.create({
      dataDir: 'opfs-ahp://my-app',
      relaxedDurability: true,
      extensions: { live },
    });
  },
});
```

## Bundler Configuration

Most bundlers (Vite, webpack 5, esbuild) handle the `new Worker(new URL(...))` pattern natively. For Vite:

```ts
const db = new PGliteWorker(
  new Worker(new URL('./pglite-worker.ts', import.meta.url), {
    type: 'module',
  }),
  {
    extensions: { live },
  },
);
```

No additional bundler configuration is needed for Vite. For webpack, ensure the `worker-loader` or built-in worker support is enabled.
