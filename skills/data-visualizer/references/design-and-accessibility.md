---
title: Design and Accessibility
description: Accessible color schemes, colorblind-safe palettes, WCAG compliance, responsive chart design, and animation best practices
tags:
  [
    color,
    accessibility,
    WCAG,
    colorblind,
    responsive,
    animation,
    mobile,
    palette,
  ]
---

# Design and Accessibility

## Accessible Color Palette

```ts
export const chartColors = {
  primary: '#0066CC',
  success: '#007A3D',
  warning: '#C87000',
  danger: '#D32F2F',

  series: [
    '#0066CC', // Blue
    '#CC6600', // Orange
    '#7A00CC', // Purple
    '#00CC66', // Green
    '#CC0066', // Magenta
  ],
};
```

## Colorblind-Safe Palette

```ts
const colorblindSafe = [
  '#000000', // Black
  '#E69F00', // Orange
  '#56B4E9', // Sky Blue
  '#009E73', // Green
  '#F0E442', // Yellow
];
```

All colors should meet WCAG AA contrast requirements (4.5:1 minimum for text). Test with browser colorblind simulation tools.

## Responsive Charts

```tsx
'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';

export default function ResponsiveChart({ data }) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <ResponsiveContainer width="100%" height={isMobile ? 200 : 400}>
      <LineChart data={data}>
        <Line dataKey="value" stroke="#8884d8" strokeWidth={isMobile ? 1 : 2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## Animation Best Practices

Smooth transitions for standard charts:

```tsx
<Line
  type="monotone"
  dataKey="value"
  stroke="#8884d8"
  animationDuration={500}
  animationEasing="ease-in-out"
/>
```

Disable animation for real-time data:

```tsx
<Line dataKey="value" isAnimationActive={false} />
```

| Scenario          | Animation                  |
| ----------------- | -------------------------- |
| Initial load      | Enable (500ms ease-in-out) |
| Real-time updates | Disable                    |
| User interaction  | Enable (300ms)             |
| Print/export      | Disable                    |
