---
title: React Hooks and Integration
description: React hooks for debouncing, throttling, rate limiting, queuing, and batching with TanStack Pacer
tags:
  [
    react,
    hooks,
    useDebouncer,
    useThrottler,
    useRateLimiter,
    useQueuer,
    useDebouncedCallback,
    useAsyncQueuer,
    useAsyncDebouncedCallback,
    useAsyncThrottledCallback,
    canLeadingExecute,
  ]
---

# React Hooks and Integration

## Installation

```bash
npm install @tanstack/react-pacer
```

The React package re-exports everything from `@tanstack/pacer`, so no separate core install is needed.

## Hook Abstraction Levels

TanStack Pacer React hooks come in four abstraction levels for each utility:

| Level    | Pattern                | Example                   | Use Case                           |
| -------- | ---------------------- | ------------------------- | ---------------------------------- |
| Instance | `useDebouncer`         | Full class access         | Complex control flow, cancel/flush |
| Callback | `useDebouncedCallback` | Stable debounced function | Event handlers, simple callbacks   |
| State    | `useDebouncedState`    | Debounced React state     | Form inputs, controlled components |
| Value    | `useDebouncedValue`    | Derived debounced value   | Derived/computed values            |

## Debouncer Hooks

### useDebouncer

Full access to the Debouncer instance:

```tsx
import { useDebouncer } from '@tanstack/react-pacer';

function SearchComponent() {
  const debouncer = useDebouncer((query: string) => fetchSearchResults(query), {
    wait: 500,
  });

  return (
    <input
      onChange={(e) => debouncer.maybeExecute(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### useDebouncer with State Selector

Opt in to re-renders for specific state changes:

```tsx
const debouncer = useDebouncer(
  (query: string) => fetchSearchResults(query),
  { wait: 500 },
  (state) => ({ isPending: state.isPending }),
);

const { isPending } = debouncer.state;
```

### useDebouncedCallback

Returns a stable debounced function reference:

```tsx
import { useDebouncedCallback } from '@tanstack/react-pacer';

function SearchInput() {
  const handleSearch = useDebouncedCallback(
    (query: string) => fetchSearchResults(query),
    { wait: 500 },
  );

  return <input type="search" onChange={(e) => handleSearch(e.target.value)} />;
}
```

### useDebouncedState

Manages debounced React state directly:

```tsx
import { useDebouncedState } from '@tanstack/react-pacer';

function FilterForm() {
  const [filter, setFilter] = useDebouncedState('', { wait: 300 });

  return (
    <div>
      <input onChange={(e) => setFilter(e.target.value)} />
      <p>Debounced filter: {filter}</p>
    </div>
  );
}
```

### useDebouncedValue

Creates a debounced version of a value:

```tsx
import { useDebouncedValue } from '@tanstack/react-pacer';

function SearchResults({ query }: { query: string }) {
  const debouncedQuery = useDebouncedValue(query, { wait: 300 });

  return <Results query={debouncedQuery} />;
}
```

## Throttler Hooks

### useThrottler

```tsx
import { useThrottler } from '@tanstack/react-pacer';

