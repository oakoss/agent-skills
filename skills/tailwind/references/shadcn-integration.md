---
title: shadcn/ui Integration
description: Tailwind v4 shadcn/ui setup with four-step architecture, components.json configuration, tw-animate-css, Vite plugin, and automatic dark mode
tags:
  [
    shadcn-ui,
    css-variables,
    theme-inline,
    dark-mode,
    components-json,
    vite,
    tw-animate,
  ]
---

# shadcn/ui Integration

## Installation

```bash
pnpm add tailwindcss @tailwindcss/vite
pnpm add -D @types/node tw-animate-css
pnpm dlx shadcn@latest init
rm -f tailwind.config.ts
```

## Vite Configuration

```ts
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
});
```

## components.json for v4

```json
{
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  }
}
```

The `config` field must be empty string for v4 (no `tailwind.config.ts`).

## Four-Step Architecture

### Step 1: Define CSS Variables at Root

```css
/* src/index.css */
@import 'tailwindcss';
@import 'tw-animate-css';

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0.024 266);
  --primary: oklch(0.488 0.134 262.9);
  --primary-foreground: oklch(0.971 0.005 266);
  --secondary: oklch(0.965 0.005 266);
  --secondary-foreground: oklch(0.345 0.03 266);
  --muted: oklch(0.965 0.005 266);
  --muted-foreground: oklch(0.556 0.015 266);
  --accent: oklch(0.965 0.005 266);
  --accent-foreground: oklch(0.345 0.03 266);
  --destructive: oklch(0.637 0.237 25.33);
  --destructive-foreground: oklch(0.971 0.005 266);
  --border: oklch(0.922 0.01 266);
  --ring: oklch(0.145 0.024 266);
  --radius: 0.5rem;
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0.024 266);
}

.dark {
  --background: oklch(0.145 0.024 266);
  --foreground: oklch(0.971 0.005 266);
  --primary: oklch(0.588 0.158 264.2);
  --primary-foreground: oklch(0.345 0.03 266);
  --secondary: oklch(0.269 0.022 266);
  --secondary-foreground: oklch(0.971 0.005 266);
  --muted: oklch(0.269 0.022 266);
  --muted-foreground: oklch(0.704 0.015 266);
  --accent: oklch(0.269 0.022 266);
  --accent-foreground: oklch(0.971 0.005 266);
  --destructive: oklch(0.444 0.177 25.33);
  --destructive-foreground: oklch(0.971 0.005 266);
  --border: oklch(0.269 0.022 266);
  --ring: oklch(0.839 0.015 266);
  --card: oklch(0.145 0.024 266);
  --card-foreground: oklch(0.971 0.005 266);
}
```

Define `:root` and `.dark` at root level using oklch values. Never inside `@layer base`.

### Step 2: Map Variables to Tailwind Utilities

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
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
  --color-ring: var(--ring);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
  --radius-sm: calc(var(--radius) - 4px);
}
```

Without this block, utility classes like `bg-background` and `text-primary` will not exist.

### Step 3: Apply Base Styles

```css
@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}
```

Reference variables directly. Never double-wrap: `hsl(var(--background))` is wrong.

### Step 4: Automatic Dark Mode

```tsx
<div className="bg-background text-foreground">
  <p className="text-muted-foreground">No dark: variants needed</p>
  <button className="bg-primary text-primary-foreground">
    Theme switches automatically via .dark class
  </button>
</div>
```

## Dark Mode Setup

Wrap the app in a ThemeProvider that toggles `.dark` class on `<html>`:

```tsx
import { ThemeProvider } from '@/components/theme-provider';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
    <App />
  </ThemeProvider>,
);
```

Add a theme toggle using shadcn's dropdown-menu:

```bash
pnpm dlx shadcn@latest add dropdown-menu
```

## The cn() Utility

```ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Setup Checklist

- `@tailwindcss/vite` installed and configured in `vite.config.ts`
- `components.json` has `"config": ""`
- No `tailwind.config.ts` file exists
- `src/index.css` follows the four-step pattern
- `:root`/`.dark` defined at root level (not in `@layer`)
- `@theme inline` maps all CSS variables
- `tw-animate-css` installed (not `tailwindcss-animate`)
- ThemeProvider wraps the app
