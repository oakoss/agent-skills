---
title: Component Patterns
description: Snippets, rendering, slots migration, each blocks, await blocks, and component composition in Svelte 5
tags: [snippets, render, each, await, slots, children, composition, conditional]
---

# Component Patterns

## Snippets

Snippets replace slots in Svelte 5. They are reusable template blocks defined with `{#snippet}` and rendered with `{@render}`.

### Basic snippet

```svelte
{#snippet greeting(name)}
  <p>Hello, {name}!</p>
{/snippet}

{@render greeting('Alice')}
{@render greeting('Bob')}
```

### Children snippet (replaces default slot)

Components receive children content as a `children` snippet prop.

```svelte
<!-- Card.svelte -->
<script lang="ts">
  import { type Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();
</script>

<div class="card">
  {@render children()}
</div>
```

```svelte
<!-- Usage -->
<Card>
  <p>This is the card content</p>
</Card>
```

### Named snippets (replaces named slots)

```svelte
<!-- Dialog.svelte -->
<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props {
    header: Snippet;
    children: Snippet;
    footer?: Snippet;
  }

  let { header, children, footer }: Props = $props();
</script>

<div class="dialog">
  <header>{@render header()}</header>
  <main>{@render children()}</main>
  {#if footer}
    <footer>{@render footer()}</footer>
  {/if}
</div>
```

```svelte
<!-- Usage -->
<Dialog>
  {#snippet header()}
    <h2>Confirm Action</h2>
  {/snippet}

  <p>Are you sure?</p>

  {#snippet footer()}
    <button onclick={confirm}>Yes</button>
    <button onclick={cancel}>No</button>
  {/snippet}
</Dialog>
```

### Snippets with typed parameters

```svelte
<script lang="ts">
  import { type Snippet } from 'svelte';

  interface Props<T> {
    items: T[];
    row: Snippet<[T, number]>;
    empty?: Snippet;
  }

  let { items, row, empty }: Props<any> = $props();
</script>

{#if items.length === 0}
  {#if empty}
    {@render empty()}
  {:else}
    <p>No items</p>
  {/if}
{:else}
  {#each items as item, index (index)}
    {@render row(item, index)}
  {/each}
{/if}
```

## Each Blocks

Iterate over arrays. Always provide a key expression for efficient DOM updates.

```svelte
<script>
  let todos = $state([
    { id: 1, text: 'Learn Svelte 5', done: false },
    { id: 2, text: 'Build an app', done: false }
  ]);
</script>

{#each todos as todo (todo.id)}
  <label>
    <input type="checkbox" bind:checked={todo.done} />
    <span class:done={todo.done}>{todo.text}</span>
  </label>
{:else}
  <p>No todos yet</p>
{/each}
```

### Destructured each

```svelte
{#each users as { name, email, avatar } (email)}
  <div class="user">
    <img src={avatar} alt={name} />
    <p>{name} ({email})</p>
  </div>
{/each}
```

## Await Blocks

Handle promises directly in templates.

```svelte
<script>
  let promise = $state(fetch('/api/data').then((r) => r.json()));
</script>

{#await promise}
  <p>Loading...</p>
{:then data}
  <pre>{JSON.stringify(data, null, 2)}</pre>
{:catch error}
  <p>Error: {error.message}</p>
{/await}
```

### Short form (no loading state)

```svelte
{#await promise then data}
  <p>{data.message}</p>
{/await}
```

## Conditional Rendering

```svelte
{#if user.role === 'admin'}
  <AdminPanel />
{:else if user.role === 'editor'}
  <EditorPanel />
{:else}
  <ViewerPanel />
{/if}
```

## Event Handling

Svelte 5 uses standard DOM property names. No more `on:` directive.

```svelte
<script lang="ts">
  let count = $state(0);

  function handleClick(event: MouseEvent) {
    count++;
  }
</script>

<button onclick={handleClick}>Clicked {count} times</button>

<!-- Inline handler -->
<button onclick={() => count++}>Increment</button>

<!-- Multiple handlers via spread -->
<button onclick={(e) => { handleClick(e); logClick(e); }}>Both</button>
```

### Callback props (replaces createEventDispatcher)

```svelte
<!-- ChildComponent.svelte -->
<script lang="ts">
  let { onsubmit }: { onsubmit: (data: FormData) => void } = $props();
</script>

<form onsubmit={(e) => {
  e.preventDefault();
  onsubmit(new FormData(e.currentTarget));
}}>
  <input name="email" type="email" />
  <button>Submit</button>
</form>
```

```svelte
<!-- Parent -->
<ChildComponent onsubmit={(data) => console.log(data.get('email'))} />
```

## Dynamic Components

```svelte
<script>
  import Home from './Home.svelte';
  import About from './About.svelte';

  const routes = { home: Home, about: About } as const;
  let current = $state<keyof typeof routes>('home');
</script>

<svelte:component this={routes[current]} />

<nav>
  <button onclick={() => current = 'home'}>Home</button>
  <button onclick={() => current = 'about'}>About</button>
</nav>
```

## Special Elements

```svelte
<!-- Reactive document title -->
<svelte:head>
  <title>{pageTitle}</title>
  <meta name="description" content={description} />
</svelte:head>

<!-- Window events -->
<svelte:window onkeydown={handleKeydown} bind:scrollY={y} />

<!-- Body classes -->
<svelte:body onmouseenter={handleMouseEnter} />

<!-- Self-referencing for recursive components -->
<svelte:self count={count - 1} />
```

## Bindings

```svelte
<script>
  let name = $state('');
  let agreed = $state(false);
  let selected = $state('a');
  let textarea = $state('');
  let inputEl: HTMLInputElement;
</script>

<input bind:value={name} />
<input type="checkbox" bind:checked={agreed} />
<select bind:value={selected}>
  <option value="a">A</option>
  <option value="b">B</option>
</select>
<textarea bind:value={textarea}></textarea>
<input bind:this={inputEl} />
```
