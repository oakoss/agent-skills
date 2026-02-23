---
title: Local and Storage Collections
description: Local-only in-memory collections and localStorage-persisted collections with cross-tab sync
tags:
  [
    local-only,
    localStorage,
    in-memory,
    cross-tab,
    storage,
    ephemeral,
    persistence,
    loopback,
  ]
---

# Local and Storage Collections

TanStack DB provides two collection types for data that does not require server sync: local-only (in-memory) and localStorage-persisted collections.

## Local-Only Collections

`localOnlyCollectionOptions` creates an in-memory collection with no persistence. Mutations apply instantly with no async handlers. Data is lost on page refresh.

### Basic Setup

```ts
import { createCollection, localOnlyCollectionOptions } from '@tanstack/db';

interface FilterState {
  id: string;
  category: string;
  sortBy: string;
  ascending: boolean;
}

const filterCollection = createCollection(
  localOnlyCollectionOptions<FilterState>({
    getKey: (item) => item.id,
    initialData: [
      { id: 'main', category: 'all', sortBy: 'createdAt', ascending: false },
    ],
  }),
);
```

### Configuration

| Option        | Type                  | Description                               |
| ------------- | --------------------- | ----------------------------------------- |
| `getKey`      | `(item: T) => string` | Extracts unique key from each item        |
| `schema`      | Standard Schema V1    | Optional validation (Zod/Valibot/ArkType) |
| `initialData` | `T[]`                 | Items to populate the collection with     |

### Direct Mutations

Local-only collections support the same mutation API as synced collections. Changes apply immediately with no async round-trip:

```ts
// Insert
filterCollection.insert({
  id: 'secondary',
  category: 'active',
  sortBy: 'priority',
  ascending: true,
});

// Update with Immer-style draft
filterCollection.update('main', (draft) => {
  draft.category = 'completed';
  draft.sortBy = 'updatedAt';
});

// Delete
filterCollection.delete('secondary');
```

### Schema Validation

Local-only collections support Standard Schema V1 (Zod, Valibot, ArkType):

```ts
import { z } from 'zod';
import { createCollection, localOnlyCollectionOptions } from '@tanstack/db';

const uiStateSchema = z.object({
  id: z.string(),
  sidebarOpen: z.boolean(),
  theme: z.enum(['light', 'dark', 'system']),
});

type UIState = z.infer<typeof uiStateSchema>;

const uiCollection = createCollection(
  localOnlyCollectionOptions<UIState>({
    getKey: (item) => item.id,
    schema: uiStateSchema,
    initialData: [{ id: 'app', sidebarOpen: true, theme: 'system' }],
  }),
);
```

### Manual Transactions with Local-Only Collections

When using `createTransaction` with local-only collections, you must call `utils.acceptMutations()` to apply the changes. Without a persistence handler, there is no automatic commit flow:

```ts
import { createTransaction } from '@tanstack/db';

const tx = createTransaction({
  mutationFn: async ({ transaction, utils }) => {
    // No server call needed — just accept the mutations
    utils.acceptMutations(transaction);
  },
});

tx.mutate(() => {
  filterCollection.update('main', (draft) => {
    draft.category = 'active';
  });
  filterCollection.insert({
    id: 'sidebar',
    category: 'all',
    sortBy: 'name',
    ascending: true,
  });
});

tx.commit();
```

### When to Use Local-Only

- Ephemeral UI state (filter selections, sort order, panel visibility)
- Derived or computed state that does not need persistence
- Temporary data during multi-step workflows
- In-memory caches that rebuild on navigation

## localStorage Collections

`localStorageCollectionOptions` persists data to `localStorage` and syncs across browser tabs via `storage` events.

### Basic Setup

```ts
import { createCollection, localStorageCollectionOptions } from '@tanstack/db';

interface UserPreferences {
  id: string;
  theme: 'light' | 'dark' | 'system';
  fontSize: number;
  language: string;
}

const preferencesCollection = createCollection(
  localStorageCollectionOptions<UserPreferences>({
    storageKey: 'user-preferences',
    getKey: (item) => item.id,
    initialData: [
      { id: 'prefs', theme: 'system', fontSize: 14, language: 'en' },
    ],
  }),
);
```

### Configuration

| Option        | Type                  | Description                               |
| ------------- | --------------------- | ----------------------------------------- |
| `storageKey`  | `string`              | Key used in `localStorage.setItem()`      |
| `getKey`      | `(item: T) => string` | Extracts unique key from each item        |
| `schema`      | Standard Schema V1    | Optional validation (Zod/Valibot/ArkType) |
| `initialData` | `T[]`                 | Default data when storage is empty        |

### Cross-Tab Sync

Changes in one tab automatically propagate to all other tabs via the browser `storage` event. No additional configuration is needed:

```ts
// Tab 1: update theme
preferencesCollection.update('prefs', (draft) => {
  draft.theme = 'dark';
});

// Tab 2: live queries automatically reflect the change
const prefs = useLiveQuery((q) =>
  q.from({ p: preferencesCollection }).where(({ p }) => eq(p.id, 'prefs')),
);
```

### Size Constraints

localStorage collections work best for small datasets:

| Guideline     | Recommendation              |
| ------------- | --------------------------- |
| Item count    | Under 100 items             |
| Total size    | Under 100 KB                |
| Item size     | Keep individual items small |
| Browser limit | ~5 MB per origin (varies)   |

For larger datasets, use a synced collection with a proper backend or consider IndexedDB-based solutions.

### When to Use localStorage Collections

- User preferences (theme, language, layout)
- Small persistent state that survives page refresh
- Cross-tab shared state (shopping cart, auth tokens)
- Feature flags or user-specific toggles

## Choosing Between Collection Types

| Criteria             | Local-Only           | localStorage           | Synced (query/electric) |
| -------------------- | -------------------- | ---------------------- | ----------------------- |
| Persistence          | None (memory only)   | Browser localStorage   | Server backend          |
| Survives refresh     | No                   | Yes                    | Yes                     |
| Cross-tab sync       | No                   | Yes (storage events)   | Yes (via server)        |
| Dataset size         | Any (memory-limited) | Small (< 100 items)    | Any                     |
| Server sync          | No                   | No                     | Yes                     |
| Persistence handlers | Not needed           | Not needed             | Required                |
| Use case             | Ephemeral UI state   | Small persistent prefs | Application data        |
