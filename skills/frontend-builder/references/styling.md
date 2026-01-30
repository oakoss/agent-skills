---
title: Styling
description: Tailwind CSS with variant-based components and cn utility, and CSS Modules as an alternative approach
tags: [tailwind, css-modules, styling, variants, shadcn]
---

# Styling

## Tailwind CSS (Recommended)

```typescript
function Button({ variant = 'primary', children, ...props }) {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded font-medium transition-colors',
        {
          'bg-blue-500 text-white hover:bg-blue-600': variant === 'primary',
          'bg-gray-200 text-gray-900 hover:bg-gray-300': variant === 'secondary',
          'bg-red-500 text-white hover:bg-red-600': variant === 'danger'
        }
      )}
      {...props}
    >
      {children}
    </button>
  )
}
```

## CSS Modules (Alternative)

```css
/* Button.module.css */
.button {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

.primary {
  background-color: blue;
  color: white;
}
```

```typescript
import styles from './Button.module.css'

export function Button({ variant = 'primary', children }) {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  )
}
```
