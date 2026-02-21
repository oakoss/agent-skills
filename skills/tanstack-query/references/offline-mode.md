---
title: Offline Mode
description: Network mode configuration, fetchStatus vs status, mutation persistence across reloads, cache persistence with localStorage and IndexedDB
tags:
  [
    offline,
    networkMode,
    persistence,
    offlineFirst,
    mutation-defaults,
    resume,
    PersistQueryClientProvider,
  ]
---

# Offline Mode and Persistence

## Network Mode

Three `networkMode` settings control fetch behavior when offline:

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

`offlineFirst` is ideal for apps with service workers or local-first architectures where the first request may succeed from a local cache.

## fetchStatus vs status

Queries have two orthogonal status axes:

| Axis          | Values                        | Meaning                           |
| ------------- | ----------------------------- | --------------------------------- |
| `status`      | `pending`, `error`, `success` | Does the query have data?         |
| `fetchStatus` | `fetching`, `paused`, `idle`  | Is the queryFn currently running? |

Combined states:

| status    | fetchStatus | Meaning                                  |
| --------- | ----------- | ---------------------------------------- |
| `success` | `fetching`  | Has data, background refetch in progress |
| `success` | `idle`      | Has data, nothing happening              |
| `pending` | `fetching`  | No data yet, first fetch in progress     |
| `pending` | `paused`    | No data, fetch paused (offline)          |
| `error`   | `idle`      | Failed, not retrying                     |
| `error`   | `fetching`  | Failed previously, retrying now          |

Use `isPaused` to detect when a query is waiting for network:

```tsx
const { data, isPending, isPaused } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

if (isPaused) return <OfflineBanner />;
if (isPending) return <Spinner />;
```

`isPaused` is `true` when `fetchStatus === 'paused'`. This happens when a query wants to fetch but cannot because the device is offline (in `online` or `offlineFirst` network mode).

## Mutation Persistence

Persist mutations across page reloads so they resume when the app restarts:

```tsx
queryClient.setMutationDefaults(['addTodo'], {
  mutationFn: addTodo,
  onMutate: async (variables, context) => {
    await context.client.cancelQueries({ queryKey: ['todos'] });
    const previous = context.client.getQueryData(['todos']);
    context.client.setQueryData(['todos'], (old: Todo[]) => [
      ...old,
      variables,
    ]);
    return { previous };
  },
  onError: (_error, _variables, onMutateResult, context) => {
    if (onMutateResult?.previous) {
      context.client.setQueryData(['todos'], onMutateResult.previous);
    }
  },
  retry: 3,
});

const state = dehydrate(queryClient);
localStorage.setItem('queryState', JSON.stringify(state));

const savedState = JSON.parse(localStorage.getItem('queryState') ?? 'null');
if (savedState) {
  hydrate(queryClient, savedState);
}

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
      gcTime: 1000 * 60 * 60 * 24,
      staleTime: 1000 * 60 * 5,
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
        maxAge: 1000 * 60 * 60 * 24,
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

Use `buster` with your app version to automatically invalidate persisted caches after deployments:

```tsx
persistOptions={{
  persister,
  maxAge: 1000 * 60 * 60 * 24,
  buster: BUILD_VERSION,
}}
```
