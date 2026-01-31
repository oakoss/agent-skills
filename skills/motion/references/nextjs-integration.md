---
title: Next.js Integration
description: Motion with Next.js App Router client component patterns, motion/react-client import, Pages Router setup, template.tsx for page transitions, and deployment checklist
tags: [nextjs, app-router, pages-router, use-client, ssr, react-client]
---

# Next.js Integration

Motion requires React 18.2+. Compatible with both App Router and Pages Router.

## App Router

Motion components only work in Client Components. Three patterns ordered by recommendation:

### Pattern 1: Wrapper Component (Recommended)

Create a single client component that re-exports Motion:

```tsx
// src/components/motion-client.tsx
'use client';
import * as motion from 'motion/react-client';
export { motion };
export {
  AnimatePresence,
  MotionConfig,
  LazyMotion,
  LayoutGroup,
  useMotionValue,
  useTransform,
  useScroll,
  useSpring,
  useAnimate,
  useInView,
} from 'motion/react-client';
```

```tsx
// src/app/page.tsx (Server Component)
import { motion } from '@/components/motion-client';

export default function Page() {
  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>;
}
```

Use `motion/react-client` instead of `motion/react` in App Router -- it excludes server-side code, reducing client JavaScript.

### Pattern 2: Direct Client Component

```tsx
'use client';
import { motion } from 'motion/react-client';

export default function AnimatedSection() {
  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>;
}
```

Downside: entire component tree becomes client-rendered.

### Pattern 3: Server Data + Client Animation

Keep data fetching on the server, pass to client components for animation:

```tsx
// src/components/AnimatedCard.tsx
'use client';
import { motion } from 'motion/react-client';

export function AnimatedCard({
  product,
  index,
}: {
  product: Product;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.05 }}
    >
      <h3>{product.name}</h3>
    </motion.div>
  );
}
```

```tsx
// src/app/products/page.tsx (Server Component)
import { AnimatedCard } from '@/components/AnimatedCard';

export default async function ProductsPage() {
  const products = await getProducts();
  return (
    <div className="grid grid-cols-3 gap-4">
      {products.map((product, i) => (
        <AnimatedCard key={product.id} product={product} index={i} />
      ))}
    </div>
  );
}
```

### MotionConfig Provider

```tsx
// src/components/MotionProvider.tsx
'use client';
import { MotionConfig } from 'motion/react-client';

export function MotionProvider({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
```

Add to root layout for global reduced-motion support.

### LazyMotion in App Router

```tsx
// src/components/LazyMotionProvider.tsx
'use client';
import { LazyMotion, domAnimation } from 'motion/react-client';

export function LazyMotionProvider({ children }: { children: ReactNode }) {
  return <LazyMotion features={domAnimation}>{children}</LazyMotion>;
}

export { m as motion } from 'motion/react-client';
```

Reduces Motion bundle from 34 KB to 4.6 KB.

## Pages Router

Works out of the box. No `"use client"` needed:

```tsx
import { motion } from 'motion/react';

export default function Page() {
  return <motion.div>No "use client" needed</motion.div>;
}
```

For hydration errors, use dynamic import:

```tsx
import dynamic from 'next/dynamic';

const AnimatedComponent = dynamic(
  () => import('@/components/AnimatedComponent'),
  { ssr: false },
);
```

## Page Transitions with template.tsx

Next.js App Router soft navigation does not trigger React unmount, so AnimatePresence exit animations do not fire for route changes. Use `template.tsx` for page enter animations:

```tsx
// src/app/template.tsx
'use client';
import { motion } from 'motion/react-client';

export default function Template({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

`template.tsx` re-mounts on every navigation (unlike `layout.tsx`), making it the correct place for page enter animations.

For exit animations, use AnimatePresence at the component level (modals, dropdowns, tooltips) rather than page level.

## Known Issues

### Reorder Component Incompatibility

Motion's `<Reorder>` component has issues with Next.js routing (stuck states, items not reordering). Auto-scroll only works inside `overflow: auto/scroll` containers, not page-level scroll. For complex drag-and-drop (multi-row, cross-column), use `@dnd-kit/core` instead.

### Code Splitting

For animations not needed on initial load:

```tsx
import dynamic from 'next/dynamic';

const AnimatedHero = dynamic(() => import('@/components/AnimatedHero'), {
  ssr: false,
});
```

## Deployment Checklist

- All Motion files have `"use client"` directive
- Using `motion/react-client` import (not `motion/react`)
- LazyMotion enabled for bundle size
- MotionConfig with `reducedMotion="user"` set up
- No Motion usage in Server Components
- AnimatePresence only for component-level animations (not routes)
- Page enter animations use `template.tsx`
- Tested with `prefers-reduced-motion` enabled
- Bundle analyzed (target < 5 KB for Motion)
