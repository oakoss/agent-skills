---
title: CRDTs and Collaborative Editing
description: CRDT engine selection, Yjs and Automerge patterns, syncing over pub/sub, presence cursors, and common pitfalls
tags: [crdt, yjs, automerge, collaboration, presence]
---

# CRDTs and Collaborative Editing

Conflict-free Replicated Data Types (CRDTs) allow multiple users to edit the same data simultaneously without a central lock. All changes merge deterministically regardless of arrival order.

## Engine Selection

| Engine    | Best For                                   | Data Model                 |
| --------- | ------------------------------------------ | -------------------------- |
| Yjs       | Text editing (Monaco, TipTap, ProseMirror) | Document with shared types |
| Automerge | JSON state (dashboards, settings, forms)   | JSON-like CRDT document    |

Both engines produce "deltas" (small change descriptions) that can be sent over any transport layer.

## Yjs Integration

### Basic Document Setup

```ts
import * as Y from 'yjs';

const ydoc = new Y.Doc();
const ytext = ydoc.getText('editor');

ytext.insert(0, 'Hello, world!');
```

### Syncing Yjs Over Pub/Sub

Bridge Yjs updates over a pub/sub channel for global persistence:

```ts
import * as Y from 'yjs';

const ydoc = new Y.Doc();
const channel = ably.channels.get('doc-123');

ydoc.on('update', (update: Uint8Array) => {
  channel.publish('yjs-update', update);
});

channel.subscribe('yjs-update', (msg) => {
  Y.applyUpdate(ydoc, new Uint8Array(msg.data));
});
```

### Initial State Sync

When a new client joins, it needs the full document state:

```ts
async function syncInitialState(ydoc: Y.Doc, channel: Channel) {
  const stateVector = Y.encodeStateVector(ydoc);
  const response = await channel.history({ limit: 1 });

  if (response.items.length > 0) {
    const snapshot = response.items[0].data;
    Y.applyUpdate(ydoc, new Uint8Array(snapshot));
  }
}
```

## Automerge Integration

For JSON-like collaborative state:

```ts
import * as Automerge from '@automerge/automerge';

let doc = Automerge.init<{ items: string[] }>();
doc = Automerge.change(doc, (d) => {
  d.items.push('New item');
});

const changes = Automerge.getAllChanges(doc);
```

## Presence: Collaborative Cursors

Show where other users are working in the document.

### Cursor Position Tracking

```ts
import { Awareness } from 'y-protocols/awareness';

const awareness = new Awareness(ydoc);

awareness.setLocalStateField('cursor', {
  anchor: { index: 42 },
  head: { index: 42 },
  user: { name: 'Alice', color: '#ff0000' },
});

awareness.on('change', () => {
  const states = awareness.getStates();
  states.forEach((state, clientId) => {
    if (clientId !== ydoc.clientID && state.cursor) {
      renderRemoteCursor(clientId, state.cursor);
    }
  });
});
```

### Cursor Rendering Best Practices

| Technique        | Purpose                                                       |
| ---------------- | ------------------------------------------------------------- |
| Interpolation    | Smooth cursor movement using `requestAnimationFrame`          |
| Throttling       | Send position updates every 50-100ms, not on every keystroke  |
| Color assignment | Assign consistent colors per user (hash clientId)             |
| Label display    | Show username near cursor, fade after 3 seconds of inactivity |

## Common CRDT Pitfalls

### Document Bloat

CRDTs store edit history. Unbounded documents grow indefinitely.

**Fix:** Use snapshotting for fields that do not need history. For example, a window width preference should use Last-Writer-Wins (LWW) rather than a full CRDT:

```ts
const ymap = ydoc.getMap('preferences');
ymap.set('window_width', 1200);
```

### Clock Drift

CRDTs do not require synchronized clocks, but massive drift between clients can cause text interleaving (characters appearing out of order in collaborative text editing).

**Fix:** Use logical clocks (Lamport timestamps) rather than wall clocks. Yjs handles this internally.

### Security

CRDT updates are opaque binary data. A malicious client can send arbitrary state.

**Fix:** Validate the final document state server-side in an "auditor" service. Do not trust client-produced CRDT updates for security-sensitive data without validation.

### Undo/Redo

CRDT undo is more complex than single-user undo because other users' changes may interleave.

**Fix:** Use Yjs `UndoManager` which tracks only the local user's operations:

```ts
const LOCAL_ORIGIN = 'local-user-input';

const undoManager = new Y.UndoManager(ytext, {
  trackedOrigins: new Set([LOCAL_ORIGIN]),
});

ydoc.transact(() => {
  ytext.insert(0, 'Hello');
}, LOCAL_ORIGIN);

undoManager.undo();
undoManager.redo();
```

## Architecture Summary

```text
Client A ──(delta)──> Pub/Sub Channel ──(delta)──> Client B
                          │
                          ├──(delta)──> Server Persistence
                          │
                          └──(delta)──> Client C
```

All clients converge to the same state regardless of message arrival order. The server persists snapshots periodically for new client onboarding.
