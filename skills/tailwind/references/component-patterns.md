---
title: Component Patterns
description: Tailwind CSS layout patterns including containers, responsive grids, container queries, 3D transforms, subgrid, sticky headers, cards, and CVA component variants
tags:
  [
    components,
    layouts,
    grids,
    container-queries,
    3d-transforms,
    subgrid,
    cva,
    variants,
  ]
---

# Component Patterns

## Section Container

```tsx
<section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
  {/* content */}
</section>
```

Container width variations: `max-w-4xl` (narrow/blog), `max-w-5xl` (medium), `max-w-6xl` (wide), `max-w-7xl` (full).

## Responsive Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <Card key={item.id} {...item} />
  ))}
</div>
```

## Auto-Fit Grid

Columns adjust automatically based on available space:

```tsx
<div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  {/* auto columns */}
</div>
```

## Container Queries

Style elements based on their parent container size instead of viewport:

```tsx
<div className="@container">
  <div className="flex flex-col @md:flex-row gap-4">
    <div className="w-full @md:w-1/3">Image</div>
    <div className="flex-1">Content</div>
  </div>
</div>
```

Built-in container breakpoints: `@xs` (16rem), `@sm` (24rem), `@md` (28rem), `@lg` (32rem), `@xl` (36rem), `@2xl` (42rem), `@3xl`-`@7xl`.

### Named Containers

Scope container queries to a specific parent:

```tsx
<div className="@container/sidebar">
  <nav className="@md/sidebar:flex @md/sidebar:flex-col">
    {/* responds to sidebar container, not viewport */}
  </nav>
</div>
```

### Max Container Queries

Apply styles when the container is at or below a breakpoint:

```tsx
<div className="@container">
  <div className="@max-md:flex-col @sm:@max-md:grid-cols-2">
    {/* combine min and max for ranges */}
  </div>
</div>
```

### Arbitrary Container Breakpoints

```tsx
<div className="@container">
  <div className="@[500px]:bg-red-100 @max-[800px]:text-sm">
    {/* custom pixel values */}
  </div>
</div>
```

## Sticky Header with Backdrop Blur

```tsx
<header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex h-16 items-center justify-between">
      <a href="/" className="font-bold text-xl">
        Brand
      </a>
      <nav className="hidden md:flex gap-6">
        <a href="#" className="text-sm hover:text-primary transition-colors">
          Features
        </a>
        <a href="#" className="text-sm hover:text-primary transition-colors">
          Pricing
        </a>
      </nav>
    </div>
  </div>
</header>
```

## Card Base

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
  <h3 className="text-lg font-semibold mb-2">Card Title</h3>
  <p className="text-muted-foreground">Card description goes here.</p>
</div>
```

## 3D Transforms

Native utilities for 3D manipulation (no plugins needed):

```tsx
<div className="perspective-1000">
  <div className="transform-3d transition-transform duration-500 hover:rotate-y-12 hover:rotate-x-6 bg-card rounded-2xl p-8">
    3D Card
  </div>
</div>
```

Key utilities: `perspective-{val}`, `rotate-x-{val}`, `rotate-y-{val}`, `rotate-z-{val}`, `translate-z-{val}`, `scale-z-{val}`, `transform-3d`.

## Subgrid

Align nested grid items with parent columns:

```tsx
<div className="grid grid-cols-4 gap-4">
  <div className="col-span-3 grid grid-cols-subgrid">
    <div>Aligns with parent column 1</div>
    <div>Aligns with parent column 2</div>
    <div>Aligns with parent column 3</div>
  </div>
</div>
```

## CVA for Component Variants

Use Class Variance Authority for type-safe variant management:

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

Usage in a component:

```tsx
interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}
```

## The cn() Utility

Merge Tailwind classes with conflict resolution:

```ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Masonry-Style Layout

```tsx
<div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
  {items.map((item) => (
    <div key={item.id} className="break-inside-avoid">
      <Card {...item} />
    </div>
  ))}
</div>
```

## Centered Content

```tsx
<div className="flex flex-col items-center justify-center text-center">
  <h1 className="text-4xl font-bold mb-4">Centered Title</h1>
  <p className="text-muted-foreground max-w-2xl">Centered description</p>
</div>
```

## Interactive Hover Effects

```tsx
{/* Lift on hover */}
<div className="transition-transform hover:scale-105">

{/* Shadow on hover */}
<div className="transition-shadow hover:shadow-lg">

{/* Color change on hover */}
<button className="transition-colors hover:bg-primary/90">
```

Always add `transition-*` classes to interactive elements for smooth state changes.
