---
title: Troubleshooting
description: Common Tailwind v4 errors and fixes including missing styles, dark mode issues, build failures, migration from v3, and shadcn/ui compatibility
tags: [troubleshooting, migration, v3-to-v4, build-errors, dark-mode]
---

# Troubleshooting

## `bg-primary` doesn't apply styles

Missing `@theme inline` mapping. Add `@theme inline { --color-primary: var(--primary); }`.

## Colors all black/white

Double `hsl()` wrapping. Use `var(--color)` not `hsl(var(--color))`.

## Dark mode not switching

Missing ThemeProvider. Wrap app in `<ThemeProvider>` that toggles `.dark` class on `<html>`.

## Build fails with "Unexpected config file"

Delete `tailwind.config.ts`. v4 uses CSS-only configuration.

## "Cannot find module tailwindcss-animate"

Replace with v4-compatible package: `pnpm add -D tw-animate-css`, then `@import "tw-animate-css";`.

## "Cannot apply unknown utility class"

In v4, `@apply` only works with `@utility`-defined classes, not `@layer components` classes. Migrate to `@utility` directive.

## `@layer base` styles ignored

v4 uses native CSS layers. Options: (a) define layers explicitly with separate imports, or (b) avoid `@layer base` and define styles at root level.

## `@theme inline` breaks dark mode in multi-theme

`@theme inline` bakes values at build time. Use `@theme` (without `inline`) for multi-theme systems.

## Ring width thinner than v3

Default changed from 3px to 1px. Use `ring-3` to match v3 appearance.

## Headings/lists unstyled after migration

v4 removed default element styles from Preflight. Use `@tailwindcss/typography` (`prose` class) or add custom base styles.

## PostCSS plugin errors

Use `@tailwindcss/vite` for Vite projects instead of PostCSS:

```ts
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({ plugins: [react(), tailwindcss()] });
```

## Migration tool fails

The `@tailwindcss/upgrade` utility often fails with complex configs. Manual migration steps:

1. Delete `tailwind.config.ts`
2. Move theme to CSS with `@theme`
3. Replace `tailwindcss-animate` with `tw-animate-css`
4. Update plugins: `require()` to `@plugin`
5. Replace `@tailwind base; @tailwind components; @tailwind utilities;` with `@import "tailwindcss";`
6. Move `:root`/`.dark` out of `@layer base`
