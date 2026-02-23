---
title: DevTools and Debugging
description: Browser DevTools inspection and debugging utilities for local-first storage, OPFS, sync events, and CRDT state
tags:
  [devtools, debugging, indexeddb, opfs, inspection, dexie, yjs, sync, storage]
---

## IndexedDB Inspection

### Chrome / Edge

1. Open DevTools (F12)
2. Navigate to **Application** tab
3. Expand **IndexedDB** in the left sidebar
4. Click a database to see object stores
5. Click an object store to browse records
6. Right-click a record to edit or delete

### Firefox

1. Open DevTools (F12)
2. Navigate to **Storage** tab
3. Expand **Indexed DB** in the left sidebar
4. Browse databases, object stores, and records

### Programmatic Listing

```ts
async function listDatabases(): Promise<IDBDatabaseInfo[]> {
  if (indexedDB.databases) {
    return indexedDB.databases();
  }
  return [];
}

async function inspectDatabase(name: string): Promise<{
  stores: string[];
  version: number;
}> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name);
    request.onsuccess = () => {
      const db = request.result;
      resolve({
        stores: Array.from(db.objectStoreNames),
        version: db.version,
      });
      db.close();
    };
    request.onerror = () => reject(request.error);
  });
}
```

## OPFS Inspection

OPFS is not visible in standard DevTools storage panels. Use browser extensions or programmatic access.

### OPFS Explorer Extension

Available for Chrome and Firefox. Adds an **OPFS Explorer** panel to DevTools that displays the OPFS file tree, file sizes, and allows downloading files.

Install from: Chrome Web Store or Firefox Add-ons (search "OPFS Explorer").

### OPFS Viewer

A standalone web-based tool for inspecting OPFS contents. Useful when extensions are not available.

### Programmatic OPFS Inspection

```ts
async function listOPFSFiles(
  dir?: FileSystemDirectoryHandle,
  path = '',
): Promise<{ path: string; kind: string }[]> {
  const root = dir ?? (await navigator.storage.getDirectory());
  const entries: { path: string; kind: string }[] = [];

  for await (const [name, handle] of root.entries()) {
    const fullPath = path ? `${path}/${name}` : name;
    entries.push({ path: fullPath, kind: handle.kind });

    if (handle.kind === 'directory') {
      const children = await listOPFSFiles(
        handle as FileSystemDirectoryHandle,
        fullPath,
      );
      entries.push(...children);
    }
  }

  return entries;
}
```

## Storage Overview Utility

```ts
async function debugStorageInfo(): Promise<{
  estimate: { usage: number; quota: number; percentUsed: number };
  persisted: boolean;
  databases: IDBDatabaseInfo[];
  opfsFiles: { path: string; kind: string }[];
}> {
  const estimate = await navigator.storage.estimate();
  const persisted = (await navigator.storage.persisted?.()) ?? false;

  let databases: IDBDatabaseInfo[] = [];
  if (indexedDB.databases) {
    databases = await indexedDB.databases();
  }

  let opfsFiles: { path: string; kind: string }[] = [];
  try {
    opfsFiles = await listOPFSFiles();
  } catch {
    // OPFS not available
  }

  return {
    estimate: {
      usage: estimate.usage ?? 0,
      quota: estimate.quota ?? 0,
      percentUsed: ((estimate.usage ?? 0) / (estimate.quota ?? 1)) * 100,
    },
    persisted,
    databases,
    opfsFiles,
  };
}
```

## Dexie.js Debug Mode

Dexie provides built-in logging for IndexedDB operations.

```ts
import Dexie from 'dexie';

Dexie.debug = true;

Dexie.debug = 'dexie';
```

With `Dexie.debug = true`, all IndexedDB transactions, queries, and mutations are logged to the console with timing information. Set to `'dexie'` for verbose output including internal operations.

Disable in production:

```ts
if (import.meta.env.DEV) {
  Dexie.debug = true;
}
```

## Yjs Document State Inspector

```ts
import { type Doc as YDoc } from 'yjs';

function inspectYDoc(doc: YDoc): {
  clientID: number;
  guid: string;
  sharedTypes: { name: string; type: string; length: number }[];
  stateVector: Map<number, number>;
  updateSize: number;
} {
  const { encodeStateAsUpdate, encodeStateVector, decodeStateVector } =
    require('yjs') as typeof import('yjs');

  const update = encodeStateAsUpdate(doc);
  const sv = decodeStateVector(encodeStateVector(doc));

  const sharedTypes: { name: string; type: string; length: number }[] = [];
  doc.share.forEach((type, name) => {
    sharedTypes.push({
      name,
      type: type.constructor.name,
      length: type.length,
    });
  });

  return {
    clientID: doc.clientID,
    guid: doc.guid,
    sharedTypes,
    stateVector: sv,
    updateSize: update.byteLength,
  };
}
```

## Sync Event Replay

Instrument sync providers to capture and replay synchronization events for debugging.

### Sync Event Logger

```ts
type SyncDirection = 'send' | 'receive';

interface SyncEvent {
  direction: SyncDirection;
  timestamp: number;
  size: number;
  type: string;
  data?: Uint8Array;
}

class SyncEventLogger {
  private events: SyncEvent[] = [];
  private maxEvents: number;

  constructor(maxEvents = 1000) {
    this.maxEvents = maxEvents;
  }

  log(direction: SyncDirection, type: string, data?: Uint8Array): void {
    if (this.events.length >= this.maxEvents) {
      this.events.shift();
    }

    this.events.push({
      direction,
      timestamp: performance.now(),
      size: data?.byteLength ?? 0,
      type,
      data: data ? new Uint8Array(data) : undefined,
    });
  }

  getEvents(): readonly SyncEvent[] {
    return this.events;
  }

  getSummary(): {
    totalSent: number;
    totalReceived: number;
    bytesSent: number;
    bytesReceived: number;
    eventTypes: Record<string, number>;
  } {
    let totalSent = 0;
    let totalReceived = 0;
    let bytesSent = 0;
    let bytesReceived = 0;
    const eventTypes: Record<string, number> = {};

    for (const event of this.events) {
      if (event.direction === 'send') {
        totalSent++;
        bytesSent += event.size;
      } else {
        totalReceived++;
        bytesReceived += event.size;
      }
      eventTypes[event.type] = (eventTypes[event.type] ?? 0) + 1;
    }

    return { totalSent, totalReceived, bytesSent, bytesReceived, eventTypes };
  }

  clear(): void {
    this.events = [];
  }
}
```

### Instrumenting a WebSocket Sync Provider

```ts
function instrumentWebSocket(
  ws: WebSocket,
  logger: SyncEventLogger,
): WebSocket {
  const originalSend = ws.send.bind(ws);

  ws.send = (data: string | ArrayBufferLike | Blob | ArrayBufferView) => {
    const size =
      data instanceof ArrayBuffer
        ? data.byteLength
        : typeof data === 'string'
          ? data.length
          : 0;
    logger.log(
      'send',
      'ws-message',
      data instanceof Uint8Array ? data : undefined,
    );
    originalSend(data);
  };

  ws.addEventListener('message', (event: MessageEvent) => {
    const data = event.data;
    logger.log(
      'receive',
      'ws-message',
      data instanceof ArrayBuffer ? new Uint8Array(data) : undefined,
    );
  });

  return ws;
}
```
