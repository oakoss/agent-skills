---
title: Troubleshooting
description: Common Motion issues including AnimatePresence exit bugs, Tailwind conflicts, Next.js client directive, layout glitches, React 19 StrictMode drag bug, and framer-motion naming migration
tags:
  [
    troubleshooting,
    animate-presence,
    tailwind,
    nextjs,
    layout,
    react-19,
    migration,
  ]
---

# Troubleshooting

## Naming Migration: framer-motion → motion

The library was renamed from **Framer Motion** to **Motion** in late 2024. Claude's training may reference the old name.

| Old (don't use)                                | New (use this)                                |
| ---------------------------------------------- | --------------------------------------------- |
| `npm install framer-motion`                    | `npm install motion`                          |
| `from 'framer-motion'`                         | `from 'motion/react'`                         |
| `import { motion } from 'framer-motion'`       | `import { motion } from 'motion/react'`       |
| `import { useAnimation } from 'framer-motion'` | `import { useAnimation } from 'motion/react'` |
| `import { LayoutGroup } from 'framer-motion'`  | `import { LayoutGroup } from 'motion/react'`  |

The API is unchanged — only the package name and import path changed. All variants, hooks, and components work the same way.

For React 19 compatibility, always use `motion/react` (not `framer-motion`).

## AnimatePresence Exit Not Playing

AnimatePresence must stay mounted. Condition goes inside, not outside:

```tsx
// Wrong
{
  isVisible && (
    <AnimatePresence>
      <motion.div>...</motion.div>
    </AnimatePresence>
  );
}

// Correct
<AnimatePresence>
  {isVisible && <motion.div key="unique">...</motion.div>}
</AnimatePresence>;
```

Also ensure every direct child has a unique `key` prop.

## AnimatePresence Exit Gets Stuck

Don't unmount motion components while AnimatePresence handles their exit. Use conditional rendering only on direct AnimatePresence children.

## Tailwind Transitions Conflict

Remove `transition-*`, `duration-*` classes from elements using Motion animate props:

```tsx
// Wrong — stuttering
<motion.div className="transition-all" animate={{ x: 100 }} />

// Correct
<motion.div animate={{ x: 100 }} />
```

## Next.js "use client" Missing

Motion components need `"use client"` directive in App Router. Import from `motion/react-client` for optimized client wrapper.

Error message: `Error: motion is not defined`

## Scrollable Container Layout Glitches

Add `layoutScroll` prop to the scrollable parent:

```tsx
<motion.div layoutScroll className="overflow-auto">
  {items.map((item) => (
    <motion.div key={item.id} layout>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

## Fixed Position Layout Animations

Add `layoutRoot` to the fixed container:

```tsx
<motion.div layoutRoot className="fixed top-0 left-0">
  <motion.div layout>Content</motion.div>
</motion.div>
```

## Layout Animations in Scaled Containers

Use `transformTemplate` to correct for parent scale:

```tsx
const scale = 2;
<div style={{ transform: `scale(${scale})` }}>
  <motion.div
    layout
    transformTemplate={(_, generated) => {
      const match = /translate3d\((.+)px,\s?(.+)px,\s?(.+)px\)/.exec(generated);
      if (match) {
        const [, x, y, z] = match;
        return `translate3d(${Number(x) / scale}px, ${Number(y) / scale}px, ${Number(z) / scale}px)`;
      }
      return generated;
    }}
  >
    Content
  </motion.div>
</div>;
```

## Reorder Component Limitations

Reorder auto-scroll only works inside `overflow: auto/scroll` containers, not page-level scroll. For complex drag-and-drop (multi-row, cross-column), use DnD Kit instead.

## React 19 StrictMode Drag Bug

Top-to-bottom drag breaks with React 19 + StrictMode + some component libraries. Temporarily disable StrictMode for drag-heavy features if affected.

## popLayout Sub-Pixel Shift

`AnimatePresence mode="popLayout"` rounds sub-pixel values causing 1px shift. Use whole pixel values for dimensions or avoid popLayout for precision-sensitive layouts.

## Percentage Values in Flex Containers

Percentage values in `initial` with flex containers can produce unexpected results. Convert to pixel values instead.

## layoutId + AnimatePresence

When using `layoutId` with `AnimatePresence`, wrap in `<LayoutGroup>`:

```tsx
import { LayoutGroup } from 'motion/react';

<LayoutGroup>
  <AnimatePresence>
    <motion.div layoutId="shared">Content</motion.div>
  </AnimatePresence>
</LayoutGroup>;
```

## Exit Props on Staggered Modal Children

Exit animations on staggered children inside modals can cause visual glitches. Remove exit or set `transition: { duration: 0 }` on children.
