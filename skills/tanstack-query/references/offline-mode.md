---
title: Offline Mode
description: Network mode configuration, mutation persistence across reloads, and offline-first data strategies
tags:
  [offline, networkMode, persistence, offlineFirst, mutation-defaults, resume]
---

# Offline Mode and Persistence

## Network Mode

Three `networkMode` settings:

| Mode               | Behavior                                               |
| ------------------ | ------------------------------------------------------ |
| `online` (default) | Queries pause when offline, resume when online         |
| `always`           | Queries always fire regardless of network              |
| `offlineFirst`     | First request always fires, retries pause when offline |

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { networkMode: 'offlineFirst' },
    mutations: { networkMode: 'offlineFirst' },
  },
});
```

## Mutation Persistence

Persist mutations across page reloads/app restarts:

```tsx
queryClient.setMutationDefaults(['addTodo'], {
  mutationFn: addTodo,
  onMutate: async (variables, context) => {
    await context.client.cancelQueries({ queryKey: ['todos'] });
    const previous = context.client.getQueryData(['todos']);
    context.client.setQueryData(['todos'], (old) => [...old, variables]);
    return { previous };
  },
  onError: (_error, _variables, result, context) => {
    context.client.setQueryData(['todos'], result?.previous);
  },
  retry: 3,
});

// Dehydrate state (e.g., on app background)
const state = dehydrate(queryClient);
localStorage.setItem('queryState', JSON.stringify(state));

// Hydrate on app start
const savedState = JSON.parse(localStorage.getItem('queryState'));
hydrate(queryClient, savedState);

// Resume paused mutations
queryClient.resumePausedMutations();
```

## Query Cache Persistence

Persist the entire query cache to storage for offline support and faster startup:

```tsx
import { QueryClient } from '@tanstack/react-query';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 hours - keep cache longer for persistence
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: 'REACT_QUERY_CACHE',
});

function App() {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{
        persister,
        maxAge: 1000 * 60 * 60 * 24, // 24 hours max
      }}
    >
      <MyApp />
    </PersistQueryClientProvider>
  );
}
```

## Async Persistence with IndexedDB

For larger caches, use IndexedDB instead of localStorage:

```tsx
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import { get, set, del } from 'idb-keyval';

const persister = createAsyncStoragePersister({
  storage: {
    getItem: async (key) => await get(key),
    setItem: async (key, value) => await set(key, value),
    removeItem: async (key) => await del(key),
  },
  key: 'REACT_QUERY_CACHE',
});
```

## Selective Persistence

Only persist certain queries:

```tsx
import { persistQueryClient } from '@tanstack/react-query-persist-client';

persistQueryClient({
  queryClient,
  persister,
  dehydrateOptions: {
    shouldDehydrateQuery: (query) => {
      if (query.queryKey[0] === 'user-session') return false;
      if (query.queryKey[0] === 'notifications') return false;
      if (query.state.status !== 'success') return false;
      return true;
    },
  },
});
```

## Persistence Configuration

| Option                                  | Purpose                                      |
| --------------------------------------- | -------------------------------------------- |
| `maxAge`                                | Maximum cache age before considered invalid  |
| `buster`                                | String to invalidate cache (use app version) |
| `dehydrateOptions.shouldDehydrateQuery` | Filter which queries to persist              |
| `hydrateOptions.shouldHydrate`          | Filter which queries to restore              |
