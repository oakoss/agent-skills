---
title: Migration Guide
description: Migrating from Redux, Context API, or Zustand v4 to v5 with code mappings and checklists
tags: [migration, redux, context, v4, v5, breaking-changes, upgrade]
---

# Migration Guide

## From Redux to Zustand

### Before (Redux)

```ts
// Action types, actions, reducer, store, provider, useSelector, useDispatch
const INCREMENT = 'INCREMENT';
const increment = () => ({ type: INCREMENT });

const reducer = (state = { count: 0 }, action) => {
  switch (action.type) {
    case INCREMENT:
      return { count: state.count + 1 };
    default:
      return state;
  }
};

const store = createStore(reducer);

// Component
const count = useSelector((state) => state.count);
const dispatch = useDispatch();
```

### After (Zustand)

```ts
import { create } from 'zustand';

interface Store {
  count: number;
  increment: () => void;
}

const useStore = create<Store>()((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

// Component - no provider needed!
const count = useStore((state) => state.count);
const increment = useStore((state) => state.increment);
```

**Benefits**: ~90% less boilerplate, no provider wrapper, no action types/creators, built-in TypeScript.

### Redux to Zustand Mapping

| Redux         | Zustand                          |
| ------------- | -------------------------------- |
| Actions       | Direct functions in store        |
| Action types  | Not needed                       |
| Reducers      | Inline in `set()` calls          |
| `useSelector` | Direct store selectors           |
| `useDispatch` | Direct function calls            |
| Provider      | Not needed                       |
| Middleware    | Built-in (`persist`, `devtools`) |
| DevTools      | `devtools` middleware            |

## From Context API to Zustand

### Before (Context)

```ts
const CountContext = createContext(null);

function CountProvider({ children }) {
  const [count, setCount] = useState(0);
  return (
    <CountContext.Provider value={{ count, increment: () => setCount((c) => c + 1) }}>
      {children}
    </CountContext.Provider>
  );
}

function useCount() {
  const context = useContext(CountContext);
  if (!context) throw new Error('useCount must be within CountProvider');
  return context;
}
```

### After (Zustand)

```ts
const useStore = create<Store>()((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

// No provider, no context null checks
const count = useStore((state) => state.count);
```

**Benefits**: No provider, no null checks, better performance (no context re-renders).

## From Zustand v4 to v5

### Breaking Changes

#### 1. TypeScript Double Parentheses

```ts
// v4
const useStore = create<Store>((set) => ({
  /* ... */
}));

// v5 - double parentheses required
const useStore = create<Store>()((set) => ({
  /* ... */
}));
```

#### 2. Persist Middleware

```ts
// v4
import { persist } from 'zustand/middleware';
const useStore = create(
  persist(
    (set) => ({
      /* ... */
    }),
    { name: 'storage' },
  ),
);

// v5 - explicit createJSONStorage
import { persist, createJSONStorage } from 'zustand/middleware';
const useStore = create<Store>()(
  persist(
    (set) => ({
      /* ... */
    }),
    {
      name: 'storage',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
```

#### 3. useShallow Import Path

```ts
// v4
import shallow from 'zustand/shallow';

// v5 - shallow comparison function (named export)
import { shallow } from 'zustand/shallow';

// v5 - useShallow hook (different import path)
import { useShallow } from 'zustand/react/shallow';
```

Note: `zustand/shallow` exports the plain `shallow` comparison function. The `useShallow` React hook is at `zustand/react/shallow`.

#### 4. Devtools Import Path

In v5, devtools is exported from `'zustand/middleware'` (not `'zustand/middleware/devtools'`).

#### 5. Immer Import

```ts
import { immer } from 'zustand/middleware/immer';
```

## Zustand v5 Key Changes

1. **Native `useSyncExternalStore`**: Full concurrent rendering support, zero tearing
2. **Smaller bundle**: Dropped legacy support
3. **Improved TypeScript**: Native support for combined stores and middleware
4. **Context-Store pattern**: Official SSR standard to prevent data leakage
5. **Manual rehydration control**: `skipHydration: true` for fine-grained persist timing
6. **`getInitialState()`**: Stores expose initial state for reliable resets

## Migration Strategies

### Gradual Migration (Recommended for Large Apps)

1. Install Zustand alongside existing solution
2. Migrate one feature at a time
3. Test thoroughly before moving to next
4. Remove old code once stable

### Migration Checklist

- Installed Zustand v5+
- Created store with `create<T>()()`
- Removed Context providers (if migrating from Context)
- Removed Redux boilerplate (if migrating from Redux)
- Updated all `useSelector` to Zustand selectors
- Updated all `useDispatch` to direct function calls
- Updated `useShallow` imports to `zustand/react/shallow`
- Added `persist` if state needs persistence
- Added `devtools` if using Redux DevTools
- Tested all components
- Verified no hydration errors (Next.js)
- Removed old state management code
