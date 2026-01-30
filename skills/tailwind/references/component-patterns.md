---
title: Component Patterns
description: Tailwind CSS layout patterns including section containers, responsive grids, auto-fit grids, sticky headers, card bases, and CVA component variants
tags: [components, layouts, grids, cva, variants, patterns]
---

# Component Patterns

## Section Container

```tsx
<section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
  {/* content */}
</section>
```

## Responsive Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* items */}
</div>
```

## Auto-Fit Grid

```tsx
<div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  {/* auto columns */}
</div>
```

## Sticky Header with Backdrop Blur

```tsx
<header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur">
  {/* nav */}
</header>
```

## Card Base

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
  {/* content */}
</div>
```

## CVA for Component Variants

```ts
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent',
        secondary:
          'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
);
```
