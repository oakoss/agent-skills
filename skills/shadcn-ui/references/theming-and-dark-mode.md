---
title: Theming and Dark Mode
description: oklch CSS variable theming, @theme inline mapping, dark mode configuration, color tokens, and Tailwind CSS 4 migration patterns for shadcn/ui
tags:
  [theming, dark-mode, oklch, css-variables, tailwind-4, theme-inline, colors]
---

# Theming and Dark Mode

shadcn/ui uses CSS variables with oklch color values for theming. Design tokens are defined in `:root` and `.dark` selectors, then mapped to Tailwind via `@theme inline`.

## Global CSS Structure

The complete theme setup in `globals.css` for Tailwind CSS 4:

```css
@import 'tailwindcss';
@import 'tw-animate-css';

@custom-variant dark (&:is(.dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.145 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.145 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --destructive-foreground: oklch(0.637 0.237 25.331);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(0.269 0 0);
  --sidebar-ring: oklch(0.439 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

## Theme Architecture

The two-layer approach separates concerns:

1. **`:root` / `.dark`** -- Define raw color values in oklch format. These are plain CSS custom properties that toggle between light and dark palettes.

2. **`@theme inline`** -- Maps raw variables to Tailwind's `--color-*` and `--radius-*` namespace. The `inline` keyword prevents Tailwind from hoisting values, keeping them responsive to the `.dark` selector.

This means `bg-primary` in Tailwind resolves to `var(--primary)`, which changes based on whether `.dark` is applied.

## Color Naming Convention

shadcn/ui uses a background/foreground pair convention:

| Variable                   | Purpose                               |
| -------------------------- | ------------------------------------- |
| `--primary`                | Background color of primary elements  |
| `--primary-foreground`     | Text color on primary backgrounds     |
| `--muted`                  | Background for muted/subdued elements |
| `--muted-foreground`       | Text on muted backgrounds             |
| `--destructive`            | Background for danger/error elements  |
| `--destructive-foreground` | Text on destructive backgrounds       |

The `background` suffix is omitted -- `--primary` IS the background color.

## Adding Custom Colors

To add a new semantic color (e.g., `warning`):

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}

.dark {
  --warning: oklch(0.72 0.19 64);
  --warning-foreground: oklch(0.98 0.01 90);
}
```

Then register it in the `@theme inline` block:

```css
@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

Now use `bg-warning` and `text-warning-foreground` in components.

## oklch Color Format

shadcn/ui uses oklch (Oklab Lightness Chroma Hue) instead of HSL:

```css
/* oklch(lightness chroma hue) */
--primary: oklch(0.205 0 0); /* Near-black, no chroma */
--destructive: oklch(0.577 0.245 27.325); /* Saturated red */
```

oklch provides perceptually uniform lightness and access to a wider color gamut on modern displays.

## Dark Mode with next-themes

For Next.js projects, use `next-themes` to manage the `.dark` class:

```tsx
import { ThemeProvider } from 'next-themes';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

Toggle with a button component:

```tsx
'use client';

import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? 'Light' : 'Dark'}
    </Button>
  );
}
```

## Custom Utilities

Define reusable utility classes with `@utility`:

```css
@utility focus-ring {
  @apply ring-2 ring-ring ring-offset-2;
}

@utility container-fluid {
  @apply mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8;
}
```

Use them as standard Tailwind classes: `class="focus-ring"`.

## Migration from Tailwind 3 / HSL

| Step | Action                                                                                 |
| ---- | -------------------------------------------------------------------------------------- |
| 1    | Replace `@tailwind base/components/utilities` with `@import "tailwindcss"`             |
| 2    | Add `@import "tw-animate-css"`                                                         |
| 3    | Add `@custom-variant dark (&:is(.dark *))`                                             |
| 4    | Convert HSL values to oklch in `:root` and `.dark`                                     |
| 5    | Replace `@theme { --color-x: oklch(...) }` with `:root` vars + `@theme inline` mapping |
| 6    | Replace `hsl(var(--x))` patterns with `var(--x)`                                       |
| 7    | Add `@layer base` rules for border and body defaults                                   |
| 8    | Remove `tailwind.config.js` (or keep only for unported plugins)                        |

## Visual Styles

The `npx shadcn@latest create` command offers five visual styles that modify component structure beyond just colors:

| Style | Characteristics                        |
| ----- | -------------------------------------- |
| Vega  | Classic shadcn/ui look                 |
| Nova  | Reduced padding for compact layouts    |
| Maia  | Soft and rounded with generous spacing |
| Lyra  | Boxy and sharp, pairs with mono fonts  |
| Mira  | Compact, designed for dense interfaces |
