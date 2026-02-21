---
title: Migration
description: Complete guide for migrating from Tailwind CSS v3 to v4 including automated upgrade tool, manual steps, breaking changes, and common gotchas
tags: [migration, v3-to-v4, upgrade, breaking-changes, postcss, preflight]
---

# Migration (v3 to v4)

## Automated Upgrade Tool

The official tool handles package updates, config migration, and template changes:

```bash
npx @tailwindcss/upgrade@latest
```

What it does:

- Updates `tailwindcss` and related dependencies to v4
- Transforms `tailwind.config.js` into `@theme` block in CSS
- Migrates `@tailwind` directives to `@import "tailwindcss"`
- Fixes renamed or removed utilities in templates

The tool often fails with complex configurations (typography plugin configs, custom plugin setups, complex theme extensions). If it fails, follow the manual steps below.

## Manual Migration Steps

### 1. Update the CSS Entry Point

```css
/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* v4 */
@import 'tailwindcss';
```

### 2. Move Config to CSS

```js
/* v3: tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6',
      },
      fontFamily: {
        display: ['Clash Display', 'Inter', 'sans-serif'],
      },
    },
  },
};
```

```css
/* v4: in your CSS file */
@theme {
  --color-brand: #3b82f6;
  --font-display: 'Clash Display', 'Inter', sans-serif;
}
```

Then delete `tailwind.config.js` / `tailwind.config.ts`.

### 3. Update Plugin Syntax

```css
/* v3 */
/* plugins: [require('@tailwindcss/typography')] in config */

/* v4 */
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

### 4. Replace Animation Package

```bash
pnpm remove tailwindcss-animate
pnpm add -D tw-animate-css
```

```css
@import 'tailwindcss';
@import 'tw-animate-css';
```

### 5. Move Custom Utilities

```css
/* v3 */
@layer utilities {
  .tab-4 {
    tab-size: 4;
  }
}

/* v4 */
@utility tab-4 {
  tab-size: 4;
}
```

### 6. Move Root Variables Out of @layer

```css
/* v3 */
@layer base {
  :root {
    --background: 0 0% 100%;
  }
}

/* v4 */
:root {
  --background: hsl(0 0% 100%);
}
```

### 7. Update theme() References

```css
/* v3 */
.my-card {
  background-color: theme('colors.brand');
}

/* v4 */
.my-card {
  background-color: var(--color-brand);
}
```

## Breaking Changes

### CSS Layers Are Now Native

v3 hijacked the CSS `@layer` at-rule. v4 uses native CSS cascade layers. Impact:

- `@apply` only works with `@utility`-defined classes, not `@layer components` classes
- `@layer base` styles may be overridden by utility layers due to CSS cascade precedence
- Define explicit layer order if using custom `@layer` blocks

### Default Ring Width Changed

```tsx
{/* v3: ring = 3px */}
<button className="ring">

{/* v4: ring = 1px (thinner) */}
<button className="ring">

{/* Match v3 appearance */}
<button className="ring-3">
```

### Preflight Changes

v4 removes default styles for headings, lists, and buttons. All headings render at the same size. Lists lose default padding.

Fix with typography plugin:

```css
@import 'tailwindcss';
@plugin "@tailwindcss/typography";
```

```tsx
<article className="prose dark:prose-invert">
  {/* headings, lists, blockquotes styled automatically */}
</article>
```

Or add custom base styles:

```css
@layer base {
  h1 {
    font-size: var(--text-4xl);
    font-weight: 700;
    margin-bottom: 1rem;
  }
  h2 {
    font-size: var(--text-3xl);
    font-weight: 700;
    margin-bottom: 0.75rem;
  }
  ul {
    list-style-type: disc;
    padding-left: 1.5rem;
    margin-bottom: 1rem;
  }
}
```

### Color Format Changed to OKLCH

v4 replaces the entire default color palette with OKLCH. Existing `hsl()` values still work, but new defaults use OKLCH. Custom colors in any format are supported.

### Container Queries Plugin Removed

Built into v4 core. Remove `@tailwindcss/container-queries` from dependencies.

### Line Clamp Plugin Removed

Built into Tailwind since v3.3. Remove `@tailwindcss/line-clamp` if still installed.

### `start-*`/`end-*` Inset Utilities Deprecated (v4.2)

Replaced by `inset-s-*` and `inset-e-*` logical inset utilities:

```tsx
{/* Deprecated */}
<div className="start-0 end-4">

{/* Current */}
<div className="inset-s-0 inset-e-4">
```

## Build Tool Changes

### Vite Projects

Replace PostCSS setup with the Vite plugin:

```ts
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

Remove `postcss.config.js` if it only contained Tailwind.

### Non-Vite Projects

Use `@tailwindcss/postcss` (separate package from v4):

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

The `tailwindcss` package itself is no longer a PostCSS plugin.

## shadcn/ui Migration

1. Delete `tailwind.config.ts`
2. Set `"config": ""` in `components.json`
3. Replace `tailwindcss-animate` with `tw-animate-css`
4. Move `:root`/`.dark` out of `@layer base`
5. Add `@theme inline` block mapping all CSS variables
6. Wrap color values in `:root` with `hsl()` (e.g., `--background: hsl(0 0% 100%)`)
7. Reference variables directly in `@layer base` (no `hsl()` wrapper)

## Migration Checklist

- [ ] Replace `@tailwind` directives with `@import "tailwindcss"`
- [ ] Move theme config from JS to `@theme` in CSS
- [ ] Delete `tailwind.config.js` / `tailwind.config.ts`
- [ ] Update plugins to `@plugin` syntax
- [ ] Replace `tailwindcss-animate` with `tw-animate-css`
- [ ] Move `@layer utilities` classes to `@utility` directive
- [ ] Move `:root`/`.dark` out of `@layer base`
- [ ] Replace `theme()` with `var(--token)`
- [ ] Update `ring` to `ring-3` where v3 width is expected
- [ ] Check heading/list styling after Preflight changes
- [ ] Remove `@tailwindcss/container-queries` plugin
- [ ] Update build tool (Vite plugin, `@tailwindcss/postcss`, or `@tailwindcss/webpack`)
- [ ] Replace `start-*`/`end-*` with `inset-s-*`/`inset-e-*` (deprecated in v4.2)
