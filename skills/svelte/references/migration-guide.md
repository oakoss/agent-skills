---
title: Migration Guide
description: Migrating from Svelte 4 to Svelte 5, covering stores to runes, slots to snippets, events, and component API changes
tags:
  [
    migration,
    svelte4,
    svelte5,
    stores,
    runes,
    slots,
    snippets,
    events,
    breaking-changes,
  ]
---

# Svelte 4 to 5 Migration Guide

## Reactive State: let to $state

Svelte 4 made top-level `let` declarations reactive automatically. Svelte 5 requires explicit `$state`.

```svelte
<!-- Svelte 4 -->
<script>
  let count = 0;
  let user = { name: 'Alice' };
</script>
```

```svelte
<!-- Svelte 5 -->
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice' });
</script>
```

## Reactive Declarations: $: to $derived / $effect

```svelte
<!-- Svelte 4 -->
<script>
  let count = 0;
  $: double = count * 2;
  $: isPositive = count > 0;
  $: {
    console.log('count changed:', count);
    updateAnalytics(count);
  }
</script>
```

```svelte
<!-- Svelte 5 -->
<script>
  let count = $state(0);
  const double = $derived(count * 2);
  const isPositive = $derived(count > 0);

  $effect(() => {
    console.log('count changed:', count);
    updateAnalytics(count);
  });
</script>
```

## Props: export let to $props

```svelte
<!-- Svelte 4 -->
<script>
  export let name;
  export let age = 25;
  export let variant = 'primary';

  $$restProps; // access rest props
</script>
```

```svelte
<!-- Svelte 5 -->
<script lang="ts">
  let { name, age = 25, variant = 'primary', ...rest } = $props<{
    name: string;
    age?: number;
    variant?: 'primary' | 'secondary';
  }>();
</script>

<div {...rest}>{name}</div>
```

## Stores to Runes

Svelte 4 stores (`writable`, `readable`, `derived`) are replaced by runes in `.svelte.ts` modules.

```ts
// Svelte 4: src/lib/stores.ts
import { writable, derived } from 'svelte/store';

export const count = writable(0);
export const double = derived(count, ($count) => $count * 2);

// Usage in component:
// $count (auto-subscribe with $ prefix)
```

```ts
// Svelte 5: src/lib/counter.svelte.ts
let count = $state(0);
const double = $derived(count * 2);

export function useCounter() {
  return {
    get count() {
      return count;
    },
    get double() {
      return double;
    },
    increment() {
      count++;
    },
    reset() {
      count = 0;
    },
  };
}
```

```svelte
<!-- Svelte 5 component -->
<script>
  import { useCounter } from '$lib/counter.svelte';

  const counter = useCounter();
</script>

<button onclick={counter.increment}>
  {counter.count} (double: {counter.double})
</button>
```

### Why getters?

Returning `count` directly would capture the value at call time. Getters ensure the consumer always reads the current reactive value.

## Slots to Snippets

```svelte
<!-- Svelte 4: Card.svelte -->
<div class="card">
  <header><slot name="header" /></header>
  <slot />
  <footer><slot name="footer" /></footer>
</div>

<!-- Svelte 4 usage -->
<Card>
  <h2 slot="header">Title</h2>
  <p>Content here</p>
  <span slot="footer">Footer</span>
</Card>
```

```svelte
<!-- Svelte 5: Card.svelte -->
<script lang="ts">
  import { type Snippet } from 'svelte';

  let { header, children, footer }: {
    header?: Snippet;
    children: Snippet;
    footer?: Snippet;
  } = $props();
</script>

<div class="card">
  {#if header}
    <header>{@render header()}</header>
  {/if}
  {@render children()}
  {#if footer}
    <footer>{@render footer()}</footer>
  {/if}
</div>

<!-- Svelte 5 usage -->
<Card>
  {#snippet header()}
    <h2>Title</h2>
  {/snippet}

  <p>Content here</p>

  {#snippet footer()}
    <span>Footer</span>
  {/snippet}
</Card>
```

## Events: on: to Properties

```svelte
<!-- Svelte 4 -->
<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
</script>

<button on:click={() => dispatch('submit', { value: 42 })}>
  Submit
</button>

<!-- Svelte 4 parent -->
<Child on:submit={(e) => console.log(e.detail.value)} />
```

```svelte
<!-- Svelte 5 -->
<script lang="ts">
  let { onsubmit }: { onsubmit: (value: number) => void } = $props();
</script>

<button onclick={() => onsubmit(42)}>
  Submit
</button>

<!-- Svelte 5 parent -->
<Child onsubmit={(value) => console.log(value)} />
```

## Event Modifiers

Svelte 4 event modifiers (`on:click|preventDefault|stopPropagation`) are replaced by explicit wrapper functions.

```svelte
<!-- Svelte 4 -->
<form on:submit|preventDefault={handleSubmit}>
<button on:click|once|capture={handleClick}>
```

```svelte
<!-- Svelte 5 -->
<form onsubmit={(e) => {
  e.preventDefault();
  handleSubmit(e);
}}>

<!-- For once/capture, use addEventListener in $effect -->
<script>
  let button: HTMLButtonElement;

  $effect(() => {
    button.addEventListener('click', handleClick, { once: true, capture: true });
  });
</script>

<button bind:this={button}>Click</button>
```

## beforeUpdate / afterUpdate to $effect

```svelte
<!-- Svelte 4 -->
<script>
  import { beforeUpdate, afterUpdate } from 'svelte';

  beforeUpdate(() => { /* before DOM update */ });
  afterUpdate(() => { /* after DOM update */ });
</script>
```

```svelte
<!-- Svelte 5 -->
<script>
  $effect.pre(() => { /* before DOM update */ });
  $effect(() => { /* after DOM update */ });
</script>
```

## Lifecycle: onMount, onDestroy

`onMount` and `onDestroy` still work in Svelte 5. However, `$effect` with a cleanup function can often replace `onDestroy`.

```svelte
<script>
  import { onMount } from 'svelte';

  onMount(() => {
    const interval = setInterval(() => tick(), 1000);
    return () => clearInterval(interval);
  });

  // Or equivalently with $effect:
  $effect(() => {
    const interval = setInterval(() => tick(), 1000);
    return () => clearInterval(interval);
  });
</script>
```

## Migration CLI Tool

Svelte provides an automated migration tool that handles most mechanical changes.

```bash
npx sv migrate svelte-5
```

This handles renaming `on:event` to `onevent`, converting `export let` to `$props()`, and other syntax changes. Review the output manually for stores-to-runes and slots-to-snippets migrations, which require structural changes.
