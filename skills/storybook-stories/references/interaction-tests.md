---
title: Interaction Tests
description: Play functions, userEvent, Testing Library queries, assertions, waitFor, and test composition
tags: [play, userEvent, Testing Library, expect, waitFor, interaction, step]
---

# Interaction Tests

## Play Function Basics

Play functions execute after a story renders, simulating user interactions and validating behavior.

### Imports

```tsx
import { expect, fn } from 'storybook/test';
```

Storybook 9 provides `canvas`, `userEvent`, and `step` directly in the play function context. The `storybook/test` package (replacing `@storybook/test`) provides `expect`, `fn`, and other utilities.

### Basic Pattern

```tsx
import { type Meta, type StoryObj } from '@storybook/react';
import { expect, fn } from 'storybook/test';
import { Button } from './button';

const meta = {
  component: Button,
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ClickInteraction: Story = {
  args: {
    children: 'Click me',
    onPress: fn(),
  },
  play: async ({ args, canvas, userEvent }) => {
    const button = canvas.getByRole('button');

    await userEvent.click(button);
    await expect(args.onPress).toHaveBeenCalledTimes(1);
  },
};
```

Always await `userEvent` methods for proper logging in the Interactions panel.

## Canvas Scoping

The `canvas` object is provided directly in the play context, scoped to the story's DOM.

```tsx
export const FormInteraction: Story = {
  play: async ({ canvas, userEvent }) => {
    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const submitButton = canvas.getByRole('button', { name: 'Submit' });

    await userEvent.type(emailInput, 'user@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);
  },
};
```

### Portal Components

For components that render in portals (modals, tooltips, dropdowns), query from `body` using `within`:

```tsx
import { expect, fn } from 'storybook/test';
import { within } from '@storybook/test';

export const DialogInteraction: Story = {
  args: {
    onOpenChange: fn(),
  },
  play: async ({ args, canvas, canvasElement, userEvent }) => {
    const body = within(canvasElement.ownerDocument.body);

    const trigger = canvas.getByRole('button', { name: 'Open Dialog' });
    await userEvent.click(trigger);

    const dialog = body.getByRole('dialog');
    await expect(dialog).toBeInTheDocument();

    const closeButton = within(dialog).getByRole('button', { name: 'Close' });
    await userEvent.click(closeButton);

    await waitFor(() => {
      expect(args.onOpenChange).toHaveBeenCalledWith(false);
    });
  },
};
```

## Testing Library Queries

### Query Priority

Use queries in this order:

1. `getByRole` - Buttons, inputs, links, headings
2. `getByLabelText` - Form fields with labels
3. `getByPlaceholderText` - Inputs without labels
4. `getByText` - Non-interactive text content
5. `getByTestId` - Last resort only

### getByRole Examples

```tsx
canvas.getByRole('button');
canvas.getByRole('button', { name: 'Submit' });
canvas.getByRole('button', { name: /submit/i });
canvas.getByRole('textbox', { name: 'Email' });
canvas.getByRole('checkbox', { name: 'Accept terms' });
canvas.getByRole('heading', { level: 1 });
canvas.getByRole('link', { name: 'Learn more' });
```

### Async Queries

Use `findBy` for elements that appear asynchronously:

```tsx
const successMessage = await canvas.findByText('Form submitted');
await expect(successMessage).toBeVisible();
```

### Query Modifiers

```tsx
canvas.getByRole('button');
canvas.getAllByRole('button');
canvas.queryByRole('button');
canvas.queryAllByRole('button');
canvas.findByRole('button');
canvas.findAllByRole('button');
```

- `getBy` - Throws if not found (use for elements that should exist)
- `queryBy` - Returns null if not found (use for conditional elements)
- `findBy` - Async, waits for element (use for elements that appear later)

## User Interactions

### Click Events

```tsx
await userEvent.click(element);
await userEvent.dblClick(element);
await userEvent.tripleClick(element);
```

### Typing

```tsx
await userEvent.type(input, 'text to type');
await userEvent.clear(input);
await userEvent.type(input, 'replace{Backspace}d text');
```

Special keys:

```tsx
await userEvent.type(input, 'text{Enter}');
await userEvent.type(input, '{Escape}');
await userEvent.type(input, '{Tab}');
await userEvent.type(input, '{Shift>}text{/Shift}');
```

### Keyboard Navigation

```tsx
await userEvent.keyboard('{Tab}');
await userEvent.keyboard('{ArrowDown}');
await userEvent.keyboard('{Space}');
await userEvent.keyboard('[ShiftLeft>]A[/ShiftLeft]');
```

### Pointer Events

```tsx
await userEvent.hover(element);
await userEvent.unhover(element);
await userEvent.pointer({ target: element, coords: { x: 10, y: 20 } });
```

### Form Controls

```tsx
await userEvent.selectOptions(select, 'option-value');
await userEvent.selectOptions(select, ['multiple', 'options']);
await userEvent.upload(fileInput, file);
```

## Assertions

### Element State

```tsx
await expect(element).toBeInTheDocument();
await expect(element).toBeVisible();
await expect(element).not.toBeVisible();
await expect(element).toBeDisabled();
await expect(element).toBeEnabled();
await expect(element).toHaveFocus();
```

### Text Content

```tsx
await expect(element).toHaveTextContent('text');
await expect(element).toHaveTextContent(/pattern/i);
```