function ScrollTracker() {
  const throttler = useThrottler(
    (position: number) => updateScrollPosition(position),
    { wait: 200, leading: true, trailing: true },
  );

  useEffect(() => {
    const handler = () => throttler.maybeExecute(window.scrollY);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, [throttler]);

  return null;
}
```

### useThrottledCallback

```tsx
import { useThrottledCallback } from '@tanstack/react-pacer';

function LivePreview() {
  const handleUpdate = useThrottledCallback(
    (content: string) => renderPreview(content),
    { wait: 200 },
  );

  return <textarea onChange={(e) => handleUpdate(e.target.value)} />;
}
```

### useThrottledValue

```tsx
import { useThrottledValue } from '@tanstack/react-pacer';

function MouseTracker({ position }: { position: { x: number; y: number } }) {
  const throttledPosition = useThrottledValue(position, { wait: 100 });

  return (
    <div>
      Position: {throttledPosition.x}, {throttledPosition.y}
    </div>
  );
}
```

## Rate Limiter Hooks

### useRateLimiter

```tsx
import { useRateLimiter } from '@tanstack/react-pacer';

function SubmitButton() {
  const limiter = useRateLimiter(
    () => submitForm(),
    {
      limit: 3,
      window: 60_000,
      onReject: () => showToast('Too many attempts'),
    },
    (state) => ({ executionCount: state.executionCount }),
  );

  return (
    <button onClick={() => limiter.maybeExecute()}>
      Submit ({limiter.state.executionCount}/3)
    </button>
  );
}
```

### useRateLimitedCallback

```tsx
import { useRateLimitedCallback } from '@tanstack/react-pacer';

function LikeButton() {
  const handleLike = useRateLimitedCallback(
    (postId: string) => likePost(postId),
    { limit: 5, window: 10_000 },
  );

  return <button onClick={() => handleLike(postId)}>Like</button>;
}
```

## Queuer Hooks

### useQueuer

```tsx
import { useQueuer } from '@tanstack/react-pacer';

function NotificationQueue() {
  const queuer = useQueuer<string>(
    (message) => showNotification(message),
    { wait: 2000 },
    (state) => ({ size: state.size }),
  );

  return (
    <div>
      <button onClick={() => queuer.addItem('New notification')}>
        Add ({queuer.state.size} pending)
      </button>
    </div>
  );
}
```

### useQueuedState

Combines queue with React state management. Takes a processing function, queue options, and an optional selector. Returns a tuple of `[items, addItem, queuerInstance]`:

```tsx
import { useQueuedState } from '@tanstack/react-pacer';

function TaskProcessor() {
  const [tasks, addTask] = useQueuedState<string>(
    (task) => console.log('Processing:', task),
    { wait: 500 },
  );

  return (
    <div>
      <button onClick={() => addTask('new-task')}>Add Task</button>
      <ul>
        {tasks.map((task, i) => (
          <li key={i}>{task}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Async Queuer Hooks

### useAsyncQueuer

```tsx
import { useAsyncQueuer } from '@tanstack/react-pacer';

function FileUploader() {
  const uploader = useAsyncQueuer<File>(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      await fetch('/api/upload', { method: 'POST', body: formData });
    },
    {
      concurrency: 3,
      onSuccess: (_result, file) => console.log(`Uploaded: ${file.name}`),
      onError: (error) => console.error('Upload failed:', error),
    },
    (state) => ({
      activeCount: state.activeCount,
      pendingCount: state.pendingCount,
    }),
  );

  return (
    <div>
      <input
        type="file"
        multiple
        onChange={(e) => {
          Array.from(e.target.files ?? []).forEach((f) => uploader.addItem(f));
        }}
      />
      <p>
        Active: {uploader.state.activeCount}, Pending:{' '}
        {uploader.state.pendingCount}
      </p>
    </div>
  );
}
```

## Async Callback Hooks

### useAsyncDebouncedCallback

Returns a stable debounced function for async operations. Simpler than `useAsyncDebouncer` but does not expose the underlying instance for manual cancellation or state access:

```tsx
import { useAsyncDebouncedCallback } from '@tanstack/react-pacer';

function EmailValidator() {
  const [result, setResult] = useState<string | null>(null);

  const validateEmail = useAsyncDebouncedCallback(
    async (email: string) => {
      const res = await fetch(`/api/validate-email?email=${email}`);
      const data = await res.json();
      setResult(data.isValid ? 'Valid' : 'Invalid');
    },
    { wait: 750 },
  );

  return <input type="email" onChange={(e) => validateEmail(e.target.value)} />;
}
```

### useAsyncThrottledCallback

Returns a stable throttled function for async operations:

```tsx
import { useAsyncThrottledCallback } from '@tanstack/react-pacer';

function AutoSave({ content }: { content: string }) {
  const saveContent = useAsyncThrottledCallback(
    async (text: string) => {
      await fetch('/api/save', {
        method: 'POST',
        body: JSON.stringify({ content: text }),
      });
    },
    { wait: 5000 },
  );

  useEffect(() => {
    saveContent(content);
  }, [content, saveContent]);

  return null;
}
```

## Async Variants

All instance-level hooks have async counterparts:

| Sync Hook        | Async Hook            |
| ---------------- | --------------------- |
| `useDebouncer`   | `useAsyncDebouncer`   |
| `useThrottler`   | `useAsyncThrottler`   |
| `useRateLimiter` | `useAsyncRateLimiter` |
| `useQueuer`      | `useAsyncQueuer`      |
| `useBatcher`     | `useAsyncBatcher`     |

Async hooks add `onSuccess` and `onError` callbacks and return Promises from `maybeExecute`.

Callback-level async hooks:

| Sync Hook                | Async Hook                    |
| ------------------------ | ----------------------------- |
| `useDebouncedCallback`   | `useAsyncDebouncedCallback`   |
| `useThrottledCallback`   | `useAsyncThrottledCallback`   |
| `useRateLimitedCallback` | `useAsyncRateLimitedCallback` |

## Selector Pattern

All instance hooks accept an optional third argument: a selector function that controls which state changes trigger re-renders:

```tsx
const debouncer = useDebouncer(fn, { wait: 500 }, (state) => ({
  isPending: state.isPending,
  executionCount: state.executionCount,
  canLeadingExecute: state.canLeadingExecute,
}));

debouncer.state.isPending;
debouncer.state.executionCount;
debouncer.state.canLeadingExecute;
```

Without a selector, no reactive state subscriptions are made, and the hook does not trigger re-renders on state changes.

### canLeadingExecute

The `canLeadingExecute` state property is available on debouncer, throttler, and their async variants. It indicates whether the next call to `maybeExecute` would trigger a leading-edge execution:

```tsx
const debouncer = useDebouncer(
  (query: string) => fetchResults(query),
  { wait: 500 },
  (state) => ({ canLeadingExecute: state.canLeadingExecute }),
);

return (
  <button
    disabled={!debouncer.state.canLeadingExecute}
    onClick={() => debouncer.maybeExecute('search')}
  >
    Search
  </button>
);
```

## Cleanup

React hooks automatically manage cleanup on unmount. For manual class instances used outside of hooks, call `cancel()` in cleanup:

```tsx
useEffect(() => {
  const debouncer = new Debouncer(handler, { wait: 300 });
  return () => debouncer.cancel();
}, []);
```
