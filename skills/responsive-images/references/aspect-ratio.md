---
title: Aspect Ratio and CLS Prevention
description: Preventing layout shift with width/height, CSS aspect-ratio, object-fit, and object-position
tags:
  [aspect-ratio, CLS, layout-shift, object-fit, object-position, width, height]
---

# Aspect Ratio and CLS Prevention

## The Problem: Cumulative Layout Shift (CLS)

When images load without reserved space, content below shifts down, causing poor user experience and hurting Core Web Vitals scores.

## Solution 1: Explicit Width and Height (Recommended)

Always include `width` and `height` attributes. Browsers use these to calculate aspect ratio and reserve space.

```html
<img src="/image.jpg" alt="Image" width="800" height="600" loading="lazy" />
```

Width/height don't constrain the image size -- they only set the aspect ratio. CSS can still make the image responsive:

```css
img {
  max-width: 100%;
  height: auto;
}
```

Or in Tailwind: `class="w-full h-auto"`

## Solution 2: CSS aspect-ratio Property

Use when dimensions aren't known or for container-based layouts:

```html
<!-- 16:9 aspect ratio -->
<div class="aspect-video">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>

<!-- 4:3 aspect ratio -->
<div class="aspect-4/3">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>

<!-- Square (1:1) -->
<div class="aspect-square">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>
```

Custom ratios in CSS:

```css
.aspect-ultrawide {
  aspect-ratio: 21 / 9;
}

.aspect-photo {
  aspect-ratio: 3 / 2;
}

.aspect-portrait {
  aspect-ratio: 9 / 16;
}
```

## Common Aspect Ratios

| Ratio | CSS             | Use Case                          |
| ----- | --------------- | --------------------------------- |
| 16:9  | `aspect-[16/9]` | Video thumbnails, hero images     |
| 4:3   | `aspect-[4/3]`  | Standard photos, older displays   |
| 3:2   | `aspect-[3/2]`  | DSLR photos, 35mm film            |
| 1:1   | `aspect-square` | Profile pictures, Instagram-style |
| 21:9  | `aspect-[21/9]` | Ultrawide banners, cinematic      |
| 9:16  | `aspect-[9/16]` | Vertical video (TikTok, Stories)  |

## object-fit Property

| Value        | Behavior                         | Use Case                 |
| ------------ | -------------------------------- | ------------------------ |
| `cover`      | Fill container, crop edges       | Card images, backgrounds |
| `contain`    | Fit inside, preserve all content | Logos, product photos    |
| `fill`       | Stretch to fill                  | Avoid unless necessary   |
| `scale-down` | Smaller of `contain` or original | Mixed content sizes      |

### When to Use Each

| Scenario         | object-fit | Reasoning                          |
| ---------------- | ---------- | ---------------------------------- |
| Card images      | `cover`    | Fill space, crop unimportant edges |
| Product photos   | `contain`  | Show entire product                |
| Profile pictures | `cover`    | Fill circle/square                 |
| Logos            | `contain`  | Show entire logo                   |
| Hero backgrounds | `cover`    | Fill viewport, no gaps             |

## object-position Property

Control which part of the image is visible when cropped with `object-cover`:

```html
<img src="/portrait.jpg" alt="Portrait" class="object-cover object-top" />
<img src="/scene.jpg" alt="Scene" class="object-cover object-center" />
<img src="/product.jpg" alt="Product" class="object-cover object-bottom" />
```

| Scenario       | Position          | Why                            |
| -------------- | ----------------- | ------------------------------ |
| Portrait faces | `object-top`      | Keep face visible when cropped |
| Landscape      | `object-center`   | Balance composition            |
| Logo in corner | `object-left-top` | Keep branding visible          |

## Complete Pattern Examples

### Card with Fixed Aspect Ratio

```html
<div class="overflow-hidden rounded-lg">
  <div class="aspect-video">
    <img
      src="/card-image-800.jpg"
      srcset="
        /card-image-400.jpg   400w,
        /card-image-800.jpg   800w,
        /card-image-1200.jpg 1200w
      "
      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
      alt="Card image"
      width="800"
      height="450"
      loading="lazy"
      class="w-full h-full object-cover"
    />
  </div>
  <div class="p-4">
    <h3>Card Title</h3>
    <p>Card content...</p>
  </div>
</div>
```

### Profile Picture (Circle)

```html
<div class="w-32 h-32 rounded-full overflow-hidden">
  <img
    src="/profile.jpg"
    alt="Profile picture"
    width="128"
    height="128"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

### Hero with Text Overlay

```html
<div class="aspect-21/9 relative">
  <img
    src="/hero-1600.jpg"
    srcset="
      /hero-800.jpg   800w,
      /hero-1200.jpg 1200w,
      /hero-1600.jpg 1600w,
      /hero-2400.jpg 2400w
    "
    sizes="100vw"
    alt="Hero image"
    width="2400"
    height="1028"
    loading="eager"
    fetchpriority="high"
    class="w-full h-full object-cover"
  />
  <div class="absolute inset-0 flex items-center justify-center">
    <h1 class="text-white text-5xl font-bold">Hero Title</h1>
  </div>
</div>
```

## Common Mistakes

```html
<!-- Bad: Missing width/height causes layout shift -->
<img src="/image.jpg" alt="Image" loading="lazy" />

<!-- Bad: Width without height, browser can't calculate ratio -->
<img src="/image.jpg" alt="Image" width="800" loading="lazy" />

<!-- Bad: object-fill distorts image -->
<img src="/portrait.jpg" alt="Portrait" class="w-full h-64 object-fill" />

<!-- Good: explicit dimensions -->
<img
  src="/image.jpg"
  alt="Image"
  width="800"
  height="600"
  loading="lazy"
  class="w-full h-auto"
/>

<!-- Good: aspect-ratio with object-fit -->
<div class="aspect-video">
  <img
    src="/image.jpg"
    alt="Image"
    width="1600"
    height="900"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

## Testing for Layout Shift

```javascript
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Layout shift:', entry.value, entry.sources);
  }
}).observe({ entryTypes: ['layout-shift'] });
```

Lighthouse audit checks CLS score and verifies image elements have explicit width and height.
