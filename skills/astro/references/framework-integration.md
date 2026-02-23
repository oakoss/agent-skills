---
title: Framework Integration
description: Using React, Svelte, and Vue components in Astro, adding integrations, passing props, sharing state, and slots
tags:
  [react, svelte, vue, integration, framework, components, slots, props, state]
---

# Framework Integration

Astro supports React, Svelte, Vue, Solid, Preact, and Lit components. Framework components are auto-detected by file extension.

## Adding Framework Support

```bash
npx astro add react
npx astro add svelte
npx astro add vue
```

This installs the framework package and Astro integration, and updates `astro.config.mjs`:

```ts
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import svelte from '@astrojs/svelte';
import vue from '@astrojs/vue';

export default defineConfig({
  integrations: [react(), svelte(), vue()],
});
```

## Using Framework Components

Import and use components in `.astro` files. Without a `client:` directive, they render to static HTML with no JavaScript.

```astro
---
import ReactCard from '../components/ReactCard.jsx';
import SvelteToggle from '../components/SvelteToggle.svelte';
import VueModal from '../components/VueModal.vue';
---
<ReactCard title="Static React" />
<SvelteToggle client:idle />
<VueModal client:visible />
```

## Passing Props

Serializable values can be passed as props. Functions, classes, and other non-serializable values cannot cross the server/client boundary.

```astro
---
import Counter from '../components/Counter.jsx';

const items = [
  { id: 1, name: 'Item A' },
  { id: 2, name: 'Item B' },
];
---
<Counter
  client:idle
  initialCount={0}
  items={items}
  label="Click count"
/>
```

## Slots and Children

### Default Slot

```astro
---
import Wrapper from '../components/Wrapper.jsx';
---
<Wrapper client:idle>
  <p>This becomes children in React or default slot in Vue/Svelte.</p>
</Wrapper>
```

React component receiving children:

```tsx
type WrapperProps = {
  children: React.ReactNode;
};

export default function Wrapper({ children }: WrapperProps) {
  return <div className="wrapper">{children}</div>;
}
```

### Named Slots

Named slots work with Svelte and Vue components.

```astro
---
import Layout from '../components/Layout.svelte';
---
<Layout client:idle>
  <h1 slot="header">Page Title</h1>
  <p>Main content goes here.</p>
  <footer slot="footer">Footer content</footer>
</Layout>
```

Svelte component:

```svelte
<div>
  <header><slot name="header" /></header>
  <main><slot /></main>
  <footer><slot name="footer" /></footer>
</div>
```

## Sharing State Between Islands

Islands are isolated by default. Use nano stores for shared reactive state across framework boundaries.

```bash
npm install nanostores @nanostores/react @nanostores/vue
```

Define a shared store:

```ts
import { atom } from 'nanostores';

export const cartCount = atom(0);

export function addToCart() {
  cartCount.set(cartCount.get() + 1);
}
```

React island:

```tsx
import { useStore } from '@nanostores/react';
import { cartCount, addToCart } from '../stores/cart';

export default function AddToCartButton() {
  const count = useStore(cartCount);
  return <button onClick={addToCart}>Add to Cart ({count})</button>;
}
```

Vue island:

```vue
<script setup lang="ts">
import { useStore } from '@nanostores/vue';
import { cartCount } from '../stores/cart';

const count = useStore(cartCount);
</script>

<template>
  <span>Cart: {{ count }}</span>
</template>
```

## React with TypeScript

Use `.tsx` extension for React components with TypeScript.

```tsx
type CardProps = {
  title: string;
  description: string;
  href?: string;
};

export default function Card({ title, description, href }: CardProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p>{description}</p>
      {href ? <a href={href}>Learn more</a> : null}
    </div>
  );
}
```

## Common Integrations

```bash
npx astro add tailwind
npx astro add mdx
npx astro add sitemap
npx astro add db
npx astro add partytown
```

```ts
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [react(), tailwind(), mdx(), sitemap()],
});
```
