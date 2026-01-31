---
title: Transitions and Keyframes
description: CSS transitions, @keyframes, animation properties, timing functions, animation composition
tags:
  [
    transition,
    keyframes,
    animation,
    timing-function,
    easing,
    cubic-bezier,
    fill-mode,
    composition,
  ]
---

# Transitions and Keyframes

## CSS Transitions

Transitions animate property changes between two states. They require a trigger (hover, class toggle, media query change).

### Transition Shorthand

```css
.card {
  transition:
    transform 200ms ease-out,
    opacity 200ms ease-out;
}

.card:hover {
  transform: translateY(-4px);
  opacity: 0.9;
}
```

### Individual Properties

```css
.element {
  transition-property: transform, opacity;
  transition-duration: 300ms;
  transition-timing-function: ease-in-out;
  transition-delay: 0ms;
}
```

### Transition Behavior for Discrete Properties

The `transition-behavior` property enables transitions on discrete properties like `display` and `visibility`.

```css
.tooltip {
  opacity: 0;
  display: none;
  transition:
    opacity 200ms ease-out,
    display 200ms ease-out allow-discrete;
}

.tooltip.visible {
  opacity: 1;
  display: block;
}
```

The `allow-discrete` keyword tells the browser to flip `display` at the right moment in the transition.

### Starting Style

The `@starting-style` rule defines the initial state for transitions when an element first appears in the DOM or transitions from `display: none`.

```css
.dialog {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 300ms ease-out,
    transform 300ms ease-out;

  @starting-style {
    opacity: 0;
    transform: translateY(20px);
  }
}
```

## Keyframe Animations

Keyframes define multi-step animation sequences that run independently of state changes.

### Basic Keyframe

```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.element {
  animation: fade-in 300ms ease-out;
}
```

### Multi-Step Keyframe

```css
@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
  80% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
  }
}
```

### Animation Shorthand

```css
.element {
  animation: bounce 600ms cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}
```

Order: `name` `duration` `timing-function` `delay` `iteration-count` `direction` `fill-mode` `play-state`.

### Individual Animation Properties

```css
.spinner {
  animation-name: spin;
  animation-duration: 1s;
  animation-timing-function: linear;
  animation-delay: 0ms;
  animation-iteration-count: infinite;
  animation-direction: normal;
  animation-fill-mode: none;
  animation-play-state: running;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

## Fill Modes

| Value       | Behavior                                       |
| ----------- | ---------------------------------------------- |
| `none`      | No styles applied before or after animation    |
| `forwards`  | Retains final keyframe values after completion |
| `backwards` | Applies first keyframe values during delay     |
| `both`      | Combines `forwards` and `backwards`            |

```css
.element {
  animation: slide-in 400ms ease-out forwards;
}
```

## Timing Functions

### Built-in Keywords

| Keyword       | Equivalent `cubic-bezier()`        | Use Case                 |
| ------------- | ---------------------------------- | ------------------------ |
| `ease`        | `cubic-bezier(0.25, 0.1, 0.25, 1)` | General purpose, default |
| `ease-in`     | `cubic-bezier(0.42, 0, 1, 1)`      | Elements exiting         |
| `ease-out`    | `cubic-bezier(0, 0, 0.58, 1)`      | Elements entering        |
| `ease-in-out` | `cubic-bezier(0.42, 0, 0.58, 1)`   | Symmetrical motion       |
| `linear`      | `cubic-bezier(0, 0, 1, 1)`         | Constant speed           |

### Custom Cubic Bezier

```css
.element {
  transition: transform 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### The `linear()` Function

The `linear()` function defines a piecewise linear easing with multiple control points, useful for spring-like or complex curves.

```css
.spring {
  transition: transform 600ms
    linear(
      0,
      0.006,
      0.025,
      0.058,
      0.104,
      0.163,
      0.234,
      0.315,
      0.404,
      0.498,
      0.592,
      0.682,
      0.764,
      0.834,
      0.893,
      0.939,
      0.972,
      0.993,
      1.002,
      1.001,
      0.994,
      0.986,
      0.979,
      0.975,
      0.974,
      0.976,
      0.979,
      0.984,
      0.989,
      0.994,
      0.998,
      1.001,
      1.002,
      1.001,
      1
    );
}
```

### Steps

```css
.typewriter {
  animation: typing 3s steps(20, end);
}
```

## Animation Composition

The `animation-composition` property controls how multiple animations combine when targeting the same property.

```css
.element {
  animation:
    move 1s ease-out,
    grow 1s ease-out;
  animation-composition: accumulate;
}

@keyframes move {
  to {
    transform: translateX(100px);
  }
}

@keyframes grow {
  to {
    transform: scale(1.5);
  }
}
```

| Value        | Behavior                                                |
| ------------ | ------------------------------------------------------- |
| `replace`    | Animation value replaces the underlying value (default) |
| `add`        | Animation value is added to the underlying value        |
| `accumulate` | Animation value is combined with the underlying value   |

## Staggered Animations with Custom Properties

```css
.list-item {
  animation: fade-slide-in 400ms ease-out backwards;
  animation-delay: calc(var(--index) * 60ms);
}
```

```html
<ul>
  <li class="list-item" style="--index: 0">First</li>
  <li class="list-item" style="--index: 1">Second</li>
  <li class="list-item" style="--index: 2">Third</li>
</ul>
```

```css
@keyframes fade-slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
}
```

## Accessibility: Reduced Motion

Always provide a reduced-motion alternative.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

For more nuanced control, opt in to motion rather than opting out:

```css
.element {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: no-preference) {
  .element {
    animation: fade-in 300ms ease-out;
  }
}
```

## Controlling Animations with JavaScript

```ts
const element = document.querySelector('.animated');

element.addEventListener('animationend', () => {
  element.classList.remove('animate');
});

element.addEventListener('transitionend', () => {
  element.classList.add('settled');
});
```

### Web Animations API Integration

```ts
const animation = element.animate(
  [
    { transform: 'translateX(0)', opacity: 1 },
    { transform: 'translateX(100px)', opacity: 0 },
  ],
  { duration: 300, easing: 'ease-out', fill: 'forwards' },
);

await animation.finished;
```
