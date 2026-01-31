---
title: WebSocket Integration
description: Event-based cache invalidation via WebSocket, direct cache updates for high-frequency data, partial data patches, and configuration
tags:
  [
    websocket,
    real-time,
    invalidation,
    cache-update,
    event-driven,
    refetchInterval,
  ]
---

# WebSocket Integration

## Strategy Selection

| Approach                 | Best For                            | Complexity |
| ------------------------ | ----------------------------------- | ---------- |
| Event-based invalidation | Most apps, low-frequency updates    | Low        |
| Direct cache updates     | High-frequency data (stock tickers) | Medium     |
| Polling                  | Simple real-time without WebSocket  | Low        |

## Event-Based Invalidation (Recommended)

Let React Query handle the refetch. WebSocket only signals staleness:

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

For high-frequency updates where refetching is too expensive, modify cache directly:

```tsx
function useRealtimeUpdates() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/stream');

    ws.onmessage = (event) => {
      const { entity, id, payload } = JSON.parse(event.data);

      queryClient.setQueryData([entity, id], (old: unknown) => {
        if (!old) return old;
        return { ...old, ...payload };
      });

      queryClient.setQueriesData({ queryKey: [entity] }, (old: unknown) => {
        if (!Array.isArray(old)) return old;
        return old.map((item) =>
          item.id === id ? { ...item, ...payload } : item,
        );
      });
    };

    return () => ws.close();
  }, [queryClient]);
}
```

`setQueriesData` updates all matching queries (fuzzy match). Use it to update both list and detail caches simultaneously.

## Polling as Alternative

For simpler setups, use `refetchInterval` instead of WebSockets:

```tsx
const { data } = useQuery({
  queryKey: ['notifications'],
  queryFn: fetchNotifications,
  refetchInterval: 1000 * 30,
  refetchIntervalInBackground: false,
});

const { data: jobStatus } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => getJobStatus(jobId),
  refetchInterval: (query) => {
    return query.state.data?.status === 'completed' ? false : 1000;
  },
});
```

Conditional polling stops once a condition is met, reducing unnecessary requests.

## Configuration for WebSocket-Driven Apps

When WebSockets handle freshness, disable automatic refetching:

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

This prevents React Query from refetching on its own, relying entirely on WebSocket events to trigger cache updates or invalidation.

## Reconnection Handling

Invalidate stale data when reconnecting after a disconnect:

```tsx
function useRealtimeSubscription() {
  const queryClient = useQueryClient();

  useEffect(() => {
    let ws: WebSocket;

    function connect() {
      ws = new WebSocket('wss://api.example.com/events');

      ws.onopen = () => {
        queryClient.invalidateQueries();
      };

      ws.onmessage = (event) => {
        const { entity, id } = JSON.parse(event.data);
        queryClient.invalidateQueries({
          queryKey: id ? [entity, id] : [entity],
        });
      };

      ws.onclose = () => {
        setTimeout(connect, 3000);
      };
    }

    connect();
    return () => ws?.close();
  }, [queryClient]);
}
```

Invalidating all queries on reconnect ensures no data went stale during the disconnect window.
