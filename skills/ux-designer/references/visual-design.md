---
title: Visual Design Fundamentals
description: Color theory, typography scales, spacing systems, visual hierarchy, dark mode strategies, and responsive design patterns
tags:
  [color-theory, typography, spacing, visual-hierarchy, dark-mode, responsive]
---

# Visual Design Fundamentals

Visual design creates consistent, accessible interfaces through systematic use of color, typography, spacing, and hierarchy.

## Color Theory

### Color Schemes

| Scheme        | Description                                      | Best For                   |
| ------------- | ------------------------------------------------ | -------------------------- |
| Complementary | Opposite colors (blue + orange)                  | High contrast, CTAs        |
| Analogous     | Adjacent colors (blue + green + teal)            | Harmonious, subtle         |
| Triadic       | Three evenly spaced colors (red + yellow + blue) | Balanced, diverse palettes |
| Monochromatic | Shades of one color                              | Minimal, safe designs      |

### 60-30-10 Rule

- **60%** -- Primary color (backgrounds, large areas)
- **30%** -- Secondary color (supporting elements)
- **10%** -- Accent color (CTAs, highlights)

### Shade Scale Generation (50-900)

```css
/* Primary color scale */
--color-primary-50: #eff6ff;
--color-primary-100: #dbeafe;
--color-primary-500: #3b82f6; /* Main brand color */
--color-primary-600: #2563eb;
--color-primary-900: #1e3a8a;

/* Neutral grays */
--color-gray-50: #f9fafb;
--color-gray-300: #d1d5db;
--color-gray-500: #6b7280;
--color-gray-700: #374151;
--color-gray-900: #111827;

/* Semantic colors */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
```

### Color Contrast Requirements

| Element               | Minimum Ratio |
| --------------------- | ------------- |
| Normal text           | 4.5:1         |
| Large text (18px+)    | 3:1           |
| UI components/borders | 3:1           |

```css
/* Good: 8:1 contrast */
.text-good {
  color: #111827;
  background: #ffffff;
}

/* Bad: 2.1:1 fails WCAG */
.text-bad {
  color: #d1d5db;
  background: #ffffff;
}
```

## Typography

### Modular Type Scale (Major Third 1.25)

```css
--text-xs: 0.64rem; /* 10.24px */
--text-sm: 0.8rem; /* 12.8px */
--text-base: 1rem; /* 16px - body text */
--text-lg: 1.25rem; /* 20px */
--text-xl: 1.563rem; /* 25px */
--text-2xl: 1.953rem; /* 31.25px */
--text-3xl: 2.441rem; /* 39px */
--text-4xl: 3.052rem; /* 48.83px */
--text-5xl: 3.815rem; /* 61px */

--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**Font pairing:** Maximum 2 fonts. Heading font distinctive, body font readable.

```css
/* Modern & clean */
--font-heading: 'Inter', sans-serif;
--font-body: 'Inter', sans-serif;

/* Classic & professional */
--font-heading: 'Playfair Display', serif;
--font-body: 'Source Sans Pro', sans-serif;
```

### Line Height and Vertical Rhythm

```css
/* Headings: tight */
h1,
h2,
h3 {
  line-height: 1.2;
}

/* Body: comfortable */
p {
  line-height: 1.6;
  max-width: 65ch; /* Optimal readability */
}

/* Letter spacing */
.heading {
  letter-spacing: -0.02em;
}
.uppercase {
  letter-spacing: 0.05em;
}

/* Lobotomized owl selector for vertical rhythm */
* + * {
  margin-top: var(--space-4);
}

h1 + p,
h2 + p {
  margin-top: var(--space-6);
}
```

### Heading Hierarchy

```css
h1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-8);
  color: var(--color-gray-900);
}

h2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-6);
  color: var(--color-gray-900);
}

h3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-4);
  color: var(--color-gray-800);
}

