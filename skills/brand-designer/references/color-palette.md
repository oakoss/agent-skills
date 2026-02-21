---
title: Color Palette
description: Brand color definitions with shade scales, Tailwind configuration, color theory, OKLCH color space, palette generation, semantic mapping, dark mode strategy, and accessibility
tags:
  [
    color,
    palette,
    tailwind,
    accessibility,
    branding,
    oklch,
    dark-mode,
    color-theory,
  ]
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

## Color Theory Fundamentals

### Color Relationships

| Harmony             | Description                               | Use Case                      |
| ------------------- | ----------------------------------------- | ----------------------------- |
| Complementary       | Opposite on the color wheel               | High contrast CTAs, alerts    |
| Analogous           | Adjacent colors (30 degrees apart)        | Cohesive, harmonious palettes |
| Triadic             | Three colors equally spaced (120 degrees) | Vibrant, balanced designs     |
| Split-complementary | Base + two adjacent to its complement     | Contrast with less tension    |

### Applying Harmony to Brand Palettes

Start with the brand primary. Use harmony rules to select secondary and accent colors:

1. **Primary**: Core brand color chosen from discovery
2. **Secondary**: Use analogous or split-complementary relationship to primary
3. **Accent**: Use complementary or triadic for high-contrast moments
4. **Neutral**: Desaturated version of primary for grays with brand warmth

## OKLCH Color Space

OKLCH provides perceptually uniform color manipulation. Unlike HSL, equal lightness values in OKLCH actually appear equally light to the human eye.

### OKLCH Components

| Component     | Range  | Purpose                    |
| ------------- | ------ | -------------------------- |
| L (lightness) | 0-1    | Perceptual brightness      |
| C (chroma)    | 0-0.4+ | Color intensity/saturation |
| H (hue)       | 0-360  | Color angle on wheel       |

### CSS oklch() Syntax

```css
:root {
  --brand-primary: oklch(0.55 0.2 250);
  --brand-light: oklch(0.85 0.08 250);
  --brand-dark: oklch(0.35 0.15 250);
}
```

### Why OKLCH Over HSL

```css
/* HSL: these look different brightness despite same L value */
.hsl-blue {
  color: hsl(220 80% 50%);
}
.hsl-yellow {
  color: hsl(60 80% 50%);
}

/* OKLCH: same L value = same perceived brightness */
.oklch-blue {
  color: oklch(0.6 0.15 250);
}
.oklch-yellow {
  color: oklch(0.6 0.15 90);
}
```

## Palette Generation with OKLCH

Generate consistent shade scales by varying the lightness channel while keeping chroma and hue stable.

### Shade Scale Pattern

```typescript
function generateShadeScale(
  hue: number,
  chroma: number,
): Record<string, string> {
  return {
    50: `oklch(0.97 ${chroma * 0.2} ${hue})`,
    100: `oklch(0.93 ${chroma * 0.3} ${hue})`,
    200: `oklch(0.85 ${chroma * 0.5} ${hue})`,
    300: `oklch(0.75 ${chroma * 0.7} ${hue})`,
    400: `oklch(0.65 ${chroma * 0.9} ${hue})`,
    500: `oklch(0.55 ${chroma} ${hue})`,
    600: `oklch(0.48 ${chroma * 0.95} ${hue})`,
    700: `oklch(0.40 ${chroma * 0.85} ${hue})`,
    800: `oklch(0.30 ${chroma * 0.7} ${hue})`,
    900: `oklch(0.20 ${chroma * 0.5} ${hue})`,
  };
}
```

### Tailwind with OKLCH

```typescript
export default {
  theme: {
    extend: {
      colors: {
        brand: {
          50: 'oklch(0.97 0.04 250)',
          100: 'oklch(0.93 0.06 250)',
          200: 'oklch(0.85 0.10 250)',
          300: 'oklch(0.75 0.14 250)',
          400: 'oklch(0.65 0.18 250)',
          500: 'oklch(0.55 0.20 250)',
          600: 'oklch(0.48 0.19 250)',
          700: 'oklch(0.40 0.17 250)',
          800: 'oklch(0.30 0.14 250)',
          900: 'oklch(0.20 0.10 250)',
        },
      },
    },
  },
};
```

## Semantic Color Mapping

Map palette colors to semantic roles. Components reference semantic tokens, not raw palette values.

### Token Structure

```css
:root {
  /* Semantic tokens reference palette values */
  --color-action: var(--primary-500);
  --color-action-hover: var(--primary-600);
  --color-accent: var(--secondary-500);
  --color-accent-subtle: var(--secondary-100);

  --color-text-primary: var(--neutral-900);
  --color-text-secondary: var(--neutral-600);
  --color-text-muted: var(--neutral-400);

  --color-bg-primary: white;
  --color-bg-secondary: var(--neutral-50);
  --color-bg-elevated: white;

  --color-border: var(--neutral-200);
  --color-border-focus: var(--primary-500);

  --color-danger: var(--red-500);
  --color-warning: var(--amber-500);
  --color-success: var(--green-500);
}
```

### Semantic Mapping Table

| Semantic Role  | Light Mode    | Purpose                          |
| -------------- | ------------- | -------------------------------- |
| Action         | Primary 500   | Buttons, links, interactive      |
| Action hover   | Primary 600   | Hover/pressed states             |
| Accent         | Secondary 500 | Highlights, badges, decorative   |
| Text primary   | Neutral 900   | Headings, body text              |
| Text secondary | Neutral 600   | Captions, labels                 |
| Background     | White         | Page background                  |
| Surface        | Neutral 50    | Cards, sections                  |
| Border         | Neutral 200   | Dividers, input borders          |
| Danger         | Red 500       | Errors, destructive actions      |
| Warning        | Amber 500     | Caution states                   |
| Success        | Green 500     | Confirmations, positive feedback |

## Dark Mode Color Strategy

Dark mode is not color inversion. It requires intentional adjustments to maintain readability and brand recognition.

### Key Principles

1. **Reduce saturation**: Vivid colors strain eyes on dark backgrounds. Drop chroma by 10-20%
2. **Adjust lightness**: Swap the scale direction. Light mode 900 text becomes dark mode 100 text
3. **Maintain contrast**: WCAG 4.5:1 for body text, 3:1 for large text and UI elements
4. **Elevate with lightness**: Instead of shadows, use lighter surface colors to show elevation

### Dark Mode Token Overrides

```css
[data-theme='dark'] {
  --color-action: var(--primary-400);
  --color-action-hover: var(--primary-300);
  --color-accent: var(--secondary-400);

  --color-text-primary: var(--neutral-100);
  --color-text-secondary: var(--neutral-400);
  --color-text-muted: var(--neutral-500);

  --color-bg-primary: var(--neutral-900);
  --color-bg-secondary: var(--neutral-800);
  --color-bg-elevated: var(--neutral-800);

  --color-border: var(--neutral-700);
  --color-border-focus: var(--primary-400);
}
```

### Surface Elevation in Dark Mode

| Elevation | Surface Color | Use Case            |
| --------- | ------------- | ------------------- |
| Base      | Neutral 900   | Page background     |
| Level 1   | Neutral 800   | Cards, sidebars     |
| Level 2   | Neutral 750   | Dropdowns, popovers |
| Level 3   | Neutral 700   | Modals, dialogs     |

### Testing Dark Mode Colors

- Verify all text passes WCAG AA contrast on its background
- Check that primary brand color is still recognizable (not washed out)
- Ensure danger/warning/success colors remain distinguishable from each other
- Test in actual dark environments, not just a dark browser window
