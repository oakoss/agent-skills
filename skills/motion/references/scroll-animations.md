---
title: Scroll Animations
description: Scroll-triggered and scroll-linked animations with useScroll, useTransform, whileInView, parallax effects, scroll progress indicators, and offset configuration
tags: [scroll, useScroll, useTransform, parallax, whileInView, progress, offset]
---

# Scroll Animations

Motion supports two types of scroll animations: **scroll-triggered** (animation fires when element enters viewport) and **scroll-linked** (animation values tied directly to scroll position).

## Scroll-Triggered (whileInView)

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
>
  Fades in when 100px from entering viewport
</motion.div>
```

### Viewport Options

| Option   | Type    | Description                                                |
| -------- | ------- | ---------------------------------------------------------- |
| `once`   | boolean | Animate only the first time element enters (no re-trigger) |
| `margin` | string  | Expand or shrink the viewport detection area               |
| `amount` | number  | Fraction of element visible to trigger (0 to 1)            |
| `root`   | ref     | Scrollable ancestor to use as viewport                     |

### Staggered Scroll Reveal

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 },
  },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

<motion.div
  variants={container}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true }}
>
  {features.map((feature) => (
    <motion.div key={feature.id} variants={item}>
      {feature.title}
    </motion.div>
  ))}
</motion.div>;
```

## Scroll-Linked (useScroll)

`useScroll` returns four motion values:

- `scrollX` / `scrollY`: scroll offset in pixels
- `scrollXProgress` / `scrollYProgress`: scroll progress between 0 and 1

### Page Scroll Progress Indicator

```tsx
import { motion, useScroll } from 'motion/react';

function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-600 origin-left z-50"
    />
  );
}
```

### Tracking a Scrollable Container

Pass a ref to `container` to track a specific scrollable element instead of the page:

```tsx
import { useRef } from 'react';
import { useScroll, useTransform, motion } from 'motion/react';

function ScrollContainer() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ container: containerRef });
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0.3, 1, 0.3]);

  return (
    <div ref={containerRef} className="h-96 overflow-y-auto">
      <motion.div style={{ opacity }}>
        Content that fades based on container scroll
      </motion.div>
    </div>
  );
}
```

### Tracking an Element in the Viewport

Pass a ref to `target` to track an element's progress through the viewport:

```tsx
function ElementProgress() {
  const targetRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: targetRef,
    offset: ['start end', 'end start'],
  });
  const scale = useTransform(scrollYProgress, [0, 1], [0.8, 1.2]);

  return (
    <motion.div ref={targetRef} style={{ scale }}>
      Scales as it moves through viewport
    </motion.div>
  );
}
```

## Offset Configuration

Offsets define which intersection between `target` and `container` maps to progress 0 and 1. Each offset is a string with two keywords: first for the target edge, second for the container edge.

### Offset Keywords

| Keyword   | Meaning                    |
| --------- | -------------------------- |
| `start`   | Top/left edge of element   |
| `end`     | Bottom/right edge          |
| `center`  | Center of element          |
| Number    | 0 = start, 1 = end of axis |
| Pixels    | `"100px"` from start       |
| Percent   | `"50%"` same as 0.5        |
| `vh`/`vw` | Viewport units             |

### Common Offset Patterns

```tsx
// Element enters from bottom, leaves at top (full travel)
offset: ['start end', 'end start'];

// Element enters from bottom, stops when fully visible
offset: ['start end', 'end end'];

// Track only while element overlaps viewport center
offset: ['start center', 'end center'];

// Trigger when element top hits 200px from viewport top
offset: ['start 200px', 'end start'];
```

## Parallax Effects

### Hero Section Parallax

```tsx
import { useScroll, useTransform, motion } from 'motion/react';

function ParallaxHero() {
  const { scrollY } = useScroll();
  const bgY = useTransform(scrollY, [0, 500], [0, 150]);
  const textY = useTransform(scrollY, [0, 500], [0, -50]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div style={{ y: bgY }} className="absolute inset-0">
        <img src="/bg.jpg" alt="" className="w-full h-full object-cover" />
      </motion.div>
      <motion.div
        style={{ y: textY, opacity }}
        className="relative z-10 flex items-center justify-center h-full"
      >
        <h1>Parallax Effect</h1>
      </motion.div>
    </div>
  );
}
```

### Multi-Layer Parallax

```tsx
function MultiLayerParallax() {
  const { scrollY } = useScroll();
  const bgY = useTransform(scrollY, [0, 600], [0, 200]);
  const midY = useTransform(scrollY, [0, 600], [0, 100]);
  const fgY = useTransform(scrollY, [0, 600], [0, 30]);

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div style={{ y: bgY }} className="absolute inset-0">
        Background layer
      </motion.div>
      <motion.div style={{ y: midY }} className="absolute inset-0">
        Middle layer
      </motion.div>
      <motion.div style={{ y: fgY }} className="absolute inset-0">
        Foreground layer
      </motion.div>
    </div>
  );
}
```

## useTransform Patterns

### Value Mapping

Map one motion value range to another:

```tsx
const { scrollYProgress } = useScroll();
const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0]);
const scale = useTransform(scrollYProgress, [0, 1], [0.5, 1.5]);
const rotate = useTransform(scrollYProgress, [0, 1], [0, 360]);
```

### Transform Function

Use a function for custom transformations. Motion values read via `get()` are auto-subscribed:

```tsx
const { scrollY } = useScroll();
const backgroundColor = useTransform(scrollY, (latest) => {
  return latest > 100 ? '#1a1a2e' : '#ffffff';
});
```

### Chaining Transforms

```tsx
const { scrollYProgress } = useScroll();
const smoothProgress = useSpring(scrollYProgress, {
  stiffness: 100,
  damping: 30,
});
const y = useTransform(smoothProgress, [0, 1], [0, -200]);
```

`useSpring` wraps a motion value with spring physics, smoothing out jerky scroll input.

## Combining useScroll with useAnimate

```tsx
import { useAnimate, useInView } from 'motion/react';
import { useEffect } from 'react';

function ScrollTriggeredSequence() {
  const [scope, animate] = useAnimate();
  const isInView = useInView(scope);

  useEffect(() => {
    if (isInView) {
      animate(scope.current, { opacity: 1, y: 0 }, { duration: 0.5 });
    }
  }, [isInView]);

  return (
    <div ref={scope} style={{ opacity: 0, transform: 'translateY(20px)' }}>
      Triggers animation sequence when scrolled into view
    </div>
  );
}
```

## Performance Notes

- Motion uses the native ScrollTimeline API when available for hardware-accelerated scroll animations
- `useScroll` values update on every scroll frame -- avoid expensive computations in `useTransform` callbacks
- Use `viewport={{ once: true }}` on `whileInView` to avoid repeated animation triggers
- For scroll-linked animations affecting many elements, prefer CSS transforms (`x`, `y`, `scale`, `rotate`, `opacity`) over layout-triggering properties
