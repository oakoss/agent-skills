---
title: Store Patterns and TypeScript
description: Basic store creation, TypeScript double-parentheses syntax, selectors, useShallow, derived values, async actions, reset with getInitialState, vanilla stores, and auto-generating selectors
tags:
  [
    store,
    TypeScript,
    selectors,
    useShallow,
    async,
    reset,
    vanilla,
    create,
    auto-selectors,
    getInitialState,
  ]
---

# Store Patterns and TypeScript

## Basic TypeScript Store

```ts
import { create } from 'zustand';

interface BearStore {
  bears: number;
  increase: (by: number) => void;
}

const useBearStore = create<BearStore>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}));

// In components - only re-renders when bears changes
const bears = useBearStore((state) => state.bears);
const increase = useBearStore((state) => state.increase);
```

## The Double-Parentheses Rule

```ts
// Bad - breaks middleware type inference
const useStore = create<MyStore>((set) => ({
  /* ... */
}));

// Good - always use double parentheses
const useStore = create<MyStore>()((set) => ({
  /* ... */
}));
```

The currying syntax `create<T>()()` enables middleware type inference in TypeScript. Always use it even without middleware for future-proofing.

## Store Interface Pattern

Separate state from actions for clarity:

```ts
interface BearState {
  bears: number;
}

interface BearActions {
  increase: (by: number) => void;
  decrease: (by: number) => void;
}

type BearStore = BearState & BearActions;

const useBearStore = create<BearStore>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
  decrease: (by) => set((state) => ({ bears: state.bears - by })),
}));
```

## Selectors

### Atomic Selectors (Preferred)

```ts
const bears = useStore((state) => state.bears);
const increase = useStore((state) => state.increase);
```

### Multiple Values with useShallow

```ts
// Bad - new object every render, causes infinite re-renders in v5
const { bears, fishes } = useStore((state) => ({
  bears: state.bears,
  fishes: state.fishes,
}));

// Good - separate selectors
const bears = useStore((state) => state.bears);
const fishes = useStore((state) => state.fishes);

// Good - useShallow for multiple values
import { useShallow } from 'zustand/react/shallow';

const { bears, fishes } = useStore(
  useShallow((state) => ({ bears: state.bears, fishes: state.fishes })),
);
```

`useShallow` performs shallow comparison on the selector output, preventing re-renders when the selected values have not changed.

### Computed/Derived Selectors

```ts
const count = useStore((state) => state.items.length);

// Parameterized selector
const selectById = (id: string) => (state: Store) =>
  state.items.find((item) => item.id === id);

const item = useStore(selectById('123'));
```

## Async Actions

```ts
const useAsyncStore = create<AsyncStore>()((set) => ({
  data: null,
  isLoading: false,
  fetchData: async () => {
    set({ isLoading: true });
    const response = await fetch('/api/data');
    set({ data: await response.text(), isLoading: false });
  },
}));
```

## Reset Store with getInitialState

Use `store.getInitialState()` which Zustand provides automatically:

```ts
const useStore = create<State & Actions>()((set, get, store) => ({
  count: 0,
  name: '',
  reset: () => {
    set(store.getInitialState());
  },
}));
```

## Vanilla Store (Without React)

```ts
import { createStore } from 'zustand/vanilla';

const store = createStore<CounterStore>()((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
}));

const unsubscribe = store.subscribe((state) => console.log(state.count));
store.getState().increment();
```

## Custom Hook with Types

```ts
import { createStore, useStore } from 'zustand';

const bearStore = createStore<BearStore>()((set) => ({
  bears: 0,
  increase: () => set((state) => ({ bears: state.bears + 1 })),
}));

function useBearStore<T>(selector: (state: BearStore) => T): T {
  return useStore(bearStore, selector);
}
```

## Auto-Generating Selectors

Create typed `store.use.field()` hooks automatically instead of writing selectors manually:

```ts
import { type StoreApi, useStore, createStore } from 'zustand';

type WithSelectors<S> = S extends { getState: () => infer T }
  ? S & { use: { [K in keyof T]: () => T[K] } }
  : never;

const createSelectors = <S extends StoreApi<object>>(_store: S) => {
  const store = _store as WithSelectors<typeof _store>;
  store.use = {} as any;
  for (const k of Object.keys(store.getState())) {
    (store.use as any)[k] = () =>
      useStore(_store, (s) => s[k as keyof typeof s]);
  }
  return store;
};

interface BearState {
  bears: number;
  increase: (by: number) => void;
  increment: () => void;
}

const store = createStore<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
  increment: () => set((state) => ({ bears: state.bears + 1 })),
}));

const useBearStore = createSelectors(store);

// Usage - no manual selector needed
const bears = useBearStore.use.bears();
const increment = useBearStore.use.increment();
```

## Direct State Mutation Anti-Pattern

```ts
// Bad
set((state) => {
  state.count++;
  return state;
});

// Good - immutable update
set((state) => ({ count: state.count + 1 }));

// Good - use immer middleware for complex nested state
```
