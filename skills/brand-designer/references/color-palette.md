---
title: Color Palette
description: Brand color definitions with full shade scales, Tailwind configuration, and color usage guidelines with accessibility notes
tags: [color, palette, tailwind, accessibility, branding]
---

# Color Palette

## Brand Colors

```typescript
export const brandColors = {
  primary: {
    50: '#E6F0FF',
    100: '#CCE0FF',
    200: '#99C2FF',
    300: '#66A3FF',
    400: '#3385FF',
    500: '#0066CC', // Main brand color
    600: '#0052A3',
    700: '#003D7A',
    800: '#002952',
    900: '#001429',
  },
  secondary: {
    50: '#FFF4E6',
    100: '#FFE9CC',
    200: '#FFD399',
    300: '#FFBD66',
    400: '#FFA733',
    500: '#FF9100', // Main accent
    600: '#CC7400',
    700: '#995700',
    800: '#663A00',
    900: '#331D00',
  },
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
};
```

## Tailwind Configuration

```typescript
module.exports = {
  theme: {
    colors: {
      primary: brandColors.primary,
      secondary: brandColors.secondary,
      gray: brandColors.neutral,
      green: brandColors.success,
    },
  },
};
```

## Color Usage Guidelines

### Primary Blue (#0066CC)

- **Use for:** Primary buttons, links, active states, brand elements
- **Don't use for:** Backgrounds, large areas
- **Accessibility:** Passes WCAG AA for text on white

### Secondary Orange (#FF9100)

- **Use for:** CTAs, highlights, important actions
- **Don't use for:** Body text
- **Pairing:** Works best with primary blue

### Neutral Grays

- **Use for:** Text, borders, backgrounds, UI elements
- **Hierarchy:**
  - 900: Headings
  - 700: Body text
  - 500: Secondary text
  - 300: Borders
  - 100: Backgrounds
