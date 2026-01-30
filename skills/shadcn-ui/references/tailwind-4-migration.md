---
title: Tailwind 4 CSS-First Migration
description: Migrating shadcn/ui projects from Tailwind config JavaScript to CSS-first architecture with @theme, @utility, and @import directives
tags: [tailwind-4, css-first, theme, migration, css-variables, globals]
---

# Tailwind 4 CSS-First Migration

Tailwind CSS 4 shifts from JavaScript configuration to native CSS. All design tokens, custom utilities, and theme values live in CSS files.

## Global Import

Replace the three Tailwind directives with a single import:

```css
/* Legacy (Tailwind 3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Current (Tailwind 4) */
@import 'tailwindcss';
```

## Theme Tokens with @theme

Define all design tokens in `globals.css` using the `@theme` directive. This replaces the `theme.extend` object in `tailwind.config.js`.

```css
/* globals.css */
@import 'tailwindcss';

@theme {
  --font-sans: 'Inter', system-ui, sans-serif;
  --color-primary: hsl(222.2 47.4% 11.2%);
  --color-primary-foreground: hsl(210 40% 98%);
  --color-secondary: hsl(210 40% 96.1%);
  --color-secondary-foreground: hsl(222.2 47.4% 11.2%);
  --color-destructive: hsl(0 84.2% 60.2%);
  --color-destructive-foreground: hsl(210 40% 98%);
  --color-muted: hsl(210 40% 96.1%);
  --color-muted-foreground: hsl(215.4 16.3% 46.9%);
  --color-accent: hsl(210 40% 96.1%);
  --color-accent-foreground: hsl(222.2 47.4% 11.2%);
  --color-border: hsl(214.3 31.8% 91.4%);
  --color-ring: hsl(222.2 84% 4.9%);
  --color-background: hsl(0 0% 100%);
  --color-foreground: hsl(222.2 84% 4.9%);
  --radius-lg: 1rem;
  --radius-md: 0.75rem;
  --radius-sm: 0.5rem;
  --breakpoint-3xl: 1920px;
}
```

## Custom Utilities

Define reusable utility classes with `@utility`:

```css
@utility focus-ring {
  @apply ring-2 ring-primary ring-offset-2;
}

@utility container-fluid {
  @apply mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8;
}
```

These are then used as standard Tailwind classes: `class="focus-ring"`.

## Dynamic Spacing and Radius

Use CSS variables for consistent, scalable layout values:

```css
:root {
  --radius: 0.75rem;
  --spacing-fluid: clamp(1rem, 5vw, 3rem);
}

.dark {
  --color-background: hsl(222.2 84% 4.9%);
  --color-foreground: hsl(210 40% 98%);
  --color-border: hsl(217.2 32.6% 17.5%);
}
```

## Dark Mode Configuration

shadcn/ui uses HSL CSS variables that swap between light and dark palettes:

```css
@theme {
  --color-background: hsl(0 0% 100%);
  --color-foreground: hsl(222.2 84% 4.9%);
}

.dark {
  --color-background: hsl(222.2 84% 4.9%);
  --color-foreground: hsl(210 40% 98%);
}
```

**HSL variable format:** In Tailwind 4, reference CSS variables directly without wrapping in `hsl()`:

```css
/* Wrong (Tailwind 3 pattern) */
background-color: hsl(var(--background));

/* Correct (Tailwind 4) */
background-color: var(--color-background);
```

## Migration Checklist

| Step | Action                                                                |
| ---- | --------------------------------------------------------------------- |
| 1    | Replace `@tailwind` directives with `@import 'tailwindcss'`           |
| 2    | Move `theme.extend` values from config to `@theme { }` in CSS         |
| 3    | Convert color values to use `--color-` prefix convention              |
| 4    | Replace `hsl(var(--x))` patterns with `var(--color-x)`                |
| 5    | Move custom plugins to `@utility` directives                          |
| 6    | Remove `tailwind.config.js` (or keep only for plugins not yet ported) |
| 7    | Test dark mode toggle with updated CSS variable selectors             |

## Color Format

The recommended format for shadcn/ui colors in Tailwind 4:

```css
@theme {
  /* HSL values without the hsl() wrapper */
  --color-primary: hsl(222.2 47.4% 11.2%);

  /* oklch is also supported for wider gamut */
  --color-brand: oklch(0.65 0.24 169.22);
}
```

Both HSL and oklch formats work. oklch provides access to a wider color gamut on modern displays.
