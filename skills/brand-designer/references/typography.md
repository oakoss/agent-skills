---
title: Typography
description: Font selection, pairing principles, type scale ratios, responsive typography, variable fonts, vertical rhythm, web font loading, and React components
tags:
  [
    typography,
    fonts,
    type-scale,
    css-variables,
    react-components,
    variable-fonts,
    clamp,
  ]
---

# Typography

## Font Selection

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --font-sans:
    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;

  --text-xs: 0.75rem; /* 12px */
  --text-sm: 0.875rem; /* 14px */
  --text-base: 1rem; /* 16px */
  --text-lg: 1.125rem; /* 18px */
  --text-xl: 1.25rem; /* 20px */
  --text-2xl: 1.5rem; /* 24px */
  --text-3xl: 1.875rem; /* 30px */
  --text-4xl: 2.25rem; /* 36px */
  --text-5xl: 3rem; /* 48px */

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

## Font Pairing Principles

### Contrast Creates Hierarchy

Pair fonts with distinct characteristics. The display font draws attention; the body font stays readable at length.

| Pairing Strategy       | Display Font     | Body Font     | Mood                 |
| ---------------------- | ---------------- | ------------- | -------------------- |
| Serif + Sans-serif     | Playfair Display | Inter         | Elegant, editorial   |
| Geometric + Humanist   | Poppins          | Source Sans 3 | Modern, approachable |
| Slab + Grotesque       | Roboto Slab      | Roboto        | Technical, grounded  |
| Monospace + Sans-serif | JetBrains Mono   | Inter         | Developer, precise   |

### Pairing Checklist

- **Contrast**: Fonts should differ in classification (serif vs sans, geometric vs humanist)
- **Mood match**: Both fonts should support the same brand personality
- **X-height alignment**: Similar x-heights prevent jarring shifts when fonts appear near each other
- **Weight range**: Both fonts should offer enough weights for hierarchy (at minimum 400 and 700)

## Type Scale Ratios

A type scale creates consistent size relationships. Multiply the base size by the ratio to get the next step.

### Common Ratios

| Ratio          | Value | Character                       |
| -------------- | ----- | ------------------------------- |
| Minor Second   | 1.067 | Subtle, tight hierarchy         |
| Major Second   | 1.125 | Compact UI, dashboards          |
| Minor Third    | 1.2   | General purpose, balanced       |
| Major Third    | 1.25  | Clear hierarchy, most versatile |
| Perfect Fourth | 1.333 | Strong contrast, editorial      |
| Golden Ratio   | 1.618 | Dramatic, hero-heavy layouts    |

### Calculating a Scale

Formula: `size = base * ratio ^ step`

```ts
function generateTypeScale(
  base: number,
  ratio: number,
  steps: number,
): number[] {
  return Array.from(
    { length: steps },
    (_, i) => Math.round(base * Math.pow(ratio, i) * 100) / 100,
  );
}
```

Major Third scale from 16px base: 16, 20, 25, 31.25, 39.06, 48.83

## Responsive Typography with CSS clamp()

`clamp()` creates fluid typography that scales smoothly between breakpoints without media queries.

### Pattern

```text
clamp(minimum, preferred, maximum)
```

- **Minimum**: smallest readable size (mobile)
- **Preferred**: fluid value using viewport units
- **Maximum**: largest size (desktop cap)

### Implementation

```css
:root {
  --text-base: clamp(1rem, 0.5rem + 1vw, 1.125rem);
  --text-lg: clamp(1.125rem, 0.75rem + 1.25vw, 1.5rem);
  --text-xl: clamp(1.25rem, 0.5rem + 2vw, 2rem);
  --text-2xl: clamp(1.5rem, 0.25rem + 3vw, 2.5rem);
  --text-hero: clamp(2rem, 1rem + 4vw, 4rem);
}
```

### Tailwind Arbitrary Values

```tsx
<h1 className="text-[clamp(2rem,1rem+4vw,4rem)] font-bold leading-tight">
  Fluid Heading
</h1>
```

## Variable Fonts

