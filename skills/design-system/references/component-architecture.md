---
title: Component Architecture
description: Component API design principles, CVA variant system, compound components, headless UI with Radix, component states, and polymorphic rendering
tags:
  [components, cva, compound-components, radix, headless-ui, variants, states]
---

# Component Architecture

## API Design Principles

1. **Sensible defaults** — works with minimal props (`<Button>Click</Button>`)
2. **Composition over configuration** — prefer compound components over prop-heavy APIs
3. **Controlled and uncontrolled modes** — support both `value` and `defaultValue`
4. **Polymorphic rendering** — `as` prop for element flexibility

## CVA Variant System

```tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
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
        sm: 'h-9 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-11 px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: { variant: 'default', size: 'md' },
  },
);
```

## Compound Components

```tsx
<Modal>
  <Modal.Header>Delete Account</Modal.Header>
  <Modal.Body>Are you sure?</Modal.Body>
  <Modal.Footer>
    <Button variant="destructive" onClick={handleDelete}>
      Delete
    </Button>
    <Button variant="secondary" onClick={handleCancel}>
      Cancel
    </Button>
  </Modal.Footer>
</Modal>
```

Compound components share implicit state through React context, allowing flexible composition without prop drilling.

## Headless UI (Radix + Tailwind)

```tsx
import * as Tooltip from '@radix-ui/react-tooltip';

export function CustomTooltip({
  children,
  content,
}: {
  children: React.ReactNode;
  content: string;
}) {
  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
      <Tooltip.Content className="bg-brand-primary text-white p-2 rounded-button shadow-xl animate-in fade-in">
        {content}
        <Tooltip.Arrow className="fill-brand-primary" />
      </Tooltip.Content>
    </Tooltip.Root>
  );
}
```

## Component States

| State          | Visual                              | ARIA                  |
| -------------- | ----------------------------------- | --------------------- |
| Default        | Base styles                         | —                     |
| Hover          | Background/shadow shift             | —                     |
| Focus          | Visible ring (`outline: 2px solid`) | —                     |
| Active/Pressed | Darker shade                        | —                     |
| Disabled       | 50% opacity, `cursor: not-allowed`  | `aria-disabled`       |
| Loading        | Spinner overlay, text hidden        | `aria-busy="true"`    |
| Error          | Red border, error message           | `aria-invalid="true"` |
