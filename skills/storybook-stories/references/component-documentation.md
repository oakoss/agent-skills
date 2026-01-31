---
title: Component Documentation
description: Autodocs, MDX, controls configuration, description tables, and documentation patterns
tags: [autodocs, MDX, controls, descriptions, argTypes, documentation]
---

# Component Documentation

## Autodocs

Enable automatic documentation generation with the `autodocs` tag:

```tsx
const meta = {
  component: Button,
  tags: ['autodocs'],
  title: 'Components/Button',
} satisfies Meta<typeof Button>;
```

Storybook generates a documentation page with:

- Component description from JSDoc comments
- Props table from TypeScript types
- Interactive controls for all stories
- Live code examples

### Component Description

Add JSDoc comments to your component:

```tsx
/**
 * Primary UI component for user interaction. Supports multiple variants,
 * sizes, and states. Built on React Aria for accessibility.
 */
export function Button({
  variant = 'default',
  size = 'medium',
  ...props
}: ButtonProps) {
  return <button {...props} />;
}
```

The description appears at the top of the docs page.

### Prop Descriptions

Document individual props:

```tsx
type ButtonProps = {
  /**
   * Visual style variant
   * @default 'default'
   */
  variant?: 'default' | 'primary' | 'secondary' | 'destructive';

  /**
   * Button size affecting padding and font size
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';

  /**
   * Disables the button and prevents interactions
   */
  disabled?: boolean;

  /**
   * Callback fired when the button is pressed
   */
  onPress?: () => void;
};
```

Descriptions appear in the props table.

## ArgTypes Configuration

### Control Types

Configure control types in meta:

```tsx
const meta = {
  argTypes: {
    variant: {
      control: 'select',
      description: 'Visual style variant',
      options: ['default', 'primary', 'secondary', 'destructive'],
    },

    size: {
      control: 'radio',
      options: ['small', 'medium', 'large'],
    },

    disabled: {
      control: 'boolean',
    },

    children: {
      control: 'text',
    },

    count: {
      control: { type: 'number', min: 0, max: 10, step: 1 },
    },

    backgroundColor: {
      control: 'color',
    },

    date: {
      control: 'date',
    },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

### Hide Props

Hide props from the controls and docs table:

```tsx
const meta = {
  argTypes: {
    className: { table: { disable: true } },
    ref: { table: { disable: true } },
    style: { table: { disable: true } },

    // Hide but keep in table
    onPress: { control: false },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

Hide non-serializable props like `className`, `ref`, and `style` to prevent errors.

### Control Categories

Group controls into categories:

```tsx
const meta = {
  argTypes: {
    variant: {
      table: { category: 'Appearance' },
    },
    size: {
      table: { category: 'Appearance' },
    },
    disabled: {
      table: { category: 'State' },
    },
    onPress: {
      table: { category: 'Events' },
    },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

### Custom Mappings

Map control values to React elements:

```tsx
const meta = {
  argTypes: {
    icon: {
      control: 'select',
      mapping: {
        None: undefined,
        Plus: <PlusIcon />,
        Check: <CheckIcon />,
        Close: <CloseIcon />,
      },
      options: ['None', 'Plus', 'Check', 'Close'],
    },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

### Default Values

Set default values for controls:

```tsx
const meta = {
  args: {
    children: 'Button',
    disabled: false,
    size: 'medium',
    variant: 'default',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'secondary'],
    },
  },
  component: Button,
} satisfies Meta<typeof Button>;
```

Default args prevent "Set boolean" placeholders in controls.

## MDX Documentation

Create custom documentation pages with MDX:

```mdx
import { Canvas, Controls, Description, Meta, Story } from '@storybook/blocks';
import * as ButtonStories from './button.stories';

<Meta of={ButtonStories} />

# Button

<Description of={ButtonStories} />

## Usage

Buttons trigger actions and events.

<Canvas of={ButtonStories.Primary} />

## Props

<Controls of={ButtonStories.Primary} />

## Variants

<Canvas of={ButtonStories.AllVariants} />

### Primary

Use for main call-to-action buttons.

<Story of={ButtonStories.Primary} />

### Secondary

Use for secondary actions.

<Story of={ButtonStories.Secondary} />

## Best Practices

- Use clear, action-oriented labels
- Provide accessible names for icon-only buttons
- Disable during async operations to prevent double-submission
```

Save as `button.mdx` and reference in stories:

```tsx
const meta = {
  component: Button,
  parameters: {
    docs: {
      page: () => import('./button.mdx'),
    },
  },
} satisfies Meta<typeof Button>;
```

## Description Blocks

### Component Description

```mdx
import { Description } from '@storybook/blocks';
import * as Stories from './button.stories';

<Description of={Stories} />
```

Pulls description from component JSDoc.

### Story Description

```tsx
export const Primary: Story = {
  args: {
    variant: 'primary',
  },
  parameters: {
    docs: {
      description: {
        story: 'Primary buttons draw attention to main actions.',
      },
    },
  },
};
```

Appears above the story in docs.

### Meta Description

```tsx
const meta = {
  component: Button,
  parameters: {
    docs: {
      description: {
        component: 'Buttons trigger actions when pressed.',
      },
    },
  },
} satisfies Meta<typeof Button>;
```

Overrides JSDoc component description.

## Code Examples

### Source Code Display

Show formatted source code:

```mdx
import { Source } from '@storybook/blocks';

<Source
  code={`
<Button variant="primary" size="large">
  Primary Button
</Button>
`}
  language="tsx"
/>
```

### Dynamic Source

Display story source:

```mdx
import { Source } from '@storybook/blocks';
import * as Stories from './button.stories';

<Source of={Stories.Primary} />
```

### Hide Source

Hide source code for a story:

```tsx
export const Internal: Story = {
  parameters: {
    docs: {
      source: { code: null },
    },
  },
};
```

## Canvas Configuration

Configure layout, backgrounds, and viewport:

```tsx
export const FullWidth: Story = {
  parameters: {
    layout: 'fullscreen', // or 'centered', 'padded'
    backgrounds: { default: 'dark' },
    viewport: { defaultViewport: 'mobile1' },
  },
};
```

## Story Sorting

Sort stories in custom order:

```tsx
const meta = {
  component: Button,
  parameters: {
    docs: {
      story: {
        inline: true,
      },
    },
  },
  title: 'Components/Button',
} satisfies Meta<typeof Button>;

export const _01_Default: Story = { args: {} };
export const _02_Primary: Story = { args: { variant: 'primary' } };
export const _03_Secondary: Story = { args: { variant: 'secondary' } };
```

Prefix story names with numbers for explicit ordering.

## Subcomponents

Document related components together:

```tsx
const meta = {
  component: Card,
  subcomponents: {
    CardContent,
    CardFooter,
    CardHeader,
  },
  title: 'Components/Card',
} satisfies Meta<typeof Card>;
```

Subcomponents appear in the props table dropdown.

## Disable Docs

Hide story from docs page:

```tsx
export const InternalOnly: Story = {
  parameters: {
    docs: { disable: true },
  },
};
```

Hide entire meta from docs:

```tsx
const meta = {
  component: Button,
  tags: ['!autodocs'],
} satisfies Meta<typeof Button>;
```
