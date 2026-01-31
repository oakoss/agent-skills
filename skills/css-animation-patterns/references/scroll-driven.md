---
title: Scroll-Driven Animations
description: Scroll-timeline, view-timeline, animation-timeline, scroll(), view(), IntersectionObserver fallbacks
tags:
  [
    scroll-timeline,
    view-timeline,
    animation-timeline,
    scroll,
    view,
    scroll-driven,
    intersection-observer,
  ]
---

# Scroll-Driven Animations

## Overview

Scroll-driven animations link CSS keyframe animations to scroll position instead of time. They run on the compositor thread, avoiding main-thread jank that JavaScript scroll listeners produce.

Two timeline types exist:

- **Scroll progress timeline** (`scroll()`): Tracks how far a container has scrolled
- **View progress timeline** (`view()`): Tracks an element's visibility within a scrollport

## Scroll Progress Timeline

The `scroll()` function creates an anonymous timeline tied to a scrolling container's position.

### Basic Scroll Progress

```css
@keyframes progress-bar {
  from {
    transform: scaleX(0);
  }
  to {
    transform: scaleX(1);
  }
}

.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent);
  transform-origin: left;
  animation: progress-bar linear both;
  animation-timeline: scroll();
}
```

### `scroll()` Parameters

```css
.element {
  animation-timeline: scroll(<scroller> <axis>);
}
```

| Parameter    | Values                      | Default   |
| ------------ | --------------------------- | --------- |
| `<scroller>` | `nearest`, `root`, `self`   | `nearest` |
| `<axis>`     | `block`, `inline`, `x`, `y` | `block`   |

```css
.parallax-bg {
  animation: parallax linear both;
  animation-timeline: scroll(root block);
}

@keyframes parallax {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-200px);
  }
}
```

### Named Scroll Timeline

Named timelines allow one container's scroll to drive animations on distant elements.

```css
.scroll-container {
  scroll-timeline-name: --main-scroll;
  scroll-timeline-axis: block;
  overflow-y: auto;
}

.distant-element {
  animation: fade-in linear both;
  animation-timeline: --main-scroll;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
```

## View Progress Timeline

The `view()` function creates a timeline based on an element's visibility within its nearest scroll container.

### Basic Reveal Animation

```css
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

### `view()` Parameters

```css
.element {
  animation-timeline: view(<axis> <inset>);
}
```

| Parameter | Values                                       | Default |
| --------- | -------------------------------------------- | ------- |
| `<axis>`  | `block`, `inline`, `x`, `y`                  | `block` |
| `<inset>` | `<length-percentage>` (start and end insets) | `auto`  |

```css
.element {
  animation-timeline: view(block 20% 10%);
}
```

The insets adjust the visibility box. A `20%` start inset means the element's visibility timeline begins when it is 20% into the scrollport from the entry edge.

### Named View Timeline

```css
.observed-element {
  view-timeline-name: --card-visibility;
  view-timeline-axis: block;
}

.related-indicator {
  animation: highlight linear both;
  animation-timeline: --card-visibility;
}

@keyframes highlight {
  from {
    background-color: transparent;
  }
  to {
    background-color: var(--highlight);
  }
}
```

## Animation Range

The `animation-range` property controls which portion of the timeline drives the animation.

### Range Keywords

| Keyword          | When                                                            |
| ---------------- | --------------------------------------------------------------- |
| `cover`          | Full visibility range, from first visible pixel to fully exited |
| `contain`        | Element is fully visible inside the scrollport                  |
| `entry`          | Element entering the scrollport                                 |
| `exit`           | Element exiting the scrollport                                  |
| `entry-crossing` | Element's leading edge crossing the entry edge                  |
| `exit-crossing`  | Element's trailing edge crossing the exit edge                  |

### Range Syntax

```css
.element {
  animation-range: entry 0% entry 100%;
}

.element-full {
  animation-range: cover 0% cover 100%;
}

.element-partial {
  animation-range: entry 25% cover 50%;
}
```

### Shorthand Examples

```css
.fade-in-on-entry {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry;
}

.fade-out-on-exit {
  animation: fade-out linear both;
  animation-timeline: view();
  animation-range: exit;
}
```

## Duration and Timing

Scroll-driven animations are controlled by scroll position, not time. The `animation-duration` is effectively ignored, but browsers may require it to be non-zero.

```css
.element {
  animation: reveal linear both;
  animation-timeline: view();
}
```

Use `linear` as the timing function since the scroll position already provides the progression. Non-linear easing can still be used for stylistic effect within the scroll range.

## Practical Patterns

### Parallax Background

```css
.hero {
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: -20% 0;
  animation: parallax-shift linear both;
  animation-timeline: scroll(root);
}

@keyframes parallax-shift {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-15%);
  }
}
```

### Sticky Header Shrink

```css
.header {
  position: sticky;
  top: 0;
  animation: shrink-header linear both;
  animation-timeline: scroll(root);
  animation-range: 0px 200px;
}

@keyframes shrink-header {
  from {
    padding-block: 1.5rem;
  }
  to {
    padding-block: 0.5rem;
  }
}
```

### Staggered Reveal

```css
.grid-item {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}

.grid-item:nth-child(2) {
  animation-delay: 50ms;
}

.grid-item:nth-child(3) {
  animation-delay: 100ms;
}
```

## Progressive Enhancement

Scroll-driven animations are not supported in all browsers. Always provide fallback styles.

### Feature Detection in CSS

```css
.card {
  opacity: 1;
  transform: none;
}

@supports (animation-timeline: view()) {
  .card {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry;
  }
}
```

### IntersectionObserver Fallback

```ts
function setupRevealFallback(selector: string) {
  if (CSS.supports('animation-timeline', 'view()')) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  document.querySelectorAll(selector).forEach((el) => observer.observe(el));
}

setupRevealFallback('.card');
```

```css
.card {
  opacity: 0;
  transform: translateY(40px);
  transition:
    opacity 400ms ease-out,
    transform 400ms ease-out;
}

.card.revealed {
  opacity: 1;
  transform: translateY(0);
}
```

## Accessibility

Always disable scroll-driven animations for users who prefer reduced motion.

```css
@media (prefers-reduced-motion: reduce) {
  .card {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

## Key Ordering Rule

The `animation` shorthand resets `animation-timeline` to `auto`. Always declare `animation-timeline` after `animation`.

```css
.element {
  animation: reveal linear both;
  animation-timeline: view();
}
```
