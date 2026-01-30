---
title: Performance Optimization
description: Eliminating waterfalls, bundle size reduction, re-render optimization, and JavaScript micro-optimizations
tags:
  [
    performance,
    waterfalls,
    bundle,
    memoization,
    useMemo,
    useCallback,
    code-splitting,
  ]
---

# Performance Optimization

## Eliminating Waterfalls (CRITICAL)

### Parallel Execution

```tsx
// Bad: Sequential -- Total time = sum of all latencies
const user = await fetchUser(); // 200ms
const posts = await fetchPosts(user.id); // 200ms
const config = await fetchConfig(); // 150ms (waits for posts)
// Total: 550ms

// Good: Parallel -- Total time = max(independent) + dependent
const userPromise = fetchUser();
const configPromise = fetchConfig();
const user = await userPromise;
const posts = await fetchPosts(user.id);
const config = await configPromise;
// Total: 400ms
```

### Defer Await Until Needed

Move `await` into branches where the value is actually used:

```typescript
// Bad: blocks both branches
async function handleRequest(userId: string, skipProcessing: boolean) {
  const userData = await fetchUserData(userId);
  if (skipProcessing) return { skipped: true };
  return processUserData(userData);
}

// Good: only blocks when needed
async function handleRequest(userId: string, skipProcessing: boolean) {
  if (skipProcessing) return { skipped: true };
  const userData = await fetchUserData(userId);
  return processUserData(userData);
}
```

### Dependency-Based Parallelization

For partial dependencies, use `better-all` to maximize parallelism:

```typescript
import { all } from 'better-all';

const { user, config, profile } = await all({
  async user() {
    return fetchUser();
  },
  async config() {
    return fetchConfig();
  },
  async profile() {
    return fetchProfile((await this.$.user).id);
  },
});
```

### Suspense Boundaries

Stream content progressively instead of blocking the entire page:

```tsx
function Page() {
  return (
    <div>
      <div>Sidebar</div>
      <div>Header</div>
      <Suspense fallback={<Skeleton />}>
        <DataDisplay />
      </Suspense>
      <div>Footer</div>
    </div>
  );
}

async function DataDisplay() {
  const data = await fetchData();
  return <div>{data.content}</div>;
}
```

### cacheSignal (React 19.2+)

Abort expensive server work when client disconnects:

```typescript
import { cache, cacheSignal } from 'react';

export const getDeepAnalysis = cache(async (id: string) => {
  const signal = cacheSignal();
  const response = await fetch(`https://api.internal/analysis/${id}`, {
    signal,
    next: { revalidate: 3600 },
  });
  if (signal.aborted) return null;
  return response.json();
});
```

## Bundle Size (CRITICAL)

### Avoid Barrel File Imports

```tsx
// Bad: imports entire library (200-800ms import cost)
import { Check, X, Menu } from 'lucide-react';

// Good: imports only what you need
import Check from 'lucide-react/dist/esm/icons/check';
import X from 'lucide-react/dist/esm/icons/x';
import Menu from 'lucide-react/dist/esm/icons/menu';
```

Libraries commonly affected: `lucide-react`, `@mui/material`, `@tabler/icons-react`, `react-icons`, `lodash`, `date-fns`.

### Dynamic Imports for Heavy Components

```tsx
import { lazy, Suspense } from 'react';

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then((m) => ({ default: m.MonacoEditor })),
);

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <MonacoEditor value={code} />
    </Suspense>
  );
}
```

### Defer Non-Critical Third-Party Libraries

```tsx
import { useEffect, useState, lazy, Suspense } from 'react';

const Analytics = lazy(() =>
  import('@vercel/analytics/react').then((m) => ({ default: m.Analytics })),
);

export default function App({ children }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div>
      {children}
      {mounted ? (
        <Suspense fallback={null}>
          <Analytics />
        </Suspense>
      ) : null}
    </div>
  );
}
```

### Preload on Intent

```tsx
function EditorButton({ onClick }: { onClick: () => void }) {
  const preload = () => {
    if (typeof window !== 'undefined') {
      void import('./monaco-editor');
    }
  };
  return (
    <button onMouseEnter={preload} onFocus={preload} onClick={onClick}>
      Open Editor
    </button>
  );
}
```

## Re-render Optimization (MEDIUM)

### React Compiler (Forget)

Automatic memoization for code following Rules of React. Check for "Memo" badge in React DevTools. Requirements: pure render functions, no side effects, treat props/state as immutable.

### useMemo Targeting

```tsx
// Skip -- cheap operation, memo overhead exceeds recomputation
const doubled = useMemo(() => value * 2, [value]);

// Use -- expensive computation (sorting, filtering large lists)
const sortedItems = useMemo(
  () => items.toSorted((a, b) => a.price - b.price),
  [items],
);

// Use -- O(1) lookup structure from array
const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);
```

### useCallback Targeting

```tsx
// Skip -- no memoized consumer, useCallback adds overhead
const handleClick = useCallback(() => doSomething(), []);
return <button onClick={handleClick}>Click</button>;

// Use -- prevents re-render of memoized child
const handleClick = useCallback(() => doSomething(id), [id]);
return <MemoizedChild onClick={handleClick} />;
```

### Stable Object References

```tsx
// Bad -- object literal creates new reference every render
<Child style={{ color: 'red' }} />;

// Good -- define outside component if static
const style = { color: 'red' };
function Parent() {
  return <Child style={style} />;
}
```

### Additional Techniques

- **Defer state reads** -- don't subscribe to state only used in callbacks
- **Primitive effect dependencies** -- use primitives, not objects
- **Hoist default props** -- non-primitive defaults outside component
- **`startTransition`** -- mark non-urgent updates as transitions
- **Move effects to events** -- interaction logic belongs in event handlers

## Rendering (MEDIUM)

- **`<Activity>` component** (React 19.2+) -- show/hide with preserved state
- **CSS `content-visibility`** -- skip rendering for off-screen content
- **Hoist static JSX** -- extract constant JSX outside component functions
- **Hydration mismatch prevention** -- use inline scripts for client-only data
- **Ternary conditionals** -- prefer `condition ? <A /> : null` over `condition && <A />`

## JavaScript Micro-Optimizations (LOW-MEDIUM)

- Batch DOM/CSS changes via classes or `cssText`
- Build `Map`/`Set` for repeated lookups (O(1) vs O(n))
- Cache property access and function results in loops
- Combine multiple `filter`/`map` into single iterations
- Use `toSorted()` for immutable sorting
