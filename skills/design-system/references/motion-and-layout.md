---
title: Motion and Layout
description: Animation tokens and timing, reduced motion support, 8pt spacing grid, responsive layout patterns, visual hierarchy, and shadow elevation system
tags:
  [
    animation,
    motion,
    spacing,
    grid,
    visual-hierarchy,
    shadows,
    elevation,
    reduced-motion,
    responsive,
  ]
---

# Motion and Layout

## Animation Tokens

Define duration and easing as tokens for consistent motion across the system:

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

.button {
  transition: all var(--duration-fast) var(--ease-in-out);
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

### Duration Guidelines

| Duration | Use Case                                    |
| -------- | ------------------------------------------- |
| Fast     | Hover states, color changes, opacity shifts |
| Normal   | Page transitions, content reveals, tooltips |
| Slow     | Full-page animations, complex transitions   |

### Performant Animations

Use `transform` and `opacity` for GPU acceleration. Never animate `width`, `height`, `top`, `left`, or `margin` — these trigger layout recalculation.

```css
/* Good: GPU-accelerated */
.card-hover {
  transition:
    transform var(--duration-fast) var(--ease-out),
    box-shadow var(--duration-fast) var(--ease-out);
}
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Bad: triggers layout */
.card-hover-bad:hover {
  margin-top: -2px;
  height: calc(100% + 2px);
}
```

## Reduced Motion

Respect the user's system preference:

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

For more granular control, check the preference in JavaScript:

```ts
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)',
).matches;
```

## 8pt Spacing Grid

Most screens are divisible by 8, creating consistent visual rhythm:

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem; /* 4px  */
  --space-2: 0.5rem; /* 8px  */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem; /* 16px */
  --space-6: 1.5rem; /* 24px */
  --space-8: 2rem; /* 32px */
  --space-12: 3rem; /* 48px */
  --space-16: 4rem; /* 64px */
  --space-20: 5rem; /* 80px */
  --space-24: 6rem; /* 96px */
}
```

Use spacing tokens for all padding, margin, and gap values. Avoid one-off pixel values.

## Responsive Breakpoints

```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}
```

Use mobile-first media queries (min-width). Test at 375px, 768px, 1024px, and 1440px.

## Visual Hierarchy

Establish importance through four tools:

1. **Size** — larger elements draw attention first
2. **Weight** — bolder text signals importance
3. **Color** — saturated/bright colors attract the eye
4. **Space** — more whitespace around an element elevates its importance

Apply these consistently. A heading that is large, bold, and surrounded by whitespace communicates top-level importance without any additional styling.

## Shadow Elevation System

```css
:root {
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05); /* Buttons, inputs */
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1); /* Cards */
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1); /* Dropdowns */
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.15); /* Modals */
}
```

Higher elevation = more shadow. Use consistently to communicate depth and layer hierarchy. In dark mode, reduce shadow opacity or rely more on surface color differentiation.

## Container Layout Pattern

```css
.container {
  width: 100%;
  max-width: var(--breakpoint-xl);
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 768px) {
  .container {
    padding-inline: var(--space-8);
  }
}
```

Use `margin-inline: auto` and `padding-inline` for logical properties that support RTL layouts.
