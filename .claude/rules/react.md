---
paths:
  - 'skills/**/references/**'
---

# React Rules

Uses React 17+ new JSX transform (`react/jsx-runtime`) - no need to import React in every file.

## Props Sorting

Props sorted alphabetically (callbacks last, reserved first, shorthand first):

```tsx
<Button
  key={id}
  ref={buttonRef}
  disabled
  className="btn"
  variant="outline"
  onPress={handleClick}
/>
```

## React Recommended (Enabled)

```tsx
// jsx-key - Arrays need keys
{items.map(item => <Item key={item.id} />)} // Good
{items.map(item => <Item />)} // Bad

// no-children-prop - Don't pass children as prop
<Component children={<Child />} /> // Bad
<Component><Child /></Component> // Good

// no-unescaped-entities - Escape &, <, >, ", '
<p>It's</p> // Bad
<p>It&apos;s</p> // Good
```

## React Hooks

```tsx
// rules-of-hooks - Hooks only at top level, only in components/hooks
if (condition) {
  useEffect(() => {}); // Bad - hook in conditional
}
useEffect(() => {}); // Good

// exhaustive-deps - OFF in this project (deps not enforced)
```

## @eslint-react Rules

```tsx
// no-array-index-key - Don't use index as key
{
  items.map((item, i) => <Item key={i} />);
} // Bad
{
  items.map((item) => <Item key={item.id} />);
} // Good

// no-leaked-conditional-rendering - Avoid 0 && <Component />
{
  count && <Component />;
} // Bad - renders "0"
{
  count > 0 && <Component />;
} // Good

// no-children-count/forEach/map/only/toArray - Avoid Children utilities
// no-clone-element - Avoid cloneElement
// no-create-ref - Use useRef instead
// no-forward-ref - Use ref prop directly (React 19+)
// no-class-component - Prefer function components
```

## Web API Cleanup Rules

```tsx
// no-leaked-event-listener - Clean up listeners
// no-leaked-interval - Clean up setInterval
// no-leaked-timeout - Clean up setTimeout
// no-leaked-resize-observer - Clean up observers

useEffect(() => {
  const handler = () => {};
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler); // cleanup
}, []);
```

## Relaxed Rules

These are explicitly allowed (rules disabled):

| Rule                  | Status  | Notes                                   |
| --------------------- | ------- | --------------------------------------- |
| `exhaustive-deps`     | OFF     | Hook dependency arrays not enforced     |
| Nested components     | Allowed | Can define components inside components |
| setState in useEffect | Allowed | No warning for this pattern             |
| Inline context values | Allowed | `value={{ foo }}` is OK                 |
| Empty fragments       | Allowed | `<><Child/></>` is OK                   |
| Inline functions      | Allowed | `onPress={() => ...}` is OK             |
| Async handlers        | Allowed | `onPress={async () => ...}` is OK       |

## React Aria Components Notes

When using React Aria Components, use their event prop names:

```tsx
// React Aria uses onPress, not onClick
<Button onPress={handleClick}>Click me</Button>

// onChange is onSelectionChange for Select
<Select onSelectionChange={handleChange}>...</Select>

// Form events use React Aria naming
<TextField onChange={handleChange} />
```
