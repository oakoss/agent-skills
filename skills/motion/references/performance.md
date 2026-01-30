---
title: Performance Optimization
description: Bundle size reduction with LazyMotion and useAnimate, hardware acceleration, large list virtualization, AnimatePresence optimization, gesture tuning, and production checklist
tags: [performance, bundle-size, lazy-motion, virtualization, gpu, optimization]
---

# Performance Optimization

## Bundle Size Reduction

### LazyMotion (Recommended — 34 KB → 4.6 KB)

```tsx
import { LazyMotion, domAnimation, m } from 'motion/react';

<LazyMotion features={domAnimation}>
  <m.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
    Uses "m" instead of "motion"
  </m.div>
</LazyMotion>;
```

`domAnimation` includes transforms, opacity, gestures, layout, useScroll. For SVG path animations use `domMax` (~6 KB).

### useAnimate Mini (Smallest — 2.3 KB)

```tsx
import { useAnimate } from 'motion/react';

const [scope, animate] = useAnimate();

useEffect(() => {
  animate(scope.current, { opacity: 1, x: 0 });
}, []);

<div ref={scope} style={{ opacity: 0, transform: 'translateX(-20px)' }}>
  Content
</div>;
```

### useAnimate Hybrid (17 KB)

Includes stagger support for imperative animations:

```tsx
import { useAnimate, stagger } from 'motion/react';

const [scope, animate] = useAnimate();

const handleAnimate = () => {
  animate('li', { opacity: 1, x: 0 }, { delay: stagger(0.1) });
};

<ul ref={scope}>
  {items.map((item) => (
    <li key={item.id}>{item.text}</li>
  ))}
</ul>;
```

## Hardware Acceleration

Add `willChange` for animated transforms:

```tsx
<motion.div
  style={{ willChange: 'transform' }}
  animate={{ x: 100, rotate: 45 }}
/>
```

Animate `transform` and `opacity` (GPU-accelerated). Avoid `width`, `height`, `top`, `left` (triggers layout reflow). Use `layout` prop for size changes instead.

## Large Lists (50+ Items)

### Virtualization (Recommended)

```tsx
import { FixedSizeList } from 'react-window';

<FixedSizeList height={600} itemCount={1000} itemSize={50}>
  {({ index, style }) => (
    <motion.div style={style} layout>
      Item {index}
    </motion.div>
  )}
</FixedSizeList>;
```

### Stagger with delayChildren (10–30 Items)

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

### whileInView (Lazy Load)

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
>
  {item.content}
</motion.div>
```

### Adaptive Simplification

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
| No optimization       | 5–10 fps  | 1000+     |
| Stagger only          | 15–20 fps | 1000+     |
| whileInView           | 40–50 fps | 1000+     |
| Simplified animations | 50–60 fps | 1000+     |
| Virtualization        | 60 fps    | ~20       |

## AnimatePresence Optimization

Use `mode="wait"` for modals (sequential enter/exit, fewer DOM nodes):

```tsx
<AnimatePresence mode="wait">
  {isVisible && <motion.div key="content">Content</motion.div>}
</AnimatePresence>
```

Only wrap components that actually exit — avoid wrapping entire layouts.

## Gesture Performance

Disable momentum when not needed (precise positioning, drag-to-reorder):

```tsx
<motion.div drag dragMomentum={false} dragElastic={0.1} />
```

Default elasticity is 0.5. Use 0.1–0.2 for most cases, 0 for performance mode.

## Transition Types

| Type   | Use Case             | Performance  |
| ------ | -------------------- | ------------ |
| spring | Interactive gestures | More JS calc |
| tween  | Simple UI animations | Less JS calc |

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
- `willChange` added for animated transforms
- Only GPU-accelerated properties (transform, opacity)
- `layout` prop instead of animating width/height
- Large lists use virtualization (50+ items)
- AnimatePresence only wraps necessary components
- `layoutScroll` on scrollable containers
- `layoutRoot` on fixed elements
- Tested on low-end devices (throttle CPU in DevTools)
- Tested with `prefers-reduced-motion` enabled
- Frame rate verified (60fps minimum)
