---
title: Transforms and Performance
description: CSS transforms, will-change, GPU acceleration, composite-only properties, layout thrashing avoidance
tags:
  [
    transform,
    will-change,
    GPU,
    compositing,
    performance,
    layout-thrashing,
    repaint,
    reflow,
  ]
---

# Transforms and Performance

## CSS Transforms

Transforms modify an element's visual rendering without affecting document layout. They are composited on the GPU, making them ideal for animation.

### 2D Transforms

```css
.card {
  transform: translateX(20px);
}

.icon {
  transform: rotate(45deg);
}

.thumbnail {
  transform: scale(1.1);
}

.combined {
  transform: translate(-50%, -50%) rotate(15deg) scale(0.9);
}
```

### 3D Transforms

```css
.scene {
  perspective: 800px;
}

.card-3d {
  transform: rotateY(180deg);
  transform-style: preserve-3d;
  backface-visibility: hidden;
}
```

### Individual Transform Properties

Modern CSS supports individual transform properties, which are easier to animate independently.

```css
.element {
  translate: 20px 10px;
  rotate: 45deg;
  scale: 1.2;
}

.element:hover {
  translate: 20px -10px;
  rotate: 90deg;
  scale: 1.4;
}
```

These can be transitioned independently with different timings:

```css
.element {
  transition:
    translate 300ms ease-out,
    rotate 500ms ease-in-out,
    scale 200ms ease-out;
}
```

### Transform Origin

```css
.element {
  transform-origin: top left;
  transform: rotate(45deg);
}

.centered {
  transform-origin: center center;
  transform: scale(1.5);
}
```

## The Rendering Pipeline

Understanding the browser rendering pipeline is key to animation performance.

```text
Style -> Layout -> Paint -> Composite
```

| Stage           | Triggered By                                                       | Cost    |
| --------------- | ------------------------------------------------------------------ | ------- |
| Layout (Reflow) | `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` | Highest |
| Paint (Repaint) | `background`, `color`, `border`, `box-shadow`, `border-radius`     | High    |
| Composite       | `transform`, `opacity`, `filter`                                   | Lowest  |

Animating composite-only properties skips Layout and Paint entirely, running on the GPU compositor thread.

## Composite-Only Properties

These properties can be animated without triggering layout or paint:

| Property    | Use Case                           |
| ----------- | ---------------------------------- |
| `transform` | Movement, rotation, scaling        |
| `opacity`   | Fade in/out                        |
| `filter`    | Blur, brightness, contrast effects |

### Movement: Transform vs Position

```css
.slow {
  transition: left 300ms ease-out;
  position: absolute;
  left: 100px;
}

.fast {
  transition: transform 300ms ease-out;
  transform: translateX(100px);
}
```

The `transform` version runs entirely on the compositor thread. The `left` version triggers layout recalculation on every frame.

### Sizing: Transform vs Dimensions

```css
.slow {
  transition:
    width 300ms,
    height 300ms;
  width: 200px;
  height: 200px;
}

.fast {
  transition: transform 300ms;
  transform: scale(2);
}
```

## The `will-change` Property

The `will-change` property hints to the browser that an element will change, prompting it to promote the element to its own compositor layer in advance.

### Correct Usage

```css
.card {
  transition: transform 200ms ease-out;
}

.card:hover {
  will-change: transform;
}

.card:active {
  transform: scale(0.98);
}
```

### Applying and Removing via JavaScript

```ts
const card = document.querySelector('.card');

card.addEventListener('pointerenter', () => {
  card.style.willChange = 'transform';
});

card.addEventListener('transitionend', () => {
  card.style.willChange = 'auto';
});
```

### Common Misuse

```css
*,
*::before,
*::after {
  will-change: transform, opacity;
}
```

This creates compositor layers for every element, consuming significant GPU memory and potentially degrading performance. Each layer requires texture memory on the GPU.

### When to Use `will-change`

| Scenario                                    | Recommendation                                   |
| ------------------------------------------- | ------------------------------------------------ |
| Element animates frequently (hover, scroll) | Apply on parent hover or via JS before animation |
| Element animates once on page load          | Do not use, animation is already optimized       |
| Many elements animate simultaneously        | Apply selectively to the most complex elements   |
| Fixed/sticky elements with transforms       | Consider applying persistently                   |

## Layout Thrashing

Layout thrashing occurs when JavaScript alternates between reading layout properties and writing style changes, forcing the browser to recalculate layout multiple times per frame.

### Problem: Interleaved Reads and Writes

```ts
const items = document.querySelectorAll('.item');

items.forEach((item) => {
  const height = item.offsetHeight;
  item.style.height = `${height * 2}px`;
});
```

### Solution: Batch Reads Then Writes

```ts
const items = document.querySelectorAll('.item');

const heights = Array.from(items, (item) => item.offsetHeight);

items.forEach((item, i) => {
  item.style.height = `${heights[i] * 2}px`;
});
```

### Solution: Use `requestAnimationFrame`

```ts
function updateLayout(element: HTMLElement, newHeight: number) {
  requestAnimationFrame(() => {
    element.style.height = `${newHeight}px`;
  });
}
```

## Properties That Trigger Layout

Avoid animating these properties:

| Property                            | Alternative                       |
| ----------------------------------- | --------------------------------- |
| `width` / `height`                  | `transform: scale()`              |
| `top` / `left` / `right` / `bottom` | `transform: translate()`          |
| `margin`                            | `transform: translate()`          |
| `padding`                           | Inner element with `transform`    |
| `border-width`                      | `box-shadow` or `outline`         |
| `font-size`                         | `transform: scale()` on container |

## Reading Layout Properties Triggers Forced Reflow

These properties and methods force the browser to calculate layout when accessed:

- `offsetTop`, `offsetLeft`, `offsetWidth`, `offsetHeight`
- `scrollTop`, `scrollLeft`, `scrollWidth`, `scrollHeight`
- `clientTop`, `clientLeft`, `clientWidth`, `clientHeight`
- `getComputedStyle()`
- `getBoundingClientRect()`

Cache these values when reading multiple times in a single frame.

## Contain Property for Isolation

The `contain` property limits the browser's rendering scope, preventing changes inside an element from affecting the rest of the page.

```css
.animated-container {
  contain: layout style;
}
```

| Value     | Effect                                                  |
| --------- | ------------------------------------------------------- |
| `layout`  | Element's layout is independent of the rest of the page |
| `paint`   | Element's contents do not render outside its bounds     |
| `style`   | Counters and quotes are scoped to the element           |
| `size`    | Element can be sized without examining its children     |
| `content` | Shorthand for `layout paint style`                      |
| `strict`  | Shorthand for `layout paint style size`                 |

## Content Visibility

The `content-visibility` property skips rendering of off-screen content, improving initial page load and scroll performance.

```css
.section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px;
}
```

The `contain-intrinsic-size` provides a placeholder size so the scrollbar does not jump when content is rendered.

## Performance Debugging

### Chrome DevTools

1. Open Performance panel, enable "Screenshots" and "Web Vitals"
2. Record an animation interaction
3. Look for long frames (red bars) in the Frames section
4. Check the "Rendering" tab > enable "Paint flashing" to see repaint areas
5. Enable "Layer borders" to visualize compositor layers

### Key Metrics

| Metric            | Target                                          |
| ----------------- | ----------------------------------------------- |
| Frame duration    | Under 16.67ms (60fps)                           |
| Paint areas       | Minimal, no full-page repaints during animation |
| Compositor layers | Only elements that need them                    |
| GPU memory        | Monitor in DevTools Layers panel                |
