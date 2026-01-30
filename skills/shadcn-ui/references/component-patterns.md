---
title: Component Patterns and Variants
description: shadcn/ui component authoring patterns including CVA variants, direct refs, polymorphic slots, and accessible composition
tags: [components, cva, variants, radix, accessibility, composition, ref]
---

# Component Patterns and Variants

shadcn/ui components are source code you own. They combine Radix UI primitives for accessibility with CVA for variant management and Tailwind for styling.

## React 19 Direct Ref Pattern

`forwardRef` is deprecated in React 19. Pass `ref` directly as a prop:

```tsx
import { type ButtonHTMLAttributes } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline:
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
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
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

interface ButtonProps
  extends
    ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({
  className,
  variant,
  size,
  asChild = false,
  ref,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : 'button';
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  );
}
```

## Polymorphic Composition with asChild

The `asChild` pattern from Radix merges the component's props onto its child element:

```tsx
import { Button } from '@/components/ui/button';
import Link from 'next/link';

function NavButton() {
  return (
    <Button asChild variant="ghost">
      <Link href="/dashboard">Go to Dashboard</Link>
    </Button>
  );
}
```

This renders a `<a>` tag with all the Button styles and accessibility behavior.

## CVA Variant Authoring

Class Variance Authority (CVA) provides type-safe variant definitions:

```tsx
import { cva, type VariantProps } from 'class-variance-authority';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        destructive:
          'border-transparent bg-destructive text-destructive-foreground',
        outline: 'text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
);

interface BadgeProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
```

## The cn() Utility

The `cn` function safely merges Tailwind classes using `clsx` and `tailwind-merge`:

```ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

This prevents class conflicts like `p-2 p-4` by keeping only the last value.

## Accessible Dialog Pattern

Radix Dialog provides keyboard navigation, focus trapping, and ARIA attributes:

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

export function ConfirmDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="destructive">Delete Account</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete your
            account and remove your data from our servers.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end gap-2">
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive">Delete</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

## Component Prop Ordering Convention

Sort props in this order: reserved, boolean, data, callbacks:

```tsx
interface CardProps {
  // Reserved
  className?: string;
  ref?: React.Ref<HTMLDivElement>;
  // Boolean
  bordered?: boolean;
  elevated?: boolean;
  // Data
  title: string;
  description?: string;
  // Callbacks
  onClick?: () => void;
}
```

## Adding New Components

Always use the canary CLI to add components:

```bash
bun x shadcn-ui@canary add button
bun x shadcn-ui@canary add dialog
bun x shadcn-ui@canary add form
```

Components are copied to `src/components/ui/` (or the configured path). From that point, you own the source code and customize it directly.
