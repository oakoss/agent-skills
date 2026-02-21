---
title: Derived State
description: Derived stores, computed values, dependency tracking, batching, and effects
tags:
  [
    derived,
    batch,
    effect,
    computed,
    deps,
    mount,
    dependency-tracking,
    recompute,
  ]
---

# Derived State

## Creating Derived Values

`Derived` creates computed state from one or more Store or Derived dependencies. It recomputes lazily when dependencies change.

```ts
import { Store, Derived } from '@tanstack/store';

const firstName = new Store('John');
const lastName = new Store('Doe');

const fullName = new Derived({
  deps: [firstName, lastName],
  fn: ({ currDepVals }) => {
    return `${currDepVals[0]} ${currDepVals[1]}`;
  },
});
```

## Mounting and Cleanup

Derived values must be mounted to activate dependency tracking. `mount()` returns a cleanup function.

```ts
const unmount = fullName.mount();

console.log(fullName.state); // "John Doe"

firstName.setState(() => 'Jane');
console.log(fullName.state); // "Jane Doe"

unmount();
```

Accessing `.state` on an unmounted Derived will not reflect dependency changes.

## Dependency Value Access

The `fn` callback receives an object with current and previous dependency values.

```ts
const items = new Store([1, 2, 3]);
const multiplier = new Store(2);

const computed = new Derived({
  deps: [items, multiplier],
  fn: ({ currDepVals, prevDepVals }) => {
    const [currentItems, currentMultiplier] = currDepVals;
    // prevDepVals available for comparison
    return currentItems.map((item) => item * currentMultiplier);
  },
});

const unmount = computed.mount();
console.log(computed.state); // [2, 4, 6]
unmount();
```

## Derived from Derived

Derived values can depend on other Derived values, forming a computation graph.

```ts
const price = new Store(100);
const taxRate = new Store(0.08);

const tax = new Derived({
  deps: [price, taxRate],
  fn: ({ currDepVals }) => currDepVals[0] * currDepVals[1],
});

const total = new Derived({
  deps: [price, tax],
  fn: ({ currDepVals }) => currDepVals[0] + currDepVals[1],
});

const taxUnmount = tax.mount();
const totalUnmount = total.mount();

console.log(total.state); // 108

price.setState(() => 200);
console.log(total.state); // 216

totalUnmount();
taxUnmount();
```

## Subscriptions on Derived

Subscribe to derived state changes the same way as Store.

```ts
const count = new Store(0);
const doubled = new Derived({
  deps: [count],
  fn: ({ currDepVals }) => currDepVals[0] * 2,
});

const unmount = doubled.mount();
const unsubscribe = doubled.subscribe(() => {
  console.log('Doubled is now:', doubled.state);
});

count.setState(() => 5);
// logs: "Doubled is now: 10"

unsubscribe();
unmount();
```

## Derived Lifecycle Hooks

Derived supports `onSubscribe` and `onUpdate` hooks, similar to Store.

```ts
const source = new Store(0);

const derived = new Derived({
  deps: [source],
  fn: ({ currDepVals }) => currDepVals[0] * 10,
  onSubscribe: (_listener, _derived) => {
    console.log('Derived subscriber added');
    return () => console.log('Derived subscriber removed');
  },
  onUpdate: () => {
    console.log('Derived recomputed');
  },
});
```

## Batching Updates

`batch` groups multiple state updates so subscribers and derived values recompute only once.

```ts
import { Store, Derived, batch } from '@tanstack/store';

const a = new Store(1);
const b = new Store(2);

const sum = new Derived({
  deps: [a, b],
  fn: ({ currDepVals }) => currDepVals[0] + currDepVals[1],
});

const unmount = sum.mount();

let recomputeCount = 0;
sum.subscribe(() => recomputeCount++);

batch(() => {
  a.setState(() => 10);
  b.setState(() => 20);
});

console.log(sum.state); // 30
console.log(recomputeCount); // 1 (computed once, not twice)

unmount();
```

Without `batch`, each `setState` triggers a separate recomputation and notification.

## Effects

`Effect` runs a side-effect function when its dependencies change. Like Derived, it requires mounting.

```ts
import { Store, Effect } from '@tanstack/store';

const theme = new Store<'light' | 'dark'>('light');

const effect = new Effect({
  deps: [theme],
  fn: () => {
    document.documentElement.dataset.theme = theme.state;
  },
});

const unmount = effect.mount();

theme.setState(() => 'dark');
// document.documentElement.dataset.theme is now "dark"

unmount();
```

Effects are useful for synchronizing store state with external systems (DOM, localStorage, analytics).

## Eager Effects

By default, an Effect waits for the first dependency change before running. Set `eager: true` to run the effect immediately when mounted.

```ts
import { Store, Effect } from '@tanstack/store';

const count = new Store(0);

const effect = new Effect({
  deps: [count],
  fn: () => {
    console.log('Count:', count.state);
  },
  eager: true,
});

const unmount = effect.mount();
// logs immediately: "Count: 0"

count.setState(() => 1);
// logs: "Count: 1"

unmount();
```

## Effect with Multiple Dependencies

```ts
const token = new Store<string | null>(null);
const baseUrl = new Store('https://api.example.com');

const effect = new Effect({
  deps: [token, baseUrl],
  fn: () => {
    if (token.state) {
      console.log(`Configured client: ${baseUrl.state} with auth`);
    }
  },
});

const unmount = effect.mount();

token.setState(() => 'abc123');
// logs: "Configured client: https://api.example.com with auth"

unmount();
```