Variable fonts contain multiple styles in a single file, reducing HTTP requests and enabling smooth weight transitions.

### Common Variation Axes

| Axis   | CSS Property          | Range (typical) | Purpose      |
| ------ | --------------------- | --------------- | ------------ |
| `wght` | `font-weight`         | 100-900         | Weight       |
| `wdth` | `font-stretch`        | 75%-125%        | Width        |
| `opsz` | `font-optical-sizing` | 8-144           | Optical size |
| `ital` | `font-style`          | 0-1             | Italic       |

### Loading a Variable Font

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
```

### Animated Weight Transition

```css
.nav-link {
  font-variation-settings: 'wght' 400;
  transition: font-variation-settings 200ms ease-out;
}

.nav-link:hover {
  font-variation-settings: 'wght' 600;
}
```

### Performance Benefits

- Single file replaces 4-8 static font files
- Smaller total download (one variable font < multiple static weights)
- Enables fine-grained weight control (e.g., 450 instead of snapping to 400 or 500)

## Vertical Rhythm

Consistent vertical spacing tied to the line-height creates visual harmony.

### Base Unit

Derive a spacing unit from the body line-height. With a 16px base and 1.5 line-height, the rhythm unit is 24px.

```css
:root {
  --rhythm: 1.5rem; /* 24px at 16px base */
}

h1 {
  margin-bottom: var(--rhythm);
}
h2 {
  margin-bottom: calc(var(--rhythm) * 0.75);
}
p {
  margin-bottom: var(--rhythm);
}
```

### Line-Height by Size

Larger text needs tighter line-height. Smaller text needs more breathing room.

| Text Size | Line-Height | Ratio   |
| --------- | ----------- | ------- |
| 48px+     | 1.1-1.2     | Tight   |
| 24-36px   | 1.2-1.3     | Snug    |
| 16-20px   | 1.5         | Normal  |
| 12-14px   | 1.6-1.75    | Relaxed |

### Spacing Relationships

```css
:root {
  --space-xs: calc(var(--rhythm) * 0.25); /* 6px */
  --space-sm: calc(var(--rhythm) * 0.5); /* 12px */
  --space-md: var(--rhythm); /* 24px */
  --space-lg: calc(var(--rhythm) * 2); /* 48px */
  --space-xl: calc(var(--rhythm) * 3); /* 72px */
}
```

## Web Font Loading Strategy

### font-display Values

| Value      | Behavior                                     | Best For                    |
| ---------- | -------------------------------------------- | --------------------------- |
| `swap`     | Shows fallback immediately, swaps when ready | Body text, critical content |
| `optional` | Shows fallback, may skip font if too slow    | Non-critical display text   |
| `fallback` | Brief blank period, then fallback            | Balance of speed and polish |

### Preload Critical Fonts

```html
<link
  rel="preload"
  href="/fonts/Inter-Variable.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

Preload only the primary body font. Let secondary fonts load normally to avoid contention.

### WOFF2 Format

Always serve WOFF2. It provides 30% better compression than WOFF and has universal browser support. No need to include WOFF fallbacks for modern applications.

### Self-Hosting vs CDN

| Approach     | Pros                                  | Cons                         |
| ------------ | ------------------------------------- | ---------------------------- |
| Self-hosted  | No third-party requests, full control | Must manage font files       |
| Google Fonts | Easy setup, global CDN                | Third-party dependency, GDPR |

Self-hosting is preferred for production brands. Eliminates third-party DNS lookups and avoids privacy concerns with Google Fonts tracking.

## React Typography Components

```typescript
export function Heading1({ children }: { children: React.ReactNode }) {
  return (
    <h1 className="text-4xl font-bold leading-tight text-gray-900">
      {children}
    </h1>
  )
}

export function Heading2({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-3xl font-semibold leading-tight text-gray-900">
      {children}
    </h2>
  )
}

export function BodyText({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-base font-normal leading-normal text-gray-700">
      {children}
    </p>
  )
}

export function Caption({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-sm font-normal leading-normal text-gray-500">
      {children}
    </p>
  )
}
```
