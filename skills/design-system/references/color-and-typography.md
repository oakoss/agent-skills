---
title: Color and Typography
description: Color theory (60-30-10 rule), color scheme relationships, WCAG contrast requirements, font pairing, modular type scale, fluid typography, and responsive type
tags:
  [
    color,
    typography,
    contrast,
    wcag,
    font-pairing,
    type-scale,
    fluid-type,
    responsive,
  ]
---

# Color and Typography

## 60-30-10 Rule

Distribute color usage across the interface:

- 60% Primary (backgrounds, large areas)
- 30% Secondary (complementary elements, cards, sidebars)
- 10% Accent (CTAs, highlights, alerts)

## Color Scheme Relationships

| Scheme        | Description                           | Use Case            |
| ------------- | ------------------------------------- | ------------------- |
| Complementary | Opposite on wheel (blue + orange)     | High contrast, CTAs |
| Analogous     | Adjacent colors (blue + teal + green) | Harmonious, calm    |
| Triadic       | Three evenly spaced                   | Balanced, vibrant   |
| Monochromatic | Shades of one color                   | Minimal, safe       |

## Semantic Color Palette

Define colors by purpose, not appearance:

```css
:root {
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}
```

Each semantic color needs a foreground and background pair that passes contrast.

## Contrast Requirements (WCAG 2.1 AA)

| Element                         | Minimum Ratio |
| ------------------------------- | ------------- |
| Normal text                     | 4.5:1         |
| Large text (18px+ or 14px bold) | 3:1           |
| UI components and borders       | 3:1           |
| Focus indicators                | 3:1           |

```css
/* Pass: 8:1 contrast */
.text-good {
  color: #111827;
  background: #ffffff;
}

/* Fail: 2.1:1 contrast */
.text-bad {
  color: #d1d5db;
  background: #ffffff;
}
```

Check contrast at the semantic token layer, where foreground actually meets background. Primitive tokens alone cannot guarantee compliance because they lack usage context.

## CSS color-mix for Derived Colors

Generate hover and active states from a base color without separate tokens:

```css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: color-mix(in srgb, var(--color-primary), black 10%);
  --color-primary-active: color-mix(in srgb, var(--color-primary), black 20%);
  --color-primary-light: color-mix(in srgb, var(--color-primary), white 80%);
}
```

## Font Pairing (Maximum Two Fonts)

| Style                    | Heading                  | Body            |
| ------------------------ | ------------------------ | --------------- |
| Modern and Clean         | Inter                    | Inter           |
| Classic and Professional | Playfair Display (serif) | Source Sans Pro |
| Tech and Minimal         | Space Grotesk            | IBM Plex Sans   |
| Creative and Friendly    | Poppins                  | Open Sans       |

Using a single font family with weight variation (Inter 400/500/600/700) reduces load time and maintains consistency.

## Modular Type Scale (1.25 ratio, 16px base)

```css
:root {
  --text-xs: 0.75rem; /* 12px */
  --text-sm: 0.875rem; /* 14px */
  --text-base: 1rem; /* 16px */
  --text-lg: 1.125rem; /* 18px */
  --text-xl: 1.25rem; /* 20px */
  --text-2xl: 1.5rem; /* 24px */
  --text-3xl: 1.875rem; /* 30px */
  --text-4xl: 2.25rem; /* 36px */
}
```

## Line Height and Letter Spacing

| Context    | Line Height | Letter Spacing    |
| ---------- | ----------- | ----------------- |
| Headings   | 1.2 (tight) | -0.02em (tighter) |
| Body text  | 1.5-1.6     | 0 (normal)        |
| Small text | 1.8         | 0 (normal)        |
| Uppercase  | 1.2         | 0.05em (wider)    |
| Captions   | 1.4         | 0.01em            |

## Fluid Typography

Scale text smoothly between breakpoints without media queries:

```css
h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
}

h2 {
  font-size: clamp(1.5rem, 3.5vw, 2.5rem);
}

body {
  font-size: clamp(1rem, 1vw + 0.75rem, 1.125rem);
}
```

`clamp(min, preferred, max)` provides a minimum, a viewport-relative value, and a maximum. The browser picks the appropriate size within that range.

## Responsive Type Scale

For projects that prefer explicit breakpoints over fluid type:

```css
:root {
  --text-h1: 2rem;
}

@media (min-width: 768px) {
  :root {
    --text-h1: 2.5rem;
  }
}

@media (min-width: 1024px) {
  :root {
    --text-h1: 3rem;
  }
}
```

## Text Readability Rules

- Maximum line width: 65-75 characters (approximately `max-width: 65ch`)
- Minimum body text size: 16px (1rem) on mobile
- Paragraph spacing: at least 1.5x the font size
- Avoid justified text in narrow containers (causes uneven spacing)
