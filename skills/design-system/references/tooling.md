---
title: Tooling
description: Style Dictionary token pipeline, Storybook documentation, component testing with Testing Library and jest-axe, and visual regression with Chromatic
tags:
  [
    style-dictionary,
    storybook,
    testing,
    chromatic,
    visual-regression,
    accessibility-testing,
  ]
---

# Tooling

## Style Dictionary Pipeline

Transform tokens from JSON to CSS/iOS/Android:

```js
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [
        {
          destination: 'variables.css',
          format: 'css/variables',
          options: { outputReferences: true },
        },
      ],
    },
    ios: {
      transformGroup: 'ios-swift',
      buildPath: 'dist/ios/',
      files: [
        {
          destination: 'DesignTokens.swift',
          format: 'ios-swift/class.swift',
          className: 'DesignTokens',
        },
      ],
    },
    android: {
      transformGroup: 'android',
      buildPath: 'dist/android/',
      files: [
        {
          destination: 'colors.xml',
          format: 'android/colors',
          filter: { attributes: { category: 'color' } },
        },
      ],
    },
  },
};
```

## Storybook Documentation

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Atoms/Button',
  component: Button,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'destructive'],
    },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    isLoading: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
};
export default meta;

type Story = StoryObj<typeof Button>;
export const Primary: Story = {
  args: { variant: 'primary', children: 'Button' },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
};
```

## Component Testing

```ts
import { render, screen } from '@testing-library/react';

it('renders children', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
});

it('disables button when loading', () => {
  render(<Button isLoading>Click me</Button>);
  expect(screen.getByRole('button')).toBeDisabled();
});
```

## Accessibility Testing

```ts
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  expect(await axe(container)).toHaveNoViolations();
});
```

## Visual Regression

Use Chromatic with Storybook for automated snapshot comparison across PRs.
