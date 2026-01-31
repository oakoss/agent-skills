---
title: Lazy Loading and LCP Optimization
description: Native lazy loading, fetchpriority, Intersection Observer, and blur-up placeholder patterns
tags:
  [lazy-loading, fetchpriority, LCP, intersection-observer, placeholder, eager]
---

# Lazy Loading and LCP Optimization

## Native Lazy Loading

```html
<!-- Lazy load (most images) -->
<img src="/image.jpg" alt="Image" loading="lazy" />

<!-- Eager load (default, LCP images) -->
<img src="/hero.jpg" alt="Hero" loading="eager" />
```

## When to Use Eager vs Lazy

### Use loading="eager"

- **LCP images**: `loading="eager" fetchpriority="high"`
- **Above-the-fold images** (first 2-3 images visible on page load)
- **Critical logos and branding**

### Use loading="lazy"

- **Below-the-fold images**
- **Carousels and tabs** (hidden until interaction)
- **Long articles** (images scattered throughout)
- **Grid/masonry layouts** (most below fold)

## fetchpriority for LCP Optimization

```html
<img
  src="/hero-1200.jpg"
  srcset="/hero-800.jpg 800w, /hero-1200.jpg 1200w, /hero-1600.jpg 1600w"
  sizes="100vw"
  alt="Hero image"
  width="1600"
  height="900"
  loading="eager"
  fetchpriority="high"
/>
```

| Value  | Meaning                    | Use Case                    |
| ------ | -------------------------- | --------------------------- |
| `high` | Prioritize this resource   | LCP images, critical assets |
| `low`  | Deprioritize this resource | Below-fold, non-critical    |
| `auto` | Browser decides (default)  | Most images                 |

## Browser Support

| Browser      | Lazy Loading | fetchpriority |
| ------------ | ------------ | ------------- |
| Chrome 77+   | Yes          | Chrome 102+   |
| Firefox 121+ | Yes          | Firefox 132+  |
| Safari 16.4+ | Yes          | Safari 17.2+  |
| Edge 79+     | Yes          | Edge 102+     |

Polyfill not needed -- gracefully degrades to eager loading.

## Loading Distance Thresholds

| Browser | Distance                            | Notes             |
| ------- | ----------------------------------- | ----------------- |
| Chrome  | 1250px on fast, 2500px on slow (4G) | Adapts to network |
| Firefox | 200px                               | Fixed threshold   |
| Safari  | ~100-200px                          | Fixed threshold   |

Browsers handle loading distance intelligently based on connection speed.

## Intersection Observer (Custom Lazy Loading)

For advanced use cases or blur-up placeholders:

```javascript
const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img.lazy').forEach((img) => {
  imageObserver.observe(img);
});
```

```html
<img data-src="/image.jpg" src="/placeholder.jpg" alt="Image" class="lazy" />
```

When to use Intersection Observer:

- **Legacy browser support**: Safari < 15.4
- **Custom loading distance**: Different threshold than default
- **Loading animations**: Fade-in effects
- **Placeholder strategies**: Blur-up, LQIP

## Blur-Up Placeholder Pattern

```javascript
const imageObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const fullSrc = img.dataset.src;
        const tempImg = new Image();
        tempImg.onload = () => {
          img.src = fullSrc;
          img.classList.add('loaded');
        };
        tempImg.src = fullSrc;
        observer.unobserve(img);
      }
    });
  },
  { rootMargin: '50px' },
);
```

```css
.lazy {
  filter: blur(10px);
  transition: filter 0.3s;
}

.lazy.loaded {
  filter: blur(0);
}
```

## Error Prevention

### Don't Lazy Load LCP Images

```html
<!-- Bad: delays LCP -->
<img src="/hero.jpg" alt="Hero" loading="lazy" />

<!-- Good: prioritizes LCP -->
<img src="/hero.jpg" alt="Hero" loading="eager" fetchpriority="high" />
```

### Don't Eager Load All Images

```html
<!-- Bad: wastes bandwidth -->
<img src="/grid-item-20.jpg" alt="Item 20" loading="eager" />

<!-- Good: defer below-fold -->
<img src="/grid-item-20.jpg" alt="Item 20" loading="lazy" />
```

## Testing Lazy Loading

### Chrome DevTools

1. Open DevTools, Network tab
2. Filter by "Img"
3. Throttle to "Slow 3G"
4. Reload page, scroll slowly
5. Observe images loading as they approach viewport

### Lighthouse

- **Offscreen Images**: Checks if below-fold images use lazy loading
- **LCP**: Checks if LCP image is eagerly loaded

### Manual Testing

```javascript
document.querySelectorAll('img').forEach((img) => {
  console.log(img.src, img.loading);
});

new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.element);
}).observe({ entryTypes: ['largest-contentful-paint'] });
```
