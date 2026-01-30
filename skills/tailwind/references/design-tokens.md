---
title: Design Tokens
description: Complete Tailwind v4 design token system with OKLCH colors, semantic tokens, dark mode, multi-theme systems, fluid typography, and monorepo token packages
tags: [design-tokens, oklch, dark-mode, multi-theme, fluid-typography, monorepo]
---

# Design Tokens

## Complete Token System

```css
@import 'tailwindcss';

@theme {
  /* Colors - OKLCH for perceptual uniformity */
  --color-surface-primary: oklch(1 0 0);
  --color-surface-secondary: oklch(0.98 0.002 250);
  --color-surface-inverse: oklch(0.15 0.02 250);

  --color-text-primary: oklch(0.15 0.02 250);
  --color-text-secondary: oklch(0.4 0.02 250);
  --color-text-disabled: oklch(0.7 0.01 250);

  --color-border-default: oklch(0.85 0.01 250);
  --color-border-subtle: oklch(0.92 0.005 250);

  /* Status colors */
  --color-success: oklch(0.6 0.18 145);
  --color-warning: oklch(0.75 0.18 85);
  --color-error: oklch(0.55 0.22 25);
  --color-info: oklch(0.6 0.18 250);

  /* Brand scale */
  --color-brand-500: oklch(0.58 0.2 250);
  --color-brand-600: oklch(0.5 0.2 250);
  --color-brand-400: oklch(0.68 0.16 250);

  /* Typography */
  --font-display: 'Cal Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Shadows with OKLCH */
  --shadow-sm:
    0 1px 3px 0 oklch(0 0 0 / 0.1), 0 1px 2px -1px oklch(0 0 0 / 0.1);
  --shadow-md:
    0 4px 6px -1px oklch(0 0 0 / 0.1), 0 2px 4px -2px oklch(0 0 0 / 0.1);
  --shadow-lg:
    0 10px 15px -3px oklch(0 0 0 / 0.1), 0 4px 6px -4px oklch(0 0 0 / 0.1);
  --shadow-brand: 0 4px 14px 0 oklch(0.58 0.2 250 / 0.3);

  /* Motion */
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

  /* Z-index scale */
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-tooltip: 700;
  --z-toast: 800;
}
```

## Dark Mode

```css
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-surface: oklch(1 0 0);
  --color-text: oklch(0.15 0 0);
  --color-border: oklch(0.9 0 0);
}

.dark {
  --color-surface: oklch(0.12 0.02 260);
  --color-text: oklch(0.95 0 0);
  --color-border: oklch(0.28 0.02 260);
}
```

## Multi-Theme Systems

```css
@custom-variant theme-ocean (&:where([data-theme="ocean"], [data-theme="ocean"] *));
@custom-variant theme-forest (&:where([data-theme="forest"], [data-theme="forest"] *));

@theme {
  --color-primary: oklch(0.6 0.2 250);
}

[data-theme='ocean'] {
  --color-primary: oklch(0.55 0.2 220);
}

[data-theme='forest'] {
  --color-primary: oklch(0.5 0.18 145);
}
```

```ts
function setTheme(theme: string) {
  if (theme === 'default') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
  localStorage.setItem('theme', theme);
}
```

Use `@theme` without `inline` for multi-theme (keeps variable references at runtime).

## Fluid Typography and Spacing

```css
@theme {
  --text-fluid-sm: clamp(0.8rem, 0.7rem + 0.5vw, 0.875rem);
  --text-fluid-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-fluid-lg: clamp(1.25rem, 1rem + 1vw, 1.5rem);
  --text-fluid-xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
  --text-fluid-2xl: clamp(2rem, 1.5rem + 2vw, 3rem);

  --space-fluid-sm: clamp(0.5rem, 0.4rem + 0.5vw, 1rem);
  --space-fluid-md: clamp(1rem, 0.8rem + 1vw, 2rem);
  --space-fluid-lg: clamp(2rem, 1.5rem + 2vw, 4rem);
}

@utility text-fluid-lg {
  font-size: var(--text-fluid-lg);
}

@utility p-fluid-md {
  padding: var(--space-fluid-md);
}
```

## Monorepo Token Package

```css
/* packages/design-tokens/tokens.css */
@theme {
  --color-brand-500: oklch(0.58 0.2 250);
  /* all tokens */
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
