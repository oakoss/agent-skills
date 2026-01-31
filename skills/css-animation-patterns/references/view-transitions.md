---
title: View Transitions API
description: View Transitions API, document.startViewTransition, view-transition-name, cross-document transitions
tags:
  [
    view-transition,
    startViewTransition,
    view-transition-name,
    cross-document,
    SPA,
    MPA,
    snapshot,
  ]
---

# View Transitions API

## Overview

The View Transitions API creates animated transitions between DOM states by capturing snapshots of the old and new states and cross-fading between them. It works for both same-document (SPA) and cross-document (MPA) navigation.

Same-document view transitions are Baseline across all major browsers. Cross-document view transitions work in Chrome and Safari but are not yet supported in Firefox.

## Same-Document View Transitions (SPA)

### Basic Usage

```ts
async function updateContent(newData: string) {
  const transition = document.startViewTransition(() => {
    document.querySelector('.content')!.innerHTML = newData;
  });

  await transition.finished;
}
```

The callback passed to `startViewTransition()` performs the DOM update. The browser:

1. Captures a snapshot of the old state
2. Runs the callback to update the DOM
3. Captures a snapshot of the new state
4. Cross-fades between the snapshots

### With Async Updates

```ts
const transition = document.startViewTransition(async () => {
  const data = await fetchNewContent();
  renderContent(data);
});
```

### ViewTransition Object

```ts
const transition = document.startViewTransition(updateDOM);

transition.ready.then(() => {
  // Snapshots captured, animation about to start
});

transition.updateCallbackDone.then(() => {
  // DOM update callback has completed
});

transition.finished.then(() => {
  // Transition animation has completed
});
```

## Naming Elements for Independent Transitions

By default, the entire page cross-fades as a single group. Use `view-transition-name` to identify elements that should transition independently.

```css
.hero-image {
  view-transition-name: hero;
}

.page-title {
  view-transition-name: title;
}
```

Each named element gets its own snapshot group, enabling independent position and size animations between states.

### Rules for `view-transition-name`

- Each value must be unique on the page at the time of snapshot capture
- The value `none` disables view transition participation
- The special value `match-element` auto-generates unique names, useful for lists

```css
.list-item {
  view-transition-name: match-element;
}
```

## Styling View Transitions

View transitions create a pseudo-element tree that can be styled with CSS.

### Pseudo-Element Structure

```text
::view-transition
  ::view-transition-group(name)
    ::view-transition-image-pair(name)
      ::view-transition-old(name)
      ::view-transition-new(name)
```

### Custom Transition Animation

```css
::view-transition-old(hero) {
  animation: fade-out 300ms ease-out;
}

::view-transition-new(hero) {
  animation: fade-in 300ms ease-out;
}

@keyframes fade-out {
  to {
    opacity: 0;
    transform: scale(0.9);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(1.1);
  }
}
```

### Controlling Duration and Easing

```css
::view-transition-group(hero) {
  animation-duration: 400ms;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Slide Transition

```css
@keyframes slide-out-left {
  to {
    transform: translateX(-100%);
  }
}

@keyframes slide-in-right {
  from {
    transform: translateX(100%);
  }
}

::view-transition-old(root) {
  animation: slide-out-left 300ms ease-in-out;
}

::view-transition-new(root) {
  animation: slide-in-right 300ms ease-in-out;
}
```

## View Transition Classes

The `view-transition-class` property groups multiple named elements to share transition styles without targeting each name individually.

```css
.card {
  view-transition-name: match-element;
  view-transition-class: card;
}

::view-transition-group(*.card) {
  animation-duration: 300ms;
  animation-timing-function: ease-out;
}
```

The `*.card` selector matches all view transition groups with the `card` class.

## View Transition Types

Types allow conditional styling based on the kind of navigation.

```ts
document.startViewTransition({
  update: updateDOM,
  types: ['slide-forward'],
});
```

```css
html:active-view-transition-type(slide-forward) {
  &::view-transition-old(root) {
    animation: slide-out-left 300ms ease-in-out;
  }
  &::view-transition-new(root) {
    animation: slide-in-right 300ms ease-in-out;
  }
}

html:active-view-transition-type(slide-back) {
  &::view-transition-old(root) {
    animation: slide-out-right 300ms ease-in-out;
  }
  &::view-transition-new(root) {
    animation: slide-in-left 300ms ease-in-out;
  }
}
```

## Cross-Document View Transitions (MPA)

Cross-document view transitions animate navigations between separate HTML pages on the same origin.

### Opt-In via CSS

Both the source and destination pages must opt in:

```css
@view-transition {
  navigation: auto;
}
```

### Naming Elements Across Pages

Elements with matching `view-transition-name` values on both pages will animate between their positions.

```css
/* Page A */
.product-image {
  view-transition-name: product;
}

/* Page B */
.product-detail-image {
  view-transition-name: product;
}
```

### Customizing Cross-Document Transitions

```css
@view-transition {
  navigation: auto;
}

::view-transition-group(product) {
  animation-duration: 400ms;
}

::view-transition-old(root) {
  animation: fade-out 200ms ease-out;
}

::view-transition-new(root) {
  animation: fade-in 200ms ease-out;
}
```

### Page Lifecycle Events

```ts
window.addEventListener('pagereveal', (event) => {
  const transition = (event as PageRevealEvent).viewTransition;
  if (transition) {
    // Customize the incoming transition
  }
});

window.addEventListener('pageswap', (event) => {
  const transition = (event as PageSwapEvent).viewTransition;
  if (transition) {
    // Customize the outgoing transition
  }
});
```

## Framework Integration

### React with `flushSync`

React batches state updates asynchronously. Use `flushSync` to ensure the DOM updates synchronously within the view transition callback.

```tsx
import { flushSync } from 'react-dom';

function NavigationLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (!document.startViewTransition) {
      navigate(to);
      return;
    }

    document.startViewTransition(() => {
      flushSync(() => {
        navigate(to);
      });
    });
  };

  return <a onClick={handleClick}>{children}</a>;
}
```

### Conditional Application of `view-transition-name`

Assign `view-transition-name` dynamically to avoid uniqueness conflicts:

```tsx
function ProductCard({
  product,
  isActive,
}: {
  product: Product;
  isActive: boolean;
}) {
  return (
    <div
      style={{
        viewTransitionName: isActive ? 'product-hero' : 'none',
      }}
    >
      <img src={product.image} alt={product.name} />
    </div>
  );
}
```

## Progressive Enhancement

Always check for API support before using view transitions.

```ts
function navigateWithTransition(updateFn: () => void) {
  if (!document.startViewTransition) {
    updateFn();
    return;
  }

  document.startViewTransition(updateFn);
}
```

### Feature Detection in CSS

```css
@supports (view-transition-name: test) {
  .hero {
    view-transition-name: hero;
  }
}
```

## Accessibility

Disable view transition animations for users who prefer reduced motion.

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation: none !important;
  }
}
```

## Active View Transition Selector

The `:active-view-transition` pseudo-class matches the root element while a view transition is running, useful for preventing interactions during transitions.

```css
html:active-view-transition {
  pointer-events: none;
}
```
