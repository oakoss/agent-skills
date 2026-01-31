---
title: Middleware
description: Persist, devtools, immer, subscribeWithSelector middleware configuration, combining middlewares, custom middleware, custom storage, and TypeScript patterns
tags:
  [
    middleware,
    persist,
    devtools,
    immer,
    subscribeWithSelector,
    custom,
    combine,
    localStorage,
    createJSONStorage,
    superjson,
  ]
---

# Middleware

## Persist Middleware

```ts
import { create } from 'zustand';
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
      if (version === 0) {
        persistedState.position = { x: persistedState.x, y: persistedState.y };
        delete persistedState.x;
        delete persistedState.y;
      }
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

### Custom Storage with Superjson

For complex types like `Map`, `Set`, `Date`, and `RegExp`:

```ts
import superjson from 'superjson';
import { type PersistStorage } from 'zustand/middleware';

interface AppState {
  cache: Map<string, string>;
  tags: Set<string>;
  lastUpdated: Date;
}

const storage: PersistStorage<AppState> = {
  getItem: (name) => {
    const str = localStorage.getItem(name);
    if (!str) return null;
    return superjson.parse(str);
  },
  setItem: (name, value) => {
    localStorage.setItem(name, superjson.stringify(value));
  },
  removeItem: (name) => localStorage.removeItem(name),
};

const useStore = create<AppState>()(
  persist(
    (set) => ({
      cache: new Map(),
      tags: new Set(),
      lastUpdated: new Date(),
    }),
    { name: 'app-storage', storage },
  ),
);
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

interface Todo {
  id: string;
  title: string;
  done: boolean;
}

type TodoStore = {
  todos: Record<string, Todo>;
  toggleTodo: (todoId: string) => void;
};

const useStore = create<TodoStore>()(
  immer((set) => ({
    todos: {},
    toggleTodo: (todoId) =>
      set((state) => {
        state.todos[todoId].done = !state.todos[todoId].done;
      }),
  })),
);
```

## SubscribeWithSelector Middleware

Subscribe to specific state slices outside React components:

```ts
import { createStore } from 'zustand/vanilla';
import { subscribeWithSelector } from 'zustand/middleware';

type PositionStore = {
  position: { x: number; y: number };
  setPosition: (pos: { x: number; y: number }) => void;
};

const store = createStore<PositionStore>()(
  subscribeWithSelector((set) => ({
    position: { x: 0, y: 0 },
    setPosition: (position) => set({ position }),
  })),
);

// Subscribe to a slice of state
store.subscribe(
  (state) => state.position,
  (position) => console.log('Position changed:', position),
);

// Subscribe to a nested value
store.subscribe(
  (state) => state.position.x,
  (x) => console.log('X changed:', x),
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
import { type StateCreator, type StoreMutatorIdentifier } from 'zustand';

type Logger = <
  T,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = [],
>(
  f: StateCreator<T, Mps, Mcs>,
  name?: string,
) => StateCreator<T, Mps, Mcs>;

const logger: Logger = (f, name) => (set, get, store) => {
  const loggedSet: typeof set = (...a) => {
    set(...a);
    console.log(`[${name ?? 'store'}]:`, get());
  };
  return f(loggedSet, get, store);
};
```

## TypeScript with Middleware

### Slices with Middleware Mutators

```ts
import { type StateCreator } from 'zustand';

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
