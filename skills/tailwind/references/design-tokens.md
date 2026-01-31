---
title: Design Tokens
description: Complete Tailwind v4 design token system with OKLCH colors, semantic naming, brand scales, shadows, z-index, motion, fluid typography, and monorepo packages
tags:
  [
    design-tokens,
    oklch,
    semantic-colors,
    fluid-typography,
    monorepo,
    shadows,
    z-index,
  ]
---

# Design Tokens

## Token Hierarchy

Design tokens follow a three-level hierarchy:

1. **Brand tokens** -- Abstract color values (`blue-500`, `brand-400`)
2. **Semantic tokens** -- Purpose-driven names (`primary`, `surface`, `error`)
3. **Component tokens** -- Specific usage (`button-bg`, `input-border`)

Always prefer semantic names over raw values in markup.

## Complete Token System

```css
@import 'tailwindcss';

@theme {
  /* Surface colors */
  --color-surface-primary: oklch(1 0 0);
  --color-surface-secondary: oklch(0.98 0.002 250);
  --color-surface-tertiary: oklch(0.95 0.004 250);
  --color-surface-inverse: oklch(0.15 0.02 250);

  /* Text colors */
  --color-text-primary: oklch(0.15 0.02 250);
  --color-text-secondary: oklch(0.4 0.02 250);
  --color-text-tertiary: oklch(0.55 0.015 250);
  --color-text-inverse: oklch(0.98 0 0);
  --color-text-disabled: oklch(0.7 0.01 250);

  /* Border colors */
  --color-border-default: oklch(0.85 0.01 250);
  --color-border-subtle: oklch(0.92 0.005 250);
  --color-border-strong: oklch(0.7 0.02 250);

  /* Status colors */
  --color-success: oklch(0.6 0.18 145);
  --color-success-subtle: oklch(0.95 0.04 145);
  --color-warning: oklch(0.75 0.18 85);
  --color-warning-subtle: oklch(0.95 0.06 85);
  --color-error: oklch(0.55 0.22 25);
  --color-error-subtle: oklch(0.95 0.04 25);
  --color-info: oklch(0.6 0.18 250);
  --color-info-subtle: oklch(0.95 0.04 250);
}
```

## Brand Color Scale

Generate a full color scale from a brand hue using OKLCH:

```css
@theme {
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-100: oklch(0.93 0.04 250);
  --color-brand-200: oklch(0.87 0.08 250);
  --color-brand-300: oklch(0.78 0.12 250);
  --color-brand-400: oklch(0.68 0.16 250);
  --color-brand-500: oklch(0.58 0.2 250);
  --color-brand-600: oklch(0.5 0.2 250);
  --color-brand-700: oklch(0.42 0.18 250);
  --color-brand-800: oklch(0.35 0.15 250);
  --color-brand-900: oklch(0.28 0.12 250);
  --color-brand-950: oklch(0.2 0.08 250);
}
```

Replace the hue value (`250`) with your brand hue. OKLCH lightness ranges from 0 (black) to 1 (white).

## Typography Tokens

```css
@theme {
  --font-display: 'Cal Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Type scale (Major Third ratio - 1.25) */
  --text-xs: 0.64rem;
  --text-sm: 0.8rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.563rem;
  --text-2xl: 1.953rem;
  --text-3xl: 2.441rem;
  --text-4xl: 3.052rem;
  --text-5xl: 3.815rem;
}
```

## Shadow Tokens with OKLCH

```css
@theme {
  --shadow-xs: 0 1px 2px 0 oklch(0 0 0 / 0.05);
  --shadow-sm:
    0 1px 3px 0 oklch(0 0 0 / 0.1), 0 1px 2px -1px oklch(0 0 0 / 0.1);
  --shadow-md:
    0 4px 6px -1px oklch(0 0 0 / 0.1), 0 2px 4px -2px oklch(0 0 0 / 0.1);
  --shadow-lg:
    0 10px 15px -3px oklch(0 0 0 / 0.1), 0 4px 6px -4px oklch(0 0 0 / 0.1);
  --shadow-xl:
    0 20px 25px -5px oklch(0 0 0 / 0.1), 0 8px 10px -6px oklch(0 0 0 / 0.1);

  /* Colored shadows for branded elements */
  --shadow-brand: 0 4px 14px 0 oklch(0.58 0.2 250 / 0.3);
  --shadow-success: 0 4px 14px 0 oklch(0.6 0.18 145 / 0.3);
  --shadow-error: 0 4px 14px 0 oklch(0.55 0.22 25 / 0.3);
}
```

## Motion Tokens

```css
@theme {
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

## Z-Index Scale

```css
@theme {
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-toast: 800;
}
```

## Fluid Typography

Use `clamp()` for responsive type that scales smoothly between viewport sizes:

```css
@theme {
  --text-fluid-sm: clamp(0.8rem, 0.7rem + 0.5vw, 0.875rem);
  --text-fluid-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-fluid-lg: clamp(1.25rem, 1rem + 1vw, 1.5rem);
  --text-fluid-xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
  --text-fluid-2xl: clamp(2rem, 1.5rem + 2vw, 3rem);
  --text-fluid-3xl: clamp(2.5rem, 1.8rem + 3vw, 4rem);
}

@utility text-fluid-lg {
  font-size: var(--text-fluid-lg);
}

@utility text-fluid-xl {
  font-size: var(--text-fluid-xl);
}

@utility text-fluid-2xl {
  font-size: var(--text-fluid-2xl);
}
```

## Fluid Spacing

```css
@theme {
  --space-fluid-sm: clamp(0.5rem, 0.4rem + 0.5vw, 1rem);
  --space-fluid-md: clamp(1rem, 0.8rem + 1vw, 2rem);
  --space-fluid-lg: clamp(2rem, 1.5rem + 2vw, 4rem);
  --space-fluid-xl: clamp(4rem, 3rem + 4vw, 8rem);
}

@utility p-fluid-md {
  padding: var(--space-fluid-md);
}

@utility gap-fluid-md {
  gap: var(--space-fluid-md);
}
```

## Monorepo Token Package

Share tokens across apps in a monorepo:

```css
/* packages/design-tokens/tokens.css */
@theme {
  --color-brand-500: oklch(0.58 0.2 250);
  --color-surface-primary: oklch(1 0 0);
  --font-body: 'Inter', system-ui, sans-serif;
  /* all shared tokens */
}
```

```json
{
  "name": "@mycompany/design-tokens",
  "exports": { ".": "./tokens.css" }
}
```

```css
/* apps/web/app.css */
@import 'tailwindcss';
@import '@mycompany/design-tokens';
```

## Semantic Token Aliases

Create semantic aliases that reference base tokens:

```css
@theme {
  --color-blue-500: oklch(0.58 0.2 250);

  --color-primary: var(--color-blue-500);
  --color-link: var(--color-blue-500);
  --color-focus-ring: var(--color-blue-500);
}
```

This lets you change the brand color in one place and have it cascade to all semantic uses.
