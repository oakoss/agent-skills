---
title: Next.js Integration
description: Motion with Next.js App Router client component patterns, Pages Router setup, known issues with soft navigation and Reorder, and deployment checklist
tags: [nextjs, app-router, pages-router, use-client, ssr, react-client]
---

# Next.js Integration

## App Router (Next.js 13+)

Motion requires Client Components. Three patterns in order of recommendation:

### Pattern 1: Wrapper Component (Recommended)

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

### Pattern 2: Direct Client Component

```tsx
'use client';
import { motion } from 'motion/react-client';

export default function Page() {
  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>;
}
```

Downside: entire page becomes client-rendered.

### Pattern 3: Server Data + Client Animation

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

### Import: `motion/react-client` vs `motion/react`

Always use `motion/react-client` in App Router — it excludes server-side code, reducing client JavaScript.

## Pages Router (Next.js 12)

Works out of the box with `import { motion } from 'motion/react'`. No `"use client"` needed.

For hydration errors, use dynamic import:

```tsx
import dynamic from 'next/dynamic';

const AnimatedComponent = dynamic(
  () => import('@/components/AnimatedComponent'),
  { ssr: false },
);
```

## Known Issues

### Soft Navigation Breaks Exit Animations

Next.js App Router soft navigation doesn't trigger React unmount, so AnimatePresence exit animations don't fire for page transitions.

**Solution**: Use AnimatePresence for component-level animations only (modals, dropdowns, tooltips). For page enter animations, use `template.tsx`:

```tsx
// src/app/template.tsx
'use client';
import { motion } from 'motion/react-client';

export default function Template({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

### Reorder Component Incompatibility

Motion's `<Reorder>` component has issues with Next.js routing (stuck states, items don't reorder). Use `@dnd-kit/core` instead.

### Large Bundle Size

Use LazyMotion to reduce from 34 KB → 4.6 KB:

```tsx
'use client';
import { LazyMotion, domAnimation } from 'motion/react-client';

export function MotionProvider({ children }: { children: ReactNode }) {
  return <LazyMotion features={domAnimation}>{children}</LazyMotion>;
}

export { m as motion } from 'motion/react-client';
```

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
- Tested with `prefers-reduced-motion` enabled
- Bundle analyzed (target < 5 KB for Motion)
