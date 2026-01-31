---
title: SSR and Hydration
description: Next.js provider pattern, per-request stores, persist hydration handling, skipHydration, onRehydrateStorage, and scoped stores with Context
tags:
  [
    SSR,
    Next.js,
    hydration,
    provider,
    context,
    createStore,
    skipHydration,
    useRef,
    scoped,
  ]
---

# SSR and Hydration

## The Problem

In SSR, creating a store as a global singleton is dangerous because it persists in memory across multiple requests, leading to data leakage between users.

## Provider Pattern (Ref-based)

Create a store instance per request and share via React Context:

```tsx
// src/providers/store-provider.tsx
'use client';

import { createContext, useContext, useRef, type ReactNode } from 'react';
import { useStore } from 'zustand';
import { createCounterStore, type CounterStore } from '@/stores/counter-store';

export const CounterStoreContext = createContext<CounterStore | null>(null);

export const CounterStoreProvider = ({ children }: { children: ReactNode }) => {
  const storeRef = useRef<CounterStore>(undefined);
  if (!storeRef.current) {
    storeRef.current = createCounterStore();
  }

  return (
    <CounterStoreContext.Provider value={storeRef.current}>
      {children}
    </CounterStoreContext.Provider>
  );
};

export const useCounterStore = <T,>(
  selector: (store: CounterStore) => T,
): T => {
  const counterStoreContext = useContext(CounterStoreContext);

  if (!counterStoreContext) {
    throw new Error(`useCounterStore must be used within CounterStoreProvider`);
  }

  return useStore(counterStoreContext, selector);
};
```

### Why useRef?

`useRef` prevents the store from being re-created if the Provider re-renders. This is crucial for state stability on the client.

## Initializing State from Server Props

Pass initial data from a Server Component to the store via the Provider:

```tsx
export const createCounterStore = (initState: Partial<CounterState> = {}) => {
  return createStore<CounterStore>()((set) => ({
    count: 0,
    ...initState,
    increment: () => set((state) => ({ count: state.count + 1 })),
  }));
};

export const CounterStoreProvider = ({
  children,
  initialCount,
}: {
  children: React.ReactNode;
  initialCount: number;
}) => {
  const storeRef = useRef<CounterStore>(undefined);
  if (!storeRef.current) {
    storeRef.current = createCounterStore({ count: initialCount });
  }
  return (
    <CounterStoreContext.Provider value={storeRef.current}>
      {children}
    </CounterStoreContext.Provider>
  );
};
```

## Scoped Stores with Dynamic Keys

For multi-instance scenarios (tabs, panels), use a Map to hold store instances:

```tsx
'use client';

import {
  type ReactNode,
  useState,
  useCallback,
  useContext,
  createContext,
} from 'react';
import { createStore, useStore } from 'zustand';

const StoresContext = createContext<Map<
  string,
  ReturnType<typeof createCounterStore>
> | null>(null);

export const StoresProvider = ({ children }: { children: ReactNode }) => {
  const [stores] = useState(
    () => new Map<string, ReturnType<typeof createCounterStore>>(),
  );

  return (
    <StoresContext.Provider value={stores}>{children}</StoresContext.Provider>
  );
};

export const useScopedStore = <T,>(
  key: string,
  selector: (state: CounterState) => T,
): T => {
  const stores = useContext(StoresContext);
  if (!stores) {
    throw new Error('useScopedStore must be used within StoresProvider');
  }

  const getOrCreate = useCallback(() => {
    if (!stores.has(key)) {
      stores.set(key, createCounterStore());
    }
    return stores.get(key)!;
  }, [stores, key]);

  return useStore(getOrCreate(), selector);
};
```

## Persist Hydration in Next.js

Because `localStorage` only exists on the client, the server renders with initial state while the client renders with persisted state, causing a hydration mismatch.

### Fix: \_hasHydrated Flag

```ts
interface StoreWithHydration {
  count: number;
  _hasHydrated: boolean;
  setHasHydrated: (hydrated: boolean) => void;
}

const useStore = create<StoreWithHydration>()(
  persist(
    (set) => ({
      count: 0,
      _hasHydrated: false,
      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
    }),
    {
      name: 'my-store',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    },
  ),
);

// In component - render fallback until hydrated
function MyComponent() {
  const hasHydrated = useStore((state) => state._hasHydrated);
  if (!hasHydrated) return <div>Loading...</div>;
  return <ActualContent />;
}
```

### Fix: skipHydration

Manually trigger hydration in a `useEffect`:

```ts
const useStore = create<MyStore>()(
  persist(
    (set) => ({
      /* ... */
    }),
    {
      name: 'app-storage',
      skipHydration: true,
    },
  ),
);

// In client component
import { useEffect } from 'react';

export function MyComponent() {
  useEffect(() => {
    useStore.persist.rehydrate();
  }, []);
  // ...
}
```

## Troubleshooting

### Hydration Mismatch

**Error**: `"Text content does not match server-rendered HTML"`

**Cause**: Persist middleware reads localStorage on client but not server.

**Fix**: Use `_hasHydrated` flag with `onRehydrateStorage` or `skipHydration`.

### Persist Import Error

**Error**: `"'createJSONStorage' is not exported from 'zustand/middleware'"`

**Fix**: Ensure zustand v5+ and correct import:

```ts
import { persist, createJSONStorage } from 'zustand/middleware';
```

## Key Rules

- Never read Zustand stores in React Server Components
- Pass data via props from Server to Client components
- Use `createStore` (not `create`) with the provider pattern
- Each SSR request must get its own store instance
- Use `useRef` (not `useState`) to hold the store reference in providers
