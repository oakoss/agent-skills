---
title: Story Writing
description: CSF3 story patterns, args, argTypes, decorators, parameters, and meta configuration
tags: [CSF3, args, argTypes, decorators, parameters, meta, render]
---

# Story Writing

## Component Story Format 3 (CSF3)

CSF3 uses object syntax with `satisfies` for type safety. Each story is an exported object with configuration.

### Basic Story with Args

Use `args` for simple stories where you render a single component with different props.

```tsx
import { type Meta, type StoryObj } from '@storybook/react';
import { Button } from './button';

const meta = {
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  title: 'Components/Button',
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Click me',
  },
};

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true,
  },
};
```

### Complex Story with Render

Use `render` when you need multiple components, wrappers, or complex layouts.

```tsx
export const WithIcon: Story = {
  render: (args) => (
    <Button {...args}>
      <Icon name="plus" className="size-4" />
      Add Item
    </Button>
  ),
};

export const ButtonGroup: Story = {
  parameters: {
    controls: { disable: true },
  },
  render: () => (
    <div className="flex gap-2">
      <Button variant="primary">Save</Button>
      <Button variant="secondary">Cancel</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  ),
};
```

Disable controls for showcase stories that demonstrate all variants.

## Meta Configuration

### Default Args

Define default args at the meta level to prevent "Set boolean" placeholders in controls.

```tsx
const meta = {
  args: {
    children: 'Button',
    disabled: false,
    size: 'medium',
    variant: 'default',
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

### ArgTypes

Configure controls and hide non-serializable props.

```tsx
const meta = {
  argTypes: {
    className: { table: { disable: true } },
    ref: { table: { disable: true } },
    style: { table: { disable: true } },

    variant: {
      control: 'select',
      options: ['default', 'primary', 'secondary', 'destructive'],
    },

    size: {
      control: 'radio',
      options: ['small', 'medium', 'large'],
    },

    icon: {
      control: 'select',
      mapping: {
        None: undefined,
        Plus: <Icon name="plus" />,
        Check: <Icon name="check" />,
      },
      options: ['None', 'Plus', 'Check'],
    },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

Hide React Aria props like `className`, `ref`, and `style` to prevent serialization errors.

### Parameters

Configure addon behavior per story or meta.

```tsx
const meta = {
  component: Dialog,
  parameters: {
    layout: 'centered',

    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a1a' },
      ],
    },

    viewport: {
      defaultViewport: 'mobile1',
    },
  },
} satisfies Meta<typeof Dialog>;
```

Override parameters in individual stories:

```tsx
export const FullWidth: Story = {
  parameters: {
    layout: 'fullscreen',
  },
  render: () => <Header />,
};
```

## Decorators

Decorators wrap stories with providers or layout containers.

### Theme Provider Decorator

```tsx
import { type Decorator } from '@storybook/react';
import { ThemeProvider } from './theme-provider';

const withTheme: Decorator = (Story) => (
  <ThemeProvider theme="light">
    <Story />
  </ThemeProvider>
);

const meta = {
  component: Button,
  decorators: [withTheme],
} satisfies Meta<typeof Button>;
```

### Layout Decorator

```tsx
const withPadding: Decorator = (Story) => (
  <div className="p-8">
    <Story />
  </div>
);

export const CardExample: Story = {
  decorators: [withPadding],
  render: () => <Card>Content</Card>,
};
```

### Router Decorator

```tsx
import { type Decorator } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';

const withRouter: Decorator = (Story) => (
  <MemoryRouter initialEntries={['/']}>
    <Story />
  </MemoryRouter>
);

const meta = {
  component: Navigation,
  decorators: [withRouter],
} satisfies Meta<typeof Navigation>;
```

## Story Organization

### Naming Stories

Use descriptive names that explain the scenario:

```tsx
export const Default: Story = { args: {} };

export const WithLongText: Story = {
  args: {
    children: 'This is a very long button label that might wrap',
  },
};

export const LoadingState: Story = {
  args: {
    children: 'Loading...',
    loading: true,
  },
};

export const ErrorState: Story = {
  args: {
    children: 'Retry',
    error: true,
  },
};
```

### Grouping with Title

Use slashes to create hierarchy:

```tsx
const meta = {
  component: Button,
  title: 'Components/Forms/Button',
} satisfies Meta<typeof Button>;
```

This creates: Components → Forms → Button

## Args Composition

Extend args from other stories:

```tsx
export const Primary: Story = {
  args: {
    variant: 'primary',
  },
};

export const PrimaryDisabled: Story = {
  args: {
    ...Primary.args,
    disabled: true,
  },
};
```

## Conditional Rendering

Always use ternary operator instead of `&&` to prevent inconsistent snapshots:

```tsx
export const ConditionalIcon: Story = {
  render: (args) => (
    <Button {...args}>
      {args.showIcon ? <Icon name="plus" /> : null}
      {args.children}
    </Button>
  ),
};
```

Avoid: `{args.showIcon && <Icon />}` because false values appear differently in snapshots.

## Multiple Components

Group related components in one file:

```tsx
import { type Meta, type StoryObj } from '@storybook/react';
import { Button } from './button';
import { ButtonGroup } from './button-group';

const meta = {
  component: Button,
  title: 'Components/Button',
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Single: Story = {
  args: { children: 'Button' },
};

const groupMeta = {
  component: ButtonGroup,
  title: 'Components/ButtonGroup',
} satisfies Meta<typeof ButtonGroup>;

export { groupMeta as ButtonGroupMeta };
```

## Story-Level TypeScript

Type args for custom properties:

```tsx
type CustomStory = StoryObj<typeof meta> & {
  args: {
    customProp?: string;
  };
};

export const WithCustomProp: CustomStory = {
  args: {
    customProp: 'value',
  },
  render: (args) => <Component {...args} />,
};
```

## Tags

Control story behavior with tags:

```tsx
const meta = {
  component: Button,
  tags: ['autodocs', 'test-only'],
} satisfies Meta<typeof Button>;

export const Example: Story = {
  tags: ['!dev'],
};
```

- `autodocs` - Generate documentation automatically
- `!dev` - Hide in dev mode
- `!test` - Exclude from test runner
- `test-only` - Only show in test runner
