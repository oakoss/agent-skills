---
title: Frontend Performance
description: Code splitting, image optimization, bundle analysis, third-party script management, network waterfall optimization, mobile performance, and React performance patterns
tags:
  [
    frontend,
    code-splitting,
    lazy-loading,
    image-optimization,
    bundle-analysis,
    tree-shaking,
    resource-hints,
    mobile-performance,
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

## Bundle Analysis

```bash
# webpack-bundle-analyzer (webpack/Next.js)
npm install --save-dev webpack-bundle-analyzer
ANALYZE=true npm run build

# source-map-explorer (works with any bundler)
npm install --save-dev source-map-explorer
npx source-map-explorer dist/assets/*.js
```

```ts
// next.config.ts — enable bundle analyzer
import withBundleAnalyzer from '@next/bundle-analyzer';

export default withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})({
  // next config
});
```

```ts
// Verify tree-shaking: named imports only
import { debounce } from 'lodash-es'; // tree-shakeable
import debounce from 'lodash/debounce'; // direct import fallback

// Verify with sideEffects in package.json
// { "sideEffects": false } — marks all modules as side-effect-free
// { "sideEffects": ["*.css"] } — except CSS files
```

## Bundle Size Reduction

```bash
# Remove unused dependencies
npx depcheck

# Check import cost before adding a dependency
npx bundlephobia-cli react-datepicker
```

## Third-Party Script Management

```html
<!-- Defer non-critical scripts (download parallel, execute after parse) -->
<script src="https://analytics.example.com/tracker.js" defer></script>

<!-- Async for independent scripts (download parallel, execute immediately) -->
<script src="https://cdn.example.com/widget.js" async></script>
```

```ts
// Dynamic import for non-critical libraries
async function initAnalytics() {
  const { init } = await import('./analytics');
  init();
}

if (typeof requestIdleCallback !== 'undefined') {
  requestIdleCallback(() => initAnalytics());
} else {
  setTimeout(() => initAnalytics(), 2000);
}
```

```ts
// Track third-party script impact with PerformanceObserver
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.initiatorType === 'script') {
      console.log(`${entry.name}: ${entry.duration.toFixed(0)}ms`);
    }
  }
});
observer.observe({ type: 'resource', buffered: true });
```

## Network Waterfall Optimization

```html
<!-- dns-prefetch: resolve DNS for third-party origins early -->
<link rel="dns-prefetch" href="https://api.example.com" />

<!-- preconnect: DNS + TCP + TLS handshake (use for critical origins) -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://cdn.example.com" crossorigin />

<!-- preload: fetch critical resources early (fonts, hero images, key scripts) -->
<link
  rel="preload"
  href="/fonts/inter.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
<link rel="preload" href="/hero.webp" as="image" />

<!-- prefetch: low-priority fetch for likely next navigation -->
<link rel="prefetch" href="/dashboard" />
```

```html
<!-- fetchpriority: signal resource importance to the browser -->
<img src="/hero.webp" fetchpriority="high" alt="Hero" />
<img
  src="/below-fold.webp"
  fetchpriority="low"
  loading="lazy"
  alt="Secondary"
/>

<script src="/critical.js" fetchpriority="high"></script>
<script src="/analytics.js" fetchpriority="low" defer></script>
```

```html
<!-- Connection coalescing: serve multiple subdomains from one HTTP/2 connection -->
<!-- Use same certificate covering *.example.com -->
<!-- Combine: api.example.com, cdn.example.com, static.example.com -->
<!-- Browser reuses single TCP connection for all, reducing handshake overhead -->
```

## Mobile Performance

```ts
// Viewport-aware loading: only load resources when they enter the viewport
const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        img.src = img.dataset.src!;
        observer.unobserve(img);
      }
    }
  },
  { rootMargin: '200px' },
);

document
  .querySelectorAll('img[data-src]')
  .forEach((img) => observer.observe(img));
```

```ts
// Adaptive loading based on connection quality
const connection = (navigator as any).connection;

function getImageQuality(): 'low' | 'medium' | 'high' {
  if (!connection) return 'high';
  if (connection.saveData) return 'low';
  if (
    connection.effectiveType === '2g' ||
    connection.effectiveType === 'slow-2g'
  )
    return 'low';
  if (connection.effectiveType === '3g') return 'medium';
  return 'high';
}
```

```text
DevTools mobile testing profiles:
  Slow 3G:  Download 500 Kbps, Upload 500 Kbps, Latency 400ms
  Fast 3G:  Download 1.5 Mbps, Upload 750 Kbps, Latency 100ms
  4G:       Download 4 Mbps, Upload 3 Mbps, Latency 20ms

Steps: DevTools → Network tab → Throttling dropdown → select profile
Also enable: DevTools → Performance tab → CPU throttling (4x/6x slowdown)
```

```css
/* Touch interaction responsiveness: remove 300ms tap delay */
html {
  touch-action: manipulation;
}

/* Reduce layout shift from tap highlights */
* {
  -webkit-tap-highlight-color: transparent;
}
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
