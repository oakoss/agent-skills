---
title: Picture Element and Art Direction
description: Art direction with picture element, media queries, format selection, and common patterns
tags: [picture, art-direction, media-queries, source, crops, orientation]
---

# Picture Element and Art Direction

## What is Art Direction?

Art direction means serving different crops or compositions of an image based on viewport size, not just scaling the same image.

| Use Case         | Mobile                   | Desktop                  | Why                      |
| ---------------- | ------------------------ | ------------------------ | ------------------------ |
| Portrait Product | Vertical crop            | Horizontal crop          | Show product differently |
| Hero with Text   | Tight crop, text outside | Wide shot, text overlaid | Layout changes           |
| Group Photo      | Face close-up            | Full group               | Show detail vs context   |

## Basic Syntax

```html
<picture>
  <source media="(max-width: 640px)" srcset="/image-portrait.jpg" />
  <source media="(min-width: 641px)" srcset="/image-landscape.jpg" />
  <img src="/image-landscape.jpg" alt="Image" />
</picture>
```

## Art Direction with Responsive Sizes

Combine `media` queries with `srcset` for both art direction AND responsive sizing:

```html
<picture>
  <source
    media="(max-width: 640px)"
    srcset="/product-portrait-400.jpg 400w, /product-portrait-800.jpg 800w"
    sizes="100vw"
  />
  <source
    media="(min-width: 641px) and (max-width: 1024px)"
    srcset="/product-square-600.jpg 600w, /product-square-1200.jpg 1200w"
    sizes="90vw"
  />
  <source
    media="(min-width: 1025px)"
    srcset="
      /product-landscape-800.jpg   800w,
      /product-landscape-1200.jpg 1200w,
      /product-landscape-1600.jpg 1600w
    "
    sizes="1200px"
  />
  <img
    src="/product-landscape-1200.jpg"
    alt="Product image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

## Art Direction + Modern Formats

Combine art direction with format selection using nested sources:

```html
<picture>
  <!-- Mobile Portrait: AVIF -->
  <source
    media="(max-width: 640px)"
    srcset="/hero-portrait-400.avif 400w, /hero-portrait-800.avif 800w"
    sizes="100vw"
    type="image/avif"
  />
  <!-- Mobile Portrait: WebP -->
  <source
    media="(max-width: 640px)"
    srcset="/hero-portrait-400.webp 400w, /hero-portrait-800.webp 800w"
    sizes="100vw"
    type="image/webp"
  />
  <!-- Mobile Portrait: JPEG -->
  <source
    media="(max-width: 640px)"
    srcset="/hero-portrait-400.jpg 400w, /hero-portrait-800.jpg 800w"
    sizes="100vw"
  />
  <!-- Desktop Landscape: AVIF -->
  <source
    media="(min-width: 641px)"
    srcset="
      /hero-landscape-800.avif   800w,
      /hero-landscape-1200.avif 1200w,
      /hero-landscape-1600.avif 1600w
    "
    sizes="100vw"
    type="image/avif"
  />
  <!-- Desktop Landscape: WebP -->
  <source
    media="(min-width: 641px)"
    srcset="
      /hero-landscape-800.webp   800w,
      /hero-landscape-1200.webp 1200w,
      /hero-landscape-1600.webp 1600w
    "
    sizes="100vw"
    type="image/webp"
  />
  <!-- Desktop Landscape: JPEG (fallback) -->
  <img
    src="/hero-landscape-1200.jpg"
    srcset="
      /hero-landscape-800.jpg   800w,
      /hero-landscape-1200.jpg 1200w,
      /hero-landscape-1600.jpg 1600w
    "
    sizes="100vw"
    alt="Hero image"
    width="1600"
    height="900"
    loading="eager"
    fetchpriority="high"
  />
</picture>
```

**Browser Selection Logic:** media query first, then type (AVIF, WebP, JPEG), then size from srcset + sizes.

## Orientation-Based Art Direction

```html
<picture>
  <source
    media="(orientation: portrait)"
    srcset="/image-portrait-600.jpg 600w, /image-portrait-1200.jpg 1200w"
    sizes="100vw"
  />
  <img
    src="/image-landscape-1200.jpg"
    srcset="
      /image-landscape-800.jpg   800w,
      /image-landscape-1200.jpg 1200w,
      /image-landscape-1600.jpg 1600w
    "
    sizes="100vw"
    alt="Image"
    width="1600"
    height="900"
  />
</picture>
```

## When NOT to Use Art Direction

- Same crop works at all sizes (just use `srcset`)
- Only format conversion needed (use `type` only)
- Minor composition adjustments (CSS `object-position` may suffice)

## Common Mistakes

### Missing Fallback img

```html
<!-- Bad: doesn't render without picture support -->
<picture>
  <source media="(max-width: 640px)" srcset="/image-mobile.jpg" />
</picture>

<!-- Good: always include img fallback -->
<picture>
  <source media="(max-width: 640px)" srcset="/image-mobile.jpg" />
  <img src="/image-desktop.jpg" alt="Image" width="1200" height="675" />
</picture>
```

### Wrong Source Order

Correct order: `media` THEN `type` THEN size selection. Place most specific format (AVIF) before less specific (WebP) before fallback (JPEG).

### Missing sizes in srcset Sources

```html
<!-- Bad: Browser defaults to 100vw for all sizes -->
<source
  media="(max-width: 640px)"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
/>

<!-- Good: includes sizes -->
<source
  media="(max-width: 640px)"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  sizes="100vw"
/>
```
