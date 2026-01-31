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

## Naming Migration: framer-motion to motion

The library was renamed from Framer Motion to Motion in late 2024.

| Old (do not use)                               | New (use this)                                |
| ---------------------------------------------- | --------------------------------------------- |
| `npm install framer-motion`                    | `npm install motion`                          |
| `from "framer-motion"`                         | `from "motion/react"`                         |
| `import { motion } from "framer-motion"`       | `import { motion } from "motion/react"`       |
| `import { useAnimation } from "framer-motion"` | `import { useAnimation } from "motion/react"` |
| `import { LayoutGroup } from "framer-motion"`  | `import { LayoutGroup } from "motion/react"`  |

The API is unchanged -- only the package name and import path changed. All variants, hooks, and components work the same way. No breaking changes in Motion v12.

## AnimatePresence Exit Not Playing

AnimatePresence must stay mounted. The condition goes inside, not outside:

```tsx
// Wrong -- AnimatePresence unmounts with condition
{
  isVisible && (
    <AnimatePresence>
      <motion.div>...</motion.div>
    </AnimatePresence>
  );
}

// Correct -- AnimatePresence stays mounted
<AnimatePresence>
  {isVisible && <motion.div key="unique">...</motion.div>}
</AnimatePresence>;
```

Every direct child of AnimatePresence must have a unique `key` prop.

## AnimatePresence Exit Gets Stuck

When a child component inside AnimatePresence unmounts immediately after exit triggers, the exit state can get stuck. Only use conditional rendering on direct AnimatePresence children, not on nested motion components.

## Exit Props on Staggered Modal Children

Exit animations on staggered children inside modals can prevent the modal from unmounting (backdrop remains visible). Remove exit from children or set instant duration:

```tsx
// Wrong -- staggered children with exit prevent modal removal
<motion.li
  key={item.id}
  exit={{ opacity: 1, scale: 1 }}
>
  {item.content}
</motion.li>

// Correct -- instant exit or no exit on children
<motion.li
  key={item.id}
  exit={{ opacity: 0, transition: { duration: 0 } }}
>
  {item.content}
</motion.li>
```

## Tailwind Transitions Conflict

Remove `transition-*`, `duration-*` classes from elements using Motion animate props:

```tsx
// Wrong -- stuttering animations
<motion.div className="transition-all" animate={{ x: 100 }} />

// Correct
<motion.div animate={{ x: 100 }} />
```

Motion uses inline styles or native browser animations. Tailwind CSS transitions interfere with Motion's animation system.

## Next.js "use client" Missing

Motion components need `"use client"` directive in App Router. Import from `motion/react-client` for optimized client bundles.

Error: `Error: motion is not defined`

## Scrollable Container Layout Glitches

Add `layoutScroll` prop to the scrollable parent so layout animations account for scroll offset:

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

Add `layoutRoot` to the fixed container so layout animations account for page scroll:

```tsx
<motion.div layoutRoot className="fixed top-0 left-0">
  <motion.div layout>Content</motion.div>
</motion.div>
```

## Layout Animations in Scaled Containers

Layout animations use pixel coordinates, but parent scale transforms affect visual coordinates. Use `transformTemplate` to correct:

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

Limitation: only corrects layout animations, requires knowing the parent scale value.

## Reorder Component Limitations

Reorder auto-scroll only works inside `overflow: auto/scroll` containers, not page-level scroll:

```tsx
// Wrong -- page-level scrolling (auto-scroll fails)
<body style={{ height: "200vh" }}>
  <Reorder.Group values={items} onReorder={setItems}>
    {/* Auto-scroll does not trigger at viewport edges */}
  </Reorder.Group>
</body>

// Correct -- container with overflow
<div style={{ height: "300px", overflow: "auto" }}>
  <Reorder.Group values={items} onReorder={setItems}>
    {items.map((item) => (
      <Reorder.Item key={item.id} value={item}>
        {item.content}
      </Reorder.Item>
    ))}
  </Reorder.Group>
</div>
```

For complex drag-and-drop (multi-row, cross-column, page-level scroll), use `@dnd-kit/core` + `@dnd-kit/sortable`.

## React 19 StrictMode Drag Bug

Top-to-bottom drag breaks with React 19 + StrictMode + some component libraries (e.g., Ant Design). Dragged element position appears offset. Does not occur in React 18 or React 19 without StrictMode. Bottom-to-top drag works fine. Temporarily disable StrictMode for drag-heavy features if affected.

## popLayout Sub-Pixel Shift

`AnimatePresence mode="popLayout"` rounds sub-pixel values from `getBoundingClientRect`, causing a visible 1px shift before exit. Can cause text wrapping changes. Use whole pixel values for dimensions or avoid popLayout for precision-sensitive layouts.

## Percentage Values in Flex Containers

Percentage-based `x` or `y` values in `initial` with flex containers using `justify-content: center` can cause layout animations to teleport instead of animating. Convert to pixel values by calculating container width.

## layoutId + AnimatePresence

When using `layoutId` inside `AnimatePresence`, wrap in `<LayoutGroup>` to prevent unmount failures:

```tsx
import { LayoutGroup, AnimatePresence } from 'motion/react';

<LayoutGroup>
  <AnimatePresence>
    {items.map((item) => (
      <motion.div key={item.id} layoutId={item.id}>
        {item.content}
      </motion.div>
    ))}
  </AnimatePresence>
</LayoutGroup>;
```

## Soft Navigation Breaks Exit Animations

Next.js App Router soft navigation does not trigger React unmount, so AnimatePresence exit animations do not fire for page transitions. Use AnimatePresence for component-level animations only (modals, dropdowns). For page enter animations, use `template.tsx`.
