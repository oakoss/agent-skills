---
title: Core Animation Patterns
description: Copy-paste ready Motion patterns for fade, exit, stagger, hover, modal, scroll, parallax, layout, drag, page transitions, loading, SVG, counters, and micro-interactions
tags: [motion, animation, patterns, gestures, scroll, layout, svg, drag]
---

# Core Animation Patterns

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

**Critical**: AnimatePresence must stay mounted. All children need unique `key` props.

## Staggered List

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
  {items.map((text, i) => (
    <motion.li key={i} variants={item}>
      {text}
    </motion.li>
  ))}
</motion.ul>;
```

## Button Hover / Tap

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

## Modal Dialog

```tsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/50 z-40"
      />
      <motion.div
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

## Accordion

```tsx
<motion.div
  animate={{ height: isOpen ? 'auto' : 0 }}
  style={{ overflow: 'hidden' }}
  transition={{ duration: 0.3 }}
>
  <div className="p-4">Content</div>
</motion.div>
```

## Tabs with Shared Underline

```tsx
<div className="flex gap-4 border-b">
  {tabs.map((tab) => (
    <button key={tab.id} onClick={() => setActive(tab.id)}>
      {tab.label}
      {active === tab.id && (
        <motion.div
          layoutId="underline"
          className="absolute bottom-0 h-0.5 bg-blue-600"
        />
      )}
    </button>
  ))}
</div>
```

## Scroll-Triggered Reveal (whileInView)

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
>
  Fades in when 100px from entering viewport
</motion.div>
```

## Scroll-Linked / Parallax

```tsx
import { useScroll, useTransform } from 'motion/react';

const { scrollYProgress } = useScroll();
const y = useTransform(scrollYProgress, [0, 1], [0, -300]);

<motion.div style={{ y }}>Moves up as user scrolls</motion.div>;
```

**Parallax hero pattern**:

```tsx
const { scrollY } = useScroll();
const y = useTransform(scrollY, [0, 500], [0, 150]);

<div className="relative h-screen overflow-hidden">
  <motion.div style={{ y }} className="absolute inset-0">
    <img src="/bg.jpg" alt="" className="w-full h-full object-cover" />
  </motion.div>
  <div className="relative z-10 flex items-center justify-center h-full">
    <h1>Parallax Effect</h1>
  </div>
</div>;
```

## Scroll Progress Indicator

```tsx
const { scrollYProgress } = useScroll();

<motion.div
  style={{ scaleX: scrollYProgress }}
  className="fixed top-0 left-0 right-0 h-1 bg-blue-600 origin-left z-50"
/>;
```

## Layout Animations (FLIP)

```tsx
<motion.div layout>{isExpanded ? <FullContent /> : <Summary />}</motion.div>
```

**Shared element transitions** between views:

```tsx
<motion.div layoutId="card-1">Card content</motion.div>
```

Special props: `layoutScroll` (scrollable containers), `layoutRoot` (fixed-position elements).

## Drag

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.1}
  className="cursor-grab active:cursor-grabbing"
/>
```

Drag carousel: `drag="x"` with `dragConstraints`.

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

**Spinner**:

```tsx
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
  className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"
/>
```

**Skeleton loader**:

```tsx
<motion.div
  animate={{ opacity: [0.5, 1, 0.5] }}
  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
  className="bg-gray-200 rounded h-4 w-full"
/>
```

**Pulsing dots**:

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
<motion.svg
  width="48"
  height="48"
  viewBox="0 0 48 48"
  initial={{ scale: 0 }}
  animate={{ scale: 1 }}
  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
>
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

## Card Expand

```tsx
<motion.div layout onClick={toggle} className={isExpanded ? 'w-full' : 'w-64'}>
  {isExpanded && <p>Extra content</p>}
</motion.div>
```

## Carousel

```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: -width, right: 0 }}
  className="flex"
>
  {images.map((img) => (
    <img key={img.id} src={img.url} />
  ))}
</motion.div>
```
