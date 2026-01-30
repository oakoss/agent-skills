---
title: Component Patterns
description: Component architecture, state management patterns, useEffect decision tree, and derived state
tags: [components, state, useEffect, derived-state, props, architecture]
---

# Component Patterns

## Component Architecture

**Component types and when to use each:**

- **Page Components** -- Route entry points. Compose feature and UI components.
- **Feature Components** -- Own business logic, fetch data, manage domain state.
- **UI Components** -- Reusable primitives with no business logic (buttons, inputs, cards).

```tsx
// Feature component: owns data, delegates rendering
export function UserList() {
  const { data, isLoading } = useUsers();
  if (isLoading) return <LoadingSpinner />;
  return (
    <div>
      {data.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

**Best practices:**

- Type all props with interfaces
- Keep components small and focused
- Compose over inheritance
- Co-locate related code

## State Management

**State proximity:** keep state as close to where it is used as possible.

**Lazy initialization:** pass a function to `useState` for expensive initial values.

```tsx
const [data, setData] = useState(() => expensiveComputation());
```

**Functional setState:** use for stable callbacks that don't need the current value in scope.

```tsx
setCount((prev) => prev + 1);
```

**Refs for transient values:** use `useRef` for values that change frequently but don't need re-renders (scroll position, timers, animation frames).

## Derived State

Compute during render, never in effects. Prefer computing values from existing state over synchronizing with effects.

```tsx
// Derive during render
const fullName = `${user.firstName} ${user.lastName}`;

// Subscribe to derived booleans, not raw values
const isEmpty = items.length === 0;

// Memoize only when the derivation is expensive
const sortedItems = useMemo(
  () => items.toSorted((a, b) => a.name.localeCompare(b.name)),
  [items],
);
```

```tsx
// Bad -- syncing derived state through an effect
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// Good -- derive inline
const fullName = `${firstName} ${lastName}`;
```

## useEffect Decision Tree

Effects are escape hatches. They synchronize React with external systems. If no external system is involved, you likely don't need one.

```text
Do I need useEffect?

Is there an external system involved?
├── No -> Don't use useEffect
│   ├── Derived state? -> Calculate during render
│   ├── Event response? -> Handle in event handler
│   └── Data fetching? -> Use React Query or use()
└── Yes -> Maybe use useEffect
    ├── Browser APIs (focus, scroll, localStorage)
    ├── Third-party widgets (maps, charts)
    ├── Network connections (WebSockets)
    └── Analytics/logging
```

**Event handlers over effects:** if logic runs in response to a user action, put it in the event handler, not an effect.

```tsx
// Bad -- effect chain for event response
useEffect(() => {
  if (submitted) {
    navigate('/success');
  }
}, [submitted]);

// Good -- handle in event
const handleSubmit = async () => {
  await submitForm();
  navigate('/success');
};
```

## Form Handling

Use React Hook Form + Zod for validated forms:

```tsx
const {
  register,
  handleSubmit,
  formState: { errors },
} = useForm<FormData>({
  resolver: zodResolver(schema),
});
```

## Error Handling

- Wrap feature boundaries with Error Boundaries
- Provide fallback UI and retry mechanisms
- Use `getDerivedStateFromError` for class-based boundaries

## TypeScript

- Type all component props with interfaces
- Type API responses explicitly
- Type state: `useState<User | null>(null)`
- Use `ReactNode` for children types
