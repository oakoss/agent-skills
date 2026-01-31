---
title: Component Patterns
description: Component architecture, state management patterns, useEffect decision tree, derived state, and form handling
tags:
  [
    components,
    state,
    useEffect,
    derived-state,
    props,
    architecture,
    forms,
    useId,
  ]
---

# Component Patterns

## Component Architecture

**Component types and when to use each:**

- **Page Components** -- Route entry points. Compose feature and UI components.
- **Feature Components** -- Own business logic, fetch data, manage domain state.
- **UI Components** -- Reusable primitives with no business logic (buttons, inputs, cards).

```tsx
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

## Component Structure

Follow a consistent internal order:

```tsx
import { useSuspenseQuery } from '@tanstack/react-query';
import { userQueries } from '@/features/users/api';
import { type User } from '@/features/users/types';

interface UserCardProps {
  userId: string;
  onSelect?: (user: User) => void;
}

export function UserCard({ userId, onSelect }: UserCardProps) {
  const { data: user } = useSuspenseQuery(userQueries.detail(userId));

  const fullName = `${user.firstName} ${user.lastName}`;

  const handleClick = () => onSelect?.(user);

  if (!user.isActive) return null;

  return (
    <article onClick={handleClick} className="user-card">
      <h3>{fullName}</h3>
      <p>{user.email}</p>
    </article>
  );
}
```

Order: imports (external, internal, types) then types then component (queries/mutations, derived state, handlers, early returns, JSX).

## State Management

**State proximity:** keep state as close to where it is used as possible.

| How many components need the state? | Solution              |
| ----------------------------------- | --------------------- |
| One component                       | `useState`            |
| Parent + children                   | Props                 |
| Siblings                            | Lift to common parent |
| Widely used                         | Context API           |
| Complex app state                   | Zustand               |
| Server data with caching            | React Query           |

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
const fullName = `${user.firstName} ${user.lastName}`;

const isEmpty = items.length === 0;

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

Use `useActionState` for forms with Server Actions (React 19+):

```tsx
import { useActionState } from 'react';
import { updateProfile } from './actions';

function ProfileForm() {
  const [state, action, isPending] = useActionState(updateProfile, {
    message: null,
  });

  return (
    <form action={action}>
      <input name="username" disabled={isPending} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Saving...' : 'Save'}
      </button>
      {state.message ? <p>{state.message}</p> : null}
    </form>
  );
}
```

For complex client-side forms with field-level validation, use React Hook Form + Zod or TanStack Form.

## Unique IDs with useId

Use `useId` for hydration-safe unique identifiers. Never use `Math.random()` or counters for IDs that appear in server-rendered HTML.

```tsx
import { useId } from 'react';

function EmailField() {
  const id = useId();
  return (
    <div>
      <label htmlFor={id}>Email</label>
      <input id={id} type="email" />
    </div>
  );
}
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
