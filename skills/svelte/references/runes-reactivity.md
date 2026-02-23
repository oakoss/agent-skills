---
title: Runes and Reactivity
description: Svelte 5 runes for state management, derived values, effects, props, and fine-grained reactivity
tags:
  [
    $state,
    $derived,
    $effect,
    $props,
    $bindable,
    $inspect,
    reactivity,
    runes,
    proxy,
  ]
---

# Runes and Reactivity

## $state

Declares reactive state. Primitives are tracked by value; objects and arrays are deeply proxied.

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
  let items = $state<string[]>([]);
</script>

<button onclick={() => count++}>Count: {count}</button>
<input bind:value={user.name} />
```

### $state.raw

Opts out of deep proxying. Use for large read-only datasets or objects passed to external libraries that do not expect proxies.

```svelte
<script>
  let rows = $state.raw(fetchedData);

  function refresh(newData: Row[]) {
    rows = newData;
  }
</script>
```

### $state.snapshot

Creates a plain, non-reactive copy of proxied state. Useful for serialization or passing to APIs that reject proxies.

```ts
let form = $state({ name: '', email: '' });

async function submit() {
  const data = $state.snapshot(form);
  await fetch('/api', { method: 'POST', body: JSON.stringify(data) });
}
```

## $derived

Computes values that automatically update when dependencies change. Replaces `$:` reactive declarations.

```svelte
<script>
  let count = $state(0);
  const double = $derived(count * 2);
  const isEven = $derived(count % 2 === 0);
</script>

<p>{count} doubled is {double} and is {isEven ? 'even' : 'odd'}</p>
```

### $derived.by

For multi-statement derived computations.

```svelte
<script>
  let items = $state<{ price: number; qty: number }[]>([]);

  const total = $derived.by(() => {
    let sum = 0;
    for (const item of items) {
      sum += item.price * item.qty;
    }
    return sum;
  });
</script>
```

## $effect

Runs side effects after the DOM updates. Automatically tracks reactive dependencies read during execution. Returns a cleanup function for teardown.

```svelte
<script>
  let query = $state('');

  $effect(() => {
    const controller = new AbortController();

    fetch(`/api/search?q=${query}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => {
        results = data;
      });

    return () => controller.abort();
  });
</script>
```

### $effect.pre

Runs before DOM updates. Use for reading DOM measurements that will change.

```svelte
<script>
  let div: HTMLDivElement;

  $effect.pre(() => {
    const scrollHeight = div?.scrollHeight;
  });
</script>
```

### Avoiding infinite loops

Effects re-run when their dependencies change. Never write to a value you also read in the same effect.

```svelte
<script>
  let count = $state(0);

  // WRONG: reads and writes count, creating an infinite loop
  // $effect(() => { count = count + 1; });

  // CORRECT: use $derived for transformations
  const next = $derived(count + 1);
</script>
```

## $props

Declares component props. Replaces `export let`. Supports defaults, rest props, and TypeScript.

```svelte
<script lang="ts">
  interface Props {
    name: string;
    age?: number;
    class?: string;
  }

  let { name, age = 25, class: className, ...rest } = $props<Props>();
</script>

<div class={className} {...rest}>
  {name} is {age} years old
</div>
```

## $bindable

Marks a prop as two-way bindable. The parent can use `bind:` to sync the value.

```svelte
<script lang="ts">
  let { value = $bindable('') } = $props<{ value: string }>();
</script>

<input bind:value />
```

Parent usage:

```svelte
<script>
  import TextInput from './TextInput.svelte';
  let name = $state('');
</script>

<TextInput bind:value={name} />
<p>You typed: {name}</p>
```

## $inspect

Dev-only debugging rune. Logs values when they change. Automatically stripped in production builds.

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice' });

  $inspect(count);
  $inspect(user);

  $inspect(count).with(console.trace);
</script>
```

## Shared reactive state (.svelte.ts modules)

Create shared state by using `$state` in `.svelte.ts` or `.svelte.js` files. This replaces Svelte 4 stores.

```ts
// src/lib/counter.svelte.ts
let count = $state(0);

export function getCount() {
  return count;
}

export function increment() {
  count++;
}

export function reset() {
  count = 0;
}
```

```svelte
<script>
  import { getCount, increment } from '$lib/counter.svelte';
</script>

<button onclick={increment}>Count: {getCount()}</button>
```

### Class-based shared state

```ts
// src/lib/todo-store.svelte.ts
export class TodoStore {
  items = $state<{ id: string; text: string; done: boolean }[]>([]);
  filter = $state<'all' | 'active' | 'done'>('all');

  filtered = $derived.by(() => {
    switch (this.filter) {
      case 'active':
        return this.items.filter((t) => !t.done);
      case 'done':
        return this.items.filter((t) => t.done);
      default:
        return this.items;
    }
  });

  add(text: string) {
    this.items.push({ id: crypto.randomUUID(), text, done: false });
  }

  toggle(id: string) {
    const item = this.items.find((t) => t.id === id);
    if (item) item.done = !item.done;
  }
}
```

```svelte
<script>
  import { TodoStore } from '$lib/todo-store.svelte';

  const store = new TodoStore();
</script>

{#each store.filtered as todo (todo.id)}
  <label>
    <input type="checkbox" checked={todo.done} onchange={() => store.toggle(todo.id)} />
    {todo.text}
  </label>
{/each}
```
