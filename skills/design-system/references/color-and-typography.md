---
title: Color and Typography
description: Color theory (60-30-10 rule), color scheme relationships, WCAG contrast requirements, font pairing, modular type scale, fluid typography, and line height rules
tags: [color, typography, contrast, wcag, font-pairing, type-scale, fluid-type]
---

# Color and Typography

## 60-30-10 Rule

- 60% Primary (backgrounds, large areas)
- 30% Secondary (complementary elements)
- 10% Accent (CTAs, highlights)

## Color Scheme Relationships

| Scheme        | Description                           | Use Case            |
| ------------- | ------------------------------------- | ------------------- |
| Complementary | Opposite on wheel (blue + orange)     | High contrast, CTAs |
| Analogous     | Adjacent colors (blue + teal + green) | Harmonious, calm    |
| Triadic       | Three evenly spaced                   | Balanced, vibrant   |
| Monochromatic | Shades of one color                   | Minimal, safe       |

## Contrast Requirements (WCAG 2.1 AA)

| Element                         | Minimum Ratio |
| ------------------------------- | ------------- |
| Normal text                     | 4.5:1         |
| Large text (18px+ or 14px bold) | 3:1           |
| UI components                   | 3:1           |

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

## Font Pairing (Maximum Two Fonts)

| Style                    | Heading                  | Body            |
| ------------------------ | ------------------------ | --------------- |
| Modern and Clean         | Inter                    | Inter           |
| Classic and Professional | Playfair Display (serif) | Source Sans Pro |
| Tech and Minimal         | Space Grotesk            | IBM Plex Sans   |
| Creative and Friendly    | Poppins                  | Open Sans       |

## Modular Type Scale (1.25 ratio, 16px base)

```css
--text-xs: 0.75rem; /* 12px */
--text-sm: 0.875rem; /* 14px */
--text-base: 1rem; /* 16px */
--text-lg: 1.125rem; /* 18px */
--text-xl: 1.25rem; /* 20px */
--text-2xl: 1.5rem; /* 24px */
--text-3xl: 1.875rem; /* 30px */
--text-4xl: 2.25rem; /* 36px */
```

## Line Height Rules

- Headings: `line-height: 1.2` (tight)
- Body: `line-height: 1.5-1.6` (comfortable)
- Small text: `line-height: 1.8` (readable)
- Uppercase: `letter-spacing: 0.05em` (wider)
- Headings: `letter-spacing: -0.02em` (tighter)

## Fluid Typography

```css
h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
}
```

Use `clamp()` for smooth scaling between breakpoints without media queries.
