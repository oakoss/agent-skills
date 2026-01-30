---
title: WebSocket Integration
description: Event-based cache invalidation via WebSocket, direct cache updates for high-frequency data, and partial data patches
tags:
  [websocket, real-time, invalidation, cache-update, event-driven, onmessage]
---

# WebSocket Integration

## Event-Based Invalidation (Recommended)

```tsx
function useRealtimeSubscription() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/events');

    ws.onmessage = (event) => {
      const { entity, id } = JSON.parse(event.data);
      const queryKey = id ? [entity, id] : [entity];
      queryClient.invalidateQueries({ queryKey });
    };

    return () => ws.close();
  }, [queryClient]);
}
```

Only active queries refetch. Works with existing query setup. Minimal code changes.

## Direct Cache Updates

For high-frequency updates, modify cache directly:

```tsx
ws.onmessage = (event) => {
  const { entity, id, payload } = JSON.parse(event.data);

  queryClient.setQueriesData({ queryKey: [entity] }, (old: unknown) => {
    if (Array.isArray(old)) {
      return old.map((item) =>
        item.id === id ? { ...item, ...payload } : item,
      );
    }
    return old;
  });
};
```

## Configuration with WebSockets

Set high `staleTime` when WebSockets handle freshness:

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
  },
});
```
