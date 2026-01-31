---
title: Configuration
description: Tailwind v4 CSS-first configuration with @theme, @theme inline, @utility, @plugin, @source, @reference, @variant directives, OKLCH colors, and Vite integration
tags:
  [tailwind-v4, configuration, theme, plugins, utility, oklch, vite, directives]
---

# Configuration

## CSS-First Config (v4)

All configuration lives in CSS. No `tailwind.config.js` needed.

```css
@import 'tailwindcss';

@theme {
  --color-brand: oklch(0.7 0.15 250);
  --color-surface-primary: oklch(1 0 0);
  --color-text-primary: oklch(0.15 0.02 250);
  --font-display: 'Cal Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --breakpoint-3xl: 1920px;
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);
}
```

## `@theme` vs `@theme inline`

**`@theme`** generates global CSS custom properties on `:root`. Variables can be overridden at runtime (dark mode, multi-theme). Use for multi-theme systems.

**`@theme inline`** inlines values directly into generated utility classes. No CSS custom properties emitted. Use for single theme + dark mode toggle (shadcn/ui pattern).

```css
/* Multi-theme: use @theme (keeps variable references) */
@theme {
  --color-primary: var(--color-blue-500);
}

/* Single theme + shadcn: use @theme inline (inlines values) */
@theme inline {
  --color-background: var(--background);
  --color-primary: var(--primary);
}
```

## Overriding vs Extending the Default Theme

Adding a variable to `@theme` extends the defaults. To reset and replace an entire category:

```css
@theme {
  --color-*: initial; /* Reset all default colors */
  --color-primary: oklch(0.58 0.2 250);
  --color-secondary: oklch(0.7 0.15 200);
}
```

The `initial` pattern works for any namespace: `--font-*: initial;`, `--spacing-*: initial;`, `--breakpoint-*: initial;`.

## `@utility` Directive

Registers custom utility classes that work with all variants (`hover:`, `md:`, `@md:`).

```css
@utility neon-text {
  color: #00f0ff;
  text-shadow: 0 0 5px #00f0ff;
}
```

In v4, only `@utility`-defined classes work with `@apply`. The v3 pattern of `@layer components` + `@apply` no longer works.

## Functional Utilities with `--value()`

Define utilities that accept dynamic values, matching against theme keys:

```css
@theme {
  --tab-size-2: 2;
  --tab-size-4: 4;
  --tab-size-github: 8;
}

@utility tab-* {
  tab-size: --value(--tab-size-*);
}
```

This enables `tab-2`, `tab-4`, `tab-github` classes. For arbitrary values, `--value()` also supports `tab-[16]`.

## `@plugin` Directive

Load plugins using `@plugin` instead of `require()` or `@import`:

```css
@import 'tailwindcss';
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

## `@source` Directive

Explicitly add source paths for class detection. Useful for scanning external libraries:

```css
@source "../node_modules/@mycompany/ui/src";
```

v4.1 additions:

```css
/* Exclude paths from scanning */
@source not "../legacy";

/* Ensure specific classes are always generated */
@source inline("bg-red-500 text-white p-4");
```

## `@reference` Directive

Import a stylesheet for access to theme variables and custom utilities without duplicating CSS. For Vue/Svelte scoped styles and CSS modules:

```html
<style>
  @reference "../../app.css";

  h1 {
    @apply text-2xl font-bold text-red-500;
  }
</style>
```

Can also reference the framework directly:

```html
<style>
  @reference "tailwindcss";
</style>
```

## `@variant` Directive

Apply a Tailwind variant to custom CSS:

```css
.my-element {
  background: white;

  @variant dark {
    background: black;
  }
}
```

Compiles to the appropriate media query or selector based on the variant configuration.

## `@custom-variant` Directive

Define custom variants for use in utility classes:

```css
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
```

Enables `dark:bg-black`, `theme-midnight:text-white` in HTML.

## OKLCH Color Space (v4 Default)

v4 uses OKLCH for all default colors. Benefits: perceptual uniformity, better gradients, wider gamut. Browser support: 93%+ globally. Tailwind generates sRGB fallbacks automatically.

```css
@theme {
  --color-brand: oklch(0.7 0.15 250); /* preferred */
  --color-legacy: hsl(240 80% 60%); /* still works */
}
```

## Vite Integration

Use `@tailwindcss/vite` instead of PostCSS for Vite projects:

```ts
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

For non-Vite environments, use `@tailwindcss/postcss` as the PostCSS plugin.

## Container Query Breakpoints

Customize container query sizes with theme variables:

```css
@theme {
  --container-8xl: 96rem;
}
```

This creates the `@8xl:` container query variant for use in markup.

## Dynamic CSS Variables in Utilities

Use CSS variables directly in utility class names:

```tsx
<div
  style={{ '--grid-count': count } as React.CSSProperties}
  className="grid grid-cols-(--grid-count)"
>
  {/* Dynamic grid columns */}
</div>
```

The `(--variable-name)` syntax works with any utility that accepts values.
