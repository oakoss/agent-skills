---
title: Frontend Performance
description: Code splitting and lazy loading, image optimization with Next.js and responsive images, bundle size reduction, and React performance patterns
tags:
  [
    frontend,
    code-splitting,
    lazy-loading,
    image-optimization,
    bundle-size,
    react-performance,
    virtualization,
  ]
---

# Frontend Performance

## Code Splitting and Lazy Loading

```typescript
import { lazy, Suspense } from 'react'

// Lazy load routes
const Dashboard = lazy(() => import('./Dashboard'))
const AdminPanel = lazy(() => import('./AdminPanel'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  )
}

// Next.js dynamic imports
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false // Skip SSR for this component
})
```

## Image Optimization

```jsx
// Next.js Image component (automatic optimization)
import Image from 'next/image'

<Image
  src="/photo.jpg"
  width={800}
  height={600}
  alt="Description"
  loading="lazy"        // Lazy load off-screen images
  placeholder="blur"    // Blur placeholder while loading
  quality={75}          // 75% quality (good balance)
/>

// WebP format with fallback
<picture>
  <source srcset="image.webp" type="image/webp" />
  <source srcset="image.jpg" type="image/jpeg" />
  <img src="image.jpg" alt="Description" loading="lazy" />
</picture>

// Responsive images
<img
  srcset="
    small.jpg 480w,
    medium.jpg 768w,
    large.jpg 1200w
  "
  sizes="(max-width: 480px) 480px, (max-width: 768px) 768px, 1200px"
  src="medium.jpg"
  alt="Description"
/>
```

## Bundle Size Optimization

```bash
# Analyze bundle
npm run build -- --analyze

# Reduce bundle size:
# 1. Remove unused dependencies
npm uninstall unused-package

# 2. Use tree-shaking compatible imports
# Bad:  import _ from 'lodash'
# Good: import debounce from 'lodash/debounce'

# 3. Dynamic imports for large libraries
# const moment = await import('moment')

# 4. Minification (automatic in production builds)
# Vite/Next.js handle this automatically
```

## React Performance

```typescript
// 1. Memoize expensive calculations
import { useMemo } from 'react'

function DataTable({ data }) {
  const sortedData = useMemo(
    () => data.sort((a, b) => a.name.localeCompare(b.name)),
    [data]
  )

  return <Table data={sortedData} />
}

// 2. Memoize components
import { memo } from 'react'

const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{/* expensive rendering */}</div>
})

// 3. useCallback for stable function references
import { useCallback } from 'react'

function Parent() {
  const handleClick = useCallback(() => {
    console.log('Clicked')
  }, [])

  return <ExpensiveChild onClick={handleClick} />
}

// 4. Virtualize long lists
import { FixedSizeList } from 'react-window'

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={50}
>
  {({ index, style }) => (
    <div style={style}>Row {index}</div>
  )}
</FixedSizeList>
```
