---
title: Performance Optimization
description: Bundle size reduction with LazyMotion and useAnimate, hardware acceleration, large list virtualization, AnimatePresence optimization, gesture tuning, and production checklist
tags: [performance, bundle-size, lazy-motion, virtualization, gpu, optimization]
---

# Performance Optimization

## Bundle Size Reduction

### LazyMotion (Recommended -- 34 KB to 4.6 KB)

```tsx
import { LazyMotion, domAnimation, m } from 'motion/react';

<LazyMotion features={domAnimation}>
  <m.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
    Uses "m" instead of "motion"
  </m.div>
</LazyMotion>;
```

`domAnimation` includes transforms, opacity, gestures, layout, and useScroll. For SVG path animations use `domMax` (~6 KB).

### Async Feature Loading

Load features asynchronously for even smaller initial bundle:

```tsx
const loadFeatures = () =>
  import('motion/dom-animation').then((res) => res.default);

<LazyMotion features={loadFeatures} strict>
  <m.div animate={{ opacity: 1 }}>Loaded async</m.div>
</LazyMotion>;
```

The `strict` prop throws an error if `motion` is used instead of `m` inside LazyMotion.

### useAnimate Mini (Smallest -- 2.3 KB)

```tsx
import { useAnimate } from 'motion/react';

function Component() {
  const [scope, animate] = useAnimate();

  useEffect(() => {
    animate(scope.current, { opacity: 1, x: 0 });
  }, []);

  return (
    <div ref={scope} style={{ opacity: 0, transform: 'translateX(-20px)' }}>
      Content
    </div>
  );
}
```

### useAnimate Hybrid (17 KB)

Includes stagger support for imperative animations:

```tsx
import { useAnimate, stagger } from 'motion/react';

function StaggeredList() {
  const [scope, animate] = useAnimate();

  const handleAnimate = () => {
    animate('li', { opacity: 1, x: 0 }, { delay: stagger(0.1) });
  };

  return (
    <ul ref={scope}>
      {items.map((item) => (
        <li key={item.id} style={{ opacity: 0 }}>
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

### Bundle Size Summary

| Approach                  | Size   | Includes                              |
| ------------------------- | ------ | ------------------------------------- |
| useAnimate mini           | 2.3 KB | Imperative animations only            |
| LazyMotion + domAnimation | 4.6 KB | Transforms, opacity, gestures, layout |
| LazyMotion + domMax       | ~6 KB  | Above + SVG path animations           |
| useAnimate hybrid         | 17 KB  | Imperative + stagger + selectors      |
| Full `motion` component   | 34 KB  | All features                          |

## Hardware Acceleration

### GPU-Accelerated Properties

| Animate (GPU-accelerated)   | Avoid (triggers layout reflow)   |
| --------------------------- | -------------------------------- |
| `x`, `y`, `scale`, `rotate` | `width`, `height`                |
| `opacity`                   | `top`, `left`, `right`, `bottom` |
| `filter` (blur, brightness) | `padding`, `margin`              |
| `clipPath`                  | `fontSize`                       |

### willChange Hint

Add `willChange` for frequently animated transforms:

```tsx
<motion.div
  style={{ willChange: 'transform' }}
  animate={{ x: 100, rotate: 45 }}
/>
```

Use sparingly -- adding `willChange` to too many elements wastes GPU memory.

### Use layout Prop for Size Changes

Instead of animating `width`/`height` directly, use the `layout` prop:

```tsx
<motion.div layout>
  {isExpanded ? <LargeContent /> : <SmallContent />}
</motion.div>
```

The `layout` prop uses FLIP (First, Last, Invert, Play) to animate via transforms instead of layout properties.

## Large Lists (50+ Items)

### Virtualization (Best for 100+ Items)

```tsx
import { FixedSizeList } from 'react-window';
import { motion } from 'motion/react';

<FixedSizeList height={600} itemCount={1000} itemSize={50}>
  {({ index, style }) => (
    <motion.div style={style} layout>
      Item {index}
    </motion.div>
  )}
</FixedSizeList>;
```

Only renders visible items, reducing DOM nodes from 1000+ to ~20.

### Stagger with delayChildren (10-30 Items)

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};
```

### whileInView Lazy Animation

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
>
  {item.content}
</motion.div>
```

Only animates when scrolled into view. Use `once: true` to avoid repeated triggers.

### Adaptive Simplification (50+ Items)

```tsx
const useReducedAnimations = items.length > 50;

<motion.div
  initial={{ opacity: useReducedAnimations ? 1 : 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: useReducedAnimations ? 0 : 0.3 }}
/>;
```

### Performance Comparison (1000 Items)

| Approach              | FPS       | DOM Nodes |
| --------------------- | --------- | --------- |
| No optimization       | 5-10 fps  | 1000+     |
| Stagger only          | 15-20 fps | 1000+     |
| whileInView           | 40-50 fps | 1000+     |
| Simplified animations | 50-60 fps | 1000+     |
| Virtualization        | 60 fps    | ~20       |

## AnimatePresence Optimization

Use `mode="wait"` for sequential enter/exit (fewer simultaneous DOM nodes):

```tsx
<AnimatePresence mode="wait">
  {isVisible && <motion.div key="content">Content</motion.div>}
</AnimatePresence>
```

Only wrap components that actually exit -- avoid wrapping entire layouts in AnimatePresence.

## Gesture Performance

Disable momentum when not needed (precise positioning, drag-to-reorder):

```tsx
<motion.div drag dragMomentum={false} dragElastic={0.1} />
```

Default elasticity is 0.5. Use 0.1-0.2 for most cases, 0 for maximum performance.

## Transition Types

| Type   | Use Case             | Performance  |
| ------ | -------------------- | ------------ |
| spring | Interactive gestures | More JS calc |
| tween  | Simple UI animations | Less JS calc |

Spring animations run more JavaScript per frame but feel more natural. Use tween for simple opacity/position changes where spring physics are not needed.

## Duration Guidelines

| Range     | Effect                 |
| --------- | ---------------------- |
| < 100ms   | Too fast (abrupt)      |
| 200-400ms | Sweet spot for most UI |
| > 500ms   | Too slow (sluggish)    |

## Performance Budget

| Metric                         | Target | Maximum |
| ------------------------------ | ------ | ------- |
| Bundle size (Motion)           | < 5 KB | 10 KB   |
| Frame rate                     | 60 FPS | 40 FPS  |
| Animated elements simultaneous | < 20   | < 50    |
| AnimatePresence wrappers       | < 5    | < 10    |
| Layout animations simultaneous | < 10   | < 20    |

## Production Checklist

- Bundle optimized (LazyMotion or useAnimate)
- `willChange` added for frequently animated transforms
- Only GPU-accelerated properties (transform, opacity)
- `layout` prop instead of animating width/height
- Large lists use virtualization (50+ items)
- AnimatePresence only wraps necessary components
- `layoutScroll` on scrollable containers with layout animations
- `layoutRoot` on fixed-position elements with layout animations
- `layoutDependency` set where layout changes are state-driven
- Tested on low-end devices (throttle CPU in DevTools)
- Tested with `prefers-reduced-motion` enabled
- Frame rate verified (60fps target)
