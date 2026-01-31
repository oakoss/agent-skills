---
title: Design Tokens
description: Three-layer token hierarchy, CSS custom properties, TypeScript definitions, W3C DTCG format, naming conventions, and file architecture
tags:
  [
    design-tokens,
    css-variables,
    primitive,
    semantic,
    component,
    hierarchy,
    naming,
  ]
---

# Design Tokens

Atomic values of a design system — colors, spacing, typography, shadows, radii — stored as data and consumed across platforms. Tokens are the single source of truth: change once, update everywhere.

## Three-Layer CSS Custom Properties

```css
/* Layer 1: Primitive tokens (raw values, never used directly in components) */
:root {
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  --color-gray-50: #fafafa;
  --color-gray-100: #f5f5f5;
  --color-gray-200: #e5e7eb;
  --color-gray-400: #9ca3af;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #171717;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* Layer 2: Semantic tokens (meaning, theme-switchable) */
:root {
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --surface-default: white;
  --surface-elevated: var(--color-gray-50);
  --border-default: var(--color-gray-200);
  --interactive-primary: var(--color-blue-500);
  --interactive-primary-hover: var(--color-blue-600);
  --focus-ring: var(--color-blue-500);
}

/* Layer 3: Component tokens (specific usage) */
:root {
  --button-bg: var(--interactive-primary);
  --button-bg-hover: var(--interactive-primary-hover);
  --button-text: white;
  --button-radius: var(--radius-md);
  --button-padding-x: var(--space-4);
  --button-padding-y: var(--space-2);
  --input-border: var(--border-default);
  --input-focus-ring: var(--focus-ring);
  --card-bg: var(--surface-elevated);
  --card-shadow: var(--shadow-md);
}
```

## Token Naming Conventions

Consistent naming prevents sprawl and makes tokens discoverable.

| Pattern                   | Example                        | Rule                                 |
| ------------------------- | ------------------------------ | ------------------------------------ |
| Primitive: category-scale | `color-blue-500`               | Descriptive of the raw value         |
| Semantic: purpose         | `text-primary`                 | Named by intent, not appearance      |
| Component: component-prop | `button-bg`                    | Scoped to specific component usage   |
| Kebab-case throughout     | `interactive-primary-hover`    | No camelCase or mixed conventions    |
| No visual descriptions    | `text-primary` not `dark-gray` | Semantic names survive theme changes |

## Token Categories

| Category   | Primitive                 | Semantic                          | Component                             |
| ---------- | ------------------------- | --------------------------------- | ------------------------------------- |
| Color      | `color-blue-500: #3b82f6` | `interactive-primary: {blue-500}` | `button-bg: {interactive-primary}`    |
| Spacing    | `space-4: 1rem`           | `spacing-default: {space-4}`      | `button-padding-x: {spacing-default}` |
| Typography | `font-size-base: 1rem`    | `text-body: {font-size-base}`     | `input-font-size: {text-body}`        |
| Shadow     | `shadow-md: 0 4px 6px...` | `elevation-card: {shadow-md}`     | `card-shadow: {elevation-card}`       |
| Radius     | `radius-md: 0.5rem`       | `radius-interactive: {radius-md}` | `button-radius: {radius-interactive}` |

## File Architecture

```sh
tokens/
  primitives/
    colors.json
    spacing.json
    typography.json
    shadows.json
    radii.json
  semantic/
    colors.json
    spacing.json
    typography.json
  components/
    button.json
    input.json
    card.json
```

## W3C Design Token Community Group Format

The DTCG format standardizes token interchange across tools (Figma, Style Dictionary, Tokens Studio).

```json
{
  "color": {
    "brand": {
      "primary": {
        "$type": "color",
        "$value": "#3b82f6",
        "$description": "Primary brand color"
      }
    }
  },
  "spacing": {
    "default": {
      "$type": "dimension",
      "$value": "1rem"
    }
  }
}
```

Use `$type`, `$value`, and `$description` fields. Tools like Style Dictionary v4 and Tokens Studio support this format natively.

## TypeScript Token Definition

```ts
export const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      900: '#1e3a8a',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      900: '#111827',
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
  },
  spacing: {
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    6: '1.5rem',
    8: '2rem',
    12: '3rem',
    16: '4rem',
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: { normal: 400, medium: 500, semibold: 600, bold: 700 },
    lineHeight: { tight: 1.25, normal: 1.5, relaxed: 1.75 },
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  },
  radii: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  },
} as const;
```
