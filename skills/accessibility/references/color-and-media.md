---
title: Color and Media
description: Color contrast requirements, avoiding color-only indicators, text alternatives for images, and video captions with track elements
tags: [color, contrast, alt-text, images, video, captions, media]
---

# Color and Media

## Color and Contrast

```css
/* WRONG: insufficient contrast */
:root {
  --text: #999999; /* 2.8:1 on white -- fails */
}

/* CORRECT: sufficient contrast */
:root {
  --text: #595959; /* 4.6:1 on white -- passes */
}
```

Never use color alone to convey state. Combine color with icons and text labels:

```tsx
// WRONG: color only
<span style={{ color: 'red' }}>Error</span>

// CORRECT: color + icon + text
<span style={{ color: 'red' }}>
  <ErrorIcon aria-hidden="true" /> Error
</span>
```

## Text Alternatives

```html
<!-- Informative images: describe content -->
<img src="chart.png" alt="Sales increased 50% in Q4" />

<!-- Decorative images: empty alt -->
<img src="border.png" alt="" />

<!-- Icon buttons: aria-label -->
<button aria-label="Close dialog"><svg>...</svg></button>
```

For complex images, use `<figure>` with `<figcaption>` containing a `<details>` element for long descriptions.

## Video and Audio

```html
<video controls>
  <source src="video.mp4" type="video/mp4" />
  <track
    kind="captions"
    src="captions.vtt"
    srclang="en"
    label="English"
    default
  />
</video>
```

Require user interaction to start media.

## Reduced Motion

Respect the user's system motion preferences. Animations that are purely decorative should be disabled. Essential motion (progress indicators, transitions that convey meaning) can be simplified rather than removed entirely.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Dragging Alternatives (WCAG 2.5.7)

Any interaction that requires dragging must also work with a single pointer without dragging. Examples: drag-and-drop reordering needs up/down buttons, custom sliders need direct value input, carousels need prev/next buttons.

```html
<!-- Sortable list with both drag and button alternatives -->
<li draggable="true">
  <span>Item 1</span>
  <button aria-label="Move Item 1 up">Up</button>
  <button aria-label="Move Item 1 down">Down</button>
</li>
```
