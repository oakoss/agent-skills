---
title: Logo Design
description: SVG logo React component with full, icon, and wordmark variants, color options, and usage patterns
tags: [logo, svg, react-component, variants, branding]
---

# Logo Design

## SVG Logo Component

```typescript
interface LogoProps {
  variant?: 'full' | 'icon' | 'wordmark'
  color?: 'primary' | 'white' | 'black'
  size?: number
}

export function Logo({ variant = 'full', color = 'primary', size = 40 }: LogoProps) {
  const colors = {
    primary: '#0066CC',
    white: '#FFFFFF',
    black: '#000000'
  }

  const fillColor = colors[color]

  if (variant === 'icon') {
    return (
      <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="18" fill={fillColor} />
        <path
          d="M15 20 L25 15 L25 25 Z"
          fill="white"
        />
      </svg>
    )
  }

  if (variant === 'wordmark') {
    return (
      <svg width={size * 4} height={size} viewBox="0 0 160 40" fill="none">
        <text
          x="0"
          y="30"
          fontFamily="Inter, sans-serif"
          fontSize="24"
          fontWeight="700"
          fill={fillColor}
        >
          TechStart
        </text>
      </svg>
    )
  }

  // Full logo (icon + wordmark)
  return (
    <svg width={size * 5} height={size} viewBox="0 0 200 40" fill="none">
      <circle cx="20" cy="20" r="18" fill={fillColor} />
      <path d="M15 20 L25 15 L25 25 Z" fill="white" />
      <text
        x="50"
        y="30"
        fontFamily="Inter, sans-serif"
        fontSize="24"
        fontWeight="700"
        fill={fillColor}
      >
        TechStart
      </text>
    </svg>
  )
}
```

## Usage

```typescript
<Logo variant="full" />
<Logo variant="icon" size={32} />
<Logo variant="wordmark" color="white" />
```
