---
title: React Integration
description: useStore hook, React bindings, selector patterns, shallow comparison, and performance optimization
tags: [useStore, react-store, selector, shallow, re-render, performance, react]
---

# React Integration

## Installation

```bash
npm install @tanstack/react-store
```

`@tanstack/react-store` re-exports the core `Store` class, so a separate `@tanstack/store` install is not required.

## useStore Hook

`useStore` subscribes a React component to a Store instance. The component re-renders when the store state changes.

```tsx
import { Store, useStore } from '@tanstack/react-store';

const countStore = new Store(0);

function Counter() {
  const count = useStore(countStore);

  return (
    <div>
      <span>Count: {count}</span>
      <button onClick={() => countStore.setState((prev) => prev + 1)}>
        Increment
      </button>
    </div>
  );
}
```

## Selectors

Pass a selector function as the second argument to subscribe to a slice of state. The component only re-renders when the selected value changes.

```tsx
const appStore = new Store({
  user: { name: 'Alice', role: 'admin' },
  theme: 'dark',
  notifications: 5,
});

function UserName() {
  const name = useStore(appStore, (state) => state.user.name);
  return <span>{name}</span>;
}

function NotificationBadge() {
  const count = useStore(appStore, (state) => state.notifications);
  return count > 0 ? <span>{count}</span> : null;
}
```

Updating `theme` does not re-render `UserName` because the selector returns `state.user.name`, which has not changed.

## Shallow Comparison

When a selector returns a new object or array reference on every call, use `shallow` to compare by value instead of reference.

```tsx
import { useStore, shallow } from '@tanstack/react-store';

const todoStore = new Store({
  items: [
    { id: 1, text: 'Buy milk', done: false },
    { id: 2, text: 'Walk dog', done: true },
  ],
});

function PendingTodos() {
  const pending = useStore(
    todoStore,
    (state) => state.items.filter((item) => !item.done),
    shallow,
  );

  return (
    <ul>
      {pending.map((item) => (
        <li key={item.id}>{item.text}</li>
      ))}
    </ul>
  );
}
```

Without `shallow`, the `filter` call creates a new array reference every time, causing re-renders even when the filtered result has not changed.

## Store Outside Components

Define stores outside of React components. This avoids recreating the store on every render and enables sharing across the component tree.

```tsx
import { Store, useStore } from '@tanstack/react-store';

export const store = new Store({
  dogs: 0,
  cats: 0,
});

function Display({ animal }: { animal: 'dogs' | 'cats' }) {
  const count = useStore(store, (state) => state[animal]);
  return (
    <div>
      {animal}: {count}
    </div>
  );
}

function Increment({ animal }: { animal: 'dogs' | 'cats' }) {
  return (
    <button
      onClick={() =>
        store.setState((prev) => ({
          ...prev,
          [animal]: prev[animal] + 1,
        }))
      }
    >
      Add {animal}
    </button>
  );
}

function App() {
  return (
    <div>
      <Increment animal="dogs" />
      <Display animal="dogs" />
      <Increment animal="cats" />
      <Display animal="cats" />
    </div>
  );
}
```

## Derived Values in React

Use `Derived` with `useStore` to subscribe to computed values. Mount the Derived outside the component.

```tsx
import { Store, Derived, useStore } from '@tanstack/react-store';

const cartStore = new Store({
  items: [
    { name: 'Widget', price: 10, qty: 2 },
    { name: 'Gadget', price: 25, qty: 1 },
  ],
});

const totalDerived = new Derived({
  deps: [cartStore],
  fn: ({ currDepVals }) => {
    const [cart] = currDepVals;
    return cart.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  },
});

totalDerived.mount();

function CartTotal() {
  const total = useStore(totalDerived);
  return <div>Total: ${total}</div>;
}
```

## Updating State from Event Handlers

Call `setState` directly in event handlers. No dispatch or action creators needed.

```tsx
const formStore = new Store({
  email: '',
  password: '',
});

function LoginForm() {
  const email = useStore(formStore, (state) => state.email);
  const password = useStore(formStore, (state) => state.password);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        console.log('Submit:', formStore.state);
      }}
    >
      <input
        type="email"
        value={email}
        onChange={(e) =>
          formStore.setState((prev) => ({ ...prev, email: e.target.value }))
        }
      />
      <input
        type="password"
        value={password}
        onChange={(e) =>
          formStore.setState((prev) => ({ ...prev, password: e.target.value }))
        }
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## Performance Tips

- **Use selectors**: Always select the narrowest slice of state a component needs
- **Use `shallow`**: When selectors return derived objects or filtered arrays
- **Avoid inline store creation**: Instantiate stores outside components or in a `useState` initializer
- **Batch related updates**: Wrap multiple `setState` calls in `batch()` to prevent intermediate renders
- **Split stores**: Prefer multiple small stores over one large store when state domains are unrelated
