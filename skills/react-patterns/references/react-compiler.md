---
title: React Compiler
description: React Compiler (Forget) patterns, rules for automatic memoization, manual optimization fallbacks, and re-render diagnosis
tags:
  [
    compiler,
    forget,
    memoization,
    useMemo,
    useCallback,
    memo,
    re-renders,
    rules-of-react,
  ]
---

# React Compiler

## How It Works

The React Compiler (stable since React 19) automatically applies memoization equivalent to `useMemo`, `useCallback`, and `React.memo`. Code that follows the Rules of React gets optimized without any manual annotations.

Check if the compiler is active: open React DevTools and look for the "Memo ✨" badge next to optimized components.

## Setup

Install as a Babel plugin:

```bash
npm i -D babel-plugin-react-compiler
```

For Next.js, enable in `next.config.ts`:

```ts
const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};
```

For other Babel-based setups, add to your Babel config:

```json
{
  "plugins": ["babel-plugin-react-compiler"]
}
```

The compiler also has experimental support via SWC and Rspack plugins.

## Rules for Compiler Compatibility

The compiler requires code to follow three rules during rendering:

1. **Pure render functions** -- components must return the same JSX for the same props and state. No reading from mutable globals during render.
2. **No side effects during render** -- no setting timeouts, mutating external variables, or writing to the DOM during the render phase. Event handlers and effects are fine.
3. **Immutable props and state** -- never mutate objects or arrays that come from props or state. Always create new references.

```tsx
// Bad -- mutates during render, breaks compiler optimization
function UserList({ users }: { users: User[] }) {
  users.sort((a, b) => a.name.localeCompare(b.name));
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}

// Good -- immutable operation, compiler can optimize
function UserList({ users }: { users: User[] }) {
  const sorted = users.toSorted((a, b) => a.name.localeCompare(b.name));
  return (
    <ul>
      {sorted.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}
```

## When Manual Memoization Is Still Needed

Even with the compiler, some patterns benefit from explicit memoization:

### Expensive Computations

```tsx
// Compiler handles simple derivations automatically.
// For genuinely expensive work (large list processing, complex math),
// useMemo provides an explicit contract.
const aggregatedData = useMemo(
  () => processLargeDataset(rawData, filters),
  [rawData, filters],
);
```

### Callbacks Passed to Memoized Children

```tsx
// Skip -- no memoized consumer
const handleClick = () => doSomething();
return <button onClick={handleClick}>Click</button>;

// Use -- prevents re-render of memoized child
const handleClick = useCallback(() => doSomething(id), [id]);
return <MemoizedChild onClick={handleClick} />;
```

### Stable Object References for Effect Dependencies

```tsx
// Bad -- new object every render triggers effect
function Chart({ data }: { data: number[] }) {
  const config = { animate: true, duration: 300 };
  useEffect(() => {
    renderChart(config);
  }, [config]);
}

// Good -- stable reference
const CHART_CONFIG = { animate: true, duration: 300 };
function Chart({ data }: { data: number[] }) {
  useEffect(() => {
    renderChart(CHART_CONFIG);
  }, []);
}
```

## Re-render Optimization Techniques

### Defer State Reads

Do not subscribe to state you only read inside callbacks:

```tsx
// Bad -- re-renders on every query change
function SearchButton() {
  const [query] = useAtom(searchAtom);
  const handleClick = () => goToSearch(query);
  return <button onClick={handleClick}>Search</button>;
}

// Good -- reads on demand, no subscription
function SearchButton() {
  const handleClick = () => {
    const query = searchStore.get();
    goToSearch(query);
  };
  return <button onClick={handleClick}>Search</button>;
}
```

### Narrow Effect Dependencies

Use primitive values instead of objects to minimize effect re-runs:

```tsx
// Bad -- re-runs whenever user object reference changes
useEffect(() => {
  track(user.id);
}, [user]);

// Good -- only re-runs when the ID actually changes
useEffect(() => {
  track(user.id);
}, [user.id]);
```

### Hoist Static JSX

Extract constant JSX outside component functions to avoid re-creation:

```tsx
const EMPTY_STATE = (
  <div className="empty">
    <p>No items found</p>
  </div>
);

function ItemList({ items }: { items: Item[] }) {
  if (items.length === 0) return EMPTY_STATE;
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

### Hoist Default Props

Non-primitive default values create new references each render:

```tsx
// Bad -- new array reference every render
function TagList({ tags = [] }: { tags?: string[] }) {
  // ...
}

// Good -- stable default reference
const EMPTY_TAGS: string[] = [];
function TagList({ tags = EMPTY_TAGS }: { tags?: string[] }) {
  // ...
}
```

## useTransition for Non-Urgent Updates

Mark non-urgent updates as interruptible so the UI stays responsive:

```tsx
const [isPending, startTransition] = useTransition();

const handleFilter = (value: string) => {
  setInputValue(value);

  startTransition(() => {
    setFilteredResults(filterLargeList(value));
  });
};
```

## Diagnosing Re-render Issues

1. **React DevTools Profiler** -- record interactions and check which components re-rendered and why
2. **Highlight Updates** -- enable "Highlight updates when components render" in React DevTools settings
3. **Check Compiler output** -- look for the "Memo" badge; missing badge means the component is not being auto-memoized
4. **Common culprits:**
   - Object/array literals as props
   - Inline function definitions passed to memoized children
   - Subscribing to state not used in the render output
   - Effect dependencies using object references instead of primitives

## O(1) Lookups with Set

Convert arrays to Sets for repeated membership checks:

```tsx
// Bad -- O(n) on every render
const isSelected = (id: string) => selectedIds.includes(id);

// Good -- O(1) lookups
const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);
const isSelected = (id: string) => selectedSet.has(id);
```

## Conditional Rendering

Use ternary operators instead of `&&` to avoid rendering falsy values like `0`:

```tsx
// Bad -- renders "0" when count is 0
{
  count && <Badge count={count} />;
}

// Good -- renders null when count is 0
{
  count > 0 ? <Badge count={count} /> : null;
}
```
