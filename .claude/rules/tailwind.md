---
paths:
  - 'skills/tailwind/references/**'
  - 'skills/shadcn-ui/references/**'
  - 'skills/css-animation-patterns/references/**'
  - 'skills/**/references/*styling*'
  - 'skills/**/references/*design-token*'
  - 'skills/**/references/*component-pattern*'
  - 'skills/**/references/*shadcn*'
  - 'skills/**/references/*theming*'
  - 'skills/**/references/*dark-mode*'
  - 'skills/**/references/*prose*'
---

# Tailwind CSS v4

## Configuration (app.css)

Tailwind v4 uses CSS-native configuration:

```css
/* Import Tailwind (replaces @tailwind directives) */
@import 'tailwindcss';

/* Custom dark mode variant */
@custom-variant dark (&:is(.dark *));

/* Theme configuration */
@theme inline {
  --color-background: var(--background);
  --color-primary: var(--primary);
  --radius-lg: var(--radius);
}

/* Base layer styles */
@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

## OKLCH Color Space

Tailwind v4 uses OKLCH for perceptually uniform colors:

```css
:root {
  --background: oklch(1 0 0); /* White */
  --foreground: oklch(0.141 0.005 285); /* Near black */
  --primary: oklch(0.21 0.006 285); /* Dark zinc */
  --destructive: oklch(0.577 0.245 27); /* Red */
}

.dark {
  --background: oklch(0.141 0.005 285);
  --foreground: oklch(0.985 0 0);
}
```

## Class Name Utility

```tsx
import { cn } from '@/lib/utils';
<div className={cn('base-class', isActive && 'active-class', className)} />;
```

## Data Attribute Selectors

```tsx
// Style based on own data attribute
<div data-active className="data-active:border-purple-500" />
<div data-size="lg" className="data-[size=lg]:p-8" />

// Style based on descendant's data attribute (has-*)
<div className="has-data-[slot=action]:grid-cols-2">
  <div data-slot="action">...</div>
</div>

// Style ALL descendants with data attribute (**)
<ul className="**:data-avatar:size-12 **:data-avatar:rounded-full">
  <li><img data-avatar /></li>
</ul>
```

| Pattern              | Meaning                             |
| -------------------- | ----------------------------------- |
| `data-active:`       | Element has `data-active`           |
| `data-[size=lg]:`    | Element has `data-size="lg"`        |
| `has-data-[slot=x]:` | Has descendant with `data-slot="x"` |
| `**:data-x:`         | All descendants with `data-x`       |

## New Variants (v4)

```tsx
// not-* - Style when condition is NOT true
<button className="hover:not-focus:bg-indigo-700" />

// inert - Style inert (non-interactive) elements
<fieldset inert className="inert:opacity-50" />

// starting: - Initial render styles (@starting-style)
<div popover className="opacity-100 starting:open:opacity-0" />

// ** - All descendants (not just direct children)
<div className="**:text-sm **:font-medium" />
```

## Container Queries

```tsx
// Named container
<div className="@container/card">
  {/* Responsive based on container, not viewport */}
  <div className="@md/card:flex-row @lg/card:gap-8" />
</div>

// Unnamed container
<div className="@container">
  <div className="@sm:grid-cols-2 @lg:grid-cols-3" />
</div>
```

## 3D Transforms (v4)

```tsx
// Enable 3D space for children
<div className="transform-3d perspective-normal">
  <div className="translate-z-12 rotate-y-45" />
</div>

// Perspective values: dramatic, near, normal, midrange, distant
<div className="perspective-dramatic" />  {/* 100px */}
<div className="perspective-distant" />   {/* 1200px */}
```

## Breaking Changes from v3

| Change       | v3                  | v4                         |
| ------------ | ------------------- | -------------------------- |
| Ring width   | `ring` = 3px        | `ring` = 1px, use `ring-3` |
| Ring color   | `ring` = blue-500   | `ring` = currentColor      |
| Border color | `border` = gray-200 | `border` = currentColor    |
| Import       | `@tailwind base`    | `@import 'tailwindcss'`    |

## Custom Utilities (@utility)

```css
/* Old v3 way */
@layer utilities {
  .tab-4 {
    tab-size: 4;
  }
}

/* New v4 way - auto-sorted, works with variants */
@utility tab-4 {
  tab-size: 4;
}

/* Component-style utility */
@utility btn {
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
}
```

## CVA Pattern (class-variance-authority)

```tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva('inline-flex items-center rounded-md', {
  variants: {
    variant: {
      default: 'bg-primary text-primary-foreground',
      outline: 'border bg-background',
    },
    size: {
      default: 'h-9 px-4',
      sm: 'h-8 px-3',
      lg: 'h-10 px-6',
    },
  },
  defaultVariants: { variant: 'default', size: 'default' },
});

type ButtonProps = VariantProps<typeof buttonVariants>;
```

## data-slot Pattern

Components use `data-slot` for styling and debugging:

```tsx
<div data-slot="card">
  <div data-slot="card-header">...</div>
  <div data-slot="card-content">...</div>
</div>

// Parent can style based on children
<div className="has-data-[slot=card-action]:grid-cols-[1fr_auto]">
```

## React Aria State Styling

React Aria exposes state via data attributes:

```tsx
<Button className="data-pressed:scale-95 data-disabled:opacity-50">
  Click me
</Button>
```

Available React Aria data attributes:

- `data-pressed` - Button is being pressed
- `data-hovered` - Element is hovered
- `data-focused` - Element has focus
- `data-focus-visible` - Element has keyboard focus
- `data-disabled` - Element is disabled
- `data-selected` - Element is selected
- `data-open` - Disclosure/popover is open
