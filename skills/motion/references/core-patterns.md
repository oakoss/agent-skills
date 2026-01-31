---
title: Core Animation Patterns
description: Copy-paste ready Motion patterns for fade, exit, stagger, gestures, modal, accordion, tabs, layout, drag, page transitions, loading, SVG, counters, and custom components
tags: [motion, animation, patterns, gestures, layout, svg, drag, variants]
---

# Core Animation Patterns

Import for all examples: `import { motion, AnimatePresence } from "motion/react"`

## Fade In on Mount

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, ease: 'easeOut' }}
>
  Content
</motion.div>
```

## Exit Animations (AnimatePresence)

```tsx
<AnimatePresence>
  {isVisible && (
    <motion.div
      key="unique"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      Content
    </motion.div>
  )}
</AnimatePresence>
```

AnimatePresence must stay mounted. All children need unique `key` props.

## Staggered List with Variants

```tsx
const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map((text) => (
    <motion.li key={text} variants={item}>
      {text}
    </motion.li>
  ))}
</motion.ul>;
```

Variants flow down to children automatically. Parent orchestrates timing with `staggerChildren` and `delayChildren`.

## Gesture Animations

### Hover and Tap

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

### Focus

```tsx
<motion.input
  whileFocus={{ borderColor: '#3b82f6', boxShadow: '0 0 0 2px #3b82f6' }}
  transition={{ duration: 0.2 }}
/>
```

### Drag

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.1}
  whileDrag={{ scale: 1.1 }}
  className="cursor-grab active:cursor-grabbing"
/>
```

### Variants with Gestures

```tsx
const buttonVariants = {
  hover: { scale: 1.1 },
  tap: { scale: 0.95 },
};

<motion.button whileTap="tap" whileHover="hover" variants={buttonVariants}>
  Button
</motion.button>;
```

Variant names in gesture props propagate to children with matching variants.

## Modal Dialog

```tsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        key="backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/50 z-40"
      />
      <motion.div
        key="dialog"
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="fixed inset-0 flex items-center justify-center z-50 p-4"
      >
        <div className="bg-white rounded-lg p-6 max-w-md w-full">
          {children}
        </div>
      </motion.div>
    </>
  )}
</AnimatePresence>
```

## Accordion (Animate Height)

```tsx
<motion.div
  animate={{ height: isOpen ? 'auto' : 0 }}
  style={{ overflow: 'hidden' }}
  transition={{ duration: 0.3 }}
>
  <div className="p-4">Content</div>
</motion.div>
```

## Tabs with Shared Underline (layoutId)

```tsx
<div className="flex gap-4 border-b relative">
  {tabs.map((tab) => (
    <button
      key={tab.id}
      onClick={() => setActive(tab.id)}
      className="relative pb-2"
    >
      {tab.label}
      {active === tab.id && (
        <motion.div
          layoutId="underline"
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
        />
      )}
    </button>
  ))}
</div>
```

## Layout Animations (FLIP)

```tsx
<motion.div layout>{isExpanded ? <FullContent /> : <Summary />}</motion.div>
```

Options for `layout` prop: `true` (animate position and size), `"position"` (position only), `"size"` (size only).

### Shared Element Transitions

```tsx
<motion.div layoutId="card-1">Card content</motion.div>
```

When a new element with the same `layoutId` enters the DOM, it animates from the previous element's position and size.

### Layout Performance

```tsx
<motion.nav layout layoutDependency={isOpen} />
```

`layoutDependency` reduces measurements -- layout changes are only detected when this value changes instead of every render.

### Special Layout Props

- `layoutScroll`: Add to scrollable containers so layout animations account for scroll offset
- `layoutRoot`: Add to `position: fixed` containers so layout animations account for page scroll

## Page Transition

```tsx
'use client';
import { motion } from 'motion/react';

<motion.div
  key={pathname}
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -20 }}
  transition={{ duration: 0.3 }}
>
  {children}
</motion.div>;
```

## Loading Animations

### Spinner

```tsx
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
  className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"
/>
```

### Skeleton Loader

```tsx
<motion.div
  animate={{ opacity: [0.5, 1, 0.5] }}
  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
  className="bg-gray-200 rounded h-4 w-full"
/>
```

### Pulsing Dots

```tsx
{
  [0, 1, 2].map((i) => (
    <motion.div
      key={i}
      animate={{ scale: [0.8, 1.2], opacity: [0.5, 1] }}
      transition={{
        duration: 0.6,
        repeat: Infinity,
        repeatType: 'reverse',
        delay: i * 0.2,
      }}
      className="w-3 h-3 bg-blue-600 rounded-full"
    />
  ));
}
```

## SVG Path Drawing

```tsx
<motion.svg width="48" height="48" viewBox="0 0 48 48">
  <motion.circle
    cx="24"
    cy="24"
    r="22"
    fill="none"
    stroke="#10B981"
    strokeWidth="4"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 0.5 }}
  />
  <motion.path
    d="M12 24 L20 32 L36 16"
    fill="none"
    stroke="#10B981"
    strokeWidth="4"
    strokeLinecap="round"
    strokeLinejoin="round"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 0.3, delay: 0.3 }}
  />
</motion.svg>
```

SVG path animations work with `pathLength`, `pathSpacing`, and `pathOffset` (values between 0 and 1). Compatible with `circle`, `ellipse`, `line`, `path`, `polygon`, `polyline`, and `rect` elements.

## Animated Number Counter

```tsx
import { useSpring, useTransform } from 'motion/react';

const spring = useSpring(0, { stiffness: 100, damping: 30 });
const display = useTransform(spring, (v) => Math.round(v).toLocaleString());

useEffect(() => {
  spring.set(value);
}, [spring, value]);

<motion.span>{display}</motion.span>;
```

## Toast Notification

```tsx
<AnimatePresence>
  {isVisible && (
    <motion.div
      key="toast"
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className="fixed top-4 right-4 bg-blue-600 text-white p-4 rounded"
    >
      Message
    </motion.div>
  )}
</AnimatePresence>
```

## Notification Badge (Micro-interaction)

```tsx
{
  count > 0 && (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 500, damping: 15 }}
      className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
    >
      {count}
    </motion.div>
  );
}
```

## Carousel (Drag)

```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: -width, right: 0 }}
  className="flex"
>
  {images.map((img) => (
    <img key={img.id} src={img.url} alt={img.alt} />
  ))}
</motion.div>
```

## Custom Components with motion.create

```tsx
import { motion } from 'motion/react';

const MotionCard = motion.create(Card);

<MotionCard
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  whileHover={{ y: -4 }}
/>;
```

For custom SVG components, pass `{ type: "svg" }`:

```tsx
const MotionIcon = motion.create(MyIcon, { type: 'svg' });
```
