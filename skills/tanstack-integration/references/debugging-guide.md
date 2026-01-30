---
title: Debugging Guide
description: DevTools setup, performance profiling, memory leak detection, network debugging, state debugging, and common error patterns
tags: [devtools, profiler, memory-leak, network, error-boundary, sentry, msw]
---

# Debugging Guide

## DevTools Setup

### Essential DevTools Extensions

```bash
pnpm add -D @tanstack/react-query-devtools @tanstack/router-devtools
```

```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <>
          <ReactQueryDevtools initialIsOpen={false} />
          <TanStackRouterDevtools position="bottom-right" />
        </>
      )}
    </QueryClientProvider>
  );
}
```

### React DevTools Profiler Setup

```tsx
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  _baseDuration: number,
  _startTime: number,
  _commitTime: number,
) {
  if (actualDuration > 16) {
    console.warn(`Slow render: ${id} took ${actualDuration}ms`);
  }
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}
```

## Performance Profiling

### Identify Unnecessary Re-renders

```ts
function useWhyDidYouUpdate(name: string, props: Record<string, unknown>) {
  const previousProps = useRef<Record<string, unknown>>();

  useEffect(() => {
    if (previousProps.current) {
      const allKeys = Object.keys({ ...previousProps.current, ...props });
      const changedProps: Record<string, unknown> = {};

      allKeys.forEach((key) => {
        if (previousProps.current![key] !== props[key]) {
          changedProps[key] = {
            from: previousProps.current![key],
            to: props[key],
          };
        }
      });

      if (Object.keys(changedProps).length) {
        console.log('[why-did-you-update]', name, changedProps);
      }
    }

    previousProps.current = props;
  });
}
```

### React DevTools Highlight Updates

1. Open React DevTools
2. Settings (gear icon) -> "Highlight updates when components render"
3. Interact with app -> highlight color indicates re-render

### Transition for Heavy Operations

```ts
import { startTransition } from 'react';

function handleHeavyOperation() {
  startTransition(() => {
    setLargeList(computeExpensiveList());
  });
}
```

## Memory Leak Detection

### Common Leak Patterns

```tsx
// LEAK: Unsubscribed event listener
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);

// LEAK: Subscription without unsubscribe
useEffect(() => {
  const subscription = eventEmitter.subscribe(handler);
  return () => subscription.unsubscribe();
}, []);

// LEAK: setInterval without clear
useEffect(() => {
  const intervalId = setInterval(() => {
    fetchData();
  }, 5000);
  return () => clearInterval(intervalId);
}, []);

// LEAK: State update after unmount (use TanStack Query instead)
const { data } = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
});
```

### Heap Snapshot Analysis

1. Chrome DevTools -> Memory tab
2. Take heap snapshot
3. Interact with app (navigate, open modals, etc)
4. Take another snapshot
5. Compare snapshots -> find objects that are not garbage collected

### Detect Leaks with Query Devtools

```ts
const queryClient = useQueryClient();
console.log('Cache size:', queryClient.getQueryCache().getAll().length);
```

## Network Debugging

### Request Interceptor for Debug

```ts
import ky from 'ky';

export const api = ky.create({
  prefixUrl: '/api',
  hooks: {
    beforeRequest: [
      (request) => {
        if (process.env.NODE_ENV === 'development') {
          console.group(`${request.method} ${request.url}`);
          console.log('Headers:', Object.fromEntries(request.headers));
          console.groupEnd();
        }
      },
    ],
    afterResponse: [
      (_request, _options, response) => {
        if (process.env.NODE_ENV === 'development') {
          console.group(`${response.status} ${response.url}`);
          console.log('Status:', response.status);
          console.groupEnd();
        }
      },
    ],
  },
});
```

### Mock Service Worker for Debug

```ts
import { http, HttpResponse, delay } from 'msw';

export const handlers = [
  http.get('/api/users', async () => {
    await delay(2000);
    return HttpResponse.json([]);
  }),

  http.post('/api/users', () => {
    return HttpResponse.json({ message: 'Server error' }, { status: 500 });
  }),
];
```

## State Debugging

### Query State Inspector

```tsx
function QueryDebugger() {
  const queryClient = useQueryClient();
  const queries = queryClient.getQueryCache().getAll();

  return (
    <div className="fixed bottom-0 left-0 bg-black p-4 text-xs text-white">
      <h3>Query Cache ({queries.length} queries)</h3>
      {queries.map((query) => (
        <div key={query.queryHash}>
          <strong>{JSON.stringify(query.queryKey)}</strong>
          <span className="ml-2">{query.state.status}</span>
          <span className="ml-2 text-gray-400">
            {query.state.dataUpdatedAt
              ? `Updated ${new Date(query.state.dataUpdatedAt).toLocaleTimeString()}`
              : 'Never fetched'}
          </span>
        </div>
      ))}
    </div>
  );
}
```

### Zustand State Logger

```ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useStore = create(
  devtools(
    (set) => ({
      count: 0,
      increment: () =>
        set((state) => ({ count: state.count + 1 }), false, 'increment'),
    }),
    { name: 'MyStore' },
  ),
);
```

## Common Error Patterns

### Error Boundaries

```tsx
import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="error-fallback">
            <h2>Something went wrong</h2>
            <pre>{this.state.error?.message}</pre>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try again
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

### Debug Hydration Mismatches

```tsx
function FormattedDate({ date }: { date: Date }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <time dateTime={date.toISOString()}>Loading...</time>;
  }

  return <time dateTime={date.toISOString()}>{date.toLocaleDateString()}</time>;
}
```

### Production Error Tracking

```ts
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
})

export function App() {
  return (
    <Sentry.ErrorBoundary fallback={<ErrorPage />}>
      <Router />
    </Sentry.ErrorBoundary>
  )
}
```
