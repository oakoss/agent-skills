---
title: Slices Pattern
description: Splitting stores into functional modules with StateCreator, combining slices, shared slices, cross-slice access, and TypeScript patterns
tags:
  [
    slices,
    StateCreator,
    combine,
    cross-slice,
    shared-slice,
    architecture,
    domain,
  ]
---

# Slices Pattern

For large applications, a single store file becomes unmaintainable. The Slices Pattern splits your store into functional modules while maintaining a single cohesive state tree.

## Defining Slices

A slice is a function that returns a part of the state and actions:

```ts
// src/stores/slices/user-slice.ts
import { type StateCreator } from 'zustand';

export interface UserSlice {
  name: string;
  setName: (name: string) => void;
}

export const createUserSlice: StateCreator<
  UserSlice & AuthSlice,
  [],
  [],
  UserSlice
> = (set) => ({
  name: '',
  setName: (name) => set({ name }),
});
```

The `StateCreator` type parameters:

1. **Combined store type** (all slices)
2. **Middleware mutators** (empty if none)
3. **Chained middleware** (empty if none)
4. **This slice type**

## Combining Slices

```ts
// src/stores/root-store.ts
import { create } from 'zustand';
import { createUserSlice, type UserSlice } from './slices/user-slice';
import { createAuthSlice, type AuthSlice } from './slices/auth-slice';

export type RootStore = UserSlice & AuthSlice;

export const useStore = create<RootStore>()((...a) => ({
  ...createUserSlice(...a),
  ...createAuthSlice(...a),
}));
```

## Cross-Slice Access

Because all slices share the same `set` and `get`, you can interact with other slices:

```ts
export interface AuthSlice {
  isLoggedIn: boolean;
  login: () => void;
}

export const createAuthSlice: StateCreator<UserSlice & AuthSlice> = (
  set,
  get,
) => ({
  isLoggedIn: false,
  login: () => {
    set({ isLoggedIn: true });
    console.log(`User ${get().name} logged in`);
  },
});
```

## Shared Slices

Create slices that compose actions from other slices:

```ts
import { create, type StateCreator } from 'zustand';

interface BearSlice {
  bears: number;
  addBear: () => void;
  eatFish: () => void;
}

interface FishSlice {
  fishes: number;
  addFish: () => void;
}

interface SharedSlice {
  addBoth: () => void;
  getBoth: () => number;
}

const createBearSlice: StateCreator<
  BearSlice & FishSlice,
  [],
  [],
  BearSlice
> = (set) => ({
  bears: 0,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
  eatFish: () => set((state) => ({ fishes: state.fishes - 1 })),
});

const createFishSlice: StateCreator<
  BearSlice & FishSlice,
  [],
  [],
  FishSlice
> = (set) => ({
  fishes: 0,
  addFish: () => set((state) => ({ fishes: state.fishes + 1 })),
});

const createSharedSlice: StateCreator<
  BearSlice & FishSlice,
  [],
  [],
  SharedSlice
> = (_set, get) => ({
  addBoth: () => {
    get().addBear();
    get().addFish();
  },
  getBoth: () => get().bears + get().fishes,
});

const useBoundStore = create<BearSlice & FishSlice & SharedSlice>()((...a) => ({
  ...createBearSlice(...a),
  ...createFishSlice(...a),
  ...createSharedSlice(...a),
}));
```

## Slices with Middleware

When using middleware, add mutators to StateCreator:

```ts
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

## Circular Reference Fix

Define combined type first, then reference in slices:

```ts
type AllSlices = BearSlice & FishSlice & SharedSlice;

const createBearSlice: StateCreator<AllSlices, [], [], BearSlice> = (set) => ({
  bears: 0,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
});
```

## Best Practices

- **Atomic Actions**: Keep actions close to the data they modify
- **Type Safety**: Use `StateCreator` type to ensure slices access the combined store type
- **Avoid Duplication**: Do not repeat state keys across slices
- **File Organization**: One slice per file in `stores/slices/`
- **Naming**: Name slices by domain (user, auth, cart), not by feature
- **Shared Slices**: Use a shared slice for cross-cutting actions that coordinate between domains
