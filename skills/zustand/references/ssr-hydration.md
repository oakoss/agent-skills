---
title: SSR and Hydration
description: Next.js provider pattern, per-request stores, persist hydration handling, skipHydration, and onRehydrateStorage
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

import { createContext, useContext, useRef } from 'react';
import { useStore } from 'zustand';
import { createCounterStore, type CounterStore } from '@/stores/counter-store';

export const CounterStoreContext = createContext<CounterStore | null>(null);

export const CounterStoreProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const storeRef = useRef<CounterStore>();
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
  return create<CounterStore>()((set) => ({
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
  const storeRef = useRef<CounterStore>();
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

### Persist Race Condition (v5.0.9 and earlier)

**Fix**: Upgrade to zustand v5.0.10+. No code changes needed.

### Experimental SSR Safe Middleware

`unstable_ssrSafe` middleware is available in v5.0.9+ but experimental. Continue using the `_hasHydrated` pattern until API stabilizes.

## Key Rules

- Never read Zustand stores in React Server Components
- Pass data via props from Server to Client components
- Use `createStore` (not `create`) with the provider pattern
- Each SSR request must get its own store instance
