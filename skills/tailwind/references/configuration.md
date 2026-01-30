---
title: Configuration
description: Tailwind v4 CSS-first configuration with @theme, @theme inline, plugin syntax, @utility directive, OKLCH color space, and Vite integration
tags: [tailwind-v4, configuration, theme, plugins, utility, oklch, vite]
---

# Configuration

## CSS-First Config (v4)

All configuration lives in CSS. No `tailwind.config.js`.

```css
@import 'tailwindcss';

@theme {
  --color-brand: oklch(0.7 0.15 250);
  --color-surface-primary: oklch(1 0 0);
  --color-text-primary: oklch(0.15 0.02 250);
  --font-display: 'Cal Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
}
```

## `@theme inline` vs `@theme`

- **`@theme inline`** — Inlines values at build time. Use for single theme + dark mode toggle (shadcn/ui default).
- **`@theme`** (without inline) — Keeps variable references. Use for multi-theme systems or dynamic theme switching beyond light/dark.

## Plugins (v4 Syntax)

```css
@import 'tailwindcss';
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

Never use `@import` or `require()` for plugins in v4.

## Custom Utilities

```css
@utility custom-button {
  @apply px-4 py-2 bg-blue-500;
}
```

In v4, only classes defined with `@utility` are available to `@apply`. The v3 pattern of defining classes in `@layer components` and using `@apply` no longer works.

## OKLCH Color Space (v4 Default)

Tailwind v4 uses OKLCH for all default colors. Benefits: perceptual uniformity, better gradients, wider gamut. Browser support: 93%+ (Chrome 111+, Firefox 113+, Safari 15.4+). Tailwind generates sRGB fallbacks automatically.

```css
@theme {
  --color-brand: oklch(0.7 0.15 250); /* preferred */
  --color-brand: hsl(240 80% 60%); /* still works */
}
```

## Vite Integration

Use `@tailwindcss/vite` instead of PostCSS:

```ts
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({ plugins: [react(), tailwindcss()] });
```
