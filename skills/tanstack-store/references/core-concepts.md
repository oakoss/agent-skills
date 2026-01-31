---
title: Core Concepts
description: Store class, setState, state access, subscriptions, lifecycle hooks, and custom updaters
tags:
  [
    store,
    setState,
    subscribe,
    onSubscribe,
    onUpdate,
    updateFn,
    listeners,
    prevState,
  ]
---

# Core Concepts

## Creating a Store

A Store wraps a value with reactive state management. Pass initial state and optional configuration.

```ts
import { Store } from '@tanstack/store';

const countStore = new Store(0);

const userStore = new Store({
  name: 'Alice',
  age: 30,
  preferences: { theme: 'dark' },
});
```

## Reading State

Access the current value synchronously via the `.state` property. The previous value is available via `.prevState`.

```ts
console.log(countStore.state); // 0

countStore.setState(() => 5);

console.log(countStore.state); // 5
console.log(countStore.prevState); // 0
```

## Updating State

`setState` accepts an updater function that receives the previous state and returns the new state. It also accepts a direct value.

```ts
countStore.setState((prev) => prev + 1);

userStore.setState((prev) => ({
  ...prev,
  name: 'Bob',
}));
```

Always return a new object reference for object state. Direct mutation does not trigger subscribers.

```ts
// Wrong - mutates in place, no notification
userStore.setState((prev) => {
  prev.name = 'Bob';
  return prev;
});

// Correct - new object reference
userStore.setState((prev) => ({ ...prev, name: 'Bob' }));
```

## Subscriptions

Subscribe to state changes with a listener function. The listener receives the store instance. `subscribe` returns an unsubscribe function.

```ts
const unsubscribe = countStore.subscribe((store) => {
  console.log('Count changed to:', store.state);
});

countStore.setState(() => 10); // logs: "Count changed to: 10"

unsubscribe();
countStore.setState(() => 20); // no log
```

## Lifecycle Hooks

### onSubscribe

Fires when the first listener subscribes. The returned function fires when the last listener unsubscribes.

```ts
const store = new Store(0, {
  onSubscribe: (_listener, store) => {
    console.log('First subscriber attached');
    return () => {
      console.log('All subscribers removed');
    };
  },
});

const unsub1 = store.subscribe(() => {});
// logs: "First subscriber attached"

const unsub2 = store.subscribe(() => {});
// no log (already has subscribers)

unsub1();
unsub2();
// logs: "All subscribers removed"
```

### onUpdate

Fires after every state update. Useful for side effects like logging or syncing to external systems.

```ts
const store = new Store(
  { count: 0 },
  {
    onUpdate: () => {
      console.log('State updated:', store.state);
    },
  },
);

store.setState((prev) => ({ count: prev.count + 1 }));
// logs: "State updated: { count: 1 }"
```

## Custom Update Function

The `updateFn` option replaces the default setState behavior. It receives the previous state and returns a function that processes the updater.

```ts
const store = new Store(0, {
  updateFn: (prev) => (updater) => {
    const next = typeof updater === 'function' ? updater(prev) : updater;
    return Math.max(0, next);
  },
});

store.setState(() => -5);
console.log(store.state); // 0 (clamped to minimum)

store.setState(() => 10);
console.log(store.state); // 10
```

## Type-Safe Stores

Store is generic over `TState`. TypeScript infers the type from the initial value.

```ts
interface AppConfig {
  apiUrl: string;
  debug: boolean;
  retryCount: number;
}

const configStore = new Store<AppConfig>({
  apiUrl: 'https://api.example.com',
  debug: false,
  retryCount: 3,
});

configStore.setState((prev) => ({ ...prev, debug: true }));
```

## Installation

```bash
npm install @tanstack/store
```

For framework adapters, install the framework-specific package instead:

```bash
npm install @tanstack/react-store
npm install @tanstack/vue-store
npm install @tanstack/solid-store
npm install @tanstack/angular-store
npm install @tanstack/svelte-store
```
