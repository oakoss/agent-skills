---
title: Middleware
description: Persist, devtools, immer middleware configuration, combining middlewares, custom middleware, and TypeScript patterns
tags:
  [
    middleware,
    persist,
    devtools,
    immer,
    custom,
    combine,
    localStorage,
    createJSONStorage,
  ]
---

# Middleware

## Persist Middleware

```ts
import { persist, createJSONStorage } from 'zustand/middleware';

const useStore = create<UserPreferences>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'user-preferences',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ theme: state.theme }),
    },
  ),
);
```

### Persist Options

| Option               | Description                            |
| -------------------- | -------------------------------------- |
| `name`               | Unique storage key (required)          |
| `storage`            | Storage engine via `createJSONStorage` |
| `partialize`         | Only save specific fields              |
| `version`            | Schema version for migrations          |
| `migrate`            | Function to transform old state        |
| `skipHydration`      | Manual hydration control               |
| `onRehydrateStorage` | Callback when hydration completes      |

### Schema Versioning and Migration

```ts
persist(
  (set) => ({
    /* ... */
  }),
  {
    name: 'app-storage',
    version: 2,
    migrate: (persistedState: any, version: number) => {
      if (version === 1) {
        return { ...persistedState, newField: 'default' };
      }
      return persistedState;
    },
  },
);
```

### Partial Persistence

```ts
persist((set) => ({ user: null, theme: 'dark', temp: 0 }), {
  name: 'settings',
  partialize: (state) => ({ theme: state.theme }),
});
```

## Devtools Middleware

```ts
import { devtools } from 'zustand/middleware';

const useStore = create<CounterStore>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () =>
        set((s) => ({ count: s.count + 1 }), undefined, 'increment'),
    }),
    { name: 'CounterStore' },
  ),
);
```

The third argument to `set` is the action name shown in Redux DevTools.

## Immer Middleware

For safe nested state mutations:

```ts
import { immer } from 'zustand/middleware/immer';

const useStore = create<TodoStore>()(
  immer((set) => ({
    todos: [],
    addTodo: (text) =>
      set((state) => {
        state.todos.push({ id: Date.now().toString(), text });
      }),
  })),
);
```

## Combining Middlewares (Order Matters)

```ts
const useStore = create<MyStore>()(
  devtools(
    persist(
      (set) => ({
        /* state */
      }),
      { name: 'storage' },
    ),
    { name: 'MyStore' },
  ),
);
```

Outer middleware wraps inner. Devtools should be outermost for debugging visibility.

## Custom Middleware

```ts
const logger = (f, name) => (set, get, store) => {
  const loggedSet = (...a) => {
    set(...a);
    console.log(`[${name}]:`, get());
  };
  return f(loggedSet, get, store);
};
```

## TypeScript with Middleware

### With Devtools

```ts
const useStore = create<Store>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () =>
        set((state) => ({ count: state.count + 1 }), undefined, 'increment'),
    }),
    { name: 'Store' },
  ),
);
```

### Slices with Middleware Mutators

```ts
import { StateCreator } from 'zustand';

const createBearSlice: StateCreator<
  BearSlice & FishSlice,
  [['zustand/devtools', never]],
  [],
  BearSlice
> = (set) => ({
  bears: 0,
  addBear: () =>
    set((state) => ({ bears: state.bears + 1 }), undefined, 'bear/add'),
});
```

## Testing Zustand Stores

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { createCounterStore } from './counter-store';

describe('Counter Store', () => {
  let store;
  beforeEach(() => {
    store = createCounterStore();
  });

  it('increments count', () => {
    const { increment } = store.getState();
    increment();
    expect(store.getState().count).toBe(1);
  });
});
```
