---
title: Undo and Redo
description: Collaborative undo/redo patterns for Yjs UndoManager and Automerge including scoped stacks and multi-document undo
tags:
  [
    undo,
    redo,
    yjs,
    automerge,
    undo-manager,
    collaborative,
    transactions,
    scoped,
  ]
---

## Yjs UndoManager

The `UndoManager` tracks changes to Yjs shared types and supports local-only undo — each user undoes their own changes without affecting other users' edits.

### Basic Setup

```ts
import * as Y from 'yjs';

const doc = new Y.Doc();
const yText = doc.getText('content');
const yMap = doc.getMap('metadata');

const undoManager = new Y.UndoManager([yText, yMap], {
  captureTimeout: 500,
  trackedOrigins: new Set(['user-edit']),
});
```

| Option           | Default | Description                                            |
| ---------------- | ------- | ------------------------------------------------------ |
| `captureTimeout` | 500ms   | Time window to merge consecutive changes into one item |
| `trackedOrigins` | all     | Set of origins to track (others are ignored)           |
| `deleteFilter`   | —       | Function to prevent specific deletions from tracking   |

### Tracked Transactions

Only changes made within a `doc.transact()` call with a tracked origin are recorded in the undo stack.

```ts
doc.transact(() => {
  yText.insert(0, 'Hello ');
  yMap.set('lastEdited', Date.now());
}, 'user-edit');
```

Changes from remote sync (different origin) are not tracked, so undoing only reverses local edits.

### Undo, Redo, and Stop Capturing

```ts
undoManager.undo();
undoManager.redo();

undoManager.stopCapturing();
```

`stopCapturing()` forces the next change to start a new undo stack item rather than merging with the previous one. Use it to create explicit undo boundaries.

```ts
yText.insert(0, 'First edit');
undoManager.stopCapturing();
yText.insert(11, ' Second edit');

undoManager.undo();
```

### Stack Item Metadata

Attach metadata (cursor position, scroll state) to undo stack items for restoring UI state on undo/redo.

```ts
undoManager.on(
  'stack-item-added',
  (event: { stackItem: Y.UndoManagerStackItem; type: 'undo' | 'redo' }) => {
    event.stackItem.meta.set('cursor', getCursorPosition());
    event.stackItem.meta.set('scroll', getScrollPosition());
  },
);

undoManager.on(
  'stack-item-popped',
  (event: { stackItem: Y.UndoManagerStackItem; type: 'undo' | 'redo' }) => {
    const cursor = event.stackItem.meta.get('cursor') as number | undefined;
    const scroll = event.stackItem.meta.get('scroll') as number | undefined;

    if (cursor !== undefined) setCursorPosition(cursor);
    if (scroll !== undefined) setScrollPosition(scroll);
  },
);
```

### Delete Filter

Prevent certain deletions from being tracked. Useful for protecting structural elements.

```ts
const undoManager = new Y.UndoManager([yText], {
  trackedOrigins: new Set(['user-edit']),
  deleteFilter: (item: Y.Item) => {
    if (
      item.parent instanceof Y.XmlElement &&
      item.parent.nodeName === 'TABLE'
    ) {
      return false;
    }
    return true;
  },
});
```

Return `false` to exclude a deletion from the undo stack.

## Local Undo vs Global Undo

| Approach    | Behavior                             | Use Case                          |
| ----------- | ------------------------------------ | --------------------------------- |
| Local undo  | Each user undoes only their changes  | Collaborative text editing        |
| Global undo | Undo reverses the most recent change | Shared whiteboard, simple co-edit |

Yjs UndoManager implements local undo by default via `trackedOrigins`. For global undo, track all origins:

```ts
const globalUndoManager = new Y.UndoManager([yText], {
  trackedOrigins: new Set([null]),
});
```

Setting `null` as a tracked origin captures changes from `doc.transact()` calls with no explicit origin.

## Automerge Undo

### automerge-repo-undo-redo

```ts
import { AutomergeRepoUndoRedo } from 'automerge-repo-undo-redo';

const undoRedo = new AutomergeRepoUndoRedo(repo);
```

### Making Tracked Changes

```ts
import { type DocHandle } from '@automerge/automerge-repo';

const handle: DocHandle<TodoDoc> = repo.find(docUrl);

undoRedo.change(handle, (doc) => {
  doc.todos.push({ id: '1', title: 'New todo', completed: false });
});
```

### Undo and Redo

```ts
undoRedo.undo(handle);
undoRedo.redo(handle);
```

### Transactions for Batch Undo

Group multiple changes into a single undoable operation.

```ts
undoRedo.transaction(handle, (tx) => {
  tx.change((doc) => {
    doc.title = 'Updated title';
  });
  tx.change((doc) => {
    doc.lastModified = Date.now();
  });
});
```

A single `undo()` call reverses both changes.

## Scoped Undo Stacks

Create separate undo stacks for isolated UI contexts like modals or dialogs.

### Yjs Scoped Origin

```ts
const MODAL_ORIGIN = 'modal-edit';
const MAIN_ORIGIN = 'main-edit';

const mainUndoManager = new Y.UndoManager([yText], {
  trackedOrigins: new Set([MAIN_ORIGIN]),
});

const modalUndoManager = new Y.UndoManager([yText], {
  trackedOrigins: new Set([MODAL_ORIGIN]),
});

doc.transact(() => {
  yText.insert(0, 'modal change');
}, MODAL_ORIGIN);

modalUndoManager.undo();
```

### Automerge Scoped Stacks

```ts
const mainUndoRedo = new AutomergeRepoUndoRedo(repo);
const modalUndoRedo = new AutomergeRepoUndoRedo(repo);
```

Each `AutomergeRepoUndoRedo` instance maintains its own stack. Changes made through `modalUndoRedo.change()` are only undone by `modalUndoRedo.undo()`.

## Multi-Document Undo

Coordinate undo across multiple documents with a unified manager.

### Yjs Multi-Document

```ts
class MultiDocUndoManager {
  private managers = new Map<string, Y.UndoManager>();

  register(id: string, types: Y.AbstractType<unknown>[], origin: string): void {
    this.managers.set(
      id,
      new Y.UndoManager(types, {
        trackedOrigins: new Set([origin]),
      }),
    );
  }

  undo(id: string): void {
    this.managers.get(id)?.undo();
  }

  redo(id: string): void {
    this.managers.get(id)?.redo();
  }

  undoAll(): void {
    for (const manager of this.managers.values()) {
      manager.undo();
    }
  }

  destroy(): void {
    for (const manager of this.managers.values()) {
      manager.destroy();
    }
    this.managers.clear();
  }
}
```

### Automerge Multi-Document

```ts
class UndoRedoManager {
  private undoRedo: AutomergeRepoUndoRedo;
  private handles = new Map<string, DocHandle<unknown>>();

  constructor(repo: Repo) {
    this.undoRedo = new AutomergeRepoUndoRedo(repo);
  }

  register(id: string, handle: DocHandle<unknown>): void {
    this.handles.set(id, handle);
  }

  change<T>(id: string, changeFn: (doc: T) => void): void {
    const handle = this.handles.get(id) as DocHandle<T> | undefined;
    if (handle) {
      this.undoRedo.change(handle, changeFn);
    }
  }

  undo(id: string): void {
    const handle = this.handles.get(id);
    if (handle) {
      this.undoRedo.undo(handle);
    }
  }

  redo(id: string): void {
    const handle = this.handles.get(id);
    if (handle) {
      this.undoRedo.redo(handle);
    }
  }
}
```
