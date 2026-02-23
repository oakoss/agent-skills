---
title: View Transitions
description: ClientRouter setup, transition directives, persisting state, programmatic navigation, and lifecycle events
tags:
  [
    view-transitions,
    ClientRouter,
    navigate,
    persist,
    animation,
    SPA,
    client-side-navigation,
  ]
---

# View Transitions

Astro provides built-in view transitions via the `<ClientRouter />` component, enabling SPA-like page navigation without a full page reload. It uses the browser View Transition API with automatic fallback for unsupported browsers.

## Setup

Add `<ClientRouter />` to the `<head>` of your layout to enable view transitions site-wide.

```astro
---
import { ClientRouter } from 'astro:transitions';
---
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{Astro.props.title}</title>
    <ClientRouter />
  </head>
  <body>
    <slot />
  </body>
</html>
```

## Transition Directives

### transition:name

Assign a unique name to pair elements across pages for animated transitions.

```astro
<h1 transition:name="page-title">{post.data.title}</h1>
<img transition:name={`hero-${post.id}`} src={post.data.image.url} alt="" />
```

### transition:animate

Control the animation style for a transitioning element.

```astro
<header transition:animate="none">
  <nav>...</nav>
</header>

<main transition:animate="slide">
  <slot />
</main>

<aside transition:animate="fade">
  <slot name="sidebar" />
</aside>
```

Built-in animations: `initial` (default), `fade`, `slide`, `none`.

### transition:persist

Maintain an island component's DOM and state across navigations instead of replacing it.

```astro
<AudioPlayer client:load transition:persist />
<VideoPlayer client:load transition:persist="media-player" />
```

The component must appear on both the old and new page with the same `transition:persist` value.

## Programmatic Navigation

```astro
<script>
  import { navigate } from 'astro:transitions/client';

  document.querySelector('#search-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = new FormData(e.currentTarget).get('q');
    navigate(`/search?q=${encodeURIComponent(String(query))}`);
  });
</script>
```

### Navigate Options

```ts
import { navigate } from 'astro:transitions/client';

navigate('/dashboard', { history: 'replace' });
```

Options for `history`: `'auto'` (default), `'push'`, `'replace'`.

## Lifecycle Events

Listen for view transition events on the `document`.

```astro
<script>
  document.addEventListener('astro:before-preparation', (event) => {
    const { to, from } = event;
  });

  document.addEventListener('astro:after-preparation', () => {});

  document.addEventListener('astro:before-swap', (event) => {
    event.newDocument.querySelector('html')?.classList.add('transition-active');
  });

  document.addEventListener('astro:after-swap', () => {});

  document.addEventListener('astro:page-load', () => {});
</script>
```

| Event                      | When it fires                              |
| -------------------------- | ------------------------------------------ |
| `astro:before-preparation` | Before fetching the new page               |
| `astro:after-preparation`  | After fetching, before swap                |
| `astro:before-swap`        | Before replacing the DOM                   |
| `astro:after-swap`         | After DOM swap, before new scripts run     |
| `astro:page-load`          | After page is fully loaded and interactive |

## Script Re-execution

By default, scripts in `<head>` only run once. Use `data-astro-rerun` to re-execute a script on every navigation.

```astro
<script data-astro-rerun>
  document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
</script>
```

## Prefetching

Astro prefetches linked pages automatically when `<ClientRouter />` is active. Control behavior with the `data-astro-prefetch` attribute.

```astro
<a href="/about" data-astro-prefetch>About</a>
<a href="/contact" data-astro-prefetch="hover">Contact</a>
<a href="/dashboard" data-astro-prefetch="viewport">Dashboard</a>
<a href="/admin" data-astro-prefetch="false">Admin (no prefetch)</a>
```

## Fallback Behavior

For browsers that do not support the View Transition API, Astro provides automatic fallback with a standard full-page swap. Configure fallback animation:

```ts
import { defineConfig } from 'astro/config';

export default defineConfig({
  prefetch: {
    defaultStrategy: 'hover',
    prefetchAll: false,
  },
});
```
