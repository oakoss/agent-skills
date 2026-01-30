---
title: srcset and sizes
description: Width descriptors, density descriptors, sizes attribute patterns, and browser selection logic
tags: [srcset, sizes, width-descriptors, density-descriptors, breakpoints, DPR]
---

# srcset and sizes Attributes

## Width Descriptors (w) - Recommended

Width descriptors tell the browser the actual width of each image file in pixels. The browser uses this with the `sizes` attribute and device pixel ratio to choose the optimal image.

```html
<img
  src="/image-800.jpg"
  srcset="
    /image-400.jpg   400w,
    /image-800.jpg   800w,
    /image-1200.jpg 1200w,
    /image-1600.jpg 1600w
  "
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Responsive image"
  width="800"
  height="600"
/>
```

**Browser Selection Logic:**

1. Calculate display width from `sizes` attribute
2. Multiply by device pixel ratio (DPR)
3. Choose smallest image >= calculated width
4. Consider network conditions and cache

**Example**: On a 375px wide phone (2x DPR):

- `sizes` evaluates to `375px` (100vw on mobile)
- Multiply by DPR: `375 * 2 = 750px`
- Browser chooses `image-800.jpg` (smallest >= 750px)

## Density Descriptors (x) - For Fixed Sizes Only

Only use for fixed-size images like logos:

```html
<img
  src="/logo.png"
  srcset="/logo.png 1x, /logo@2x.png 2x, /logo@3x.png 3x"
  alt="Company logo"
  width="150"
  height="50"
/>
```

## Common sizes Patterns

```html
<!-- Full width -->
sizes="100vw"

<!-- Content width (max 800px) -->
sizes="(max-width: 768px) 100vw, 800px"

<!-- Sidebar (fixed 300px) -->
sizes="300px"

<!-- 2-column grid -->
sizes="(max-width: 768px) 100vw, 50vw"

<!-- 3-column grid -->
sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"

<!-- Responsive with max-width -->
sizes="(max-width: 640px) 100vw, (max-width: 1024px) 90vw, 1200px"

<!-- Grid with gaps (12 cols, 3-wide, 2rem gap) -->
sizes="(max-width: 768px) 100vw, calc((100vw - 4rem) / 3)"
```

## Recommended Breakpoints

| Use Case           | Recommended Widths        | Reasoning                                   |
| ------------------ | ------------------------- | ------------------------------------------- |
| Full-width hero    | 800w, 1200w, 1600w, 2400w | Covers mobile, tablet, desktop, retina      |
| Content images     | 400w, 800w, 1200w         | Covers mobile, tablet, desktop at 1x/2x DPR |
| Grid cards (3-col) | 300w, 600w, 900w          | Covers ~33vw at 1x/2x/3x DPR                |
| Thumbnails         | 150w, 300w                | Small fixed-size images at 1x/2x            |

## DPR Considerations

| Device Type      | Typical DPR | Example                    |
| ---------------- | ----------- | -------------------------- |
| Standard desktop | 1x          | Older monitors             |
| Retina desktop   | 2x          | MacBook Pro, 4K monitors   |
| Standard mobile  | 2x          | iPhone 11, Pixel 4         |
| High-end mobile  | 3x          | iPhone 14 Pro, Samsung S23 |

**Formula**: `Display Width x Max DPR = Image Width`

## Common Mistakes

### Missing sizes Attribute

```html
<!-- Bad: Browser defaults to 100vw, wastes bandwidth -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  alt="Image"
/>

<!-- Good: specifies display size -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
  width="800"
  height="600"
/>
```

### Using Density Descriptors for Responsive Images

```html
<!-- Bad: only considers DPR, not viewport -->
<img src="/image.jpg" srcset="/image.jpg 1x, /image@2x.jpg 2x" alt="Image" />

<!-- Good: considers viewport + DPR -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
  width="800"
  height="600"
/>
```

## Tips for Writing sizes

1. **Mobile-first**: Start with mobile sizes, then add larger breakpoints
2. **Match layout breakpoints**: Use same breakpoints as your CSS
3. **Consider container width**: Account for padding, gaps, max-width
4. **Test with DevTools**: Chrome DevTools shows which image was selected
5. **Don't overthink**: Browser is smart, close approximations work fine

## Testing Tools

- **Chrome DevTools**: Right-click image, Inspect, check `currentSrc` in Elements panel
- **Firefox DevTools**: Computed tab shows `currentSrc`, Responsive Design Mode for viewports
- **Online**: [Responsive Image Breakpoints Generator](https://responsivebreakpoints.com/), [RespImageLint](https://ausi.github.io/respimagelint/)