### Attributes

```tsx
await expect(element).toHaveAttribute('aria-expanded', 'true');
await expect(element).toHaveAttribute('disabled');
await expect(element).toHaveClass('active');
await expect(element).toHaveValue('value');
```

### Accessibility

```tsx
await expect(element).toHaveAccessibleName('Button label');
await expect(element).toHaveAccessibleDescription('Helper text');
```

### Function Calls

```tsx
await expect(args.onPress).toHaveBeenCalled();
await expect(args.onPress).toHaveBeenCalledTimes(2);
await expect(args.onPress).toHaveBeenCalledWith('arg1', 'arg2');
await expect(args.onPress).not.toHaveBeenCalled();
```

## Mocking Event Handlers

Use `fn()` from `storybook/test` to create mock functions:

```tsx
export const WithCallbacks: Story = {
  args: {
    onChange: fn(),
    onBlur: fn(),
    onFocus: fn(),
  },
  play: async ({ args, canvas, userEvent }) => {
    const input = canvas.getByRole('textbox');

    await userEvent.click(input);
    await expect(args.onFocus).toHaveBeenCalledTimes(1);

    await userEvent.type(input, 'text');
    await expect(args.onChange).toHaveBeenCalled();

    await userEvent.tab();
    await expect(args.onBlur).toHaveBeenCalledTimes(1);
  },
};
```

## WaitFor Pattern

Use `waitFor` for animations, async state updates, or delayed assertions:

```tsx
export const AsyncUpdate: Story = {
  args: {
    onSave: fn(),
  },
  play: async ({ args, canvas, userEvent }) => {
    const button = canvas.getByRole('button', { name: 'Save' });
    await userEvent.click(button);

    await waitFor(
      async () => {
        await expect(args.onSave).toHaveBeenCalled();
      },
      { timeout: 3000 },
    );

    const successMessage = await canvas.findByText('Saved successfully');
    await expect(successMessage).toBeVisible();
  },
};
```

## Play Function Composition

Reuse setup across stories:

```tsx
export const FilledForm: Story = {
  play: async ({ canvas, userEvent }) => {
    await userEvent.type(canvas.getByLabelText('Email'), 'test@example.com');
    await userEvent.type(canvas.getByLabelText('Password'), 'password123');
  },
};

export const SubmittedForm: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async (context) => {
    await FilledForm.play?.(context);

    const { args, canvas, userEvent } = context;
    const submitButton = canvas.getByRole('button', { name: 'Submit' });

    await userEvent.click(submitButton);
    await expect(args.onSubmit).toHaveBeenCalledTimes(1);
  },
};

export const ValidationError: Story = {
  play: async (context) => {
    await FilledForm.play?.(context);

    const { canvas, userEvent } = context;

    await userEvent.clear(canvas.getByLabelText('Email'));
    await userEvent.tab();

    const errorMessage = await canvas.findByText('Email is required');
    await expect(errorMessage).toBeVisible();
  },
};
```

Always use optional chaining `?.()` when calling composed play functions.

## Step Function

Group related interactions for better debugging. The `step` helper is available directly in the play context:

```tsx
export const MultiStepForm: Story = {
  play: async ({ canvas, step, userEvent }) => {
    await step('Fill personal information', async () => {
      await userEvent.type(canvas.getByLabelText('Name'), 'John Doe');
      await userEvent.type(canvas.getByLabelText('Email'), 'john@example.com');
    });

    await step('Select preferences', async () => {
      await userEvent.click(canvas.getByLabelText('Marketing emails'));
      await userEvent.selectOptions(canvas.getByLabelText('Country'), 'US');
    });

    await step('Submit form', async () => {
      const submitButton = canvas.getByRole('button', { name: 'Submit' });
      await userEvent.click(submitButton);
    });
  },
};
```

Steps appear as collapsible groups in the Interactions panel.

## beforeEach Hook

Set up mocks and preconditions before the story renders:

```tsx
import { expect, fn } from 'storybook/test';

export const WithMockedData: Story = {
  args: {
    getUsers: fn(),
    onSubmit: fn(),
  },
  beforeEach: async ({ args }) => {
    args.getUsers.mockResolvedValue([
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
    ]);
  },
  play: async ({ args, canvas, userEvent }) => {
    const usersList = canvas.getAllByRole('listitem');
    await expect(usersList).toHaveLength(2);

    const submitButton = canvas.getByRole('button', { name: 'Submit' });
    await userEvent.click(submitButton);

    await expect(args.onSubmit).toHaveBeenCalled();
  },
};
```

## Debugging Failed Tests

### Log Element State

```tsx
play: async ({ canvas }) => {
  console.log(canvas.getByRole('button').outerHTML);

  canvas.debug();

  canvas.debug(canvas.getByRole('button'));
};
```

### Check Element Visibility

```tsx
const element = canvas.queryByRole('button');
if (!element) {
  console.log('Button not found in DOM');
} else if (!element.offsetParent) {
  console.log('Button exists but is not visible');
}
```

### Increase Timeout

```tsx
export const SlowAnimation: Story = {
  parameters: {
    test: {
      timeout: 10000,
    },
  },
  play: async ({ canvasElement }) => {
    await waitFor(() => {}, { timeout: 5000 });
  },
};
```
