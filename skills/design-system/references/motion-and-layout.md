---
title: Motion and Layout
description: Animation tokens and timing, reduced motion support, 8pt spacing grid, visual hierarchy principles, and shadow elevation system
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
  ]
---

# Motion and Layout

## Animation Tokens

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
}

.button {
  transition: all var(--duration-fast) var(--ease-in-out);
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

Use `transform` and `opacity` for GPU acceleration. Never animate `width`, `height`, or `top`/`left`.

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 8pt Spacing Grid

```css
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
```

Most screens are divisible by 8, creating consistent visual rhythm.

## Visual Hierarchy

Establish importance through four tools:

1. **Size** — larger = more important
2. **Weight** — bolder = more important
3. **Color** — brighter/saturated = more important
4. **Space** — more whitespace = more important

## Shadow Elevation System

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05); /* Buttons, inputs */
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1); /* Cards */
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1); /* Dropdowns */
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15); /* Modals */
```

Higher elevation = more shadow. Use consistently to communicate depth and importance.
