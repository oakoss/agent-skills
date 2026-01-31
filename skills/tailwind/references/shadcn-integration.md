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
  --background: hsl(0 0% 100%);
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  --primary-foreground: hsl(210 40% 98%);
  --secondary: hsl(210 40% 96.1%);
  --secondary-foreground: hsl(222.2 47.4% 11.2%);
  --muted: hsl(210 40% 96.1%);
  --muted-foreground: hsl(215.4 16.3% 46.9%);
  --accent: hsl(210 40% 96.1%);
  --accent-foreground: hsl(222.2 47.4% 11.2%);
  --destructive: hsl(0 84.2% 60.2%);
  --destructive-foreground: hsl(210 40% 98%);
  --border: hsl(214.3 31.8% 91.4%);
  --ring: hsl(222.2 84% 4.9%);
  --radius: 0.5rem;
  --card: hsl(0 0% 100%);
  --card-foreground: hsl(222.2 84% 4.9%);
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  --primary-foreground: hsl(222.2 47.4% 11.2%);
  --secondary: hsl(217.2 32.6% 17.5%);
  --secondary-foreground: hsl(210 40% 98%);
  --muted: hsl(217.2 32.6% 17.5%);
  --muted-foreground: hsl(215 20.2% 65.1%);
  --accent: hsl(217.2 32.6% 17.5%);
  --accent-foreground: hsl(210 40% 98%);
  --destructive: hsl(0 62.8% 30.6%);
  --destructive-foreground: hsl(210 40% 98%);
  --border: hsl(217.2 32.6% 17.5%);
  --ring: hsl(212.7 26.8% 83.9%);
  --card: hsl(222.2 84% 4.9%);
  --card-foreground: hsl(210 40% 98%);
}
```

Define `:root` and `.dark` at root level. Never inside `@layer base`.

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
