---
title: Island Architecture
description: Hydration directives, choosing the right directive, island patterns, and when to avoid islands
tags:
  [
    islands,
    hydration,
    client:load,
    client:idle,
    client:visible,
    client:media,
    client:only,
    interactive,
  ]
---

# Island Architecture

Astro renders all components to static HTML by default. Interactive "islands" are created by adding a `client:` directive to UI framework components (React, Svelte, Vue, Solid, Preact). Astro ships zero JavaScript unless a `client:` directive is explicitly used.

## Hydration Directives

### client:load

Hydrates immediately when the page loads. Use for above-the-fold interactive elements that must be ready instantly.

```astro
---
import Navigation from '../components/Navigation.jsx';
---
<Navigation client:load />
```

### client:idle

Hydrates once the browser is idle (uses `requestIdleCallback`). Best default choice for most interactive components.

```astro
---
import Newsletter from '../components/Newsletter.jsx';
---
<Newsletter client:idle />
```

### client:visible

Hydrates when the component scrolls into the viewport (uses `IntersectionObserver`). Ideal for below-the-fold content.

```astro
---
import Comments from '../components/Comments.jsx';
---
<Comments client:visible />
```

### client:media

Hydrates when a CSS media query matches. Useful for mobile-only or desktop-only interactive components.

```astro
---
import MobileMenu from '../components/MobileMenu.jsx';
---
<MobileMenu client:media="(max-width: 768px)" />
```

### client:only

Skips server-side rendering entirely. The component renders only on the client. Must specify the framework as a string value.

```astro
---
import BrowserOnlyChart from '../components/BrowserOnlyChart.jsx';
---
<BrowserOnlyChart client:only="react" />
```

## Choosing the Right Directive

| Priority           | Directive        | Example Use Case                      |
| ------------------ | ---------------- | ------------------------------------- |
| Critical (instant) | `client:load`    | Auth state, navigation, hero CTA      |
| Standard           | `client:idle`    | Newsletter signup, search bar         |
| Deferred           | `client:visible` | Comments, footer widgets, carousels   |
| Conditional        | `client:media`   | Mobile hamburger menu                 |
| No SSR             | `client:only`    | Browser API dependent (canvas, WebGL) |

## Mixing Frameworks

Only `.astro` files can contain components from multiple UI frameworks in the same template.

```astro
---
import ReactCounter from '../components/ReactCounter.jsx';
import SvelteToggle from '../components/SvelteToggle.svelte';
import VueCard from '../components/VueCard.vue';
---
<div>
  <ReactCounter client:idle initialCount={0} />
  <SvelteToggle client:visible />
  <VueCard client:idle title="Hello from Vue" />
</div>
```

## Nesting Framework Components

Framework components can be nested as children within other framework components from the same or different framework.

```astro
---
import ReactSidebar from '../components/ReactSidebar.jsx';
import ReactButton from '../components/ReactButton.jsx';
import SvelteButton from '../components/SvelteButton.svelte';
---
<ReactSidebar client:idle>
  <p>Static content passed as children.</p>
  <div slot="actions">
    <ReactButton client:idle />
    <SvelteButton client:idle />
  </div>
</ReactSidebar>
```

## Passing Data to Islands

Islands receive props just like regular components. Only serializable data can be passed across the server/client boundary.

```astro
---
import { getCollection } from 'astro:content';
import PostFilter from '../components/PostFilter.jsx';

const posts = await getCollection('blog');
const tags = [...new Set(posts.flatMap((p) => p.data.tags))];
---
<PostFilter client:idle tags={tags} postCount={posts.length} />
```

## Server Islands

Server islands defer rendering of specific components to after the initial page response. The static HTML shell loads first, then the server island streams in.

```astro
---
import UserGreeting from '../components/UserGreeting.astro';
import ProductRecommendations from '../components/ProductRecommendations.astro';
---
<h1>Welcome to our store</h1>

<UserGreeting server:defer>
  <p slot="fallback">Loading user info...</p>
</UserGreeting>

<ProductRecommendations server:defer>
  <div slot="fallback" class="skeleton" />
</ProductRecommendations>
```

## Static Components (No Directive)

Without a `client:` directive, framework components render to static HTML at build time with zero client-side JavaScript.

```astro
---
import Card from '../components/Card.jsx';
---
<Card title="Static" description="No JavaScript shipped for this component." />
```
