---
title: Typography
description: Font selection with Inter and JetBrains Mono, CSS custom properties for type scale, and React typography components
tags: [typography, fonts, type-scale, css-variables, react-components]
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
