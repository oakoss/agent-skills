---
title: Anti-Patterns and Troubleshooting
description: Common React anti-patterns across data fetching, state, components, performance, and troubleshooting solutions
tags:
  [
    anti-patterns,
    troubleshooting,
    hydration,
    stale-closures,
    re-renders,
    bundle-size,
  ]
---

# Anti-Patterns and Troubleshooting

## Data Fetching Anti-Patterns

- Fetching in `useEffect` with `useState` -- use `use()` or React Query
- Sequential awaits for independent data -- use `Promise.all()`
- Fetching the same data in multiple components -- deduplicate with `React.cache()` or SWR

## State Anti-Patterns

- Storing derived values in state -- compute during render
- Syncing state with effects -- derive inline or use `useSyncExternalStore`
- Prop drilling through many layers -- use Context or Zustand
- Orphan event listeners -- deduplicate global listeners

## Component Anti-Patterns

- Giant multi-responsibility components -- split into focused pieces
- Untyped props -- always use TypeScript interfaces
- Business logic in UI components -- separate feature from presentation
- Barrel file imports from large libraries -- import specific modules

## Performance Anti-Patterns

- Manual `useMemo`/`useCallback` on everything -- trust React Compiler first
- `array.sort()` mutating state -- use `toSorted()` for immutability
- Animating SVG elements directly -- wrap in a `div` and animate the wrapper
- Eager initialization in `useState` -- use lazy initializer function
- `Array.includes` in render loops -- use `Set` with `useMemo` for O(1) lookups
- Object literals as props to memoized children -- define outside component or use `useMemo`
- Effect chains (A triggers B triggers C) -- derive all values directly during render

## Troubleshooting

### Hydration Mismatch

- **Cause:** Server and client render different output (dates, random values, browser APIs)
- **Fix:** Use inline `<script>` to set client-only values before React hydrates; use `suppressHydrationWarning` for intentional mismatches

### Unnecessary Re-renders

- **Cause:** Object/array references changing, subscribing to unused state
- **Fix:** Defer state reads to callbacks, use primitive dependencies, hoist default non-primitive props, check React Compiler output

### Data Fetching Waterfalls

- **Cause:** Sequential `await` calls, fetch in child after parent renders
- **Fix:** Parallelize with `Promise.all()`, hoist fetches, use Suspense boundaries to stream

### Bundle Size Bloat

- **Cause:** Barrel file imports pulling entire libraries, no code splitting
- **Fix:** Direct path imports, dynamic `import()` for heavy components, defer third-party scripts

### Stale Closures

- **Cause:** Event handlers or effects capturing old state values
- **Fix:** Use refs for latest values (`useLatest` pattern), functional `setState`, or `useEffectEvent`

```tsx
// BUG: count is always 0 inside the interval
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1); // Always sets to 1
  }, 1000);
  return () => clearInterval(interval);
}, []);

// FIX: Functional update
useEffect(() => {
  const interval = setInterval(() => {
    setCount((prev) => prev + 1);
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### Race Conditions

- **Cause:** Old async response overriding newer one when dependencies change quickly
- **Fix:** AbortController, cancelled flag, or TanStack Query (handles automatically)

```tsx
// BUG: User A request -> User B request -> User A response arrives last
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);

// FIX: AbortController
useEffect(() => {
  const controller = new AbortController();
  fetchUser(userId, { signal: controller.signal })
    .then(setUser)
    .catch((err) => {
      if (err.name !== 'AbortError') throw err;
    });
  return () => controller.abort();
}, [userId]);
```

### Memory Leaks

- **Cause:** Uncleared subscriptions, intervals, or event listeners
- **Fix:** Always return cleanup functions from effects

```tsx
useEffect(() => {
  const unsubscribe = eventBus.on('event', handler);
  return () => unsubscribe();
}, []);
```

### TypeScript Pitfalls

- **Type assertion without validation:** Use Zod `parse()` instead of `as User`
- **Optional chaining hiding bugs:** If `user.profile` should always exist, throw instead of using `?.`
- **Non-null assertion (`!`):** Handle null case explicitly
- **Using `any`:** Define proper interfaces for data structures

### React Compiler Not Optimizing

- **Cause:** Side effects during render, mutating props/state, non-idempotent render functions
- **Fix:** Follow Rules of React -- pure render functions, no side effects, treat props and state as immutable
