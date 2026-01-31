---
title: Testing Stores
description: Testing Zustand stores with Vitest and Jest, mock patterns, store isolation between tests, and resetting state
tags: [testing, vitest, jest, mock, reset, isolation, getInitialState]
---

# Testing Stores

## Testing with Vitest

Create a fresh store instance per test to prevent state leakage:

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { createStore } from 'zustand/vanilla';

interface CounterStore {
  count: number;
  increment: () => void;
}

function createCounterStore() {
  return createStore<CounterStore>()((set) => ({
    count: 0,
    increment: () => set((state) => ({ count: state.count + 1 })),
  }));
}

describe('Counter Store', () => {
  let store: ReturnType<typeof createCounterStore>;

  beforeEach(() => {
    store = createCounterStore();
  });

  it('starts at zero', () => {
    expect(store.getState().count).toBe(0);
  });

  it('increments count', () => {
    store.getState().increment();
    expect(store.getState().count).toBe(1);
  });

  it('increments multiple times', () => {
    store.getState().increment();
    store.getState().increment();
    expect(store.getState().count).toBe(2);
  });
});
```

## Jest Mock for Global Stores

When stores are defined as module-level singletons, mock Zustand to auto-reset after each test:

```ts
// __mocks__/zustand.ts
import { act } from '@testing-library/react';
import type * as ZustandExportedTypes from 'zustand';
export * from 'zustand';

const { create: actualCreate, createStore: actualCreateStore } =
  jest.requireActual<typeof ZustandExportedTypes>('zustand');

export const storeResetFns = new Set<() => void>();

const createUncurried = <T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  const store = actualCreate(stateCreator);
  const initialState = store.getInitialState();
  storeResetFns.add(() => {
    store.setState(initialState, true);
  });
  return store;
};

export const create = (<T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  return typeof stateCreator === 'function'
    ? createUncurried(stateCreator)
    : createUncurried;
}) as typeof ZustandExportedTypes.create;

const createStoreUncurried = <T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  const store = actualCreateStore(stateCreator);
  const initialState = store.getInitialState();
  storeResetFns.add(() => {
    store.setState(initialState, true);
  });
  return store;
};

export const createStore = (<T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  return typeof stateCreator === 'function'
    ? createStoreUncurried(stateCreator)
    : createStoreUncurried;
}) as typeof ZustandExportedTypes.createStore;

afterEach(() => {
  act(() => {
    storeResetFns.forEach((resetFn) => {
      resetFn();
    });
  });
});
```

Place this file at `__mocks__/zustand.ts` (or `.js`) in your project root. Jest will auto-discover it via module name mapping.

## Vitest Mock Equivalent

```ts
// __mocks__/zustand.ts
import { act } from '@testing-library/react';
import type * as ZustandExportedTypes from 'zustand';

const { create: actualCreate, createStore: actualCreateStore } =
  await vi.importActual<typeof ZustandExportedTypes>('zustand');

export * from 'zustand';

export const storeResetFns = new Set<() => void>();

const createUncurried = <T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  const store = actualCreate(stateCreator);
  const initialState = store.getInitialState();
  storeResetFns.add(() => {
    store.setState(initialState, true);
  });
  return store;
};

export const create = (<T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  return typeof stateCreator === 'function'
    ? createUncurried(stateCreator)
    : createUncurried;
}) as typeof ZustandExportedTypes.create;

const createStoreUncurried = <T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  const store = actualCreateStore(stateCreator);
  const initialState = store.getInitialState();
  storeResetFns.add(() => {
    store.setState(initialState, true);
  });
  return store;
};

export const createStore = (<T>(
  stateCreator: ZustandExportedTypes.StateCreator<T>,
) => {
  return typeof stateCreator === 'function'
    ? createStoreUncurried(stateCreator)
    : createStoreUncurried;
}) as typeof ZustandExportedTypes.createStore;

afterEach(() => {
  act(() => {
    storeResetFns.forEach((resetFn) => {
      resetFn();
    });
  });
});
```

For Vitest, configure the mock in `vitest.config.ts`:

```ts
export default defineConfig({
  test: {
    setupFiles: ['./setup-tests.ts'],
  },
});
```

## Testing Async Actions

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createStore } from 'zustand/vanilla';

interface AsyncStore {
  data: string | null;
  isLoading: boolean;
  fetchData: () => Promise<void>;
}

function createAsyncStore() {
  return createStore<AsyncStore>()((set) => ({
    data: null,
    isLoading: false,
    fetchData: async () => {
      set({ isLoading: true });
      const response = await fetch('/api/data');
      set({ data: await response.text(), isLoading: false });
    },
  }));
}

describe('Async Store', () => {
  let store: ReturnType<typeof createAsyncStore>;

  beforeEach(() => {
    store = createAsyncStore();
    vi.restoreAllMocks();
  });

  it('fetches data', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(new Response('test data'));

    await store.getState().fetchData();

    expect(store.getState().data).toBe('test data');
    expect(store.getState().isLoading).toBe(false);
  });

  it('sets loading state', async () => {
    vi.spyOn(global, 'fetch').mockImplementation(() => new Promise(() => {}));

    const promise = store.getState().fetchData();

    expect(store.getState().isLoading).toBe(true);
  });
});
```

## Testing with Subscribe

```ts
it('notifies subscribers on state change', () => {
  const store = createCounterStore();
  const listener = vi.fn();

  store.subscribe(listener);
  store.getState().increment();

  expect(listener).toHaveBeenCalledTimes(1);
  expect(listener).toHaveBeenCalledWith(
    expect.objectContaining({ count: 1 }),
    expect.objectContaining({ count: 0 }),
  );
});
```

## Resetting State in Tests

Use `getInitialState()` for reliable resets:

```ts
it('resets to initial state', () => {
  const store = createCounterStore();

  store.getState().increment();
  store.getState().increment();
  expect(store.getState().count).toBe(2);

  store.setState(store.getInitialState(), true);
  expect(store.getState().count).toBe(0);
});
```

The second argument `true` to `setState` replaces the state entirely instead of merging.
