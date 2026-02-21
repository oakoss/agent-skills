---
title: Component Architecture
description: CVA variant system, compound components, headless UI with Radix, polymorphic rendering, controlled/uncontrolled patterns, component states, and atomic design
tags:
  [
    components,
    cva,
    compound-components,
    radix,
    headless-ui,
    variants,
    polymorphic,
    atomic-design,
  ]
---

# Component Architecture

## API Design Principles

1. **Sensible defaults** — works with minimal props (`<Button>Click</Button>`)
2. **Composition over configuration** — prefer compound components over prop-heavy APIs
3. **Controlled and uncontrolled modes** — support both `value` and `defaultValue`
4. **Polymorphic rendering** — `as` prop for element flexibility

## CVA Variant System

Type-safe variant management with class-variance-authority:

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

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

interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

export function Button({
  className,
  variant,
  size,
  isLoading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      {...props}
    >
      {children}
    </button>
  );
}
```

## Compound Components

Compound components share implicit state through React context, allowing flexible composition without prop drilling.

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

Prefer this over a single component with many props:

```tsx
/* Avoid this pattern */
<Modal
  title="Delete Account"
  body="Are you sure?"
  confirmText="Delete"
  cancelText="Cancel"
  onConfirm={handleDelete}
  onCancel={handleCancel}
/>
```

## Headless UI (Radix + Tailwind)

Radix provides accessible behavior; you provide the styles. This separates logic from presentation.

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
      <Tooltip.Content className="bg-surface-elevated text-text-primary p-2 rounded-md shadow-lg animate-in fade-in">
        {content}
        <Tooltip.Arrow className="fill-surface-elevated" />
      </Tooltip.Content>
    </Tooltip.Root>
  );
}
```

## Polymorphic Components

Allow components to render as different HTML elements or framework-specific components:

```tsx
type PolymorphicProps<T extends React.ElementType> = {
  as?: T;
} & React.ComponentPropsWithoutRef<T>;

function Button<T extends React.ElementType = 'button'>({
  as,
  ...props
}: PolymorphicProps<T>) {
  const Component = as || 'button';
  return <Component {...props} />;
}
```

Usage:

```tsx
<Button onClick={handleClick}>Click</Button>
<Button as="a" href="/dashboard">Dashboard</Button>
<Button as={Link} href="/about">About</Button>
```

## Controlled and Uncontrolled Patterns

Support both modes so consumers can choose:

```tsx
interface InputProps {
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
}

function Input({ value, defaultValue, onChange, ...props }: InputProps) {
  const [internal, setInternal] = useState(defaultValue ?? '');
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internal;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!isControlled) setInternal(e.target.value);
    onChange?.(e.target.value);
  };

  return <input value={currentValue} onChange={handleChange} {...props} />;
}
```

## FormField Pattern (Molecule)

Compose atoms into a labeled, accessible form field:

```tsx
function FormField({
  label,
  error,
  hint,
  required,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: (props: {
    id: string;
    'aria-invalid'?: boolean;
    'aria-describedby'?: string;
  }) => React.ReactNode;
}) {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const describedBy =
    [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ') ||
    undefined;

  return (
    <div>
      <label htmlFor={id}>
        {label}
        {required ? <span aria-label="required">*</span> : null}
      </label>
      {hint ? <div id={hintId}>{hint}</div> : null}
      {children({
        id,
        'aria-invalid': error ? true : undefined,
        'aria-describedby': describedBy,
      })}
      {error ? (
        <div id={errorId} role="alert">
          {error}
        </div>
      ) : null}
    </div>
  );
}
```

## Component States

Every interactive component must implement these states:

| State          | Visual                              | ARIA                  |
| -------------- | ----------------------------------- | --------------------- |
| Default        | Base styles                         | --                    |
| Hover          | Background/shadow shift             | --                    |
| Focus          | Visible ring (`outline: 2px solid`) | --                    |
| Active/Pressed | Darker shade                        | --                    |
| Disabled       | 50% opacity, `cursor: not-allowed`  | `aria-disabled`       |
| Loading        | Spinner overlay, text hidden        | `aria-busy="true"`    |
| Error          | Red border, error message           | `aria-invalid="true"` |

## Atomic Design Levels

| Level    | Description             | Examples                          |
| -------- | ----------------------- | --------------------------------- |
| Atom     | Smallest UI unit        | Button, Input, Label, Icon, Badge |
| Molecule | Group of atoms          | FormField, SearchBar, Card        |
| Organism | Complex UI section      | Header, LoginForm, ProductGrid    |
| Template | Page layout structure   | DashboardLayout, MarketingLayout  |
| Page     | Template with real data | HomePage, SettingsPage            |

Build atoms first, compose into molecules, then organisms. Templates define layout without content; pages fill in real data.
