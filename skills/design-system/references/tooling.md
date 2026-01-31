---
title: Tooling
description: Style Dictionary token pipeline, Storybook documentation and addons, component testing with Testing Library and jest-axe, visual regression with Chromatic, and CI/CD integration
tags:
  [
    style-dictionary,
    storybook,
    testing,
    chromatic,
    visual-regression,
    accessibility-testing,
    ci-cd,
  ]
---

# Tooling

## Style Dictionary Pipeline

Transform tokens from JSON to CSS, iOS, Android, and other platforms. Use `outputReferences: true` to preserve the token reference chain in CSS output.

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
    scss: {
      transformGroup: 'scss',
      buildPath: 'dist/scss/',
      files: [
        {
          destination: '_variables.scss',
          format: 'scss/variables',
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

Build tokens:

```bash
npx style-dictionary build
```

Style Dictionary v4 supports the W3C DTCG token format (`$type`, `$value` fields) natively.

## Figma to Code Sync

Use Tokens Studio (formerly Figma Tokens) to sync design tokens from Figma to JSON files in your repository. The flow:

1. Designers define tokens in Figma via Tokens Studio plugin
2. Tokens Studio syncs token JSON to a GitHub branch
3. CI runs Style Dictionary to transform tokens into platform outputs
4. PR review ensures token changes are intentional

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

### Storybook Addons

| Addon                           | Purpose                       |
| ------------------------------- | ----------------------------- |
| `@storybook/addon-a11y`         | Accessibility audit per story |
| `@storybook/addon-interactions` | Test user interactions        |
| `storybook-addon-designs`       | Link Figma frames to stories  |

## Component Testing

Test components by role and accessible name, not by implementation details:

```ts
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('renders children', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
});

it('calls onClick when clicked', async () => {
  const user = userEvent.setup();
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  await user.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
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

Run axe on every component in CI to catch regressions.

## Visual Regression with Chromatic

Chromatic captures snapshots of every Storybook story and compares them across PRs.

```bash
npx chromatic --project-token=$CHROMATIC_TOKEN
```

Add to CI:

```yaml
- name: Visual regression
  run: npx chromatic --project-token=${{ secrets.CHROMATIC_TOKEN }} --exit-zero-on-changes
```

Chromatic flags visual diffs for human review before merge.

## CI/CD Integration

A design system CI pipeline should include:

| Step              | Tool                    | Purpose                         |
| ----------------- | ----------------------- | ------------------------------- |
| Lint              | ESLint, Stylelint       | Code quality                    |
| Type check        | TypeScript              | Type safety                     |
| Unit tests        | Vitest, Testing Library | Component behavior              |
| A11y tests        | jest-axe                | Accessibility compliance        |
| Build tokens      | Style Dictionary        | Token transformation            |
| Visual regression | Chromatic               | Catch unintended visual changes |
| Build Storybook   | Storybook               | Documentation generation        |
| Publish           | Changesets, npm         | Package release                 |

## Changesets for Versioning

Changesets automates versioning and changelog generation in monorepos:

```bash
npx changeset
npx changeset version
npx changeset publish
```

Each PR includes a changeset file describing the change type (major/minor/patch) and a description. The `version` command bumps versions and generates changelog entries.