p {
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--color-gray-700);
}
```

## Spacing System

### 8pt Grid System

```css
--space-1: 0.25rem; /* 4px */
--space-2: 0.5rem; /* 8px */
--space-3: 0.75rem; /* 12px */
--space-4: 1rem; /* 16px */
--space-6: 1.5rem; /* 24px */
--space-8: 2rem; /* 32px */
--space-12: 3rem; /* 48px */
--space-16: 4rem; /* 64px */
--space-24: 6rem; /* 96px */
```

**Usage patterns:**

```css
.button {
  padding: var(--space-3) var(--space-6);
}
.card {
  padding: var(--space-6);
}
.section {
  padding: var(--space-16) 0;
  margin-bottom: var(--space-12);
}
.stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
```

### Spacing Scale Reference

| Use Case        | Value        | Size |
| --------------- | ------------ | ---- |
| Icon padding    | `--space-1`  | 4px  |
| Dense lists     | `--space-2`  | 8px  |
| Button padding  | `--space-3`  | 12px |
| Default margin  | `--space-4`  | 16px |
| Card padding    | `--space-6`  | 24px |
| Section spacing | `--space-12` | 48px |

## Visual Hierarchy Principles

### 1. Contrast

```css
h1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--color-gray-900);
}

.caption {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
}
```

### 2. Alignment

```css
.content {
  text-align: left;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

### 3. Repetition

```css
.button {
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  transition: all 200ms ease-in-out;
}
```

### 4. Proximity

```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2); /* Related items close */
  margin-bottom: var(--space-6); /* Groups separated */
}
```

## Dark Mode Strategy

### CSS Custom Properties

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --border-color: #4b5563;
  }
}

.card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
```

### System Preference Detection

```css
/* Respect system preference */
@media (prefers-color-scheme: dark) {
  body {
    background: var(--bg-primary);
    color: var(--text-primary);
  }
}

/* Manual toggle */
[data-theme='dark'] {
  --bg-primary: #111827;
  --text-primary: #f9fafb;
}
```

**Dark mode considerations:**

| Element          | Light Mode | Dark Mode |
| ---------------- | ---------- | --------- |
| Pure white       | `#ffffff`  | `#f9fafb` |
| Pure black       | `#000000`  | `#111827` |
| Shadow intensity | Strong     | Subtle    |
| Border contrast  | Medium     | Low       |

## Responsive Typography

### Fluid Typography with clamp()

```css
/* Syntax: clamp(min, preferred, max) */
h1 {
  font-size: clamp(2rem, 5vw, 4rem);
}

h2 {
  font-size: clamp(1.5rem, 4vw, 3rem);
}

p {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
}

.section {
  padding: clamp(2rem, 8vw, 6rem) 0;
}
```

### Breakpoint-Based Scaling

```css
h1 {
  font-size: 2rem;
}

@media (min-width: 768px) {
  h1 {
    font-size: 3rem;
  }
}

@media (min-width: 1024px) {
  h1 {
    font-size: 3.5rem;
  }
}
```

### Responsive Layout Patterns

**Mobile-first grid:**

```css
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

**Container with max-width:**

```css
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

@media (min-width: 768px) {
  .container {
    padding: 0 var(--space-6);
  }
}
```

## Visual Design Checklist

**Color System:**

- [ ] Primary, secondary, accent colors defined
- [ ] Complete shade scales (50-900)
- [ ] Neutral grays defined
- [ ] Semantic colors (success, warning, error, info)
- [ ] All text meets WCAG 4.5:1 contrast
- [ ] Dark mode palette tested

**Typography:**

- [ ] Maximum 2 font families
- [ ] Modular type scale (8-10 sizes)
- [ ] Font weights specified
- [ ] Line heights appropriate
- [ ] Body text max-width 65ch
- [ ] Responsive scaling defined

**Spacing:**

- [ ] 8pt grid implemented
- [ ] Consistent spacing scale
- [ ] Adequate whitespace
- [ ] Vertical rhythm with lobotomized owl

**Visual Hierarchy:**

- [ ] Size, weight, color establish importance
- [ ] Elements aligned consistently
- [ ] Visual patterns repeated
- [ ] Related elements grouped

**Responsive Design:**

- [ ] Mobile-first approach
- [ ] Breakpoints defined
- [ ] Touch targets 44x44px minimum
- [ ] Typography scales appropriately
- [ ] Layouts stack on smaller screens
