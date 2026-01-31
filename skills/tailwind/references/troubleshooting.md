---
title: Troubleshooting
description: Common Tailwind v4 errors and fixes including missing styles, dark mode issues, build failures, CSS layer problems, PostCSS errors, and shadcn/ui compatibility
tags: [troubleshooting, errors, build-fixes, dark-mode, postcss, css-layers]
---

# Troubleshooting

## `bg-primary` Doesn't Apply Styles

**Cause**: Missing `@theme inline` mapping.

**Fix**: Add the variable mapping so Tailwind generates the utility class:

```css
@theme inline {
  --color-primary: var(--primary);
}
```

## Colors All Black or White

**Cause**: Double `hsl()` wrapping.

**Fix**: Reference variables directly, never wrap:

```css
/* Wrong */
background-color: hsl(var(--background));

/* Correct */
background-color: var(--background);
```

## Dark Mode Not Switching

**Cause**: Missing ThemeProvider or wrong class target.

**Fix**:

1. Wrap app in `<ThemeProvider>` that toggles `.dark` class
2. Verify `.dark` class toggles on `<html>` element (not `<body>`)
3. For class-based dark mode, add: `@custom-variant dark (&:where(.dark, .dark *));`

## Build Fails with "Unexpected Config File"

**Cause**: v4 does not use `tailwind.config.ts`.

**Fix**: Delete the config file. All configuration goes in CSS via `@theme`.

```bash
rm -f tailwind.config.ts tailwind.config.js
```

## "Cannot Find Module tailwindcss-animate"

**Cause**: `tailwindcss-animate` is incompatible with v4.

**Fix**: Replace with v4-compatible package:

```bash
pnpm remove tailwindcss-animate
pnpm add -D tw-animate-css
```

```css
@import 'tailwindcss';
@import 'tw-animate-css';
```

## "Cannot Apply Unknown Utility Class"

**Cause**: In v4, `@apply` only works with `@utility`-defined classes.

**Fix**: Migrate from `@layer components` to `@utility`:

```css
/* Wrong: v3 pattern */
@layer components {
  .custom-button {
    @apply px-4 py-2 bg-blue-500;
  }
}

/* Correct: v4 pattern */
@utility custom-button {
  @apply px-4 py-2 bg-blue-500;
}
```

## `@layer base` Styles Not Applying

**Cause**: v4 uses native CSS cascade layers. Base-layer styles have lower specificity than utility-layer styles.

**Fix Option 1**: Define styles at root level without `@layer`:

```css
@import 'tailwindcss';

body {
  background-color: var(--background);
}
```

**Fix Option 2**: Import layers explicitly for correct ordering:

```css
@import 'tailwindcss/theme.css' layer(theme);
@import 'tailwindcss/base.css' layer(base);
@import 'tailwindcss/components.css' layer(components);
@import 'tailwindcss/utilities.css' layer(utilities);

@layer base {
  body {
    background-color: var(--background);
  }
}
```

## `@theme inline` Breaks Multi-Theme Dark Mode

**Cause**: `@theme inline` bakes values at build time. When dark mode changes the underlying CSS variables, utilities still reference the inlined original values.

**Fix**: Use `@theme` (without `inline`) for multi-theme:

```css
@theme {
  --color-text-primary: var(--color-slate-900);
  --color-bg-primary: var(--color-white);
}

.dark {
  --color-text-primary: var(--color-white);
  --color-bg-primary: var(--color-slate-900);
}
```

**When to use `@theme inline`**: Single theme + light/dark toggle (shadcn/ui default).

**When to use `@theme`**: Multi-theme systems, dynamic theme switching.

## Ring Width Thinner Than v3

**Cause**: Default ring width changed from 3px to 1px in v4.

**Fix**: Use `ring-3` to match v3 appearance:

```tsx
<button className="ring-3">Match v3 ring width</button>
```

## Headings and Lists Unstyled After Migration

**Cause**: v4 removed default element styles from Preflight. All headings render at the same size, lists lose padding.

**Fix**: Use the typography plugin or add custom base styles:

```css
@plugin "@tailwindcss/typography";
```

```tsx
<article className="prose dark:prose-invert">
  {/* All elements styled automatically */}
</article>
```

## PostCSS Plugin Errors

**Error**: "It looks like you're trying to use tailwindcss directly as a PostCSS plugin"

**Cause**: v4's PostCSS plugin is a separate package.

**Fix for Vite projects**: Use the Vite plugin instead:

```ts
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

**Fix for non-Vite projects**: Install the PostCSS package:

```bash
pnpm add -D @tailwindcss/postcss
```

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

## Duplicate `@layer base` Error

**Cause**: Multiple `@layer base` blocks in CSS (shadcn init may add one).

**Fix**: Consolidate to a single `@layer base` block. Keep `:root`/`.dark` variables outside any layer.

## `@apply` Not Working in Vue/Svelte Scoped Styles

**Cause**: Scoped `<style>` blocks do not have access to theme variables.

**Fix**: Use `@reference` to import definitions:

```html
<style>
  @reference '../../app.css';

  h1 {
    @apply text-2xl font-bold text-red-500;
  }
</style>
```

## Classes from External Library Not Detected

**Cause**: Tailwind ignores dependencies listed in `.gitignore` by default.

**Fix**: Add the source path explicitly:

```css
@source '../node_modules/@mycompany/ui/src';
```

## Migration Tool Fails

The `@tailwindcss/upgrade` utility often fails with complex configurations.

**Workaround**: Follow manual migration steps. Key changes:

1. Replace `@tailwind` directives with `@import "tailwindcss"`
2. Move theme to `@theme` in CSS, delete config file
3. Replace `tailwindcss-animate` with `tw-animate-css`
4. Update plugins: `require()` to `@plugin`
5. Move `:root`/`.dark` out of `@layer base`
6. Replace `@layer utilities` with `@utility`
