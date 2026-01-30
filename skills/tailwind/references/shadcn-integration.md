---
title: shadcn/ui Integration
description: Tailwind v4 shadcn/ui four-step architecture for CSS variables, @theme inline mapping, base styles, and automatic dark mode
tags: [shadcn-ui, css-variables, theme-inline, dark-mode, components-json]
---

# shadcn/ui Integration

## Four-Step Architecture

### Step 1: Define CSS Variables at Root

```css
@import 'tailwindcss';
@import 'tw-animate-css';

:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  --primary-foreground: hsl(210 40% 98%);
  /* ... all light mode colors with hsl() wrapper */
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  /* ... all dark mode colors */
}
```

### Step 2: Map to Tailwind Utilities

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ... map ALL CSS variables */
}
```

Without this, utility classes like `bg-background` and `text-primary` will not exist.

### Step 3: Apply Base Styles

```css
@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}
```

Reference variables directly. Never double-wrap: `hsl(var(--background))`.

### Step 4: Automatic Dark Mode

```tsx
<div className="bg-background text-foreground">
  {/* No dark: variants needed - theme switches via .dark class */}
</div>
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

The `config` field must be empty string for v4.
