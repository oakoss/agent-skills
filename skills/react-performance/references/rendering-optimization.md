---
title: Rendering Optimization
description: React.memo, useMemo, useCallback targeting, React Compiler automatic memoization, re-render elimination patterns, startTransition, and state management for performance
tags:
  [
    memo,
    useMemo,
    useCallback,
    compiler,
    re-renders,
    startTransition,
    derived-state,
    functional-setState,
  ]
---

# Rendering Optimization

## React Compiler (Preferred)

React Compiler automatically applies memoization equivalent to `useMemo`, `useCallback`, and `React.memo` at build time. Code that follows the Rules of React gets optimized without manual intervention.

When the compiler is enabled, remove manual memoization unless the compiler explicitly skips a component (check React DevTools for the "Memo" badge).

```tsx
function ExpensiveComponent({ data, onClick }: Props) {
  const processedData = expensiveProcessing(data);

  const handleClick = (item: Item) => {
    onClick(item.id);
  };

  return (
    <div>
      {processedData.map((item) => (
        <Item key={item.id} onClick={() => handleClick(item)} />
      ))}
    </div>
  );
}
```

The compiler optimizes this automatically. No `useMemo`, `useCallback`, or `memo` needed.

## When to Use Manual Memoization

Without React Compiler, or when the compiler skips a component, apply memoization selectively.

### React.memo -- Component-Level Memoization

Wrap components that receive stable props from frequently re-rendering parents:

```tsx
const UserAvatar = memo(function UserAvatar({ user }: { user: User }) {
  const id = useMemo(() => computeAvatarId(user), [user]);
  return <Avatar id={id} />;
});

function Profile({ user, loading }: Props) {
  if (loading) return <Skeleton />;
  return (
    <div>
      <UserAvatar user={user} />
    </div>
  );
}
```

Extracting into a memoized component enables early returns before expensive computation.

### useMemo -- Expensive Computations Only

```tsx
const doubled = value * 2;

const sortedItems = useMemo(
  () => items.toSorted((a, b) => a.price - b.price),
  [items],
);

const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);
```

Skip `useMemo` for cheap operations (arithmetic, string concatenation). Use it for sorting, filtering, or building lookup structures from arrays.

### useCallback -- Memoized Child Consumers Only

```tsx
const handleClick = useCallback(() => doSomething(id), [id]);
return <MemoizedChild onClick={handleClick} />;
```

Skip `useCallback` when the consumer is not memoized -- the overhead exceeds the benefit.

## Functional setState for Stable Callbacks

Use the functional update form to eliminate state dependencies from callbacks:

```tsx
function TodoList() {
  const [items, setItems] = useState(initialItems);

  const addItems = useCallback((newItems: Item[]) => {
    setItems((curr) => [...curr, ...newItems]);
  }, []);

  const removeItem = useCallback((id: string) => {
    setItems((curr) => curr.filter((item) => item.id !== id));
  }, []);

  return <ItemsEditor items={items} onAdd={addItems} onRemove={removeItem} />;
}
```

Callbacks with empty dependency arrays are never recreated, preventing unnecessary child re-renders.

## Defer State Reads

Avoid subscribing to dynamic state that is only used inside callbacks:

```tsx
function ShareButton({ chatId }: { chatId: string }) {
  const handleShare = () => {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    shareChat(chatId, { ref });
  };

  return <button onClick={handleShare}>Share</button>;
}
```

Reading `searchParams` on demand instead of via `useSearchParams()` avoids re-renders when URL changes.

## Subscribe to Derived State

Subscribe to derived booleans instead of continuous values:

```tsx
function Sidebar() {
  const isMobile = useMediaQuery('(max-width: 767px)');
  return <nav className={isMobile ? 'mobile' : 'desktop'} />;
}
```

This re-renders only when the boolean changes, not on every pixel of window resize.

## Derive State During Render

Compute derived values during render instead of syncing with effects:

```tsx
function FilteredList({ items, filter }: Props) {
  const filtered = items.filter((item) => item.category === filter);

  return (
    <ul>
      {filtered.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

Using `useEffect` to sync derived state adds an extra render cycle and is unnecessary.

## startTransition for Non-Urgent Updates

Mark frequent, non-urgent state updates as transitions to keep the UI responsive:

```tsx
import { startTransition } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);

  const handleChange = (value: string) => {
    setQuery(value);
    startTransition(() => {
      setResults(search(value));
    });
  };

  return (
    <>
      <input value={query} onChange={(e) => handleChange(e.target.value)} />
      <ResultsList results={results} />
    </>
  );
}
```

The input stays responsive while search results update in the background.

## Stable Object References

Avoid creating new object or array literals as props on every render:

```tsx
const style = { color: 'red' };

function Parent() {
  return <Child style={style} />;
}
```

For dynamic values, use `useMemo`:

```tsx
function Parent({ color }: { color: string }) {
  const style = useMemo(() => ({ color }), [color]);
  return <MemoizedChild style={style} />;
}
```

## content-visibility for Long Lists

Use CSS `content-visibility` to skip layout and paint for off-screen items:

```css
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

```tsx
function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="overflow-y-auto h-screen">
      {messages.map((msg) => (
        <div key={msg.id} className="list-item">
          <Avatar user={msg.author} />
          <div>{msg.content}</div>
        </div>
      ))}
    </div>
  );
}
```

For 1000 items, the browser skips layout/paint for ~990 off-screen items.

## Hoist Static JSX

Extract constant JSX elements outside component functions to avoid recreation:

```tsx
const emptyState = <div className="empty">No items found</div>;

function ItemList({ items }: { items: Item[] }) {
  if (items.length === 0) return emptyState;
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

Static JSX hoisted outside the component is created once and reused across renders.
